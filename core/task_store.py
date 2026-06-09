"""
core/task_store.py — B-002: TaskStore Persistence Layer
=========================================================
JSON-backed task store with atomic writes, file locking, backup/rollback
resilience, and full CRUD operations for the AG1 Agentic Pipeline.

Usage example::

    from core.task_store import TaskStore, TaskStatus

    store = TaskStore()                              # default: data/tasks.json
    task  = store.create_task("Summarise inbox",
                               metadata={"source": "telegram"})
    print(task.id, task.status)                      # uuid  TaskStatus.PENDING

    store.update_task(task.id, status=TaskStatus.IN_PROGRESS)
    tasks = store.list_tasks(status=TaskStatus.PENDING, limit=20)
    ok    = store.delete_task(task.id)               # hard delete by default
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from filelock import FileLock, Timeout as FileLockTimeout

logger = logging.getLogger("nina.task_store")

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class TaskNotFoundError(KeyError):
    """Raised when a task_id does not exist in the store."""


class TaskStoreCorruptedError(RuntimeError):
    """Raised when the JSON store cannot be parsed or fails schema validation."""


class TaskStoreLockError(RuntimeError):
    """Raised when the file lock cannot be acquired within the timeout."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    """Lifecycle states for a Task."""

    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    FAILED      = "failed"
    CANCELLED   = "cancelled"


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string (e.g. 2026-06-08T16:30:00Z)."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


@dataclass
class Task:
    """Represents a single agentic task.

    Attributes:
        id:          UUID-based unique identifier (auto-generated).
        description: Human-readable goal / instruction.
        status:      Current lifecycle state (TaskStatus enum).
        created_at:  ISO 8601 UTC timestamp of creation.
        updated_at:  ISO 8601 UTC timestamp of last update.
        metadata:    Arbitrary extensible dict for planner, verifier, etc.
    """

    description: str
    id:          str        = field(default_factory=lambda: str(uuid.uuid4()))
    status:      TaskStatus = field(default=TaskStatus.PENDING)
    created_at:  str        = field(default_factory=_now_iso)
    updated_at:  str        = field(default_factory=_now_iso)
    metadata:    Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a JSON-compatible dict.

        Returns:
            dict with all fields; ``status`` stored as its string value.
        """
        data = asdict(self)
        data["status"] = self.status.value          # enum → str
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialise from a raw dict (e.g. loaded from JSON).

        Performs backward-compatibility migration for legacy fields
        (``goal``, ``plan_steps``, ``retries``, ``tool_used``, etc.) that
        are folded into ``metadata`` so existing dashboard integrations
        continue to work.

        Args:
            data: Raw dict representation.

        Returns:
            A fully-initialised :class:`Task` instance.

        Raises:
            TaskStoreCorruptedError: If required fields are missing.
        """
        data = dict(data)  # shallow copy — do not mutate caller's dict

        # --- legacy field migration -------------------------------------------
        legacy_keys = ("goal", "plan_steps", "retries", "result",
                       "tool_used", "priority", "tags")
        metadata = data.pop("metadata", {}) or {}
        for key in legacy_keys:
            if key in data:
                metadata.setdefault(key, data.pop(key))
        # If legacy records used 'goal' as the primary description
        if "description" not in data and "goal" in metadata:
            data["description"] = metadata["goal"]
        # running → in_progress status rename
        raw_status = data.get("status", "pending")
        if raw_status == "running":
            raw_status = "in_progress"
        # Validate description present
        if "description" not in data:
            raise TaskStoreCorruptedError(
                f"Task record missing 'description' field: {data!r}"
            )
        try:
            return cls(
                id          = data.get("id", str(uuid.uuid4())),
                description = data["description"],
                status      = TaskStatus(raw_status),
                created_at  = data.get("created_at", _now_iso()),
                updated_at  = data.get("updated_at", _now_iso()),
                metadata    = metadata,
            )
        except (ValueError, KeyError) as exc:
            raise TaskStoreCorruptedError(
                f"Cannot deserialise Task record: {exc}  data={data!r}"
            ) from exc


# ---------------------------------------------------------------------------
# TaskStore
# ---------------------------------------------------------------------------

# Minimal required keys for a valid tasks JSON object
_REQUIRED_TASK_KEYS = {"id", "description", "status"}


class TaskStore:
    """JSON-backed persistent store for :class:`Task` objects.

    Guarantees:
    - **Atomic writes**: data is written to a temp file then renamed so a
      process kill mid-write never corrupts the store.
    - **File locking**: :pypi:`filelock` prevents concurrent write corruption
      when multiple threads or processes share the same file.
    - **Backup / rollback**: a ``<path>.bak`` snapshot is taken before every
      write; on write failure the store rolls back to the last good snapshot.
    - **Resilience**: truncated or invalid JSON is detected on load; the store
      falls back to the backup and logs the corruption event.
    - **Soft delete**: controlled by the *soft_delete* constructor flag.

    Args:
        storage_path: Path to the JSON tasks file.
                      Defaults to ``"data/tasks.json"``.
        lock_timeout: Seconds to wait for the file lock before raising
                      :class:`TaskStoreLockError`.  Defaults to ``5``.
        soft_delete:  When *True*, ``delete_task`` sets
                      ``status=CANCELLED`` instead of removing the record.
                      Defaults to ``False`` (hard delete).
    """
    _shared_locks = {}

    def __init__(
        self,
        storage_path: str = "data/tasks.json",
        lock_timeout: float = 5.0,
        soft_delete: bool = False,
    ) -> None:
        self.storage_path = Path(storage_path)
        self.lock_path    = Path(f"{storage_path}.lock")
        self.bak_path     = Path(f"{storage_path}.bak")
        self.lock_timeout = lock_timeout
        self.soft_delete  = soft_delete
        self._lock        = self._shared_locks.setdefault(self.storage_path.resolve(), threading.RLock())
        self._ensure_storage()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_storage(self) -> None:
        """Create the data directory and initialise an empty store if needed."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            # Write empty dict-of-tasks directly (no locking needed yet)
            self.storage_path.write_text("{}", encoding="utf-8")
            logger.debug("Initialised empty task store at %s", self.storage_path)

    def _read_tasks(self) -> Dict[str, Task]:
        """Load all tasks from the JSON file into a dict keyed by task_id.

        Handles:
        - Empty file → empty dict.
        - Legacy list format → auto-migrated to dict format.
        - Truncated / malformed JSON → falls back to ``.bak`` if present.

        Returns:
            Dict mapping task_id → :class:`Task`.

        Raises:
            TaskStoreCorruptedError: If neither the main file nor backup can
                be parsed.
        """
        with self._lock:
            try:
                raw = self.storage_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                logger.warning("Cannot read task store: %s", exc)
                return {}

            if not raw:
                return {}

            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                return self._recover_from_backup(f"JSON decode error: {exc}")

            # --- schema validation + legacy list migration ---
            if isinstance(payload, list):
                logger.info(
                    "Migrating legacy list-format task store (%d items) → dict format",
                    len(payload),
                )
                payload = {item["id"]: item for item in payload if "id" in item}

            if not isinstance(payload, dict):
                return self._recover_from_backup(
                    f"Unexpected JSON root type: {type(payload).__name__}"
                )

            tasks: Dict[str, Task] = {}
            for tid, record in payload.items():
                if not isinstance(record, dict):
                    logger.warning("Skipping non-dict task record for id=%s", tid)
                    continue
                try:
                    tasks[tid] = Task.from_dict(record)
                except TaskStoreCorruptedError as exc:
                    logger.error("Skipping unparseable task %s: %s", tid, exc)
            return tasks

    def _recover_from_backup(self, reason: str) -> Dict[str, Task]:
        """Attempt to restore the task store from a backup snapshot.

        Args:
            reason: Human-readable description of why recovery was triggered.

        Returns:
            Parsed tasks from the backup, or an empty dict if unavailable.

        Raises:
            TaskStoreCorruptedError: If the backup also cannot be parsed.
        """
        with self._lock:
            logger.error(
                "Task store corrupted (%s) — attempting backup recovery from %s",
                reason, self.bak_path,
            )
            if not self.bak_path.exists():
                logger.error("No backup available at %s; starting with empty store", self.bak_path)
                return {}
            try:
                payload = json.loads(self.bak_path.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    payload = {item["id"]: item for item in payload if "id" in item}
                tasks = {}
                for tid, record in payload.items():
                    try:
                        tasks[tid] = Task.from_dict(record)
                    except TaskStoreCorruptedError:
                        pass
                logger.info("Recovered %d task(s) from backup", len(tasks))
                # Restore good backup over the corrupted main file
                shutil.copy2(self.bak_path, self.storage_path)
                return tasks
            except Exception as exc:  # noqa: BLE001
                raise TaskStoreCorruptedError(
                    f"Backup recovery failed: {exc}"
                ) from exc

    def _write_tasks(self, tasks: Dict[str, Task]) -> None:
        """Persist the task dict using an atomic temp-file rename.

        Steps:
        1. Acquire file lock (raises :class:`TaskStoreLockError` on timeout).
        2. Copy current file to ``<path>.bak``.
        3. Serialise to a temp file in the same directory.
        4. ``os.replace()`` the temp file over the target (atomic on POSIX).
        5. On any failure: delete temp file, roll back to backup, re-raise.

        Args:
            tasks: Dict mapping task_id → :class:`Task` to persist.

        Raises:
            TaskStoreLockError: If the lock cannot be acquired.
            TaskStoreCorruptedError: If the write or rollback fails.
        """
        if not self._lock.acquire(timeout=self.lock_timeout):
            raise TaskStoreLockError(
                "TaskStore internal lock acquisition timed out"
            )
        try:
            try:
                lock = FileLock(str(self.lock_path), timeout=self.lock_timeout)
            except Exception as exc:  # noqa: BLE001
                raise TaskStoreLockError(f"Cannot create lock file: {exc}") from exc

            try:
                with lock:
                    # 1. Backup current file
                    if self.storage_path.exists():
                        shutil.copy2(self.storage_path, self.bak_path)

                    # 2. Write to temp file
                    tmp_fd, tmp_path = tempfile.mkstemp(
                        dir=self.storage_path.parent,
                        prefix=".tasks_tmp_",
                        suffix=".json",
                    )
                    try:
                        with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
                            json.dump(
                                {tid: t.to_dict() for tid, t in tasks.items()},
                                fh,
                                indent=2,
                                ensure_ascii=False,
                            )
                        # 3. Atomic rename
                        os.replace(tmp_path, self.storage_path)
                        # 4. Update backup with the fresh success
                        shutil.copy2(self.storage_path, self.bak_path)
                    except Exception as exc:  # noqa: BLE001
                        # Cleanup temp
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass
                        # Rollback
                        if self.bak_path.exists():
                            try:
                                shutil.copy2(self.bak_path, self.storage_path)
                                logger.warning(
                                    "Write failed (%s) — rolled back to backup", exc
                                )
                            except OSError as rb_exc:
                                raise TaskStoreCorruptedError(
                                    f"Write failed AND rollback failed: {rb_exc}"
                                ) from rb_exc
                        raise TaskStoreCorruptedError(f"Write failed: {exc}") from exc
            except FileLockTimeout as exc:
                raise TaskStoreLockError(
                    f"Could not acquire task store lock within {self.lock_timeout}s"
                ) from exc

        finally:
            self._lock.release()
    # ------------------------------------------------------------------
    # Public CRUD API
    # ------------------------------------------------------------------

    def create_task(
        self,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task and persist it.

        Args:
            description: Human-readable goal / instruction.
            metadata:    Optional extra fields (planner context, source, etc.).

        Returns:
            The newly created :class:`Task` with ``status=PENDING``.
        """
        if not self._lock.acquire(timeout=self.lock_timeout):
            raise TaskStoreLockError("TaskStore internal lock acquisition timed out")
        try:
            task = Task(description=description, metadata=metadata or {})
            tasks = self._read_tasks()
            tasks[task.id] = task
            self._write_tasks(tasks)
            logger.info(
                '{"event":"task_created","task_id":"%s","status":"%s"}',
                task.id, task.status.value,
            )
            return task

        finally:
            self._lock.release()
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its UUID.

        Args:
            task_id: UUID string of the task.

        Returns:
            The matching :class:`Task`, or *None* if not found.
        """
        with self._lock:
            return self._read_tasks().get(task_id)

    def update_task(self, task_id: str, **kwargs: Any) -> Task:
        """Update one or more fields of an existing task.

        ``updated_at`` is automatically refreshed on every successful call.

        Args:
            task_id: UUID of the task to update.
            **kwargs: Field name → new value pairs.  ``status`` may be
                      supplied as a :class:`TaskStatus` member or its string
                      value.

        Returns:
            The updated :class:`Task`.

        Raises:
            TaskNotFoundError: If *task_id* does not exist.
        """
        if not self._lock.acquire(timeout=self.lock_timeout):
            raise TaskStoreLockError("TaskStore internal lock acquisition timed out")
        try:
            tasks = self._read_tasks()
            if task_id not in tasks:
                raise TaskNotFoundError(
                    f"Task '{task_id}' not found — cannot update"
                )
            task = tasks[task_id]
            for key, value in kwargs.items():
                if key == "status" and isinstance(value, str):
                    value = TaskStatus(value)
                if hasattr(task, key):
                    setattr(task, key, value)
                else:
                    # Store unknown kwargs in metadata rather than silently dropping
                    task.metadata[key] = value
            task.updated_at = _now_iso()
            tasks[task_id] = task
            self._write_tasks(tasks)
            logger.info(
                '{"event":"task_updated","task_id":"%s","status":"%s"}',
                task.id, task.status.value,
            )
            return task

        finally:
            self._lock.release()
    def delete_task(self, task_id: str) -> bool:
        """Remove or soft-cancel a task.

        Behaviour is controlled by the *soft_delete* constructor flag:
        - ``soft_delete=False`` (default): permanently removes the record.
        - ``soft_delete=True``: sets ``status=CANCELLED`` and keeps the record.

        Args:
            task_id: UUID of the task to delete.

        Returns:
            ``True`` if the task existed and was deleted/cancelled;
            ``False`` if *task_id* was not found.
        """
        if not self._lock.acquire(timeout=self.lock_timeout):
            raise TaskStoreLockError("TaskStore internal lock acquisition timed out")
        try:
            tasks = self._read_tasks()
            if task_id not in tasks:
                return False
            if self.soft_delete:
                tasks[task_id].status     = TaskStatus.CANCELLED
                tasks[task_id].updated_at = _now_iso()
                logger.info('{"event":"task_soft_deleted","task_id":"%s"}', task_id)
            else:
                del tasks[task_id]
                logger.info('{"event":"task_deleted","task_id":"%s"}', task_id)
            self._write_tasks(tasks)
            return True

        finally:
            self._lock.release()
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit:  Optional[int]        = None,
    ) -> List[Task]:
        """Return tasks optionally filtered by status and/or paginated.

        Results are returned in ascending ``created_at`` order.

        Args:
            status: If provided, only tasks with this :class:`TaskStatus` are
                    returned.  Accepts enum member or its string value.
            limit:  Maximum number of tasks to return.  *None* means no cap.

        Returns:
            List of matching :class:`Task` objects.
        """
        with self._lock:
            if isinstance(status, str):
                status = TaskStatus(status)

            # Optimization: Filter by status before sorting to reduce sort payload from O(N log N) to O(k log k)
            tasks_iter = self._read_tasks().values()
            if status is not None:
                tasks_iter = [t for t in tasks_iter if t.status == status]

            tasks = sorted(
                tasks_iter,
                key=lambda t: t.created_at,
            )

            if limit is not None:
                tasks = tasks[:limit]
            return tasks

    # ------------------------------------------------------------------
    # Convenience helpers (used by router / dashboard)
    # ------------------------------------------------------------------

    def get_task_metrics(self) -> Dict[str, Any]:
        """Return aggregate counts by status.

        Returns:
            Dict with ``total``, ``by_status`` sub-dict.
        """
        with self._lock:
            all_tasks = self._read_tasks().values()
            by_status: Dict[str, int] = {}
            for t in all_tasks:
                by_status[t.status.value] = by_status.get(t.status.value, 0) + 1
            return {"total": len(list(all_tasks)), "by_status": by_status}

    def format_tasks_summary(self) -> str:
        """Return a human-readable multi-line summary of active tasks.

        Returns:
            Formatted string suitable for Telegram / CLI output.
        """
        with self._lock:
            active_statuses = {
                TaskStatus.IN_PROGRESS, TaskStatus.PENDING, TaskStatus.FAILED
            }
            active = [
                t for t in self._read_tasks().values() if t.status in active_statuses
            ]
            if not active:
                return "✅ No active tasks."

            order = {
                TaskStatus.IN_PROGRESS: 0,
                TaskStatus.PENDING:     1,
                TaskStatus.FAILED:      2,
            }
            active.sort(key=lambda t: order.get(t.status, 99))
            symbols = {
                TaskStatus.IN_PROGRESS: "🔵",
                TaskStatus.PENDING:     "🟡",
                TaskStatus.FAILED:      "❌",
            }
            lines = [f"📋 NINA Tasks ({len(active)} active)"]
            for t in active[:10]:
                sym  = symbols.get(t.status, "❓")
                goal = t.description
                if len(goal) > 40:
                    goal = goal[:37] + "..."
                lines.append(f"{sym} {t.status.value}: {goal} [{t.id[:8]}]")
            if len(active) > 10:
                lines.append(f"...and {len(active) - 10} more")
            return "\n".join(lines)
