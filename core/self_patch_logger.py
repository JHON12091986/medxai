"""core/self_patch_logger.py — Self-Patch Cycle Logger
Blueprint: nina_blueprint_23.06.2026.md §V
Pass 3 · 24 Jun 2026

Logs every confirmed self-patch cycle to:
  docs/nina_error_register.md  (human-readable markdown audit trail)
  data/self_patch_history.json (machine-readable, last 200 entries)

This resolves Blueprint §V marker:
  'First confirmed self-patch cycle logged in nina_error_register.md'

Usage:
    from core.self_patch_logger import SelfPatchLogger
    logger = SelfPatchLogger()
    await logger.log_patch(
        file_path="core/agent_loop.py",
        patch_description="Wrapped blocking call in asyncio.to_thread()",
        success=True,
        ratchet=ratchet_instance,   # optional AutonomyRatchet
    )

Wiring:
    Called by core/ast_refactor.py:apply_patch() on successful write.
    Called by guardian_loop.py on any fault-triggered patch.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.self_patch_logger")

_REGISTER_PATH = Path("docs/nina_error_register.md")
_HISTORY_PATH  = Path("data/self_patch_history.json")
_MAX_HISTORY   = 200


class SelfPatchLogger:
    """Append-only audit log for NINA self-patch cycles."""

    def __init__(
        self,
        register_path: Path = _REGISTER_PATH,
        history_path: Path  = _HISTORY_PATH,
    ) -> None:
        self._register = register_path
        self._history  = history_path

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def log_patch(
        self,
        file_path: str,
        patch_description: str,
        success: bool,
        ratchet: Any = None,          # AutonomyRatchet instance (optional)
        guardian_flags: list[str] | None = None,
        diff_summary: str = "",
    ) -> None:
        """Append a patch entry to both the markdown register and JSON history.

        Args:
            file_path:         Path of the patched file (relative to repo root).
            patch_description: Human-readable description of what was changed.
            success:           True if patch applied and verified; False if rejected.
            ratchet:           AutonomyRatchet instance for ratchet snapshot.
            guardian_flags:    List of flag names raised by guardian_loop (if any).
            diff_summary:      Optional short diff / what changed.
        """
        entry = _build_entry(
            file_path=file_path,
            patch_description=patch_description,
            success=success,
            ratchet=ratchet,
            guardian_flags=guardian_flags or [],
            diff_summary=diff_summary,
        )
        # Run both I/O operations concurrently, non-blocking
        await asyncio.gather(
            asyncio.to_thread(self._write_register, entry),
            asyncio.to_thread(self._write_history,  entry),
        )
        log.info(
            "self_patch_logged file=%s success=%s",
            file_path, success
        )

    async def last_n(self, n: int = 10) -> list[dict]:
        """Return the last N patch entries from the JSON history."""
        return await asyncio.to_thread(self._read_history, n)

    async def summary(self) -> str:
        """One-line summary for Telegram /ratchet or /status output."""
        history = await self.last_n(50)
        if not history:
            return "No self-patch cycles recorded yet."
        total    = len(history)
        success  = sum(1 for e in history if e.get("success"))
        last_ts  = history[-1].get("ts", "")[:16]
        last_file= history[-1].get("file", "unknown")
        return (
            f"Self-patches: {total} total | "
            f"{success}/{total} succeeded | "
            f"last: {last_file} @ {last_ts}"
        )

    # ------------------------------------------------------------------ #
    #  Internal (sync — called via asyncio.to_thread)                     #
    # ------------------------------------------------------------------ #

    def _write_register(self, entry: dict) -> None:
        self._register.parent.mkdir(parents=True, exist_ok=True)
        ts     = entry["ts"][:19].replace("T", " ")
        status = "✅ APPLIED" if entry["success"] else "❌ REJECTED"
        flags  = ", ".join(entry["guardian_flags"]) or "none"
        ratchet_line = ""
        if entry.get("ratchet"):
            r = entry["ratchet"]
            ratchet_line = (
                f"\n**Ratchet:** rung={r.get('current_rung')} "
                f"({r.get('rung_name')}) | "
                f"rate={r.get('success_rate', 0):.1%} | "
                f"streak={r.get('streak')}"
            )
        diff_line = f"\n**Diff:** {entry['diff_summary']}" if entry["diff_summary"] else ""
        block = (
            f"\n---\n"
            f"### [{ts}] {status} — `{entry['file']}`\n"
            f"**Description:** {entry['description']}\n"
            f"**Guardian flags:** {flags}"
            f"{ratchet_line}"
            f"{diff_line}\n"
        )
        # Initialise file if missing
        if not self._register.exists():
            self._register.write_text(
                "# NINA Self-Patch Register\n"
                "> Append-only audit trail. Newest entry at bottom.\n",
                encoding="utf-8",
            )
        with open(self._register, "a", encoding="utf-8") as f:
            f.write(block)

    def _write_history(self, entry: dict) -> None:
        self._history.parent.mkdir(parents=True, exist_ok=True)
        history: list[dict] = []
        if self._history.exists():
            try:
                history = json.loads(self._history.read_text(encoding="utf-8"))
            except Exception:
                history = []
        history.append(entry)
        history = history[-_MAX_HISTORY:]
        self._history.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _read_history(self, n: int) -> list[dict]:
        if not self._history.exists():
            return []
        try:
            history = json.loads(self._history.read_text(encoding="utf-8"))
            return history[-n:]
        except Exception:
            return []


# ------------------------------------------------------------------ #
#  Module-level singleton (import and use directly)                   #
# ------------------------------------------------------------------ #

_default_logger = SelfPatchLogger()


async def log_patch(
    file_path: str,
    patch_description: str,
    success: bool,
    ratchet: Any = None,
    guardian_flags: list[str] | None = None,
    diff_summary: str = "",
) -> None:
    """Module-level convenience wrapper around SelfPatchLogger()."""
    await _default_logger.log_patch(
        file_path=file_path,
        patch_description=patch_description,
        success=success,
        ratchet=ratchet,
        guardian_flags=guardian_flags,
        diff_summary=diff_summary,
    )


# ------------------------------------------------------------------ #
#  Entry builder                                                       #
# ------------------------------------------------------------------ #

def _build_entry(
    file_path: str,
    patch_description: str,
    success: bool,
    ratchet: Any,
    guardian_flags: list[str],
    diff_summary: str,
) -> dict:
    ratchet_snapshot: dict = {}
    if ratchet is not None:
        try:
            ratchet_snapshot = ratchet.audit_report()
        except Exception:
            pass
    return {
        "ts":            datetime.now(timezone.utc).isoformat(),
        "file":          str(file_path),
        "description":   patch_description[:500],
        "success":       success,
        "guardian_flags":guardian_flags,
        "ratchet":       ratchet_snapshot,
        "diff_summary":  diff_summary[:300],
    }
