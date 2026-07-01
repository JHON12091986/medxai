import json
import datetime
import pathlib
import os

# Resolve path relative to repo root so it works regardless of CWD
REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
HEARTBEAT_FILE = REPO_ROOT / "data" / "heartbeats.json"

def write_heartbeat(service_name: str) -> None:
    try:
        try:
            with open(HEARTBEAT_FILE, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[service_name] = datetime.datetime.utcnow().isoformat() + "Z"

        # Write atomically
        tmp_file = HEARTBEAT_FILE.with_suffix(".tmp")
        HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_file, HEARTBEAT_FILE)
    except Exception:
        # Catch and log all exceptions silently (never crash the caller)
        pass
