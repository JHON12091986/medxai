"""
core/bloom_filter.py
NINA Probabilistic Dedup Gate

Before any expensive disk scan, LLM call, or WAL write,
query the Bloom filter. Zero false negatives — if it says
"not seen", that's 100% guaranteed. Saves tokens on every
loop iteration by killing duplicate event triggers early.

Usage:
    from core.bloom_filter import BloomFilter

    bf = BloomFilter.load()          # persistent across restarts
    if bf.might_contain(event_key):
        return                       # already processed — skip
    bf.add(event_key)
    bf.save()
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
STORE = ROOT / "data" / "bloom_filter.json"


class BloomFilter:
    """Simple persistent Bloom filter backed by a JSON bitarray.

    Default parameters (capacity=50_000, error_rate=0.01) give
    a ~479 KB bitarray — negligible RAM footprint.
    """

    def __init__(self, capacity: int = 50_000, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        self.size = self._optimal_size(capacity, error_rate)
        self.hash_count = self._optimal_hashes(self.size, capacity)
        self._bits: list[int] = [0] * self.size
        self._count = 0

    # ------------------------------------------------------------------ #
    #  Core ops                                                            #
    # ------------------------------------------------------------------ #
    def add(self, item: str) -> None:
        for i in self._hash_positions(item):
            self._bits[i] = 1
        self._count += 1

    def might_contain(self, item: str) -> bool:
        """Return True if item *might* be in the set (possible false positive).
        Return False means item is DEFINITELY not in the set."""
        return all(self._bits[i] for i in self._hash_positions(item))

    def __contains__(self, item: str) -> bool:
        return self.might_contain(item)

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #
    def save(self) -> None:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STORE.with_suffix(".tmp")
        tmp.write_text(json.dumps({
            "capacity": self.capacity,
            "error_rate": self.error_rate,
            "size": self.size,
            "hash_count": self.hash_count,
            "count": self._count,
            "bits": self._bits,
        }))
        tmp.replace(STORE)

    @classmethod
    def load(cls, capacity: int = 50_000, error_rate: float = 0.01) -> "BloomFilter":
        """Load from disk or create fresh."""
        bf = cls(capacity=capacity, error_rate=error_rate)
        if STORE.exists():
            try:
                data = json.loads(STORE.read_text())
                bf.capacity = data["capacity"]
                bf.error_rate = data["error_rate"]
                bf.size = data["size"]
                bf.hash_count = data["hash_count"]
                bf._count = data["count"]
                bf._bits = data["bits"]
            except Exception:
                pass  # corrupt store — start fresh
        return bf

    def reset(self) -> None:
        """Clear all bits — use after a full WAL replay/rebuild."""
        self._bits = [0] * self.size
        self._count = 0
        self.save()

    # ------------------------------------------------------------------ #
    #  Internals                                                           #
    # ------------------------------------------------------------------ #
    def _hash_positions(self, item: str):
        """Generate k hash positions for item."""
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha256(item.encode()).hexdigest(), 16)
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        return math.ceil(-n * math.log(p) / (math.log(2) ** 2))

    @staticmethod
    def _optimal_hashes(m: int, n: int) -> int:
        return max(1, round((m / n) * math.log(2)))

    @property
    def fill_ratio(self) -> float:
        return sum(self._bits) / self.size

    def __repr__(self) -> str:
        return (f"BloomFilter(capacity={self.capacity}, "
                f"count={self._count}, fill={self.fill_ratio:.2%})")


# Module-level singleton — import and use directly
_instance: Optional[BloomFilter] = None


def get_bloom() -> BloomFilter:
    """Return the module-level singleton (lazy-loaded from disk)."""
    global _instance
    if _instance is None:
        _instance = BloomFilter.load()
    return _instance


def seen(key: str) -> bool:
    """Quick check: has this event key been processed before?"""
    return get_bloom().might_contain(key)


def mark_seen(key: str, persist: bool = True) -> None:
    """Mark event key as processed. persist=False for hot-path batching."""
    bf = get_bloom()
    bf.add(key)
    if persist:
        bf.save()
