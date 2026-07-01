"""NINA HyperDrive — Goals Engine (Phase 2, expanded by ARCHITECT-OVERWATCH 2026-06-22).

Full persistent goal store with:
  - 6 goal states: active | paused | blocked | completed | failed | pending
  - Per-goal: id, title, description, state, priority, created_at, updated_at, tags, dependencies
  - Step-level checkpoints (list of {id, description, status, updated_at})
  - TaskQueue: ordered FIFO per goal_id with add_task / pop_next / is_empty
  - Cross-session: load on init, save on every mutation
  - serialize_state_capsule: context injection string for agent.py
"""
from __future__ import annotations
import json
import logging
import os
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nina.hyperdrive.goals")

GOALS_FILE = "data/goals.json"

VALID_STATES = {"pending", "active", "paused", "blocked", "completed", "failed"}


class TaskQueue:
    """Simple per-goal ordered FIFO task queue (in-memory, backed by goal record)."""

    def __init__(self) -> None:
        self._queues: Dict[str, deque] = {}

    def add_task(self, goal_id: str, task_str: str) -> None:
        if goal_id not in self._queues:
            self._queues[goal_id] = deque()
        self._queues[goal_id].append({"task": task_str, "added_at": time.time()})

    def pop_next(self, goal_id: str) -> Optional[Dict[str, Any]]:
        q = self._queues.get(goal_id)
        if q:
            return q.popleft()
        return None

    def is_empty(self, goal_id: str) -> bool:
        q = self._queues.get(goal_id)
        return not q

    def peek(self, goal_id: str) -> Optional[Dict[str, Any]]:
        q = self._queues.get(goal_id)
        if q:
            return q[0]
        return None

    def list_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        return list(self._queues.get(goal_id, []))


