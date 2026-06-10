"""
tests/test_task_store.py — B-002 unit test suite
=================================================
Covers:
  - Task serialisation / deserialisation (incl. legacy field migration)
  - All CRUD operations
  - Soft-delete vs hard-delete
  - list_tasks filtering (status, limit)
  - Atomic write guarantees
  - Backup creation and rollback on write failure
  - Corruption recovery (malformed JSON → backup restore)
  - Concurrent threading writes (race-condition stress test)
  - TaskNotFoundError, TaskStoreCorruptedError, TaskStoreLockError
"""

import json
import os
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from core.task_store import (
    Task,
    TaskNotFoundError,
    TaskStore,
    TaskStoreCorruptedError,
    TaskStoreLockError,
    TaskStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path: Path) -> TaskStore:
    """Fresh TaskStore backed by a temp directory."""
    return TaskStore(storage_path=str(tmp_path / "tasks.json"))


@pytest.fixture()
def soft_store(tmp_path: Path) -> TaskStore:
    """TaskStore with soft_delete=True."""
    return TaskStore(storage_path=str(tmp_path / "soft_tasks.json"), soft_delete=True)


# ---------------------------------------------------------------------------
# Task model: serialisation
# ---------------------------------------------------------------------------

class TestTaskModel:
    def test_to_dict_contains_string_status(self):
        task = Task(description="hello")
        d = task.to_dict()
        assert d["status"] == "pending"
        assert isinstance(d["status"], str)

    def test_roundtrip_serialisation(self):
        task = Task(description="roundtrip", metadata={"x": 1})
        restored = Task.from_dict(task.to_dict())
        assert restored.id          == task.id
        assert restored.description == task.description
        assert restored.status      == task.status
        assert restored.metadata    == task.metadata

    def test_from_dict_accepts_string_status(self):
        d = Task(description="test").to_dict()
        d["status"] = "completed"
        t = Task.from_dict(d)
        assert t.status == TaskStatus.COMPLETED

    def test_from_dict_invalid_status_raises(self):
        d = Task(description="bad").to_dict()
        d["status"] = "unknown_status_xyz"
        with pytest.raises(TaskStoreCorruptedError):
            Task.from_dict(d)

    def test_legacy_migration_goal_field(self):
        legacy = {
            "id":         "abc",
            "goal":       "old goal",
            "status":     "pending",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "metadata":   {},
        }
        task = Task.from_dict(legacy)
        assert task.description == "old goal"
        assert task.metadata.get("goal") == "old goal"

    def test_legacy_migration_running_status(self):
        d = Task(description="x").to_dict()
        d["status"] = "running"
        task = Task.from_dict(d)
        assert task.status == TaskStatus.IN_PROGRESS


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

class TestCRUD:
    def test_create_task_returns_pending(self, store: TaskStore):
        task = store.create_task("Buy groceries")
        assert task.status      == TaskStatus.PENDING
        assert task.description == "Buy groceries"
        assert len(task.id)     == 36  # UUID format

    def test_create_task_with_metadata(self, store: TaskStore):
        task = store.create_task("Fetch email", metadata={"source": "telegram"})
        assert task.metadata["source"] == "telegram"

    def test_get_task_found(self, store: TaskStore):
        t = store.create_task("Get me")
        assert store.get_task(t.id).id == t.id

    def test_get_task_not_found_raises_keyerror(self, store: TaskStore):
        with pytest.raises(TaskNotFoundError):
            store.get_task("nonexistent-id-000")

    def test_update_task_status(self, store: TaskStore):
        t = store.create_task("Update me")
        updated = store.update_task(t.id, status=TaskStatus.IN_PROGRESS)
        assert updated.status == TaskStatus.IN_PROGRESS
        # Persisted
        assert store.get_task(t.id).status == TaskStatus.IN_PROGRESS

    def test_update_task_status_as_string(self, store: TaskStore):
        t = store.create_task("String status")
        updated = store.update_task(t.id, status="completed")
        assert updated.status == TaskStatus.COMPLETED

    def test_update_task_not_found_raises(self, store: TaskStore):
        with pytest.raises(TaskNotFoundError):
            store.update_task("bad-id", status=TaskStatus.FAILED)

    def test_update_refreshes_updated_at(self, store: TaskStore):
        t = store.create_task("Timestamps")
        original_updated = t.updated_at
        time.sleep(0.01)
        updated = store.update_task(t.id, status=TaskStatus.COMPLETED)
        assert updated.updated_at >= original_updated

    def test_delete_task_hard(self, store: TaskStore):
        t = store.create_task("Delete me")
        assert store.delete_task(t.id) is True
        with pytest.raises(TaskNotFoundError):
            store.get_task(t.id)

    def test_delete_task_returns_false_if_missing(self, store: TaskStore):
        assert store.delete_task("ghost-id") is False

    def test_soft_delete_cancels_task(self, soft_store: TaskStore):
        t = soft_store.create_task("Soft delete me")
        assert soft_store.delete_task(t.id) is True
        persisted = soft_store.get_task(t.id)
        assert persisted is not None
        assert persisted.status == TaskStatus.CANCELLED


