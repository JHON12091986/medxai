#!/usr/bin/env python3
"""
Nina Memory Updater — diffs nina_update_log.md since last MEMORY.md update,
auto-appends a structured summary section.
Usage: python3 tools/update_memory.py [--dry-run]
NINA_FEATURE: update-memory v1.0
"""
import re, argparse
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_FILE = REPO_ROOT / "MEMORY.md"
LOG_FILE = REPO_ROOT / "nina_update_log.md"

TS_PATTERN = re.compile(r"###\s+(\d{4}-\d{2}-\d{2})")


def parse_last_memory_ts():
    if not MEMORY_FILE.exists():
        return None
    text = MEMORY_FILE.read_text()
    # Find latest date stamp in MEMORY.md
    dates = TS_PATTERN.findall(text)
    if dates:
        return max(dates)
    # Try ## updated: header
    m = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else None


def parse_log_entries_since(since_date):
    if not LOG_FILE.exists():
        return []
    text = LOG_FILE.read_text()
    sections = TS_PATTERN.split(text)
    entries = []
    # sections alternates: [preamble, date, body, date, body, ...]
    it = iter(sections[1:])
    for date_str, body in zip(it, it):
        if since_date is None or date_str > since_date:
            entries.append((date_str, body.strip()))
    return entries


def build_summary_section(entries):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [f"\n\n---\n\n## Auto-Summary — Updated {today} by update_memory.py\n"]
    for date_str, body in entries[-10:]:  # cap at last 10 entries
        # Extract first meaningful line as headline
        first = next((l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")), "")
        lines.append(f"- **{date_str}**: {first[:120]}")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print diff without writing")
    args = ap.parse_args()

    last_ts = parse_last_memory_ts()
    new_entries = parse_log_entries_since(last_ts)

    if not new_entries:
        print(f"✓ MEMORY.md already up-to-date (last_ts={last_ts}, no new log entries).")
        exit(0)

    summary = build_summary_section(new_entries)

    if args.dry_run:
        print(f"Would append to MEMORY.md ({len(new_entries)} new entries):")
        print(summary)
    else:
        with open(MEMORY_FILE, "a") as f:
            f.write(summary)
        print(f"✓ MEMORY.md updated with {len(new_entries)} new log entries.")
