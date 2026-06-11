import json
import os
from datetime import datetime

def write_log(entry: dict, log_path: str = "logs/router.log"):
    """Writes a structured JSON log entry to the specified path."""
    entry["ts"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