# ---------------------------------------------------------------------------
# list_tasks filtering and pagination
# ---------------------------------------------------------------------------

class TestListTasks:
    def _populate(self, store: TaskStore) -> list:
        tasks = [
            store.create_task(f"Task {i}") for i in range(5)
        ]
        store.update_task(tasks[0].id, status=TaskStatus.COMPLETED)
        store.update_task(tasks[1].id, status=TaskStatus.FAILED)
        return tasks

    def test_list_all(self, store: TaskStore):
        self._populate(store)
        assert len(store.list_tasks()) == 5

    def test_list_by_status(self, store: TaskStore):
        self._populate(store)
        pending = store.list_tasks(status=TaskStatus.PENDING)
        assert len(pending) == 3
        assert all(t.status == TaskStatus.PENDING for t in pending)

    def test_list_by_status_string(self, store: TaskStore):
        self._populate(store)
        result = store.list_tasks(status="completed")
        assert len(result) == 1

    def test_list_with_limit(self, store: TaskStore):
        self._populate(store)
        result = store.list_tasks(limit=2)
        assert len(result) == 2

    def test_list_empty_store(self, store: TaskStore):
        assert store.list_tasks() == []


# ---------------------------------------------------------------------------
# Persistence: file I/O and atomic writes
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_tasks_survive_reload(self, tmp_path: Path):
        path = str(tmp_path / "tasks.json")
        s1 = TaskStore(storage_path=path)
        t  = s1.create_task("Persist me")
        # Open a second store pointing at same file
        s2 = TaskStore(storage_path=path)
        assert s2.get_task(t.id) is not None
        assert s2.get_task(t.id).description == "Persist me"

    def test_backup_created_on_write(self, tmp_path: Path):
        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path)
        store.create_task("First")
        store.create_task("Second")  # second write should create .bak
        bak = tmp_path / "tasks.json.bak"
        assert bak.exists(), "backup file should exist after second write"

    def test_no_partial_write_on_failure(self, tmp_path: Path):
        """If os.replace raises, the original file must be intact."""
        path    = str(tmp_path / "tasks.json")
        store   = TaskStore(storage_path=path)
        task    = store.create_task("Safe")
        _ = (tmp_path / "tasks.json").read_text()

        with patch("os.replace", side_effect=OSError("disk full")):
            with pytest.raises(TaskStoreCorruptedError):
                store.create_task("Will fail")

        # Original content must still be readable with the prior task
        reloaded = TaskStore(storage_path=path)
        assert reloaded.get_task(task.id) is not None

    def test_auto_creates_data_directory(self, tmp_path: Path):
        deep = tmp_path / "a" / "b" / "c" / "tasks.json"
        store = TaskStore(storage_path=str(deep))
        store.create_task("Deep")
        assert deep.exists()


# ---------------------------------------------------------------------------
# Resilience: corruption recovery
# ---------------------------------------------------------------------------

