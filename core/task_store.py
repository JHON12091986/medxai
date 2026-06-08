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
    RESUMABLE_STATUSES = frozenset(['pending', 'running', 'paused'])

    def __init__(self, path: str = 'data/tasks.json'):
        self.path = Path(path)
        self.lock_path = str(self.path) + ".lock"
        self._ensure_file()
        self.resume_open_tasks()

    def resume_open_tasks(self) -> List[Task]:
        all_tasks = self.list_tasks()
        resumable_tasks = [t for t in all_tasks if t.status in self.RESUMABLE_STATUSES]
        found = len(resumable_tasks)
        reset = 0
        for t in resumable_tasks:
            if t.status == 'running':
                self.update_task(t.id, status='pending')
                t.status = 'pending'
                reset += 1
        logger.info(json.dumps({"event": "task_resume_scan", "found": found, "reset_to_pending": reset}))
        return resumable_tasks

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

    def get_resumable_tasks(self) -> List[Task]:
        pending_tasks = self.list_tasks(status='pending')
        prio_map = {'high': 0, 'normal': 1, 'low': 2}
        return sorted(pending_tasks, key=lambda t: (prio_map.get(t.priority, 1), t.created_at))

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

    def format_tasks_summary(self) -> str:
        tasks = self._read_tasks()
        active = [t for t in tasks if t.status in ["running", "pending", "paused", "failed"]]
        if not active:
            return "✅ No active tasks."

        status_order = {"running": 0, "pending": 1, "paused": 2, "failed": 3}
        active.sort(key=lambda t: status_order.get(t.status, 99))

        lines = [f"📋 NINA Tasks ({len(active)} active)"]

        symbols = {
            "running": "🔴",
            "pending": "🟡",
            "paused": "⚪",
            "failed": "❌"
        }

        for t in active[:10]:
            sym = symbols.get(t.status, "❓")
            short_id = t.id[:8]

            goal = t.goal if len(t.goal) <= 40 else t.goal[:37] + "..."

            if t.status == "failed":
                reason = t.result or "Unknown error"
                reason = reason if len(reason) <= 30 else reason[:27] + "..."
                lines.append(f"{sym} {t.status}: {goal} [id: {short_id}] — {reason}")
            else:
                lines.append(f"{sym} {t.status}: {goal} [id: {short_id}]")

        if len(active) > 10:
            lines.append(f"...and {len(active) - 10} more")

        return "\n".join(lines)

    def format_task_detail(self, task_id: str) -> str:
        t = self.get_task(task_id)
        if not t:
            return "Task not found."

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(t.created_at.replace("Z", "+00:00"))
            created = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            created = t.created_at

        res = t.result or "pending"
        res = res if len(res) <= 100 else res[:97] + "..."

        lines = [
            f"📌 Task {t.id[:8]}",
            f"Goal: {t.goal}",
            f"Status: {t.status}",
            f"Priority: {t.priority}",
            f"Created: {created}",
            f"Retries: {t.retries}",
            f"Steps: {len(t.plan_steps)}",
            f"Result: {res}"
        ]
        return "\n".join(lines)
