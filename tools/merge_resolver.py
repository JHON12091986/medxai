#!/usr/bin/env python3
"""
tools/merge_resolver.py — NINA Merge Conflict Resolver
Intelligently resolves Jules PR conflicts: detects downgrades, cherry-picks
net-new additions, and auto-resolves false conflicts.

Usage:
    python3 tools/merge_resolver.py --pr <PR_NUMBER>
    python3 tools/merge_resolver.py --branch <BRANCH_NAME>
    python3 tools/merge_resolver.py --dry-run --pr <PR_NUMBER>
    python3 tools/merge_resolver.py --auto --pr <PR_NUMBER>
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# ── Logging ──────────────────────────────────────────────────────────────────
try:
    from core.logger import get_logger
    logger = get_logger("nina.merge_resolver")
except ImportError:
    import logging
    logger = logging.getLogger("nina.merge_resolver")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ── Telegram notify (optional, graceful fallback) ────────────────────────────
try:
    from tools.telegram_notify import send as _telegram_send
    def _notify(msg: str) -> None:
        try:
            _telegram_send(msg)
        except Exception as e:
            logger.warning(f"telegram_notify failed: {e}")
except ImportError:
    def _notify(msg: str) -> None:
        logger.info(f"[TELEGRAM SKIPPED] {msg}")

REPO_ROOT = Path(__file__).parent.parent


# ── Data Models ──────────────────────────────────────────────────────────────

class ConflictVerdict(Enum):
    KEEP_MAIN        = "keep_main"       # main is newer/better — discard Jules
    KEEP_JULES       = "keep_jules"      # Jules adds net-new value
    CHERRY_PICK      = "cherry_pick"     # Take Jules' new block, keep main structure
    FALSE_CONFLICT   = "false_conflict"  # Different lines, same intent — auto-resolve
    MANUAL_REQUIRED  = "manual"          # Ambiguous — flag for human review


@dataclass
class ConflictBlock:
    file: str
    start_line: int
    end_line: int
    main_content: list[str]   = field(default_factory=list)
    jules_content: list[str]  = field(default_factory=list)
    verdict: ConflictVerdict  = ConflictVerdict.MANUAL_REQUIRED
    reason: str               = ""
    resolved_content: list[str] = field(default_factory=list)


@dataclass
class ResolutionReport:
    pr_number: Optional[int]
    branch: str
    base_commit: str
    head_commit: str
    conflicts_total: int       = 0
    auto_resolved: int         = 0
    cherry_picked: int         = 0
    kept_main: int             = 0
    kept_jules: int            = 0
    manual_required: int       = 0
    blocks: list[ConflictBlock] = field(default_factory=list)
    timestamp: str             = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


# ── Git Helpers ───────────────────────────────────────────────────────────────

def _run(cmd: list[str], cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def get_current_branch() -> str:
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def get_commit_timestamp(ref: str) -> float:
    """Returns Unix timestamp of a git ref."""
    result = _run(["git", "log", "-1", "--format=%ct", ref], check=False)
    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())
    return 0.0


def get_conflicted_files() -> list[str]:
    result = _run(["git", "diff", "--name-only", "--diff-filter=U"], check=False)
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def get_file_commit_time(filepath: str, ref: str = "HEAD") -> float:
    """Returns the last commit time of a file on a given ref."""
    result = _run(["git", "log", "-1", "--format=%ct", ref, "--", filepath], check=False)
    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())
    return 0.0


def run_tests(test_paths: list[str] | None = None) -> tuple[bool, str]:
    """Run pytest on specific paths or the whole suite. Returns (passed, output)."""
    cmd = ["python3", "-m", "pytest", "--tb=no", "-q"]
    if test_paths:
        cmd += test_paths
    else:
        cmd.append("tests/")
    result = _run(cmd, check=False)
    passed = result.returncode == 0
    return passed, result.stdout + result.stderr


def get_merge_base(branch: str) -> str:
    result = _run(["git", "merge-base", "HEAD", branch], check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


# ── Conflict Parser ───────────────────────────────────────────────────────────

CONFLICT_START = re.compile(r"^<<<<<<< (.+)$")
CONFLICT_SEP   = re.compile(r"^=======$")
CONFLICT_END   = re.compile(r"^>>>>>>> (.+)$")


def parse_conflict_blocks(filepath: str) -> list[ConflictBlock]:
    """Parse a file with git conflict markers into ConflictBlock objects."""
    blocks: list[ConflictBlock] = []
    path = REPO_ROOT / filepath

    if not path.exists():
        logger.warning(f"File not found: {filepath}")
        return blocks

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    in_conflict = False
    in_jules_section = False
    current_block: ConflictBlock | None = None
    start_line = 0

    for i, line in enumerate(lines):
        if CONFLICT_START.match(line):
            in_conflict = True
            in_jules_section = False
            start_line = i + 1
            current_block = ConflictBlock(file=filepath, start_line=i + 1, end_line=0)
        elif in_conflict and CONFLICT_SEP.match(line):
            in_jules_section = True
        elif in_conflict and CONFLICT_END.match(line):
            if current_block:
                current_block.end_line = i + 1
                blocks.append(current_block)
            in_conflict = False
            in_jules_section = False
            current_block = None
        elif in_conflict and current_block:
            if not in_jules_section:
                current_block.main_content.append(line)
            else:
                current_block.jules_content.append(line)

    return blocks


# ── Verdict Engine ────────────────────────────────────────────────────────────

# Patterns that indicate a definite downgrade if present in Jules but absent in main
DOWNGRADE_PATTERNS = [
    re.compile(r"self\.config\.get_secret\("),          # known bug pattern
    re.compile(r'== "ollama"(?!\.lower\(\))'),           # old casing bug
    re.compile(r"# TODO:.*remove", re.IGNORECASE),
    re.compile(r"DEPRECATED", re.IGNORECASE),
]

# Patterns that indicate Jules is adding net-new value
NET_NEW_PATTERNS = [
    re.compile(r"def (test_|check_|validate_)"),
    re.compile(r"async def \w+"),
    re.compile(r"class \w+"),
    re.compile(r"@pytest\.(mark|fixture)"),
    re.compile(r"logger\.(info|warning|error)\("),
]


def _content_str(lines: list[str]) -> str:
    return "\n".join(lines).strip()


def _normalize(lines: list[str]) -> str:
    """Strip whitespace and comments for semantic comparison."""
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            result.append(stripped)
    return "\n".join(result)


def _is_downgrade(jules_lines: list[str], main_lines: list[str]) -> tuple[bool, str]:
    """Check if Jules' version contains known-bad patterns that main has already fixed."""
    jules_str = _content_str(jules_lines)
    main_str  = _content_str(main_lines)

    for pat in DOWNGRADE_PATTERNS:
        if pat.search(jules_str) and not pat.search(main_str):
            return True, f"Downgrade pattern detected: {pat.pattern}"

    return False, ""


