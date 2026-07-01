import json
import os
import threading
from pathlib import Path
from datetime import datetime
from core.task_manager.task_spec import TaskSpec

class TaskQueue:
    """
    File-backed, thread-safe task queue.
    Persists to data/task_queue.json.
    All writes are atomic (write temp, os.replace).
    """

    QUEUE_FILE = Path("data/task_queue.json")

    def __init__(self, queue_file: Path = None):
        self.queue_file = Path(queue_file) if queue_file is not None else self.QUEUE_FILE
        self.lock = threading.Lock()
        # Ensure parent directory exists
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        # Initialize queue file if it doesn't exist
        if not self.queue_file.exists():
            self._write_tasks_unlocked([])

    def _load_tasks_unlocked(self) -> list[TaskSpec]:
        if not self.queue_file.exists():
            return []
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return [TaskSpec.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_tasks_unlocked(self, tasks: list[TaskSpec]):
        tmp_file = self.queue_file.with_suffix(".tmp")
        data = [task.to_dict() for task in tasks]
        # Ensure parent of temp exists too
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, self.queue_file)

    def enqueue(self, spec: TaskSpec) -> bool:
        """
        Add a task to the queue.
        Returns False (no-op) if a task with the same idempotency_key already exists
        in any status. This is the PRIMARY dedup guard.
        Returns True if successfully enqueued.
        """
        with self.lock:
            tasks = self._load_tasks_unlocked()
            for t in tasks:
                if t.idempotency_key == spec.idempotency_key:
                    return False
            tasks.append(spec)
            self._write_tasks_unlocked(tasks)
            return True

    def dequeue(self, priority_order: list[str] = None) -> TaskSpec | None:
        """
        Pop the highest-priority PENDING task.
        priority_order defaults to ["P1", "P2", "P3"].
        Also checks depends_on — only returns a task whose dependencies are all DONE.
        Returns None if queue is empty or no unblocked tasks.
        """
        if priority_order is None:
            priority_order = ["P1", "P2", "P3"]
        with self.lock:
            tasks = self._load_tasks_unlocked()
            status_map = {t.task_id: t.status for t in tasks}
            
            for priority in priority_order:
                for t in tasks:
                    if t.status == "PENDING" and t.priority == priority:
                        # Check dependencies
                        dependencies_satisfied = True
                        for dep_id in t.depends_on:
                            if status_map.get(dep_id) != "DONE":
                                dependencies_satisfied = False
                                break
                        if dependencies_satisfied:
                            return t
            return None

    def peek(self, n: int = 5) -> list[TaskSpec]:
        """Return top N pending tasks without removing them."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            pending = [t for t in tasks if t.status == "PENDING"]
            priority_map = {"P1": 0, "P2": 1, "P3": 2}
            pending_sorted = sorted(pending, key=lambda t: priority_map.get(t.priority, 3))
            return pending_sorted[:n]

    def mark_done(self, task_id: str, pr_number: int = 0) -> bool:
        """Mark a task DONE, set done_at and pr_number."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            found = False
            for t in tasks:
                if t.task_id == task_id:
                    t.status = "DONE"
                    t.pr_number = pr_number
                    t.done_at = datetime.now().isoformat()
                    found = True
                    break
            if found:
                self._write_tasks_unlocked(tasks)
            return found

    def mark_skipped(self, task_id: str, reason: str = "") -> bool:
        """Mark a task SKIPPED."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            found = False
            for t in tasks:
                if t.task_id == task_id:
                    t.status = "SKIPPED"
                    t.done_at = datetime.now().isoformat()
                    found = True
                    break
            if found:
                self._write_tasks_unlocked(tasks)
            return found

    def mark_failed(self, task_id: str, reason: str = "") -> bool:
        """Mark a task FAILED."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            found = False
            for t in tasks:
                if t.task_id == task_id:
                    t.status = "FAILED"
                    t.done_at = datetime.now().isoformat()
                    found = True
                    break
            if found:
                self._write_tasks_unlocked(tasks)
            return found

    def mark_dispatched(self, task_id: str) -> bool:
        """Mark a task DISPATCHED."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            found = False
            for t in tasks:
                if t.task_id == task_id:
                    t.status = "DISPATCHED"
                    t.dispatched_at = datetime.now().isoformat()
                    found = True
                    break
            if found:
                self._write_tasks_unlocked(tasks)
            return found

    def list_pending(self) -> list[TaskSpec]:
        """Return all PENDING tasks."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            return [t for t in tasks if t.status == "PENDING"]

    def list_all(self) -> list[TaskSpec]:
        """Return all tasks regardless of status."""
        with self.lock:
            return self._load_tasks_unlocked()

    def stats(self) -> dict:
        """
        Return summary: {"total": N, "pending": N, "done": N,
                         "skipped": N, "failed": N, "dispatched": N}
        """
        with self.lock:
            tasks = self._load_tasks_unlocked()
            total = len(tasks)
            pending = sum(1 for t in tasks if t.status == "PENDING")
            done = sum(1 for t in tasks if t.status == "DONE")
            skipped = sum(1 for t in tasks if t.status == "SKIPPED")
            failed = sum(1 for t in tasks if t.status == "FAILED")
            dispatched = sum(1 for t in tasks if t.status == "DISPATCHED")
            return {
                "total": total,
                "pending": pending,
                "done": done,
                "skipped": skipped,
                "failed": failed,
                "dispatched": dispatched
            }

    def purge_done(self, keep_last: int = 50) -> int:
        """Remove all DONE/SKIPPED tasks older than keep_last. Returns count removed."""
        with self.lock:
            tasks = self._load_tasks_unlocked()
            done_skipped = [t for t in tasks if t.status in ("DONE", "SKIPPED")]
            active_failed_dispatched = [t for t in tasks if t.status not in ("DONE", "SKIPPED")]
            
            if len(done_skipped) <= keep_last:
                return 0
            
            keep_tasks = done_skipped[-keep_last:]
            removed_count = len(done_skipped) - len(keep_tasks)
            
            remaining_ids = {t.task_id for t in keep_tasks} | {t.task_id for t in active_failed_dispatched}
            final_tasks = [t for t in tasks if t.task_id in remaining_ids]
            
            self._write_tasks_unlocked(final_tasks)
            return removed_count