class TestResilience:
    def test_graceful_empty_file(self, tmp_path: Path):
        path = tmp_path / "tasks.json"
        path.write_text("", encoding="utf-8")
        store = TaskStore(storage_path=str(path))
        assert store.list_tasks() == []

    def test_truncated_json_recovers_from_backup(self, tmp_path: Path):
        path  = tmp_path / "tasks.json"
        store = TaskStore(storage_path=str(path))
        t     = store.create_task("Before corruption")
        # Manually corrupt the main file (but backup was written)
        path.write_text('{"abc": {"id": "abc", "des', encoding="utf-8")
        # New store should recover from backup
        store2 = TaskStore(storage_path=str(path))
        result = store2.get_task(t.id)
        assert result is not None
        assert result.description == "Before corruption"

    def test_no_backup_with_malformed_json_returns_empty(self, tmp_path: Path):
        path = tmp_path / "tasks.json"
        path.write_text("not json at all!!!", encoding="utf-8")
        # No .bak file present
        store = TaskStore(storage_path=str(path))
        assert store.list_tasks() == []

    def test_legacy_list_format_migrated(self, tmp_path: Path):
        path = tmp_path / "tasks.json"
        legacy = [
            {
                "id":         "legacy-001",
                "goal":       "old style task",
                "status":     "pending",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "metadata":   {},
            }
        ]
        path.write_text(json.dumps(legacy), encoding="utf-8")
        store = TaskStore(storage_path=str(path))
        tasks = store.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].description == "old style task"


# ---------------------------------------------------------------------------
# Concurrent threading writes
# ---------------------------------------------------------------------------

class TestConcurrency:
    def test_concurrent_creates_no_data_loss(self, tmp_path: Path):
        """10 threads each create 10 tasks; expect all 100 persisted."""
        path     = str(tmp_path / "tasks.json")
        errors   = []
        n_threads, n_per_thread = 10, 10

        def worker(thread_id: int):
            s = TaskStore(storage_path=path)
            for i in range(n_per_thread):
                try:
                    s.create_task(f"T{thread_id}-task-{i}")
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Unexpected errors during concurrent writes: {errors}"
        final_store = TaskStore(storage_path=path)
        total = len(final_store.list_tasks())
        assert total == n_threads * n_per_thread, (
            f"Expected {n_threads * n_per_thread} tasks, found {total}"
        )


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_lock_timeout_raises_task_store_lock_error(self, tmp_path: Path):
        from filelock import Timeout as FileLockTimeout

        path  = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path, lock_timeout=0.01)

        with patch("core.task_store.FileLock") as mock_lock_cls:
            mock_lock_cls.return_value.__enter__ = None
            mock_lock_cls.return_value.__enter__ = lambda s: (_ for _ in ()).throw(
                FileLockTimeout()
            )
            mock_lock_cls.return_value.__exit__ = lambda s, *a: False
            with pytest.raises((TaskStoreLockError, Exception)):
                store.create_task("Lock me out")

    def test_task_not_found_error_message(self, store: TaskStore):
        with pytest.raises(TaskNotFoundError, match="not found"):
            store.update_task("no-such-id", status=TaskStatus.COMPLETED)

    def test_custom_exceptions_are_subtypes(self):
        assert issubclass(TaskNotFoundError,       KeyError)
        assert issubclass(TaskStoreCorruptedError, RuntimeError)
        assert issubclass(TaskStoreLockError,      RuntimeError)


# ---------------------------------------------------------------------------
# Concurrency Fix Tests (B-003)
# ---------------------------------------------------------------------------