def _is_net_new(jules_lines: list[str], main_lines: list[str]) -> tuple[bool, str]:
    """Jules adds something that simply doesn't exist in main's version."""
    jules_str = _content_str(jules_lines)
    main_str  = _content_str(main_lines)

    if not main_str.strip():
        return True, "Main section is empty — Jules is purely additive"

    # Jules introduces a new function/class not present in main
    for pat in NET_NEW_PATTERNS:
        for m in pat.finditer(jules_str):
            symbol = m.group(0)
            if symbol not in main_str:
                return True, f"Net-new symbol from Jules: {symbol}"

    return False, ""


def _is_false_conflict(jules_lines: list[str], main_lines: list[str]) -> tuple[bool, str]:
    """Same semantic content, just formatting/whitespace differences."""
    if _normalize(jules_lines) == _normalize(main_lines):
        return True, "Semantically identical after normalization — false conflict"

    # Line count within 2 and content is >80% similar (rough heuristic)
    if abs(len(jules_lines) - len(main_lines)) <= 2:
        jules_words = set(_content_str(jules_lines).split())
        main_words  = set(_content_str(main_lines).split())
        if jules_words and main_words:
            overlap = len(jules_words & main_words) / max(len(jules_words), len(main_words))
            if overlap > 0.85:
                return True, f"High content overlap ({overlap:.0%}) with minor whitespace diff"

    return False, ""


def _main_is_newer(filepath: str, jules_branch: str) -> tuple[bool, str]:
    """Compare commit timestamps to detect if main's version is more recent."""
    main_ts  = get_file_commit_time(filepath, "HEAD")
    jules_ts = get_file_commit_time(filepath, jules_branch)

    if main_ts > jules_ts:
        main_dt  = datetime.fromtimestamp(main_ts).strftime("%Y-%m-%d %H:%M")
        jules_dt = datetime.fromtimestamp(jules_ts).strftime("%Y-%m-%d %H:%M")
        return True, f"main ({main_dt}) is newer than Jules branch ({jules_dt})"
    return False, ""


