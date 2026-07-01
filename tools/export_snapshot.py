#!/usr/bin/env python3
"""
Nina Export Snapshot — writes a dated JSON state snapshot to exports/.
Captures: health, registry summary, telemetry digest, open errors, ready tasks, service status.
Usage: python3 tools/export_snapshot.py [--pretty]
NINA_FEATURE: export-snapshot v1.0
Output: exports/nina_state_YYYYMMDD.json
"""
import json, subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = REPO_ROOT / "exports"


def read_json_safe(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def git(cmd):
    try:
        return subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def service_status(name):
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", name], capture_output=True, text=True)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def main(pretty=False):
    today = datetime.utcnow().strftime("%Y%m%d")
    out_file = EXPORTS_DIR / f"nina_state_{today}.json"
    EXPORTS_DIR.mkdir(exist_ok=True)

    # Agent context (written by agent_context_writer.py)
    agent_ctx = read_json_safe(REPO_ROOT / "data" / "agent_context.json")

    # Telemetry digest (import inline)
    telemetry_digest = {}
    try:
        import sys
        sys.path.insert(0, str(REPO_ROOT / "tools"))
        from telemetry_digest import load_events, digest
        telemetry_digest = digest(load_events(last_n=500))
    except Exception as e:
        telemetry_digest = {"error": str(e)}

    # SSOT index summary
    index_summary = {}
    idx = REPO_ROOT / "docs" / "space" / "nina_index.json"
    if idx.exists():
        try:
            data = json.loads(idx.read_text())
            index_summary = {"file_count": len(data) if isinstance(data, list) else len(data.get("files", []))}
        except Exception:
            pass

    snapshot = {
        "snapshot_date": today,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "git": {
            "branch": git(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
            "last_commit": git(["git", "log", "-1", "--format=%h %s"]),
            "dirty_count": len([l for l in git(["git", "status", "--short"]).splitlines() if l.strip()]),
        },
        "agent_context": agent_ctx,
        "telemetry_digest": telemetry_digest,
        "ssot": index_summary,
        "services": {
            "nina": service_status("nina.service"),
            "ninagate": service_status("ninagate.service"),
            "ninajulesgithub": service_status("ninajulesgithub.service"),
            "nina-dashboard": service_status("nina-dashboard.service"),
        },
    }

    indent = 2 if pretty else None
    out_file.write_text(json.dumps(snapshot, indent=indent))
    print(f"✓ Snapshot written: {out_file} ({out_file.stat().st_size} bytes)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()
    main(pretty=args.pretty)
