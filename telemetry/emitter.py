"""telemetry/emitter.py — JSONL atomic event emitter for NINA pipeline.
Blueprint: nina_blueprint_23.06.2026.md § II (telemetry/ namespace)
Pass 2 · 25 Jun 2026

Stage values : "ninagate" | "ouroboros" | "opencode"
Event values : "request_in" | "route_start" | "route_ok" | "route_ok_stream"
              | "route_exhausted" | "provider_call_ok" | "response_out"
              | "error"
"""
from __future__ import annotations

import json
import pathlib
import threading
import time
import uuid

_LOG = pathlib.Path("telemetry.jsonl")
_LOCK = threading.Lock()
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB rotation threshold


def emit(
    stage: str,
    event: str,
    payload: dict,
    span_id: str | None = None,
) -> None:
    """Append one structured telemetry event to telemetry.jsonl.

    Thread-safe, never raises — all I/O errors are silently swallowed so
    this can be called from any pipeline stage without risking a crash.
    """
    record = {
        "ts": round(time.time(), 4),
        "span_id": span_id or str(uuid.uuid4())[:8],
        "stage": stage,
        "event": event,
        "payload": payload,
    }
    line = json.dumps(record, ensure_ascii=False) + "\n"
    try:
        with _LOCK:
            # Rotate if over size limit before appending
            if _LOG.exists() and _LOG.stat().st_size >= _MAX_BYTES:
                _rotate()
            with _LOG.open("a", encoding="utf-8") as fh:
                fh.write(line)
    except Exception:
        # Emitter must never crash the pipeline — fail silently
        pass


def _rotate() -> None:
    """Rename telemetry.jsonl → telemetry.jsonl.1, dropping the older .1 if present."""
    rotated = _LOG.with_suffix(".jsonl.1")
    try:
        if rotated.exists():
            rotated.unlink()
        _LOG.rename(rotated)
    except Exception:
        pass
