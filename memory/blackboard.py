"""memory/blackboard.py — Hot Memory blackboard re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Blackboard wraps EventBus — the asyncio.Queue backbone for HOT tier.
All logic lives in core/event_bus.py — this is a thin shim.
"""
from core.event_bus import EventBus as Blackboard

__all__ = ["Blackboard"]
