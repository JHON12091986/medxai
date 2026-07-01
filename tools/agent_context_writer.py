#!/usr/bin/env python3
"""
Nina Agent Context Writer — writes data/agent_context.json after every OODA audit.
Provides a compact (<5KB) machine-readable snapshot every agent reads on startup.
Usage: python3 tools/agent_context_writer.py
NINA_FEATURE: agent-context-writer v1.0
Output: data/agent_context.json
"""
import json, subprocess, os
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = REPO_ROOT / "data" / "agent_context.json"


def git(cmd):
    try:
        return subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def read_health():
    ctx_graph = REPO_ROOT / "nina_context_graph.json"
    if ctx_graph.exists():
        try:
            g = json.loads(ctx_graph.read_text())
            return g.get("summary", {}).get("health", "unknown"), g.get("summary", {}).get("top_priority", "none")
        except Exception:
            pass
    return "unknown", "none"


def read_open_errors():
    err_reg = REPO_ROOT / "docs" / "space" / "nina_error_register.md"
    if not err_reg.exists():
        return []
    lines = err_reg.read_text().splitlines()
    return [l.strip() for l in lines if "OPEN" in l][:5]


def read_ready_tasks():
    backlog = REPO_ROOT / "docs" / "space" / "jules_backlog.md"
    if not backlog.exists():
        return []
    lines = backlog.read_text().splitlines()
    return [l.strip() for l in lines if "READY" in l][:5]


def service_status(name):
    try:
        r = subprocess.run(["systemctl", "--user", "is-active", name],
                           capture_output=True, text=True)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def cron_health():
    stamp_file = REPO_ROOT / ".cache" / "cron_health.json"
    if stamp_file.exists():
        try:
            return json.loads(stamp_file.read_text())
        except Exception:
            pass
    return {}


def main():
    health, top_priority = read_health()
    branch = git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    last_commit = git(["git", "log", "-1", "--format=%h %s"])
    dirty_files = [l for l in git(["git", "status", "--short"]).splitlines() if l.strip()]

    context = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repo": "aibony/nina",
        "branch": branch,
        "last_commit": last_commit,
        "dirty_files_count": len(dirty_files),
        "dirty_files_sample": dirty_files[:10],
        "health": health,
        "top_priority": top_priority,
        "open_errors": read_open_errors(),
        "ready_tasks": read_ready_tasks(),
        "services": {
            "nina": service_status("nina.service"),
            "ninagate": service_status("ninagate.service"),
            "ninajulesgithub": service_status("ninajulesgithub.service"),
            "nina-dashboard": service_status("nina-dashboard.service"),
        },
        "cron_health": cron_health(),
        "new_features": [
            "incremental-dedup-scanner v1.0 (tools/dedup_scan.py)",
            "semantic-dedup-gpu v1.0 (tools/semantic_dedup.py)",
            "telemetry-digest v1.0 (tools/telemetry_digest.py)",
            "agent-context-writer v1.0 (tools/agent_context_writer.py)",
            "cron-sentinel v1.0 (tools/cron_sentinel.py)",
            "update-memory v1.0 (tools/update_memory.py)",
            "bench-providers v1.0 (tools/bench_providers.py)",
        ],
    }

    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text(json.dumps(context, indent=2))
    print(f"✓ agent_context.json written ({OUT_FILE.stat().st_size} bytes)")
    print(f"  health={health}  branch={branch}  dirty={len(dirty_files)}")


if __name__ == "__main__":
    main()
