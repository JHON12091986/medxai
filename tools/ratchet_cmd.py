"""tools/ratchet_cmd.py — /ratchet Telegram command handler
Blueprint: nina_blueprint_23.06.2026.md §V
Pass 3 · 24 Jun 2026

Exposes the autonomy ratchet to Telegram commands:
  /ratchet              — show current status
  /ratchet status       — same as above
  /ratchet ceiling <N>  — set max_rung to N (0-4)
  /ratchet reset        — emergency reset to OBSERVE
  /ratchet patches      — show last 10 self-patch entries
  /ratchet proposals    — show pending proposals

Wiring:
  In interfaces/telegram_interface.py, register:
    "/ratchet": handle_ratchet_command
  Or dispatch from the existing command router.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.autonomy_ratchet import AutonomyRatchet

log = logging.getLogger("nina.ratchet_cmd")


async def handle_ratchet_command(
    args: str,
    ratchet: "AutonomyRatchet",
    nina=None,  # Nina instance for self_patch_logger access
) -> str:
    """Dispatch /ratchet subcommand and return response string.

    Args:
        args:    Everything after '/ratchet' (stripped), e.g. 'ceiling 2'
        ratchet: Live AutonomyRatchet instance from nina.pipeline or nina
        nina:    Optional Nina instance for patch history access
    """
    cmd = args.strip().lower() if args else "status"
    parts = cmd.split()
    sub = parts[0] if parts else "status"

    # ── /ratchet  or  /ratchet status ────────────────────────────────
    if sub in ("status", ""):
        return ratchet.telegram_status()

    # ── /ratchet ceiling <N> ─────────────────────────────────────────
    if sub == "ceiling":
        if len(parts) < 2 or not parts[1].isdigit():
            return (
                "Usage: /ratchet ceiling <N>\n"
                "N = 0 (observe) → 4 (adaptive)\n"
                "Current ceiling: " + str(ratchet._state.max_rung)
            )
        new_max = int(parts[1])
        return ratchet.set_max_rung(new_max, reason="telegram command")

    # ── /ratchet reset ───────────────────────────────────────────────
    if sub == "reset":
        ratchet.reset_to_observe(reason="telegram /ratchet reset")
        return "⚠️ Ratchet reset to OBSERVE. All autonomy suspended."

    # ── /ratchet patches ─────────────────────────────────────────────
    if sub == "patches":
        try:
            from core.self_patch_logger import SelfPatchLogger
            spl = SelfPatchLogger()
            entries = await spl.last_n(10)
            if not entries:
                return "No self-patch cycles recorded yet."
            lines = ["🔧 *Last 10 self-patches:*"]
            for e in reversed(entries):
                ts     = e.get("ts", "")[:16].replace("T", " ")
                status = "✅" if e.get("success") else "❌"
                fname  = e.get("file", "unknown")
                desc   = e.get("description", "")[:60]
                lines.append(f"{status} `{fname}` @ {ts}\n   _{desc}_")
            return "\n".join(lines)
        except Exception as exc:
            log.warning("ratchet_cmd patches error: %s", exc)
            return f"Error reading patch history: {exc}"

    # ── /ratchet proposals ───────────────────────────────────────────
    if sub == "proposals":
        proposals = ratchet.get_proposals(unexecuted_only=True, limit=10)
        if not proposals:
            return "No pending proposals."
        lines = [f"📋 *{len(proposals)} pending proposals:*"]
        for p in proposals:
            ts   = p.get("ts", "")[:16].replace("T", " ")
            risk = p.get("risk", "?")
            desc = p.get("description", "")[:80]
            lines.append(f"• [{risk}] {ts} — {desc}")
        return "\n".join(lines)

    # ── unknown ───────────────────────────────────────────────────────
    return (
        "*Ratchet commands:*\n"
        "`/ratchet` — status\n"
        "`/ratchet ceiling <0-4>` — set ceiling\n"
        "`/ratchet reset` — emergency reset to OBSERVE\n"
        "`/ratchet patches` — last 10 self-patches\n"
        "`/ratchet proposals` — pending proposals"
    )
