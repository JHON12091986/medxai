"""Task DAG — decomposes multi-step user requests into a directed acyclic graph of atomic subtasks. Each node is a TaskNode; edges represent dependency (must_complete_before). Persists to state/active_task.json."""

import dataclasses
import enum
import json
import logging
import os
import time
import uuid
import pathlib
import typing

_ = typing


ACTIVE_TASK_PATH = pathlib.Path(os.path.dirname(__file__)).parent.parent / 'state' / 'active_task.json'

class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskExecutor(enum.Enum):
    AGY = "AGY"
    JULES = "JULES"
    LOCAL_MODEL = "LOCAL_MODEL"
    NINAFLASH = "NINAFLASH"
    PERPLEXITY = "PERPLEXITY"

@dataclasses.dataclass
class TaskNode:
    description: str
    executor: TaskExecutor
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4())[:8])
    depends_on: list[str] = dataclasses.field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str = ''
    created_at: float = dataclasses.field(default_factory=time.time)
    completed_at: float = 0.0

    def is_ready(self, completed_ids: set[str]) -> bool:
        """True if all dependencies are in completed_ids."""
        return all(dep in completed_ids for dep in self.depends_on)

@dataclasses.dataclass
class TaskDAG:
    goal: str
    dag_id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4())[:8])
    nodes: list[TaskNode] = dataclasses.field(default_factory=list)
    created_at: float = dataclasses.field(default_factory=time.time)

    def add_node(self, node: TaskNode) -> None:
        """Add a TaskNode to the DAG. Raises ValueError if a node with the same id already exists."""
        if any(n.id == node.id for n in self.nodes):
            raise ValueError(f"Node with id {node.id} already exists in DAG.")
        self.nodes.append(node)

    def get_ready_nodes(self) -> list[TaskNode]:
        """Return all PENDING nodes whose dependencies are all DONE."""
        completed = {n.id for n in self.nodes if n.status == TaskStatus.DONE}
        return [n for n in self.nodes if n.status == TaskStatus.PENDING and n.is_ready(completed)]

    def is_complete(self) -> bool:
        """True if all nodes are DONE or FAILED."""
        return all(n.status in (TaskStatus.DONE, TaskStatus.FAILED) for n in self.nodes)

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict."""
        nodes_dicts = []
        for node in self.nodes:
            n_dict = dataclasses.asdict(node)
            n_dict['status'] = node.status.value
            n_dict['executor'] = node.executor.value
            nodes_dicts.append(n_dict)
        return {
            "dag_id": self.dag_id,
            "goal": self.goal,
            "created_at": self.created_at,
            "nodes": nodes_dicts
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'TaskDAG':
        """Reconstruct from dict, converting status and executor strings back to enums."""
        nodes = []
        for n_dict in d.get('nodes', []):
            node = TaskNode(
                id=n_dict['id'],
                description=n_dict['description'],
                executor=TaskExecutor(n_dict['executor']),
                depends_on=n_dict.get('depends_on', []),
                status=TaskStatus(n_dict['status']),
                result=n_dict.get('result', ''),
                created_at=n_dict.get('created_at', time.time()),
                completed_at=n_dict.get('completed_at', 0.0)
            )
            nodes.append(node)
        return cls(
            dag_id=d['dag_id'],
            goal=d['goal'],
            nodes=nodes,
            created_at=d.get('created_at', time.time())
        )

def save_active_dag(dag: TaskDAG) -> None:
    """Persist DAG to state/active_task.json. Creates state/ dir if missing."""
    ACTIVE_TASK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVE_TASK_PATH, 'w', encoding='utf-8') as f:
        json.dump(dag.to_dict(), f, indent=2)

def load_active_dag() -> TaskDAG | None:
    """Load active DAG from state/active_task.json. Returns None if file missing or corrupt."""
    if not ACTIVE_TASK_PATH.exists():
        return None
    try:
        with open(ACTIVE_TASK_PATH, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return TaskDAG.from_dict(d)
    except Exception as e:
        logging.warning(f"Failed to load active DAG: {e}")
        return None

def clear_active_dag() -> None:
    """Delete state/active_task.json."""
    if ACTIVE_TASK_PATH.exists():
        ACTIVE_TASK_PATH.unlink()
