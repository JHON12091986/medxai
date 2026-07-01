#!/usr/bin/env python3
"""
Nina Telemetry Digest — reads telemetry.jsonl, outputs aggregated stats.
Usage: python3 tools/telemetry_digest.py [--json] [--last N]
NINA_FEATURE: telemetry-digest v1.0
Writes: exports/telemetry_digest.json (if --export)
"""
import json, sys, argparse, statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_FILE = REPO_ROOT / "telemetry.jsonl"


def load_events(last_n=None):
    if not TELEMETRY_FILE.exists():
        return []
    lines = TELEMETRY_FILE.read_text().strip().splitlines()
    if last_n:
        lines = lines[-last_n:]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except Exception:
            pass
    return events


def digest(events):
    latencies = defaultdict(list)
    errors = defaultdict(int)
    models = defaultdict(int)
    providers = defaultdict(int)
    total = len(events)
    error_count = 0

    for e in events:
        model = e.get("model", "unknown")
        provider = e.get("provider", "unknown")
        latency = e.get("latency_ms") or e.get("duration_ms")
        status = e.get("status", "ok")
        err = e.get("error") or e.get("err")

        models[model] += 1
        providers[provider] += 1
        if latency:
            latencies[provider].append(float(latency))
        if status not in ("ok", "success", "200") or err:
            error_count += 1
            errors[provider] += 1

    provider_stats = {}
    for p, lats in latencies.items():
        provider_stats[p] = {
            "calls": providers[p],
            "errors": errors.get(p, 0),
            "error_rate": round(errors.get(p, 0) / providers[p], 3) if providers[p] else 0,
            "p50_ms": round(statistics.median(lats), 1) if lats else None,
            "p95_ms": round(sorted(lats)[int(len(lats) * 0.95)], 1) if len(lats) >= 2 else None,
            "min_ms": round(min(lats), 1) if lats else None,
            "max_ms": round(max(lats), 1) if lats else None,
        }

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_events": total,
        "total_errors": error_count,
        "overall_error_rate": round(error_count / total, 3) if total else 0,
        "top_models": dict(sorted(models.items(), key=lambda x: -x[1])[:10]),
        "provider_stats": provider_stats,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Nina telemetry digest")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    ap.add_argument("--last", type=int, default=None, help="Only process last N events")
    ap.add_argument("--export", action="store_true", help="Write to exports/telemetry_digest.json")
    args = ap.parse_args()

    events = load_events(args.last)
    result = digest(events)

    if args.export:
        out = REPO_ROOT / "exports" / "telemetry_digest.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(f"✓ Exported to {out}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Telemetry Digest — {result['total_events']} events")
        print(f"  Overall error rate : {result['overall_error_rate']*100:.1f}%")
        print(f"  Top models         : {', '.join(list(result['top_models'].keys())[:5])}")
        print("  Provider stats:")
        for p, s in result["provider_stats"].items():
            print(f"    {p:20s}  calls={s['calls']}  err={s['error_rate']*100:.0f}%  p50={s['p50_ms']}ms  p95={s['p95_ms']}ms")