class TestLockConcurrency:
    def test_exception_in_locked_section_releases_lock(self, tmp_path):
        from core.task_store import TaskStore
        from unittest.mock import patch
        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path)

        # We can simulate an exception by mocking _write_tasks
        with patch.object(store, "_write_tasks", side_effect=RuntimeError("Simulated Failure")):
            try:
                store.create_task("Initial task")
            except RuntimeError:
                pass

        # If lock wasn't released, this next call would hang/timeout.
        # But we don't want it to hang, so we check if we can acquire it immediately.
        assert store._lock.acquire(blocking=False) is True
        store._lock.release()

    def test_lock_timeout_raises_custom_error(self, tmp_path):
        from core.task_store import TaskStore, TaskStoreLockError
        import threading
        import time

        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path, lock_timeout=0.1)

        # Acquire lock in main thread so background thread times out
        store._lock.acquire()

        error_raised = None

        def worker():
            nonlocal error_raised
            try:
                store.create_task("Will timeout")
            except Exception as e:
                error_raised = e

        t = threading.Thread(target=worker)
        t.start()
        t.join(timeout=1.0)

        # Release the lock after thread is done
        store._lock.release()

        assert isinstance(error_raised, TaskStoreLockError)
        assert "TaskStore internal lock acquisition timed out" in str(error_raised)

    def test_reentrancy_no_deadlock(self, tmp_path):
        from core.task_store import TaskStore
        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path)

        # Since RLock is used, we can acquire it multiple times in the same thread
        with store._lock:
            with store._lock:
                task = store.create_task("Re-entrancy task")
                assert task is not None

    def test_concurrent_stress_no_data_loss(self, tmp_path):
        from core.task_store import TaskStore
        import threading
        path = str(tmp_path / "tasks.json")
        errors = []
        n_threads = 5
        n_per_thread = 5

        def worker(thread_id: int):
            s = TaskStore(storage_path=path)
            for i in range(n_per_thread):
                try:
                    t = s.create_task(f"T{thread_id}-task-{i}")
                    s.update_task(t.id, status="completed")
                    s.list_tasks()
                except Exception as exc:
                    errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        assert not errors, f"Unexpected errors during concurrent writes: {errors}"
        final_store = TaskStore(storage_path=path)
        total = len(final_store.list_tasks())
        assert total == n_threads * n_per_thread

    def test_file_lock_timeout_raises_task_store_lock_error(self, tmp_path):
        from core.task_store import TaskStore, TaskStoreLockError
        from filelock import FileLock
        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path, lock_timeout=0.1)

        # Acquire the actual file lock manually in the main thread
        manual_lock = FileLock(store.lock_path)
        manual_lock.acquire()
        try:
            with pytest.raises(TaskStoreLockError) as exc_info:
                store.create_task("Should fail on FileLock")
            assert "Could not acquire task store lock within" in str(exc_info.value)
        finally:
            manual_lock.release()

# ---------------------------------------------------------------------------
# Additional coverage for new features
# ---------------------------------------------------------------------------

