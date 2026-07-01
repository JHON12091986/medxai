"""memory/indexer.py — Warm Memory indexer re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Indexer wraps LayeredMemory — aiosqlite WAL-mode WARM tier.
All logic lives in core/layered_memory.py — this is a thin shim.
"""
try:
    from core.layered_memory import LayeredMemory as Indexer  # type: ignore[import]
except ImportError:
    from core.memory import Memory as Indexer  # type: ignore[import]

__all__ = ["Indexer"]
