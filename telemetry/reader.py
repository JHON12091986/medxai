"""telemetry/reader.py — CLI tail & filter tool for NINA telemetry.jsonl
Blueprint: nina_blueprint_23.06.2026.md § II (telemetry/ namespace)
Pass 3 · 25 Jun 2026

Usage examples
--------------
    python -m telemetry.reader                         # last 10 events
    python -m telemetry.reader --tail 30               # last 30 events
    python -m telemetry.reader --stage ninagate        # filter by stage
    python -m telemetry.reader --event route_ok        # filter by event
    python -m telemetry.reader --span abc12345         # filter by span_id prefix
    python -m telemetry.reader --follow                # live tail (like tail -f)
    python -m telemetry.reader --tail 5 --json         # raw JSON output
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

_LOG = pathlib.Path("telemetry.jsonl")

# ANSI colour codes (auto-disabled when stdout is not a tty)
_COLOUR = sys.stdout.isatty()
_C = {
    "ninagate":  "\033[36m",   # cyan
    "ouroboros": "\033[35m",   # magenta
    "opencode":  "\033[33m",   # yellow
    "RESET":     "\033[0m",
    "DIM":       "\033[2m",
    "BOLD":      "\033[1m",
    "RED":       "\033[31m",
    "GREEN":     "\033[32m",
}


def _col(key: str, text: str) -> str:
    if not _COLOUR:
        return text
    return f"{_C.get(key, '')}{text}{_C['RESET']}"


def _fmt(record: dict) -> str:
    ts    = record.get("ts", 0)
    hms   = time.strftime("%H:%M:%S", time.localtime(ts))
    stage = record.get("stage", "?")
    event = record.get("event", "?")
    span  = record.get("span_id", "?")
    pay   = record.get("payload", {})

    # Pick a few key payload fields for the summary line
    summary_keys = ["provider", "task_type", "latency_ms", "status",
                    "exc_type", "fallback_attempt", "circuit_state",
                    "stream", "tokens_in", "tokens_out"]
    parts = [f"{k}={pay[k]}" for k in summary_keys if k in pay]
    summary = "  ".join(parts) if parts else json.dumps(pay)[:120]

    stage_col = _col(stage, f"{stage:<10}")
    event_col = _col("BOLD", f"{event:<20}")
    span_col  = _col("DIM", f"span={span}")
    return f"{_col('DIM', hms)}  {stage_col}  {event_col}  {span_col}  {summary}"


def _load_lines(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def _filter(records: list[dict], args: argparse.Namespace) -> list[dict]:
    if args.stage:
        records = [r for r in records if r.get("stage") == args.stage]
    if args.event:
        records = [r for r in records if r.get("event") == args.event]
    if args.span:
        records = [r for r in records if r.get("span_id", "").startswith(args.span)]
    return records


def _print(records: list[dict], as_json: bool) -> None:
    for r in records:
        if as_json:
            print(json.dumps(r, ensure_ascii=False))
        else:
            print(_fmt(r))


def _follow(args: argparse.Namespace) -> None:
    """Live tail — poll file for new lines every 0.4 s."""
    offset = _LOG.stat().st_size if _LOG.exists() else 0
    print(_col("DIM", f"[follow] watching {_LOG} — Ctrl-C to stop"))
    try:
        while True:
            time.sleep(0.4)
            if not _LOG.exists():
                continue
            size = _LOG.stat().st_size
            if size <= offset:
                continue
            with _LOG.open("r", encoding="utf-8", errors="replace") as fh:
                fh.seek(offset)
                new_lines = fh.readlines()
            offset = size
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if args.stage and r.get("stage") != args.stage:
                        continue
                    if args.event and r.get("event") != args.event:
                        continue
                    if args.span and not r.get("span_id", "").startswith(args.span):
                        continue
                    print(_fmt(r) if not args.json else json.dumps(r))
                except json.JSONDecodeError:
                    pass
    except KeyboardInterrupt:
        print(_col("DIM", "\n[follow] stopped"))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m telemetry.reader",
        description="Tail and filter NINA telemetry.jsonl",
    )
    parser.add_argument("--tail",   type=int, default=10,  metavar="N",
                        help="Show last N events (default: 10)")
    parser.add_argument("--stage",  type=str, default=None,
                        help="Filter by stage: ninagate | ouroboros | opencode")
    parser.add_argument("--event",  type=str, default=None,
                        help="Filter by event name (e.g. route_ok)")
    parser.add_argument("--span",   type=str, default=None,
                        help="Filter by span_id prefix")
    parser.add_argument("--follow", action="store_true",
                        help="Live tail (poll every 0.4s)")
    parser.add_argument("--json",   action="store_true",
                        help="Raw JSON output instead of formatted")
    args = parser.parse_args()

    if args.follow:
        _follow(args)
        return

    records = _load_lines(_LOG)
    records = _filter(records, args)
    records = records[-args.tail:]

    if not records:
        print(_col("DIM", f"[reader] no matching events in {_LOG}"))
        return

    _print(records, args.json)


if __name__ == "__main__":
    main()