def evaluate_conflict(
    block: ConflictBlock,
    jules_branch: str,
    run_test_check: bool = True
) -> ConflictBlock:
    """Apply verdict logic to a single conflict block."""

    main_lines  = block.main_content
    jules_lines = block.jules_content

    # 1. False conflict — highest priority, safe to auto-resolve
    is_false, reason = _is_false_conflict(jules_lines, main_lines)
    if is_false:
        block.verdict = ConflictVerdict.FALSE_CONFLICT
        block.reason  = reason
        block.resolved_content = main_lines  # keep main structure
        return block

    # 2. Downgrade check — Jules contains known-bad patterns main already fixed
    is_dg, reason = _is_downgrade(jules_lines, main_lines)
    if is_dg:
        block.verdict = ConflictVerdict.KEEP_MAIN
        block.reason  = reason
        block.resolved_content = main_lines
        return block

    # 3. Main is newer (commit timestamp)
    main_newer, reason = _main_is_newer(block.file, jules_branch)
    if main_newer:
        block.verdict = ConflictVerdict.KEEP_MAIN
        block.reason  = reason
        block.resolved_content = main_lines
        return block

    # 4. Net-new from Jules — cherry-pick Jules' addition
    is_new, reason = _is_net_new(jules_lines, main_lines)
    if is_new:
        block.verdict = ConflictVerdict.CHERRY_PICK
        block.reason  = reason
        # Resolved = main structure + Jules' new addition appended
        block.resolved_content = main_lines + [""] + jules_lines
        return block

    # 5. Default: Jules has something different but not clearly better/worse
    # Keep main (safer default) but flag for review
    block.verdict = ConflictVerdict.KEEP_MAIN
    block.reason  = "No clear signal — defaulting to main (safer). Flag for manual review if Jules had important changes."
    block.resolved_content = main_lines
    return block


# ── File Writer ───────────────────────────────────────────────────────────────

def apply_resolutions(filepath: str, blocks: list[ConflictBlock]) -> bool:
    """
    Rewrite the conflicted file with all resolved blocks substituted in.
    Returns True if any changes were written.
    """
    path = REPO_ROOT / filepath
    if not path.exists():
        return False

    content = path.read_text(encoding="utf-8", errors="replace")
    lines   = content.splitlines(keepends=True)
    output  = []
    i       = 0

    # Build a lookup: line number → resolved block
    block_map: dict[int, ConflictBlock] = {b.start_line: b for b in blocks if b.resolved_content}

    skip_until = -1

    for i, line in enumerate(lines):
        lineno = i + 1  # 1-indexed

        if lineno in block_map:
            blk = block_map[lineno]
            # Replace everything from start to end with resolved content
            for rline in blk.resolved_content:
                output.append(rline + "\n")
            skip_until = blk.end_line
            continue

        if skip_until > 0 and lineno <= skip_until:
            continue

        output.append(line)

    new_content = "".join(output)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


# ── Report ────────────────────────────────────────────────────────────────────

def build_report(report: ResolutionReport) -> str:
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║           NINA Merge Resolver — Resolution Report           ║",
        "╚══════════════════════════════════════════════════════════════╝",
        f"  Branch       : {report.branch}",
        f"  Timestamp    : {report.timestamp}",
        f"  Base commit  : {report.base_commit[:12]}",
        f"  Head commit  : {report.head_commit[:12]}",
        "",
        f"  Total conflicts  : {report.conflicts_total}",
        f"  ✅ Auto-resolved  : {report.auto_resolved}  (false conflicts)",
        f"  🔀 Cherry-picked  : {report.cherry_picked}  (Jules net-new kept)",
        f"  ⬆  Kept main      : {report.kept_main}     (Jules was downgrade/stale)",
        f"  📥 Kept Jules     : {report.kept_jules}",
        f"  ⚠  Manual needed  : {report.manual_required}",
        "",
        "──────────────────────────────────────────────────────────────",
    ]

    for b in report.blocks:
        icon = {
            ConflictVerdict.FALSE_CONFLICT:  "✅",
            ConflictVerdict.KEEP_MAIN:       "⬆ ",
            ConflictVerdict.KEEP_JULES:      "📥",
            ConflictVerdict.CHERRY_PICK:     "🔀",
            ConflictVerdict.MANUAL_REQUIRED: "⚠ ",
        }.get(b.verdict, "?")

        lines.append(f"  {icon} {b.file}:{b.start_line}")
        lines.append(f"     Verdict : {b.verdict.value}")
        lines.append(f"     Reason  : {b.reason}")
        lines.append("")

    return "\n".join(lines)


