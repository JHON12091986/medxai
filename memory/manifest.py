"""memory/manifest.py — File manifest re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Manifest wraps file_registry — the COLD tier file manifest tracker.
All logic lives in core/file_registry.py — this is a thin shim.
"""
from core.file_registry import FileRegistry as Manifest  # type: ignore[import]

__all__ = ["Manifest"]
