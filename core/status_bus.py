"""
core/status_bus.py — Per-request async live-status push bus.
Pass 0 · 25 Jun 2026 · Nina Live Status Display

Purpose
-------
Pipeline stages (router, ninagate, opencode) call ``push()`` with a human-
readable status string.  The Telegram interface subscribes a callback per
request so the in-flight placeholder message is edited live.

Design rules
------------
* Uses ``contextvars.ContextVar`` — each asyncio Task gets its own subscriber.
  Concurrent requests CANNOT cross-contaminate each other's status messages.
* ``push()`` is fire-and-forget: 2.0 s timeout, silent drop on any error.
  The pipeline is NEVER blocked or crashed by a status update.
* Zero external dependencies.  Pure stdlib asyncio + contextvars.
* Thin shim — no state accumulation, no retries, no queuing.

Usage
-----
# In the Telegram handler (per-request):
    from core.status_bus import subscribe, push

    token = subscribe(lambda msg: edit_message(sent, msg))
    try:
        result = await router.route(...)
    finally:
        unsubscribe(token)   # always clean up

# In the router / ninagate / opencode:
    from core.status_bus import push
    await push(StatusStages.ROUTING.format(provider="GEMINI"))
"""
from __future__ import annotations

import asyncio
import logging
from contextvars import ContextVar, Token
from typing import Awaitable, Callable, Optional

_log = logging.getLogger("nina.status_bus")

# One subscriber callback per asyncio context (per request Task)
_STATUS_CB: ContextVar[Optional[Callable[[str], Awaitable[None]]]] = ContextVar(
    "_STATUS_CB", default=None
)

_PUSH_TIMEOUT_S: float = 2.0  # max seconds to wait for a Telegram edit


def subscribe(callback: Callable[[str], Awaitable[None]]) -> Token:
    """
    Register *callback* as the status receiver for the current asyncio context.

    Returns the ``Token`` produced by ``ContextVar.set()``; pass it to
    ``unsubscribe()`` when the request is finished to restore the previous
    subscriber (or None).

    Parameters
    ----------
    callback:
        An async callable that accepts a single ``str`` message and updates
        the user-visible Telegram placeholder.  Must not raise.
    """
    return _STATUS_CB.set(callback)


def unsubscribe(token: Token) -> None:
    """
    Restore the ContextVar to its previous value using *token*.
    Always call this in a ``finally`` block after ``subscribe()``.
    """
    _STATUS_CB.reset(token)


async def push(msg: str) -> None:
    """
    Emit a live-status message to the current request's subscriber.

    Behaviour
    ---------
    * If no subscriber is registered (e.g. CLI mode, unit tests) → silent no-op.
    * Calls the subscriber with a 2-second timeout.
    * Any exception from the subscriber (network error, Telegram rate-limit,
      cancelled task) is caught and logged at DEBUG level — the pipeline
      continues unaffected.
    """
    cb = _STATUS_CB.get()
    if cb is None:
        return
    try:
        await asyncio.wait_for(cb(msg), timeout=_PUSH_TIMEOUT_S)
    except asyncio.TimeoutError:
        _log.debug("status_bus: push timed out after %ss — msg=%r", _PUSH_TIMEOUT_S, msg)
    except asyncio.CancelledError:
        # Request was aborted — do not re-raise, just stop
        pass
    except Exception as exc:
        _log.debug("status_bus: push suppressed error — %s: %s", type(exc).__name__, exc)


async def push_safe(msg: str) -> None:
    """Alias for push() — explicit naming for call-sites that want to signal
    they are intentionally not awaiting the result in a critical path."""
    await push(msg)
