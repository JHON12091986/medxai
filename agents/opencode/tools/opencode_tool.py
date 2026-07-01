"""Nina tool: dispatch tasks to OpenCode autonomously.

Usage (from Nina tool registry):
    from opencode.tools.opencode_tool import dispatch, dispatch_async

Telegram trigger:
    User sends: "opencode: implement memory_indexer.py"
    Nina routes to: dispatch("implement memory_indexer.py")
"""

import subprocess
import logging
import os
import asyncio
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("nina.opencode")

NINA_ROOT = Path("/home/aibony/nina")
OPENCODE_BIN = Path("/home/aibony/.opencode/bin/opencode")
LOG_DIR = NINA_ROOT / "opencode" / "logs"
LAST_TASK_FILE = LOG_DIR / "last_task.txt"
LAST_RUN_LOG = LOG_DIR / "last_run.log"


def dispatch(task: str, timeout: int = 300) -> dict:
    """Dispatch a task to OpenCode synchronously.

    Args:
        task: Natural language task description for OpenCode.
        timeout: Max seconds to wait (default 5 min).

    Returns:
        dict with keys: success (bool), output (str), error (str), duration_s (float)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Log the task
    timestamp = datetime.now().isoformat()
    LAST_TASK_FILE.write_text(f"[{timestamp}]\n{task}\n")
    logger.info(f"[OpenCode] Dispatching task: {task[:80]}...")

    start = datetime.now()
    try:
        result = subprocess.run(
            [str(OPENCODE_BIN), "run", task],
            cwd=str(NINA_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "NO_COLOR": "1"},  # strip ANSI for clean logs
        )
        duration = (datetime.now() - start).total_seconds()
        output = result.stdout.strip()
        error = result.stderr.strip()
        success = result.returncode == 0

        # Write run log
        log_content = (
            f"=== OpenCode Run [{timestamp}] ===\n"
            f"TASK: {task}\n"
            f"EXIT: {result.returncode}\n"
            f"DURATION: {duration:.1f}s\n\n"
            f"--- STDOUT ---\n{output}\n\n"
            f"--- STDERR ---\n{error}\n"
        )
        LAST_RUN_LOG.write_text(log_content)
        logger.info(f"[OpenCode] Done in {duration:.1f}s. Success={success}")

        return {
            "success": success,
            "output": output,
            "error": error,
            "duration_s": duration,
            "task": task,
        }

    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start).total_seconds()
        logger.error(f"[OpenCode] Timeout after {timeout}s")
        return {
            "success": False,
            "output": "",
            "error": f"Timed out after {timeout}s",
            "duration_s": duration,
            "task": task,
        }
    except Exception as e:
        logger.error(f"[OpenCode] Exception: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "duration_s": 0,
            "task": task,
        }


async def dispatch_async(task: str, timeout: int = 300) -> dict:
    """Async version for use inside Nina's async event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, dispatch, task, timeout)


def get_last_run_log() -> str:
    """Return the content of the last OpenCode run log."""
    if LAST_RUN_LOG.exists():
        return LAST_RUN_LOG.read_text()
    return "No runs yet."


def get_last_task() -> str:
    """Return the last dispatched task."""
    if LAST_TASK_FILE.exists():
        return LAST_TASK_FILE.read_text()
    return "No tasks dispatched yet."


if __name__ == "__main__":
    # Quick test
    import sys
    task = " ".join(sys.argv[1:]) or "list files in the nina/opencode folder"
    print(f"Dispatching: {task}")
    result = dispatch(task)
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration_s']:.1f}s")
    print(f"Output:\n{result['output']}")
    if result['error']:
        print(f"Error:\n{result['error']}")
