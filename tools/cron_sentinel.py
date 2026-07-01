#!/usr/bin/env python3
"""
Nina Cron Sentinel — checks cron job health stamps, alerts on staleness.
Each cron job should call: python3 tools/cron_sentinel.py --stamp <job_name> --interval <seconds>
To check all stamps: python3 tools/cron_sentinel.py --check
NINA_FEATURE: cron-sentinel v1.0
Stamp file: .cache/cron_health.json
"""
import json, argparse, time
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
STAMP_FILE = REPO_ROOT / ".cache" / "cron_health.json"

# Default expected intervals (seconds) per job name
DEFAULT_INTERVALS = {
    "ooda_audit": 3600,        # hourly
    "nina_sync": 1800,         # 30 min
    "dedup_scan": 86400,       # daily
    "telemetry_digest": 3600,  # hourly
    "bench_providers": 604800, # weekly
    "memory_update": 86400,    # daily
    "export_snapshot": 86400,  # daily
}


def load_stamps():
    if STAMP_FILE.exists():
        try:
            return json.loads(STAMP_FILE.read_text())
        except Exception:
            pass
    return {}


def save_stamps(stamps):
    STAMP_FILE.parent.mkdir(exist_ok=True)
    STAMP_FILE.write_text(json.dumps(stamps, indent=2))


def do_stamp(job_name, interval=None):
    stamps = load_stamps()
    stamps[job_name] = {
        "last_run": datetime.utcnow().isoformat() + "Z",
        "last_epoch": int(time.time()),
        "interval_s": interval or DEFAULT_INTERVALS.get(job_name, 3600),
        "status": "ok",
    }
    save_stamps(stamps)
    print(f"✓ Stamped cron job: {job_name}")


def do_check():
    stamps = load_stamps()
    now = int(time.time())
    stale = []
    missing = set(DEFAULT_INTERVALS.keys()) - set(stamps.keys())

    print(f"Cron Health Check — {datetime.utcnow().isoformat()}Z")
    print(f"  Registered jobs: {len(stamps)}  |  Never-run: {len(missing)}")
    if missing:
        print(f"  ⚠️  Never stamped : {', '.join(sorted(missing))}")

    for job, info in stamps.items():
        elapsed = now - info.get("last_epoch", 0)
        interval = info.get("interval_s", DEFAULT_INTERVALS.get(job, 3600))
        overdue = elapsed > interval * 1.5
        symbol = "⚠️ " if overdue else "✓ "
        print(f"  {symbol}{job:30s} last={info.get('last_run','?')}  elapsed={elapsed//60}m  interval={interval//60}m")
        if overdue:
            stale.append(job)

    if stale:
        print(f"\n⚠️  STALE JOBS: {', '.join(stale)}")
        return 1
    print("\n✓ All registered cron jobs healthy.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Nina cron sentinel")
    ap.add_argument("--stamp", metavar="JOB", help="Record successful run for JOB")
    ap.add_argument("--interval", type=int, help="Expected interval in seconds (used with --stamp)")
    ap.add_argument("--check", action="store_true", help="Check all stamps for staleness")
    args = ap.parse_args()

    if args.stamp:
        do_stamp(args.stamp, args.interval)
    elif args.check:
        exit(do_check())
    else:
        ap.print_help()
