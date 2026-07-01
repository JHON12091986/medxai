"""
core/idempotency.py
NINA Idempotency Enforcer — stores last_run_hash per script.
Skip if unchanged. Every hook is safe to run twice.

Usage:
    from core.idempotency import should_run, mark_done

    if not should_run("build_ssot_index", inputs=["/path/to/repo"]):
        print("Skipping — no changes since last run.")
        sys.exit(0)
    # ... do work ...
    mark_done("build_ssot_index", inputs=["/path/to/repo"])
"""

from __future__ import annotations
import hashlib, json, time
from pathlib import Path

ROOT = Path(__file__).parent.parent
STORE = ROOT / "data" / "run_hashes.json"
STORE.parent.mkdir(parents=True, exist_ok=True)


def _load() -> dict:
    if STORE.exists():
        try:
            return json.loads(STORE.read_text())
        except Exception:
            pass
    return {}


def _save(data: dict) -> None:
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(STORE)


def _input_hash(inputs: list) -> str:
    """Hash a list of inputs (file paths or strings) into a single key."""
    parts = []
    for item in inputs:
        p = Path(item)
        if p.exists():
            parts.append(hashlib.sha256(p.read_bytes()).hexdigest()[:16])
        else:
            parts.append(hashlib.sha256(str(item).encode()).hexdigest()[:16])
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


def should_run(script_name: str, inputs: list = None) -> bool:
    """Return True if the script should run (inputs changed since last run)."""
    data = _load()
    current_hash = _input_hash(inputs or [])
    stored = data.get(script_name, {})
    return stored.get("hash") != current_hash


def mark_done(script_name: str, inputs: list = None) -> None:
    """Record that script ran successfully with current inputs."""
    import datetime
    data = _load()
    data[script_name] = {
        "hash": _input_hash(inputs or []),
        "ts": time.time(),
        "ran_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _save(data)


def force_reset(script_name: str) -> None:
    """Force a script to run next time regardless of input hash."""
    data = _load()
    data.pop(script_name, None)
    _save(data)


def status() -> dict:
    return _load()
