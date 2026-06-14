import json, time, os
from datetime import datetime, timezone

SCRATCH = 'data/gemini_scratch.jsonl'

def log_step(step, action, detail, file="", status="ok"):
    entry = {
        "t": datetime.now(tz=timezone.utc).isoformat(),
        "step": step,
        "action": action,
        "file": file,
        "detail": detail,
        "status": status
    }
    with open(SCRATCH, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        log_step(int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "", sys.argv[5] if len(sys.argv) > 5 else "ok")
