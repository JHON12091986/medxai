"""
core — NINA core pipeline package.

Public surface exported here for convenient imports across the codebase.

Example::

    from core import TaskStore, Task, TaskStatus
"""

from core.task_store import Task, TaskStatus, TaskStore  # noqa: F401
from core.task_store import (
    TaskNotFoundError,
    TaskStoreCorruptedError,
    TaskStoreLockError,
)

__all__ = [
    "Task",
    "TaskStatus",
    "TaskStore",
    "TaskNotFoundError",
    "TaskStoreCorruptedError",
    "TaskStoreLockError",
]
