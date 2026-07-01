"""
core/__init__.py
NINA Core — single import point for all infrastructure modules.

Usage:
    from core import cache_key, get_cached, set_cached
    from core import count_tokens, fits_budget, trim_to_budget
    from core import route_query, route_agent
    from core import compress_file, compress_for_query
    from core import should_run, mark_done
    from core import HyperDriveCache, cache
"""

from core.memo_cache import cache_key, get_cached, set_cached, invalidate, cache_stats, HyperDriveCache, cache
from core.token_counter import count_tokens, fits_budget, trim_to_budget, token_report
from core.semantic_router import NINASemanticRouter
from core.context_compressor import compress_file, compress_for_query
from core.idempotency import should_run, mark_done, force_reset

__all__ = [
    "cache_key", "get_cached", "set_cached", "invalidate", "cache_stats",
    "HyperDriveCache", "cache",
    "count_tokens", "fits_budget", "trim_to_budget", "token_report",
    "NINASemanticRouter",
    "compress_file", "compress_for_query",
    "should_run", "mark_done", "force_reset",
]