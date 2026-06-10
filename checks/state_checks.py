from checks.runner import record, NINA_DIR
import re
def check_idle_queue_path():
    nina_path     = NINA_DIR / "core" / "nina.py"
    pipeline_path = NINA_DIR / "tools" / "upgradepipeline.py"

    if not nina_path.exists() or not pipeline_path.exists():
        record("INFO", "queue.path_mismatch.missing", "core/nina.py or tools/upgradepipeline.py not found — skipping")
        return

    nina_src     = nina_path.read_text(errors="replace")

    # R-61: idlequeue.json is the wrong path
    if re.search(r"idlequeue\.json", nina_src) and not re.search(r"IDLE_QUEUE", nina_src):
        record(
            "WARN", "queue.path_mismatch",
            "core/nina.py uses hardcoded 'idlequeue.json' instead of importing IDLE_QUEUE",
            detail="Should import IDLE_QUEUE from tools/upgradepipeline.py (single source of truth).",
            fix="Add: from tools.upgradepipeline import IDLE_QUEUE and use it in run_idle_summary (R-61).",
        )
    else:
        record("PASS", "queue.path_mismatch", "Idle queue path — IDLE_QUEUE imported correctly — OK")

def check_duplicate_log_handler():
    nina_path = NINA_DIR / "core" / "nina.py"
    if not nina_path.exists():
        record("INFO", "logger.duplicate_handler.missing", "core/nina.py not found — skipping handler check")
        return

    source = nina_path.read_text(errors="replace")

    handler_guard_count = len(re.findall(r"if not root\.handlers", source))
    add_handler_count   = len(re.findall(r"root\.addHandler", source))

    if handler_guard_count == 0 and add_handler_count > 0:
        record(
            "WARN", "logger.duplicate_handler",
            "root.addHandler called without 'if not root.handlers' guard in core/nina.py",
            detail="Duplicate handlers added on every restart → duplicate log lines.",
            fix="Wrap root.addHandler(ch) inside a single 'if not root.handlers:' guard (R-65 fix).",
        )
    elif add_handler_count > handler_guard_count + 1:
        record(
            "WARN", "logger.duplicate_handler",
            f"Multiple addHandler calls ({add_handler_count}) vs guard blocks ({handler_guard_count}) in core/nina.py",
            detail="Some addHandler calls may be outside the guard, causing duplicate log lines.",
            fix="Ensure every root.addHandler(ch) is inside a single guard (R-65 fix).",
        )
    else:
        record("PASS", "logger.duplicate_handler", "Log handler guard — OK")
