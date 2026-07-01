import hashlib
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class TaskSpec:
    task_id: str          # unique, e.g. "VAULT-001" or "IDLE-20260618-1017"
    title: str            # human-readable one-line title
    body: str             # full task body — the prompt Jules will receive
    priority: str         # "P1" | "P2" | "P3"
    tier: str             # "INFRA" | "OMNI" | "PERF" | "OBS" | "GOVERN" | "BACKLOG"
    source: str           # "idleloop" | "ooda" | "manual" | "scheduler"
    status: str           # "PENDING" | "DISPATCHED" | "DONE" | "SKIPPED" | "FAILED"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    dispatched_at: str = ""
    done_at: str = ""
    pr_number: int = 0
    idempotency_key: str = ""
    tags: list[str] = field(default_factory=list)
    target_files: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Compute idempotency_key if not provided
        if not self.idempotency_key:
            self.idempotency_key = hashlib.sha256(f"{self.task_id}:{self.title}".encode()).hexdigest()[:16]
        
        # Validation
        valid_priorities = {"P1", "P2", "P3"}
        if self.priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of {valid_priorities}")
            
        valid_statuses = {"PENDING", "DISPATCHED", "DONE", "SKIPPED", "FAILED"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {valid_statuses}")

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "body": self.body,
            "priority": self.priority,
            "tier": self.tier,
            "source": self.source,
            "status": self.status,
            "created_at": self.created_at,
            "dispatched_at": self.dispatched_at,
            "done_at": self.done_at,
            "pr_number": self.pr_number,
            "idempotency_key": self.idempotency_key,
            "tags": self.tags,
            "target_files": self.target_files,
            "depends_on": self.depends_on
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TaskSpec":
        return cls(
            task_id=d.get("task_id", ""),
            title=d.get("title", ""),
            body=d.get("body", ""),
            priority=d.get("priority", "P3"),
            tier=d.get("tier", "BACKLOG"),
            source=d.get("source", "manual"),
            status=d.get("status", "PENDING"),
            created_at=d.get("created_at", ""),
            dispatched_at=d.get("dispatched_at", ""),
            done_at=d.get("done_at", ""),
            pr_number=d.get("pr_number", 0),
            idempotency_key=d.get("idempotency_key", ""),
            tags=d.get("tags", []),
            target_files=d.get("target_files", []),
            depends_on=d.get("depends_on", [])
        )