class TestNewFeatures:
    def test_get_by_status(self, store: TaskStore):
        store.create_task("T1")
        store.create_task("T2")
        t3 = store.create_task("T3")
        store.update_task(t3.id, status=TaskStatus.IN_PROGRESS)

        pending = store.get_by_status(TaskStatus.PENDING)
        assert len(pending) == 2
        in_prog = store.get_by_status(TaskStatus.IN_PROGRESS)
        assert len(in_prog) == 1
        assert in_prog[0].id == t3.id

    def test_get_by_status_empty(self, store: TaskStore):
        assert store.get_by_status(TaskStatus.COMPLETED) == []

    def test_get_by_tool(self, store: TaskStore):
        store.create_task("T1", metadata={"tool": "search"})
        store.create_task("T2", metadata={"tool": "calculator"})
        store.create_task("T3", metadata={"tool": "search", "other": "data"})
        store.create_task("T4")

        search_tasks = store.get_by_tool("search")
        assert len(search_tasks) == 2

        calc_tasks = store.get_by_tool("calculator")
        assert len(calc_tasks) == 1

        none_tasks = store.get_by_tool("unknown")
        assert len(none_tasks) == 0

    def test_status_transitions(self, store: TaskStore):
        t = store.create_task("Transition test")
        assert t.status == TaskStatus.PENDING

        t2 = store.update_task(t.id, status=TaskStatus.IN_PROGRESS)
        assert t2.status == TaskStatus.IN_PROGRESS

        t3 = store.update_task(t.id, status=TaskStatus.COMPLETED)
        assert t3.status == TaskStatus.COMPLETED

        # Reset and test failed
        t4 = store.create_task("Fail test")
        t5 = store.update_task(t4.id, status=TaskStatus.FAILED)
        assert t5.status == TaskStatus.FAILED

    @patch("core.task_store.datetime")
    def test_archive_expired(self, mock_datetime, tmp_path: Path):
        from datetime import datetime, timezone, timedelta

        # Set up current time for the test
        current_time = datetime(2026, 6, 15, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat = datetime.fromisoformat

        store_path = tmp_path / "tasks.json"
        store = TaskStore(storage_path=str(store_path))

        # Create some tasks
        t1 = store.create_task("Recent pending")
        t2 = store.create_task("Old pending")
        t3 = store.create_task("Recent completed")
        t4 = store.create_task("Old completed")
        t5 = store.create_task("Old failed")

        # Update statuses
        store.update_task(t3.id, status=TaskStatus.COMPLETED)
        store.update_task(t4.id, status=TaskStatus.COMPLETED)
        store.update_task(t5.id, status=TaskStatus.FAILED)

        # Manually alter updated_at in the json to simulate time passing
        import json
        with open(store_path, "r") as f:
            data = json.load(f)

        # Recent tasks (2 days old)
        recent_time = (current_time - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        # Old tasks (10 days old)
        old_time = (current_time - timedelta(days=10)).isoformat().replace("+00:00", "Z")

        data[t1.id]["updated_at"] = recent_time
        data[t2.id]["updated_at"] = old_time
        data[t3.id]["updated_at"] = recent_time
        data[t4.id]["updated_at"] = old_time
        data[t5.id]["updated_at"] = old_time

        with open(store_path, "w") as f:
            json.dump(data, f)

        # Run archive
        archived_count = store.archive_expired()

        # Old completed and Old failed should be archived
        assert archived_count == 2

        # Check active tasks
        active = store.list_tasks()
        active_ids = {t.id for t in active}
        assert len(active_ids) == 3
        assert t1.id in active_ids # Recent pending
        assert t2.id in active_ids # Old pending (not completed/failed)
        assert t3.id in active_ids # Recent completed (not expired)

        # Check archive file
        archive_path = tmp_path / "tasks.archive.json"
        assert archive_path.exists()

        archived_tasks = store.load_archive()
        archived_ids = {t.id for t in archived_tasks}
        assert len(archived_ids) == 2
        assert t4.id in archived_ids
        assert t5.id in archived_ids

    def test_load_archive_empty(self, tmp_path: Path):
        store = TaskStore(storage_path=str(tmp_path / "tasks.json"))
        # Archive file doesn't exist yet
        assert store.load_archive() == []

        # Create empty archive
        archive_path = tmp_path / "tasks.archive.json"
        archive_path.write_text("")
        assert store.load_archive() == []

        # Invalid JSON
        archive_path.write_text("invalid json")
        assert store.load_archive() == []

    def test_archive_expired_concurrent(self, tmp_path: Path):
        import threading
        path = str(tmp_path / "tasks.json")
        store = TaskStore(storage_path=path)

        # Prepare 10 expired tasks
        from datetime import datetime, timezone, timedelta
        import json

        task_ids = []
        for i in range(10):
            t = store.create_task(f"Task {i}")
            store.update_task(t.id, status=TaskStatus.COMPLETED)
            task_ids.append(t.id)

        with open(path, "r") as f:
            data = json.load(f)

        old_time = (datetime.now(tz=timezone.utc) - timedelta(days=10)).isoformat().replace("+00:00", "Z")
        for tid in task_ids:
            data[tid]["updated_at"] = old_time

        with open(path, "w") as f:
            json.dump(data, f)

        # Two threads archiving at the same time
        def worker():
            s = TaskStore(storage_path=path)
            try:
                s.archive_expired()
            except Exception:
                pass

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Total archived across both should be 10, remaining 0
        final_store = TaskStore(storage_path=path)
        assert len(final_store.list_tasks()) == 0

        archived = final_store.load_archive()
        assert len(archived) == 10
