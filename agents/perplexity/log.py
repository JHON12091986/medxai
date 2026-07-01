"""perplexity/log.py — single logging entry point for all relay modules."""
import logging
import datetime
from pathlib import Path

logger = logging.getLogger("nina.perplexity.relay")

REPO_ROOT = Path(__file__).parent.parent
UPDATE_LOG = REPO_ROOT / "nina_update_log.md"
RELAY_LOG = REPO_ROOT / "docs" / "space" / "relay_activity_log.md"


def log_action(task_id: str, action: str, status: str, detail: str = "") -> None:
    """Append one entry to nina_update_log.md and relay_activity_log.md."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")

    # nina_update_log.md — match existing format: '- [ts] task_id | action | status'
    update_line = f"- [{ts}] {task_id} | {action} | {status}"
    if detail:
        update_line += f" | {detail[:120]}"
    try:
        UPDATE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with UPDATE_LOG.open("a", encoding="utf-8") as f:
            f.write(update_line + "\n")
    except Exception as e:
        logger.warning(f"log_action: failed to write update log: {e}")

    # relay_activity_log.md — full structured audit trail
    relay_line = f"[{ts}] {task_id} | {action} | {status} | {detail}"
    try:
        RELAY_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not RELAY_LOG.exists():
            RELAY_LOG.write_text("# Relay Activity Log\n\n", encoding="utf-8")
        with RELAY_LOG.open("a", encoding="utf-8") as f:
            f.write(relay_line + "\n")
    except Exception as e:
        logger.warning(f"log_action: failed to write relay log: {e}")
