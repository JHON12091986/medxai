"""
core/cognitive/reflector.py — DEPRECATED duplicate.
Redirects to the canonical core.reflexion.ReflexionEngine.

Do NOT add logic here. All reflexion implementation lives in core/reflexion.py.
"""
from __future__ import annotations
from core.reflexion import ReflexionEngine  # noqa: F401 — re-export for backward compat

# Legacy alias some old callers may have used
Reflector = ReflexionEngine

__all__ = ["ReflexionEngine", "Reflector"]
