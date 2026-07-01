"""
opencode.py — Nina tool: full NDEV + NinaSuperCLI + NinaGate + Perplexity symbiosis.

This is the complete bidirectional loop:

  Perplexity (Brain)
      │  pushes task via GitHub MCP
      ▼
  tools/opencode.py  ← YOU ARE HERE
      │  1. nina-super doctor   (health check)
      │  2. opencode run <task> (OpenCode executes, calls NinaMCP mid-task)
      │  3. write output to ~/nina_debug_out.txt  (NDEV feedback layer)
      │  4. bash upload_debug_out.sh              (push output → GitHub)
      │  5. nina-super sync audit                 (commit artifacts)
      ▼
  docs/space/nina_debug_out.txt  (on GitHub)
      │
      ▼
  Perplexity reads output → plans next step → loop repeats

Public API:
    run(task, timeout, skip_ndev_upload, skip_super_sync) -> dict
    run_async(...)  -> same, awaitable
    tail_last_log(lines) -> str
    doctor() -> dict
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── paths ────────────────────────────────────────────────────────────────────
NINA_ROOT     = Path.home() / "nina"
LOGS_DIR      = NINA_ROOT / "opencode" / "logs"
LAST_LOG      = LOGS_DIR / "last_run.log"
DEBUG_OUT     = Path.home() / "nina_debug_out.txt"   # NDEV feedback file
UPLOAD_SH     = NINA_ROOT / "scripts" / "upload_debug_out.sh"
TASK_JSON     = NINA_ROOT / "nina_debug_task.json"
OPENCODE_BIN  = "opencode"
NINA_SUPER    = "nina-super"   # bin/nina-super on PATH from repo

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _sh(cmd: str, timeout: int = 30) -> tuple[bool, str]:
    """Run a shell command in NINA_ROOT. Returns (ok, output)."""
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=str(NINA_ROOT),
            capture_output=True, text=True, timeout=timeout
        )
        out = _strip_ansi((r.stdout + r.stderr).strip())
        return r.returncode == 0, out
    except Exception as e:
        return False, str(e)


def _current_round() -> str:
    """Read current NDEV round from nina_debug_task.json."""
    try:
        data = json.loads(TASK_JSON.read_text())
        return str(data.get("round", "?"))
    except Exception:
        return "?"


def _write_ndev_output(task: str, result: dict) -> None:
    """
    Append OpenCode run result to ~/nina_debug_out.txt in NDEV format.
    This is what Perplexity reads on the next turn.
    """
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S +06")
    ok    = "✅ SUCCESS" if result["success"] else "❌ FAILED"
    block = (
        f"\n{'='*60}\n"
        f" OPENCODE RUN — {ts}\n"
        f" Task    : {task}\n"
        f" Status  : {ok}\n"
        f" Duration: {result['duration_s']}s\n"
        f"{'='*60}\n"
        f"--- STDOUT ---\n{result['output']}\n"
    )
    if result["error"]:
        block += f"--- STDERR ---\n{result['error']}\n"
    block += f"{'='*60}\n"
    with open(DEBUG_OUT, "a", encoding="utf-8") as f:
        f.write(block)


def _save_log(task: str, result: dict) -> str:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = LOGS_DIR / f"run_{ts}.log"
    body = (
        f"TASK:     {task}\n"
        f"SUCCESS:  {result['success']}\n"
        f"DURATION: {result['duration_s']:.2f}s\n"
        f"ROUND:    {_current_round()}\n"
        f"--- STDOUT ---\n{result['output']}\n"
        f"--- STDERR ---\n{result['error']}\n"
    )
    log.write_text(body, encoding="utf-8")
    LAST_LOG.write_text(body, encoding="utf-8")
    return str(log)


# ── public API ───────────────────────────────────────────────────────────────

def doctor() -> dict:
    """
    Run nina-super doctor and return parsed health dict.
    Call this before dispatching tasks to catch broken state early.
    """
    ok, out = _sh(f"{NINA_SUPER} doctor", timeout=15)
    try:
        data = json.loads(out)
    except Exception:
        data = {"raw": out}
    data["doctor_ok"] = ok
    return data


def run(
    task: str,
    timeout: int = 300,
    skip_ndev_upload: bool = False,
    skip_super_sync: bool = False,
) -> dict:
    """
    Full symbiosis dispatch: doctor → opencode → NDEV feedback → sync.

    Steps executed:
      1. nina-super doctor          — preflight health check
      2. opencode run "<task>"      — OpenCode executes (NinaMCP available mid-task)
      3. write nina_debug_out.txt   — NDEV feedback layer output
      4. bash upload_debug_out.sh   — push output to GitHub (Brain reads next turn)
      5. nina-super sync audit      — commit any new artifacts

    Args:
        task:             Natural-language task for OpenCode.
        timeout:          Max seconds for OpenCode step (default 300).
        skip_ndev_upload: Skip step 4 (useful for dry-runs / testing).
        skip_super_sync:  Skip step 5.

    Returns dict:
        success, output, error, duration_s, log_path,
        doctor, ndev_upload_ok, super_sync_ok
    """
    result: dict = {
        "success": False,
        "output": "",
        "error": "",
        "duration_s": 0.0,
        "log_path": "",
        "doctor": {},
        "ndev_upload_ok": None,
        "super_sync_ok": None,
    }

    # ── Step 1: doctor ──────────────────────────────────────────────────────
    result["doctor"] = doctor()

    # ── Step 2: opencode run ────────────────────────────────────────────────
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [OPENCODE_BIN, "run", task],
            cwd=str(NINA_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result["success"] = proc.returncode == 0
        result["output"]  = _strip_ansi(proc.stdout.strip())
        result["error"]   = _strip_ansi(proc.stderr.strip())
    except subprocess.TimeoutExpired:
        result["error"] = f"opencode timed out after {timeout}s"
    except FileNotFoundError:
        result["error"] = "'opencode' binary not found — install it in the venv"
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        result["duration_s"] = round(time.monotonic() - t0, 2)

    # ── Step 3: write NDEV output ───────────────────────────────────────────
    _write_ndev_output(task, result)

    # ── Step 4: NDEV upload (upload_debug_out.sh) ───────────────────────────
    if not skip_ndev_upload and UPLOAD_SH.exists():
        ok, out = _sh(f"bash {UPLOAD_SH}", timeout=60)
        result["ndev_upload_ok"] = ok
        if not ok:
            result["error"] += f"\n[NDEV upload failed] {out[:300]}"
    elif not UPLOAD_SH.exists():
        result["ndev_upload_ok"] = False
        result["error"] += "\n[NDEV upload skipped] upload_debug_out.sh not found"

    # ── Step 5: nina-super sync audit ───────────────────────────────────────
    if not skip_super_sync:
        ok, _ = _sh(f"{NINA_SUPER} sync audit", timeout=45)
        result["super_sync_ok"] = ok

    # ── save log ────────────────────────────────────────────────────────────
    result["log_path"] = _save_log(task, result)
    return result


async def run_async(
    task: str,
    timeout: int = 300,
    skip_ndev_upload: bool = False,
    skip_super_sync: bool = False,
) -> dict:
    """
    Async wrapper for Nina's Telegram handler / OODA loop.

    Example (Telegram):
        if msg.startswith("opencode:"):
            r = await run_async(msg[9:].strip())
            status = "✅" if r["success"] else "❌"
            reply  = f"{status} {r['duration_s']}s\n{r['output'][:500]}"
            if r["ndev_upload_ok"]:
                reply += "\n📤 Output pushed to GitHub (NDEV loop closed)"
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: run(task, timeout, skip_ndev_upload, skip_super_sync)
    )


def tail_last_log(lines: int = 40) -> str:
    """Return the last N lines of the most recent opencode run log."""
    if not LAST_LOG.exists():
        return "No opencode run log found yet."
    text = LAST_LOG.read_text(encoding="utf-8")
    return "\n".join(text.splitlines()[-lines:])


# ── self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "echo symbiosis-test"
    print(f"[opencode] dry-run: skip_ndev_upload=True, skip_super_sync=True")
    r = run(task, timeout=30, skip_ndev_upload=True, skip_super_sync=True)
    print(json.dumps({k: v for k, v in r.items() if k != "doctor"}, indent=2))
