import sys
import re

with open("tests/test_task_store.py", "r", encoding="utf-8") as f:
    content = f.read()

# Patch test_get_task_not_found_returns_none
orig_test_not_found = """    def test_get_task_not_found_returns_none(self, store: TaskStore):
        assert store.get_task("nonexistent-id-000") is None"""

new_test_not_found = """    def test_get_task_not_found_raises_keyerror(self, store: TaskStore):
        with pytest.raises(TaskNotFoundError):
            store.get_task("nonexistent-id-000")"""

content = content.replace(orig_test_not_found, new_test_not_found)

# Write test implementations
new_tests = """
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
"""

content += new_tests

with open("tests/test_task_store.py", "w", encoding="utf-8") as f:
    f.write(content)
