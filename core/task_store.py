import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from filelock import FileLock

logger = logging.getLogger("nina.task_store")

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

@dataclass
class Task:
    goal: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plan_steps: list = field(default_factory=list)
    status: str = "pending"
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    retries: int = 0
    result: Optional[str] = None
    tool_used: Optional[str] = None
    priority: str = "normal"
    tags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

class TaskStore:
    def __init__(self, path: str = 'data/tasks.json'):
        self.path = Path(path)
        self.lock_path = str(self.path) + ".lock"
        self._ensure_file()

    def _ensure_file(self):
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(self.lock_path):
            if not self.path.exists():
                self.path.write_text(json.dumps([]))

    def _read_tasks(self) -> List[Task]:
        with FileLock(self.lock_path):
            try:
                data = json.loads(self.path.read_text())
                return [Task(**t) for t in data]
            except Exception as e:
                logger.error(f"Failed to read tasks: {e}")
                return []

    def _write_tasks(self, tasks: List[Task]):
        with FileLock(self.lock_path):
            data = [asdict(t) for t in tasks]
            self.path.write_text(json.dumps(data, indent=2))

    def create_task(self, goal: str, plan_steps: list = None, priority: str = 'normal') -> Task:
        tasks = self._read_tasks()
        task = Task(goal=goal, plan_steps=plan_steps or [], priority=priority)
        tasks.append(task)
        self._write_tasks(tasks)
        logger.info(json.dumps({"event": "task_created", "task_id": task.id, "status": task.status}))
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        tasks = self._read_tasks()
        for t in tasks:
            if t.id == task_id:
                return t
        return None

    def update_task(self, task_id: str, **fields) -> Task:
        tasks = self._read_tasks()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                for k, v in fields.items():
                    if hasattr(t, k):
                        setattr(t, k, v)
                t.updated_at = _now_iso()
                tasks[i] = t
                self._write_tasks(tasks)
                logger.info(json.dumps({"event": "task_updated", "task_id": t.id, "status": t.status}))
                return t
        raise ValueError(f"Task with id {task_id} not found")

    def delete_task(self, task_id: str) -> bool:
        tasks = self._read_tasks()
        initial_len = len(tasks)
        tasks = [t for t in tasks if t.id != task_id]
        if len(tasks) < initial_len:
            self._write_tasks(tasks)
            logger.info(json.dumps({"event": "task_deleted", "task_id": task_id, "status": "deleted"}))
            return True
        return False

    def list_tasks(self, status: str = None) -> List[Task]:
        tasks = self._read_tasks()
        if status:
            return [t for t in tasks if t.status == status]
        return tasks

    def get_task_metrics(self) -> Dict:
        tasks = self._read_tasks()
        metrics = {
            "total": len(tasks),
            "by_status": {},
            "by_priority": {}
        }
        for t in tasks:
            metrics["by_status"][t.status] = metrics["by_status"].get(t.status, 0) + 1
            metrics["by_priority"][t.priority] = metrics["by_priority"].get(t.priority, 0) + 1
        return metrics
