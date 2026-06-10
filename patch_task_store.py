import sys
import re

with open("core/task_store.py", "r", encoding="utf-8") as f:
    content = f.read()

# Patch get_task
get_task_orig = """    def get_task(self, task_id: str) -> Optional[Task]:
        \"\"\"Retrieve a task by its UUID.

        Args:
            task_id: UUID string of the task.

        Returns:
            The matching :class:`Task`, or *None* if not found.
        \"\"\"
        with self._lock:
            return self._read_tasks().get(task_id)"""

get_task_new = """    def get_task(self, task_id: str) -> Optional[Task]:
        \"\"\"Retrieve a task by its UUID.

        Args:
            task_id: UUID string of the task.

        Returns:
            The matching :class:`Task`, or *None* if not found.

        Raises:
            TaskNotFoundError: If *task_id* does not exist.
        \"\"\"
        with self._lock:
            tasks = self._read_tasks()
            if task_id not in tasks:
                raise TaskNotFoundError(f"Task '{task_id}' not found")
            return tasks[task_id]"""

content = content.replace(get_task_orig, get_task_new)

# Append new methods
new_methods = """
    def get_by_status(self, status: TaskStatus) -> List[Task]:
        \"\"\"Return all tasks with the given status.\"\"\"
        return self.list_tasks(status=status)

    def get_by_tool(self, tool_name: str) -> List[Task]:
        \"\"\"Return all tasks that use the given tool (via metadata).\"\"\"
        with self._lock:
            return [
                t for t in self._read_tasks().values()
                if t.metadata.get("tool") == tool_name
            ]

    def archive_expired(self) -> int:
        \"\"\"Move expired (done/failed/cancelled + past TTL) tasks to the archive.

        Returns:
            The number of tasks archived.
        \"\"\"
        if not self._lock.acquire(timeout=self.lock_timeout):
            raise TaskStoreLockError("TaskStore internal lock acquisition timed out")
        try:
            tasks = self._read_tasks()
            now = datetime.now(tz=timezone.utc)

            to_archive = {}
            active = {}
            for tid, t in tasks.items():
                if t.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
                    # check if expired (e.g. updated_at is more than 7 days ago, or we'll just archive all completed for this step if TTL isn't strictly defined, but requirement says "expired" - let's check updated_at)
                    try:
                        updated = datetime.fromisoformat(t.updated_at.replace("Z", "+00:00"))
                        if (now - updated).days > 7:
                            to_archive[tid] = t
                        else:
                            active[tid] = t
                    except ValueError:
                        to_archive[tid] = t # if invalid date, archive it
                else:
                    active[tid] = t

            if not to_archive:
                return 0

            # Write to archive
            archive_path = self.storage_path.with_name(self.storage_path.stem + ".archive.json")
            archived_tasks = {}
            if archive_path.exists():
                try:
                    raw = archive_path.read_text(encoding="utf-8").strip()
                    if raw:
                        payload = json.loads(raw)
                        for tid, record in payload.items():
                            archived_tasks[tid] = Task.from_dict(record)
                except Exception as exc:
                    logger.warning("Failed to read archive, overwriting: %s", exc)

            archived_tasks.update(to_archive)

            # Atomic write to archive
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=archive_path.parent,
                prefix=".archive_tmp_",
                suffix=".json",
            )
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as fh:
                    json.dump(
                        {tid: t.to_dict() for tid, t in archived_tasks.items()},
                        fh,
                        indent=2,
                        ensure_ascii=False,
                    )
                os.replace(tmp_path, archive_path)
            except Exception as exc:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise TaskStoreCorruptedError(f"Failed to write archive: {exc}") from exc

            # Update main store
            self._write_tasks(active)
            return len(to_archive)

        finally:
            self._lock.release()

    def load_archive(self) -> List[Task]:
        \"\"\"Read and return tasks from the archive file.\"\"\"
        with self._lock:
            archive_path = self.storage_path.with_name(self.storage_path.stem + ".archive.json")
            if not archive_path.exists():
                return []
            try:
                raw = archive_path.read_text(encoding="utf-8").strip()
                if not raw:
                    return []
                payload = json.loads(raw)
                tasks = []
                for tid, record in payload.items():
                    if isinstance(record, dict):
                        tasks.append(Task.from_dict(record))
                return sorted(tasks, key=lambda t: t.created_at)
            except Exception as exc:
                logger.error("Failed to load archive: %s", exc)
                return []
"""

content += new_methods

with open("core/task_store.py", "w", encoding="utf-8") as f:
    f.write(content)
