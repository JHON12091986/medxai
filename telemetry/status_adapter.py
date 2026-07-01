"""
telemetry/status_adapter.py — Bridge: status_bus → telemetry.jsonl
Pass 0 · 25 Jun 2026 · Nina Live Status Display

Purpose
-------
Every message pushed through ``core.status_bus.push()`` is also written as a
structured JSONL record to ``telemetry.jsonl``.  This gives you a free audit
trail of all live-status events without any extra instrumentation.

This module is OPTIONAL.  If it is not imported, status_bus still works.
If telemetry.jsonl is unwritable, the adapter logs a warning and keeps running.

Activation
----------
Call ``attach()`` once at Nina startup (e.g. in main.py after NinaOS.start()):

    from telemetry.status_adapter import attach
    attach()

That's it.  The adapter wraps the global status_bus push so every event is
recorded automatically.  Use ``detach()`` to remove the hook (e.g. in tests).

Record schema
-------------
{"ts": 1719270000.0, "stage": "status", "msg": "🔀 Routing → GEMINI"}
"""
from __future__ import annotations

import json
import logging
import pathlib
import threading
import time
from typing import Optional

import core.status_bus as _bus

_log = logging.getLogger("nina.telemetry.status_adapter")
_LOCK = threading.Lock()
_LOG_PATH = pathlib.Path("telemetry.jsonl")
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB rotation threshold
_original_push: Optional[object] = None


def _rotate_if_needed() -> None:
    """Rename telemetry.jsonl → telemetry.jsonl.1 when it exceeds 10 MB."""
    try:
        if _LOG_PATH.exists() and _LOG_PATH.stat().st_size > _MAX_BYTES:
            _LOG_PATH.rename(_LOG_PATH.with_suffix(".jsonl.1"))
    except Exception as exc:
        _log.warning("telemetry rotate failed: %s", exc)


def _write(msg: str) -> None:
    """Append one JSONL record — lock-safe, never raises."""
    record = {"ts": time.time(), "stage": "status", "msg": msg}
    try:
        _rotate_if_needed()
        with _LOCK:
            with _LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        _log.warning("telemetry write failed: %s", exc)


def attach() -> None:
    """
    Monkey-patch ``core.status_bus.push`` to also call ``_write``.

    Idempotent — calling attach() twice does nothing.
    """
    global _original_push
    if _original_push is not None:
        return  # already attached

    _original_push = _bus.push

    async def _patched_push(msg: str) -> None:
        _write(msg)          # sync write — fast, negligible latency
        await _original_push(msg)  # type: ignore[misc]

    _bus.push = _patched_push  # type: ignore[assignment]
    _bus.push_safe = _patched_push  # type: ignore[assignment]
    _log.info("telemetry.status_adapter attached — writing to %s", _LOG_PATH)


def detach() -> None:
    """Restore the original ``push`` function (useful in tests)."""
    global _original_push
    if _original_push is None:
        return
    _bus.push = _original_push  # type: ignore[assignment]
    _bus.push_safe = _original_push  # type: ignore[assignment]
    _original_push = None
    _log.info("telemetry.status_adapter detached")
