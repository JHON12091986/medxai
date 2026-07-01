"""Task lock registry — ensures each subtask has exactly one executor. Prevents two agents from working on the same atomic task simultaneously. In-memory only; resets on process restart."""

import threading
import logging
import time

class TaskLockRegistry:
    """Singleton in-memory lock registry. Maps task_id → (executor_name, acquired_at)."""
    
    _instance = None
    _meta_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'TaskLockRegistry':
        """Return the thread-safe singleton TaskLockRegistry instance."""
        if cls._instance is None:
            with cls._meta_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._locks: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def acquire(self, task_id: str, executor_name: str) -> bool:
        """Attempt to acquire exclusive lock on task_id for executor_name. Returns True if acquired, False if already locked by another executor."""
        with self._lock:
            if task_id in self._locks:
                owner, _ = self._locks[task_id]
                if owner != executor_name:
                    logging.warning(f"Task {task_id} already locked by {owner}, cannot assign to {executor_name}")
                    return False
            self._locks[task_id] = (executor_name, time.time())
            return True

    def release(self, task_id: str) -> None:
        """Release lock on task_id. No-op if not locked."""
        with self._lock:
            self._locks.pop(task_id, None)
        logging.debug(f"Task lock released: {task_id}")

    def is_locked(self, task_id: str) -> bool:
        """True if task_id has an active lock."""
        with self._lock:
            return task_id in self._locks

    def locked_by(self, task_id: str) -> str | None:
        """Return executor name holding the lock, or None."""
        with self._lock:
            entry = self._locks.get(task_id)
            return entry[0] if entry else None

    def all_locks(self) -> dict:
        """Return copy of current locks dict."""
        with self._lock:
            return dict(self._locks)
