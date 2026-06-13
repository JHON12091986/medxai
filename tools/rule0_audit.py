#!/usr/bin/env python3
"""
rule0_audit.py — RULE 0 Compliance Auditor for NINA.
Parses logs/ninagate.log and reports local vs cloud routing ratio per session.
Run at end of every session: python3 tools/rule0_audit.py
Also callable with --hours N to scope the window.
"""
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

NINA_ROOT = Path(__file__).parent.parent.resolve()
LOG = NINA_ROOT / "logs" / "ninagate.log"
SCRATCH = NINA_ROOT / "data" / "gemini_scratch.jsonl"

# Banned tool patterns to scan for in gemini_scratch.jsonl
BANNED_PATTERNS = [
    ("run_shell_command: cat ", "nf file read"),
    ("run_shell_command: grep", "nf file grep"),
    ("run_shell_command: git log", "nf git log"),
    ("run_shell_command: git diff", "nf file diff"),
    ("run_shell_command: git status", "nf git changed"),
    ("run_shell_command: ls", "nf code index"),
    ("run_shell_command: find", "nf code index"),
    ("run_shell_command: head", "nf file read"),
    ("run_shell_command: tail", "nf file read"),
    ("run_shell_command: wc", "nf file read"),
]


def parse_log(hours: int = 8):
    """Parse ninagate.log for the last N hours."""
    if not LOG.exists():
        return 0, 0, 0, []

    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    total, local, cloud = 0, 0, 0
    violations = []  # SIMPLE tasks that still went to cloud

    for raw in LOG.read_text(errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            e = json.loads(raw)
            ts_str = e.get("ts", "")
            if not ts_str:
                continue
            # Handle both naive and aware datetimes
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                continue
            total += 1
            provider = e.get("provider", "")
            task_type = e.get("task_type", "")
            if provider == "ollama":
                local += 1
            else:
                cloud += 1
                if task_type == "SIMPLE":
                    violations.append(e)
        except Exception:
            continue

    return total, local, cloud, violations


def scan_banned_tools(hours: int = 8) -> list[dict]:
    """Scan gemini_scratch.jsonl for banned tool patterns."""
    if not SCRATCH.exists():
        return []

    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    hits = []

    for raw in SCRATCH.read_text(errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            e = json.loads(raw)
            ts_str = e.get("t", "")
            if not ts_str:
                continue
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                continue
            detail = e.get("detail", "")
            for pattern, alt in BANNED_PATTERNS:
                if pattern.lower() in detail.lower():
                    hits.append({
                        "ts": ts_str,
                        "detail": detail,
                        "pattern": pattern.strip(),
                        "alternative": alt,
                    })
        except Exception:
            continue

    return hits


def audit(hours: int = 8, write_scratch: bool = True) -> dict:
    total, local, cloud, cloud_violations = parse_log(hours)
    banned_hits = scan_banned_tools(hours)

    local_pct = (local / total * 100) if total else 0.0
    met_target = local_pct >= 66.0

    status = "ok" if met_target else "fail"
    icon = "✅" if met_target else "❌"

    summary_line = (
        f"RULE0 AUDIT ({hours}h): {local}/{total} local ({local_pct:.1f}%). "
        f"CloudViolations={len(cloud_violations)} BannedTools={len(banned_hits)}. "
        f"{icon} {'TARGET MET (≥66%)' if met_target else 'BELOW 66% TARGET'}"
    )

    result = {
        "hours": hours,
        "total_requests": total,
        "local_requests": local,
        "cloud_requests": cloud,
        "local_pct": round(local_pct, 2),
        "target_met": met_target,
        "cloud_violations": len(cloud_violations),
        "banned_tool_hits": len(banned_hits),
        "status": status,
        "summary": summary_line,
    }

    # Append to gemini_scratch.jsonl
    if write_scratch:
        scratch_entry = {
            "t": datetime.now(tz=timezone.utc).isoformat(),
            "step": -99,
            "action": "audit",
            "file": "logs/ninagate.log",
            "detail": summary_line,
            "status": status,
        }
        SCRATCH.parent.mkdir(parents=True, exist_ok=True)
        with open(SCRATCH, "a") as f:
            f.write(json.dumps(scratch_entry) + "\n")

    return result, cloud_violations, banned_hits


def main():
    parser = argparse.ArgumentParser(description="RULE 0 Compliance Auditor")
    parser.add_argument("--hours", type=int, default=8,
                        help="Audit window in hours (default: 8)")
    parser.add_argument("--no-scratch", action="store_true",
                        help="Skip writing result to gemini_scratch.jsonl")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON result")
    args = parser.parse_args()

    result, cloud_violations, banned_hits = audit(
        hours=args.hours,
        write_scratch=not args.no_scratch
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # ── Human-readable output ──────────────────────────────────────────
    print()
    print("══════════════════════════════════════════════════════")
    print("  NINA — RULE 0 COMPLIANCE AUDIT")
    print("══════════════════════════════════════════════════════")
    print(f"  Window : last {args.hours} hours")
    print(f"  Total  : {result['total_requests']} routed requests")
    print(f"  Local  : {result['local_requests']} ({result['local_pct']:.1f}%) → ollama/NinaFlash")
    print(f"  Cloud  : {result['cloud_requests']} ({100 - result['local_pct']:.1f}%) → cloud LLM")
    print(f"  Target : ≥66% local")
    print()

    if result["target_met"]:
        print("  ✅  TARGET MET — local routing is compliant")
    else:
        gap = 66.0 - result["local_pct"]
        print(f"  ❌  BELOW TARGET — need {gap:.1f}% more local routing")

    if cloud_violations:
        print()
        print(f"  ⚠️  SIMPLE→Cloud violations ({len(cloud_violations)}):")
        for v in cloud_violations[:5]:
            ms = v.get("total_ms", 0)
            print(f"     [{v.get('ts','?')[-19:]}] provider={v.get('provider','?')} latency={ms:.0f}ms")
        if len(cloud_violations) > 5:
            print(f"     ... and {len(cloud_violations) - 5} more")

    if banned_hits:
        print()
        print(f"  🚫  Banned tool usage ({len(banned_hits)}):")
        seen = set()
        for h in banned_hits:
            key = h["pattern"]
            if key not in seen:
                seen.add(key)
                print(f"     USED: {h['pattern']}")
                print(f"     USE:  {h['alternative']} instead")

    print()
    print("══════════════════════════════════════════════════════")
    print()

    sys.exit(0 if result["target_met"] else 1)


if __name__ == "__main__":
    main()
