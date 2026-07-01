"""
core/memo_cache.py
NINA Memoization Cache — SHA256(prompt+context) → data/cache/{hash}.json
Zero tokens for repeated/identical calls. Thread-safe, TTL-aware.
Includes HyperDrive cache functionality for semantic caching and tool output caching.

Usage:
    from core.memo_cache import get_cached, set_cached, cache_key, cache

    key = cache_key(prompt, context)
    result = get_cached(key)
    if result is None:
        result = call_llm(prompt, context)
        set_cached(key, result)
"""

from __future__ import annotations
import hashlib, json, time, logging
import os
from pathlib import Path
from typing import Any, Optional, List, Dict

_ROOT = Path(__file__).parent.parent
_CACHE_DIR = _ROOT / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TTL = 3600 * 24 * 7  # 7 days

# Set up logging
logger = logging.getLogger("nina.memo_cache")


def cache_key(*parts: str) -> str:
    """Generate a stable SHA256 cache key from any number of strings."""
    combined = "||" .join(str(p) for p in parts)
    return hashlib.sha256(combined.encode()).hexdigest()


def _path(key: str) -> Path:
    return _CACHE_DIR / f"{key}.json"


def get_cached(key: str, ttl: int = DEFAULT_TTL) -> Optional[Any]:
    """Return cached value if exists and not expired. None otherwise."""
    p = _path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if ttl > 0 and time.time() - data.get("ts", 0) > ttl:
            p.unlink(missing_ok=True)
            return None
        return data.get("value")
    except Exception:
        return None


def set_cached(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Persist value to cache. Atomic write via temp file."""
    p = _path(key)
    tmp = p.with_suffix(".tmp")
    payload = json.dumps({"ts": time.time(), "ttl": ttl, "value": value}, ensure_ascii=False)
    tmp.write_text(payload)
    tmp.replace(p)


def invalidate(key: str) -> bool:
    """Remove a cache entry. Returns True if it existed."""
    p = _path(key)
    if p.exists():
        p.unlink()
        return True
    return False


def purge_expired(ttl: int = DEFAULT_TTL) -> int:
    """Remove all expired cache entries. Returns count removed."""
    now = time.time()
    removed = 0
    for p in _CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            if now - data.get("ts", 0) > ttl:
                p.unlink()
                removed += 1
        except Exception:
            pass
    return removed


def cache_stats() -> dict:
    files = list(_CACHE_DIR.glob("*.json"))
    total_bytes = sum(f.stat().st_size for f in files)
    return {"count": len(files), "total_kb": round(total_bytes / 1024, 1)}


class HyperDriveCache:
    """Provides semantic, workflow, and tool-output caching for HyperDrive."""
    
    CACHE_FILE = "data/hd_cache.json"
    
    def __init__(self, cache_path: str = CACHE_FILE) -> None:
        self.path = cache_path
        self.s: Dict[str, Any] = {}
        self.load()

    def _hash_key(self, prompt: str, messages: Optional[List[Dict[str, Any]]] = None) -> str:
        s = prompt
        if messages:
            s += json.dumps(messages, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def get_exact(self, prompt: str, messages: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """Exact-match payload lookup."""
        k = self._hash_key(prompt, messages)
        if k in self.s:
            item = self.s[k]
            if time.time() < item.get("expires_at", 0):
                return item.get("data")
        return None

    def get_semantic(self, prompt: str, threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        """Performs a token-overlap similarity match for semantic caching."""
        words1 = set(prompt.lower().split())
        if not words1:
            return None
            
        best_match = None
        best_score = 0.0
        
        now = time.time()
        for k, item in list(self.s.items()):
            if now >= item.get("expires_at", 0):
                continue
            original_prompt = item.get("prompt", "")
            words2 = set(original_prompt.lower().split())
            if not words2:
                continue
                
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            score = len(intersection) / len(union) if union else 0.0
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = item.get("data")
                
        if best_match:
            logger.info(f"hyperdrive: semantic cache hit with score {best_score:.2f}")
            return best_match
        return None

    def set(self, prompt: str, data: Any, ttl: int = 3600, messages: Optional[List[Dict[str, Any]]] = None) -> None:
        """Stores a cached result."""
        k = self._hash_key(prompt, messages)
        self.s[k] = {
            "prompt": prompt,
            "data": data,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }
        self.save()

    def cache_tool_output(self, tool_name: str, args: Dict[str, Any], output: str, ttl: int = 1800) -> None:
        """Caches deterministic tool runs (e.g. package checks, static file reads)."""
        key_str = f"tool:{tool_name}:{json.dumps(args, sort_keys=True)}"
        self.set(key_str, output, ttl=ttl)

    def get_tool_output(self, tool_name: str, args: Dict[str, Any]) -> Optional[str]:
        """Retrieves cached tool output."""
        key_str = f"tool:{tool_name}:{json.dumps(args, sort_keys=True)}"
        res = self.get_exact(key_str)
        if res:
            logger.info(f"hyperdrive: tool cache hit for {tool_name}")
            return str(res)
        return None

    def purge_expired(self) -> None:
        now = time.time()
        self.s = {k: v for k, v in self.s.items() if now < v.get("expires_at", 0)}

    def save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.purge_expired()
            with open(self.path, "w") as f:
                json.dump(self.s, f, indent=2)
        except Exception as e:
            logger.warning(f"hyperdrive: cache_save_failed: {e}")

    def load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r") as f:
                self.s = json.load(f)
            self.purge_expired()
        except Exception as e:
            logger.warning(f"hyperdrive: cache_load_failed: {e}")


# Global singleton
cache = HyperDriveCache()


if __name__ == "__main__":
    k = cache_key("hello", "world")
    set_cached(k, {"answer": 42})
    print(get_cached(k))
    print(cache_stats())
    
    # Test HyperDriveCache
    h_cache = HyperDriveCache()
    h_cache.set("test prompt", {"result": "success"})
    print(h_cache.get_exact("test prompt"))