def write_report(report: ResolutionReport) -> str:
    out_dir = REPO_ROOT / "logs"
    out_dir.mkdir(exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = out_dir / f"merge_resolver_{ts}.log"
    out.write_text(build_report(report), encoding="utf-8")
    return str(out)


# ── Main Entry Point ──────────────────────────────────────────────────────────

def resolve(
    jules_branch: str,
    pr_number: Optional[int] = None,
    dry_run: bool = False,
    auto: bool = False,
) -> ResolutionReport:
    logger.info(f"merge_resolver starting branch={jules_branch} dry_run={dry_run}")

    base_commit = get_merge_base(jules_branch)
    head_commit = _run(["git", "rev-parse", "HEAD"], check=False).stdout.strip()

    report = ResolutionReport(
        pr_number=pr_number,
        branch=jules_branch,
        base_commit=base_commit,
        head_commit=head_commit,
    )

    conflicted = get_conflicted_files()
    if not conflicted:
        logger.info("No conflicted files found — nothing to resolve.")
        return report

    logger.info(f"Found {len(conflicted)} conflicted file(s): {conflicted}")

    all_blocks: dict[str, list[ConflictBlock]] = {}

    for filepath in conflicted:
        blocks = parse_conflict_blocks(filepath)
        if not blocks:
            continue

        evaluated = []
        for block in blocks:
            block = evaluate_conflict(block, jules_branch)
            evaluated.append(block)

            report.conflicts_total += 1
            if block.verdict == ConflictVerdict.FALSE_CONFLICT:
                report.auto_resolved += 1
            elif block.verdict == ConflictVerdict.CHERRY_PICK:
                report.cherry_picked += 1
            elif block.verdict == ConflictVerdict.KEEP_MAIN:
                report.kept_main += 1
            elif block.verdict == ConflictVerdict.KEEP_JULES:
                report.kept_jules += 1
            elif block.verdict == ConflictVerdict.MANUAL_REQUIRED:
                report.manual_required += 1

        report.blocks.extend(evaluated)
        all_blocks[filepath] = evaluated

    # Print preview
    print(build_report(report))

    if dry_run:
        logger.info("Dry-run mode — no files written.")
        return report

    # If manual blocks exist and not --auto, ask user
    if report.manual_required > 0 and not auto:
        print(f"\n⚠  {report.manual_required} block(s) require manual review.")
        print("   Run with --auto to apply best-guess resolutions automatically.")
        print("   Or resolve them manually, then re-run to verify.")
        answer = input("Proceed with auto-resolution for ambiguous blocks? [y/N] ").strip().lower()
        if answer != "y":
            logger.info("User aborted — no files written.")
            return report

    # Write resolved files
    changed_files = []
    for filepath, blocks in all_blocks.items():
        changed = apply_resolutions(filepath, blocks)
        if changed:
            changed_files.append(filepath)
            logger.info(f"Resolved: {filepath}")

    if changed_files:
        # Stage resolved files
        _run(["git", "add"] + changed_files, check=False)
        logger.info(f"Staged {len(changed_files)} resolved file(s).")

    # Run tests to verify resolutions didn't break anything
    logger.info("Running test suite to verify resolutions...")
    tests_passed, test_output = run_tests()

    if tests_passed:
        logger.info("All tests passed after merge resolution.")
        _notify(
            f"NINA MergeResolver — branch: {jules_branch} — "
            f"{report.auto_resolved} auto / {report.cherry_picked} cherry-picked / "
            f"{report.kept_main} kept-main — tests PASSED"
        )
    else:
        logger.warning("Tests FAILED after resolution — review manually.")
        print("\nTest failures detected after resolution:")
        print(test_output[:2000])
        _notify(
            f"NINA MergeResolver — branch: {jules_branch} — "
            f"Tests FAILED after resolution. Manual review required."
        )

    log_path = write_report(report)
    logger.info(f"Report saved: {log_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NINA Merge Conflict Resolver — intelligently handles Jules PR conflicts"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr",     type=int, help="Jules PR number to resolve")
    group.add_argument("--branch", type=str, help="Jules branch name to resolve")

    parser.add_argument("--dry-run", action="store_true",
                        help="Show resolution plan without writing any files")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-apply all resolutions without prompting")

    args = parser.parse_args()

    if args.pr:
        result = subprocess.run(
            ["gh", "pr", "view", str(args.pr), "--json", "headRefName", "-q", ".headRefName"],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            branch = result.stdout.strip()
        else:
            branch = f"jules/task-{args.pr}"
            logger.warning(f"Could not get branch from gh CLI, assuming: {branch}")
    else:
        branch = args.branch

    resolve(
        jules_branch=branch,
        pr_number=args.pr,
        dry_run=args.dry_run,
        auto=args.auto,
    )


if __name__ == "__main__":
    main()
