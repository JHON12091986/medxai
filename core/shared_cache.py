#!/usr/bin/env python3
"""
NINA Shared Cache Manager
Implements a multi-process safe file-backed cache system
that allows both nina.service and ninagate.service to share metrics,
routing telemetry, and response caches.
"""

import os
import json
import time
import fcntl
import logging
import pathlib
from typing import Any, Optional

logger = logging.getLogger("nina.shared_cache")

class SharedCache:
    def __init__(self, filepath: str = "data/shared_routing_cache.json"):
        self.path = pathlib.Path(filepath)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_file()

    def _init_file(self):
        """Initializes cache file if it does not exist."""
        if not self.path.exists():
            self._write_atomic({})

    def _lock_and_read(self, f) -> dict:
        """Helper to lock file and read dict contents safely."""
        try:
            fcntl.flock(f, fcntl.LOCK_SH)
            f.seek(0)
            data = f.read()
            if not data:
                return {}
            return json.loads(data)
        except Exception as e:
            logger.error(f"Error locking and reading shared cache: {e}")
            return {}
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    def _write_atomic(self, data: dict):
        """Writes to a temporary file and renames to prevent partial write corruption."""
        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, "w") as tf:
                fcntl.flock(tf, fcntl.LOCK_EX)
                json.dump(data, tf, indent=2)
                tf.flush()
                os.fsync(tf.fileno())
                fcntl.flock(tf, fcntl.LOCK_UN)
            temp_path.replace(self.path)
        except Exception as e:
            logger.error(f"Error executing atomic write on shared cache: {e}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def get(self, key: str) -> Optional[Any]:
        """Gets value from shared cache safely across processes."""
        if not self.path.exists():
            return None
        try:
            with open(self.path, "r") as f:
                cached = self._lock_and_read(f)
                entry = cached.get(key)
                if entry:
                    # Check expiration
                    if "expires_at" in entry and entry["expires_at"] < time.time():
                        # Lazy delete
                        self.delete(key)
                        return None
                    return entry.get("value")
        except Exception as e:
            logger.error(f"Error fetching from shared cache: {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Sets value in shared cache with optional TTL."""
        try:
            with open(self.path, "r+") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                cached = json.loads(f.read() or "{}")
                
                expires_at = time.time() + ttl if ttl else None
                cached[key] = {
                    "value": value,
                    "expires_at": expires_at,
                    "updated_at": time.time()
                }
                
                # Prune expired entries to prevent cache growth
                now = time.time()
                pruned = {
                    k: v for k, v in cached.items()
                    if v.get("expires_at") is None or v["expires_at"] > now
                }
                
                self._write_atomic(pruned)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Error updating shared cache: {e}")

    def delete(self, key: str):
        """Deletes key from shared cache."""
        try:
            with open(self.path, "r+") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                cached = json.loads(f.read() or "{}")
                if key in cached:
                    del cached[key]
                    self._write_atomic(cached)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Error deleting key from shared cache: {e}")

    def clear(self):
        """Clears entire shared cache."""
        self._write_atomic({})