class HyperDriveGoalsManager:
    """Manages long-term active missions, sub-steps, dependencies, and state checkpoints."""

    def __init__(self, path: str = GOALS_FILE) -> None:
        self.path = Path(path)
        self.goals: Dict[str, Any] = {}
        self.task_queue = TaskQueue()
        self.load()

    # ------------------------------------------------------------------ #
    #  Core CRUD                                                           #
    # ------------------------------------------------------------------ #

    def add_goal(
        self,
        title: str,
        description: str = "",
        priority: int = 5,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        goal_id: Optional[str] = None,
    ) -> str:
        """Create a new goal. Returns the goal_id."""
        gid = goal_id or str(uuid.uuid4())[:8]
        now = time.time()
        self.goals[gid] = {
            "title": title,
            "description": description,
            "state": "pending",
            "priority": priority,
            "tags": tags or [],
            "dependencies": dependencies or [],
            "steps": [],
            "created_at": now,
            "updated_at": now,
        }
        self.save()
        logger.info(f"goal_added id={gid} title={title!r}")
        return gid

    def update_state(self, goal_id: str, state: str) -> bool:
        """Transition goal to a new state. Returns True on success."""
        if state not in VALID_STATES:
            logger.warning(f"update_state: invalid state={state!r}")
            return False
        if goal_id not in self.goals:
            logger.warning(f"update_state: unknown goal_id={goal_id!r}")
            return False
        self.goals[goal_id]["state"] = state
        self.goals[goal_id]["updated_at"] = time.time()
        self.save()
        return True

    def get_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        g = self.goals.get(goal_id)
        if g:
            return {"id": goal_id, **g}
        return None

    def get_active(self) -> List[Dict[str, Any]]:
        """Return all goals in 'active' state, sorted by priority desc."""
        result = [
            {"id": k, **v}
            for k, v in self.goals.items()
            if v.get("state") == "active"
        ]
        result.sort(key=lambda x: x.get("priority", 5), reverse=True)
        return result

    def list_all(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self.goals.items()]

    # ------------------------------------------------------------------ #
    #  Dependency resolution                                               #
    # ------------------------------------------------------------------ #

    def resolve_dependencies(self, goal_id: str) -> Dict[str, Any]:
        """Check if all dependencies of goal_id are completed.

        Returns:
            {"ready": bool, "blocking": List[str]}  — blocking is the list
            of dependency goal_ids that are not yet completed.
        """
        g = self.goals.get(goal_id)
        if not g:
            return {"ready": False, "blocking": [f"unknown_goal:{goal_id}"]}
        blocking = []
        for dep_id in g.get("dependencies", []):
            dep = self.goals.get(dep_id)
            if dep is None:
                blocking.append(f"missing:{dep_id}")
            elif dep.get("state") not in ("completed",):
                blocking.append(dep_id)
        return {"ready": len(blocking) == 0, "blocking": blocking}

    # ------------------------------------------------------------------ #
    #  Step-level checkpoints                                              #
    # ------------------------------------------------------------------ #

    def add_step(self, goal_id: str, step_description: str) -> Optional[str]:
        """Append a step to the goal. Returns step_id."""
        g = self.goals.get(goal_id)
        if not g:
            return None
        step_id = str(uuid.uuid4())[:6]
        g["steps"].append({
            "id": step_id,
            "description": step_description,
            "status": "pending",
            "updated_at": time.time(),
        })
        g["updated_at"] = time.time()
        self.save()
        return step_id

    def update_step(self, goal_id: str, step_id: str, status: str) -> bool:
        g = self.goals.get(goal_id)
        if not g:
            return False
        for step in g.get("steps", []):
            if step["id"] == step_id:
                step["status"] = status
                step["updated_at"] = time.time()
                g["updated_at"] = time.time()
                self.save()
                return True
        return False

    # ------------------------------------------------------------------ #
    #  Legacy compat (upsert_goal / get_goal / list_active_goals)          #
    # ------------------------------------------------------------------ #

    def upsert_goal(
        self,
        goal_id: str,
        title: str,
        description: str,
        steps: List[Dict[str, Any]],
        status: str = "PENDING",
    ) -> None:
        """Backward-compatible upsert (used by old callers)."""
        state = status.lower() if status.lower() in VALID_STATES else "pending"
        if goal_id in self.goals:
            self.goals[goal_id]["title"] = title
            self.goals[goal_id]["description"] = description
            self.goals[goal_id]["steps"] = steps
            self.goals[goal_id]["state"] = state
            self.goals[goal_id]["updated_at"] = time.time()
        else:
            now = time.time()
            self.goals[goal_id] = {
                "title": title,
                "description": description,
                "state": state,
                "priority": 5,
                "tags": [],
                "dependencies": [],
                "steps": steps,
                "created_at": now,
                "updated_at": now,
            }
        self.save()

    def get_goal(self, goal_id: str) -> Optional[Dict[str, Any]]:
        return self.goals.get(goal_id)

    def list_active_goals(self) -> List[Dict[str, Any]]:
        """Returns all goals not in a terminal state (backward compat)."""
        return [
            {"id": k, **v}
            for k, v in self.goals.items()
            if v.get("state", "") not in ("completed", "failed")
        ]

    # ------------------------------------------------------------------ #
    #  Context injection                                                   #
    # ------------------------------------------------------------------ #

    def serialize_state_capsule(self, session_id: str = "") -> str:
        """Compact context string for injection into agent system frame."""
        active = self.get_active()
        if not active:
            return ""
        lines = ["[NINA HyperDrive Active Goals]"]
        for g in active[:5]:  # cap at 5 to avoid bloating context
            completed = sum(1 for s in g.get("steps", []) if s.get("status") == "completed")
            total = len(g.get("steps", []))
            dep_info = ""
            if g.get("dependencies"):
                dep_res = self.resolve_dependencies(g["id"])
                if not dep_res["ready"]:
                    dep_info = f" [BLOCKED by {dep_res['blocking']}]"
            lines.append(
                f"  [{g['priority']}] {g['title']} ({g['state']}, {completed}/{total} steps){dep_info}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Persistence                                                         #
    # ------------------------------------------------------------------ #

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.goals, f, indent=2)
        except Exception as e:
            logger.warning(f"hyperdrive: goals_save_failed: {e}")

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Migrate old records that used 'status' key instead of 'state'
            for gid, g in raw.items():
                if "status" in g and "state" not in g:
                    s = g.pop("status").lower()
                    g["state"] = s if s in VALID_STATES else "pending"
                if "priority" not in g:
                    g["priority"] = 5
                if "tags" not in g:
                    g["tags"] = []
                if "dependencies" not in g:
                    g["dependencies"] = []
                if "created_at" not in g:
                    g["created_at"] = g.get("updated_at", time.time())
            self.goals = raw
        except Exception as e:
            logger.warning(f"hyperdrive: goals_load_failed: {e}")


# Global singleton
goals_manager = HyperDriveGoalsManager()
