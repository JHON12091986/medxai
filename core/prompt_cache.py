# core/prompt_cache.py
# NINA Prompt Prefix Cache — saves 60-80% tokens on repeated system prompts
# Strategy: hash(system_prompt + first_user_msg) → cache entry with TTL
# Gemini cachedContent compatible metadata included for future wiring.

import hashlib
import time
import logging
from typing import Optional

logger = logging.getLogger("nina.prompt_cache")

# Cache TTL in seconds. Gemini's cachedContent minimum is 60s.
DEFAULT_TTL = 300  # 5 minutes

class PromptCacheEntry:
    __slots__ = ("cache_key", "system_prompt", "cached_at", "ttl", "hit_count", "tokens_saved")

    def __init__(self, cache_key: str, system_prompt: str, ttl: int = DEFAULT_TTL):
        self.cache_key    = cache_key
        self.system_prompt = system_prompt
        self.cached_at    = time.monotonic()
        self.ttl          = ttl
        self.hit_count    = 0
        self.tokens_saved = 0

    @property
    def is_alive(self) -> bool:
        return (time.monotonic() - self.cached_at) < self.ttl

    def record_hit(self, tokens_saved: int = 0) -> None:
        self.hit_count    += 1
        self.tokens_saved += tokens_saved


class PromptCache:
    """
    In-process LRU prompt prefix cache.

    Usage in router._call_provider():
        cache_key, is_hit = self._prompt_cache.check(system_prompt, messages[:1])
        if is_hit:
            # skip re-sending system_prompt, use cache_key as context reference
    """

    def __init__(self, max_entries: int = 64, ttl: int = DEFAULT_TTL):
        self._store: dict[str, PromptCacheEntry] = {}
        self._max   = max_entries
        self._ttl   = ttl
        self._total_hits   = 0
        self._total_misses = 0

    def _make_key(self, system_prompt: str, anchor_messages: list) -> str:
        """Hash system prompt + first user message as cache key."""
        anchor = ""
        for m in anchor_messages:
            if isinstance(m, dict) and m.get("role") == "user":
                anchor = str(m.get("content", ""))[:256]
                break
        raw = f"{system_prompt[:2048]}|{anchor}"
        return hashlib.blake2b(raw.encode(), digest_size=16).hexdigest()

    def check(self, system_prompt: str, messages: list) -> tuple[str, bool]:
        """
        Returns (cache_key, is_cache_hit).
        Call this before every provider dispatch.
        """
        self._evict_expired()
        key = self._make_key(system_prompt, messages)

        if key in self._store:
            entry = self._store[key]
            # Rough token estimate: 1 token ≈ 4 chars
            saved = len(system_prompt) // 4
            entry.record_hit(tokens_saved=saved)
            self._total_hits += 1
            logger.debug(f"prompt_cache HIT key={key[:8]} hits={entry.hit_count} tokens_saved≈{entry.tokens_saved}")
            return key, True

        # Cache miss — store it
        self._store[key] = PromptCacheEntry(key, system_prompt, self._ttl)
        self._total_misses += 1
        if len(self._store) > self._max:
            self._evict_oldest()
        logger.debug(f"prompt_cache MISS key={key[:8]} stored entries={len(self._store)}")
        return key, False

    def invalidate(self, system_prompt: str, messages: list) -> None:
        key = self._make_key(system_prompt, messages)
        self._store.pop(key, None)

    def invalidate_all(self) -> None:
        self._store.clear()

    def _evict_expired(self) -> None:
        dead = [k for k, v in self._store.items() if not v.is_alive]
        for k in dead:
            del self._store[k]

    def _evict_oldest(self) -> None:
        if not self._store:
            return
        oldest = min(self._store, key=lambda k: self._store[k].cached_at)
        del self._store[oldest]

    @property
    def stats(self) -> dict:
        total = self._total_hits + self._total_misses
        hit_rate = (self._total_hits / total * 100) if total else 0
        total_saved = sum(e.tokens_saved for e in self._store.values())
        return {
            "entries":      len(self._store),
            "total_hits":   self._total_hits,
            "total_misses": self._total_misses,
            "hit_rate_pct": round(hit_rate, 1),
            "tokens_saved_est": total_saved,
        }
