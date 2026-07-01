"""Telegram /setkey command handler.

Usage (in private chat with NINA):
  /setkey GROQ_API_KEY gsk_...
  /setkey TELEGRAM_CHAT_ID 123456789
  /setkey GEMINI_API_KEY AIza...

The key-value pair is persisted immediately to data/secrets.json via
KeyResolver.set_key() — no service restart required.  The resolver's
in-memory cache is also updated so the new value is live instantly.

Security
--------
- Only the authorised user (TELEGRAM_CHAT_ID) may execute /setkey.
- Keys containing PASSWORD, SECRET, TOKEN are confirmed but NOT echoed.
- The handler is intentionally standalone — import it in your telegram
  dispatcher alongside other command handlers.

Wiring example (in your Telegram bot dispatcher setup)::

    from telegram.setkey_handler import handle_setkey
    dispatcher.add_handler(CommandHandler("setkey", handle_setkey))
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger("nina.setkey")

_SENSITIVE_SUBSTRINGS = ("PASSWORD", "SECRET", "TOKEN", "KEY")


def _is_authorised(user_id: int) -> bool:
    """Return True if the Telegram user_id matches the configured TELEGRAM_CHAT_ID."""
    try:
        from core.key_resolver import resolver
        chat_id = resolver.get("TELEGRAM_CHAT_ID", required=False)
    except Exception:
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        return False
    return str(user_id).strip() == str(chat_id).strip()


def _is_sensitive(key: str) -> bool:
    return any(sub in key.upper() for sub in _SENSITIVE_SUBSTRINGS)


def _safe_echo(key: str, value: str) -> str:
    """Return a redacted representation for sensitive keys."""
    if _is_sensitive(key):
        visible = value[:4] if len(value) > 8 else "****"
        return f"{visible}{'*' * max(4, len(value) - 4)}"
    return value


# ---------------------------------------------------------------------------
# Core logic — framework-agnostic so it can be unit-tested without Telegram
# ---------------------------------------------------------------------------

def process_setkey(user_id: int, text: str) -> str:
    """Parse the /setkey command and persist the key.

    Args:
        user_id: Telegram sender ID (int).
        text:    Full message text including the /setkey prefix.

    Returns:
        Human-readable reply string.
    """
    if not _is_authorised(user_id):
        logger.warning("setkey_unauthorized user_id=%s", user_id)
        return "\u26d4 Unauthorised."

    parts = text.strip().split(None, 2)  # ['/setkey', KEY, VALUE]
    if len(parts) != 3 or parts[0].lower() not in ("/setkey", "setkey"):
        return (
            "\u2139\ufe0f Usage:  /setkey KEY VALUE\n\n"
            "Examples:\n"
            "  /setkey GROQ_API_KEY gsk_...\n"
            "  /setkey GEMINI_API_KEY AIza...\n"
            "  /setkey TELEGRAM_CHAT_ID 123456789"
        )

    key   = parts[1].strip().upper()
    value = parts[2].strip()

    if not key or not value:
        return "\u274c KEY and VALUE must not be empty."

    # Reject obviously bad values
    if any(bad in value.lower() for bad in ("your_", "<your", "example", "dummy")):
        return f"\u274c Value looks like a placeholder — not saved."

    try:
        from core.key_resolver import resolver
        resolver.set_key(key, value)
        logger.info("setkey_persisted key=%s source=telegram", key)
    except Exception as exc:
        logger.error("setkey_failed key=%s error=%s", key, exc)
        return f"\u274c Failed to save {key}: {exc}"

    echo = _safe_echo(key, value)
    return f"\u2705 {key} saved ({echo})  — active immediately, no restart needed."


# ---------------------------------------------------------------------------
# python-telegram-bot v20+ async handler
# ---------------------------------------------------------------------------

try:
    from telegram import Update
    from telegram.ext import ContextTypes

    async def handle_setkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa: E501
        """Async handler for python-telegram-bot v20+."""
        if not update.message or not update.effective_user:
            return
        reply = process_setkey(
            user_id=update.effective_user.id,
            text=update.message.text or "",
        )
        await update.message.reply_text(reply)

except ImportError:
    # python-telegram-bot not installed (e.g. unit-test environment)
    async def handle_setkey(*args, **kwargs):  # type: ignore[misc]
        pass
