"""core/goal_manager.py — Persistent cross-session goal manager for NINA vNext.

Maintains a durable goal store with states:
  ACTIVE    — currently being worked on
  PAUSED    — waiting for external input or lower-priority
  BLOCKED   — dependency not yet met
  COMPLETED — successfully finished
  FAILED    — abandoned after max retries

Features:
  - JSON persistence (survives restarts)
  - Priority queue (higher priority goals execute first)
  - Dependency edges (goal B blocked until goal A completes)
  - Retry tracking with configurable max_retries
  - Session resumption (loads incomplete goals on startup)

Used by:
  core/autonomy_ratchet  — picks next executable goal
  core/react_engine      — reports goal completion/failure
  idleloop.py            — background goal processing
  Telegram interface     — user goal commands (!goal, !status)

Usage:
    from core.goal_manager import GoalManager, GoalState
    gm = GoalManager()
    gid = await gm.add("Research NINA vNext memory patterns", priority=8)
    await gm.complete(gid, outcome="Found 3 relevant papers")
    goals = await gm.get_active()
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.goal_manager")

GOALS_JSON   = Path(os.getenv("NINA_GOALS_JSON", "./data/goals.json"))
DEFAULT_MAX_RETRIES = 3


class GoalState(str, Enum):
    ACTIVE    = "active"
    PAUSED    = "paused"
    BLOCKED   = "blocked"
    COMPLETED = "completed"
    FAILED    = "failed"


@dataclass
class Goal:
    id:           str
    title:        str
    description:  str          = ""
    state:        GoalState    = GoalState.ACTIVE
    priority:     int          = 5            # 1 (low) – 10 (critical)
    created_at:   str          = field(default_factory=lambda: _now_iso())
    updated_at:   str          = field(default_factory=lambda: _now_iso())
    deadline:     str          = ""           # ISO datetime or empty
    depends_on:   list[str]    = field(default_factory=list)  # goal IDs
    tags:         list[str]    = field(default_factory=list)
    outcome:      str          = ""           # set on completion
    retry_count:  int          = 0
    max_retries:  int          = DEFAULT_MAX_RETRIES
    session_id:   str          = ""           # last worked session
    meta:         dict         = field(default_factory=dict)

    def is_ready(self, completed_ids: set[str]) -> bool:
        """Return True if all dependencies are met."""
        return all(dep in completed_ids for dep in self.depends_on)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Goal":
        d = dict(d)
        d["state"] = GoalState(d.get("state", "active"))
        return cls(**d)

    def summary(self) -> str:
        return (
            f"[{self.id[:8]}] ({self.state.value}) P{self.priority} "
            f"\u2018{self.title[:60]}\u2019"
            + (f" → depends_on={self.depends_on}" if self.depends_on else "")
        )


class GoalManager:
    """Persistent cross-session goal store."""

    def __init__(self, goals_path: Path = GOALS_JSON):
        self._path   = goals_path
        self._goals: dict[str, Goal] = {}
        self._load()

    # ─ CRUD ──────────────────────────────────────────────────────────────────

    async def add(
        self,
        title: str,
        description: str = "",
        priority: int = 5,
        depends_on: list[str] | None = None,
        tags: list[str] | None = None,
        deadline: str = "",
        max_retries: int = DEFAULT_MAX_RETRIES,
        meta: dict | None = None,
    ) -> str:
        """Create a new goal. Returns goal ID."""
        gid  = uuid.uuid4().hex[:16]
        deps = depends_on or []
        state = GoalState.BLOCKED if deps else GoalState.ACTIVE
        goal = Goal(
            id=gid,
            title=title,
            description=description,
            state=state,
            priority=max(1, min(10, priority)),
            depends_on=deps,
            tags=tags or [],
            deadline=deadline,
            max_retries=max_retries,
            meta=meta or {},
        )
        self._goals[gid] = goal
        self._save()
        log.info("goal_manager: ADD %s", goal.summary())
        return gid

    async def complete(
        self, goal_id: str, outcome: str = ""
    ) -> bool:
        """Mark a goal as completed. Unblocks dependents."""
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        goal.state      = GoalState.COMPLETED
        goal.outcome    = outcome
        goal.updated_at = _now_iso()
        self._unblock_dependents(goal_id)
        self._save()
        log.info("goal_manager: COMPLETE %s outcome=%s", goal.summary(), outcome[:80])
        return True

    async def fail(
        self, goal_id: str, reason: str = ""
    ) -> bool:
        """Mark a goal as failed (or schedule retry)."""
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        goal.retry_count += 1
        if goal.retry_count < goal.max_retries:
            goal.state = GoalState.PAUSED
            log.info(
                "goal_manager: RETRY %s count=%d/%d",
                goal.summary(), goal.retry_count, goal.max_retries
            )
        else:
            goal.state = GoalState.FAILED
            goal.outcome = reason
            log.warning("goal_manager: FAILED %s reason=%s", goal.summary(), reason[:80])
        goal.updated_at = _now_iso()
        self._save()
        return True

    async def pause(self, goal_id: str) -> bool:
        return self._set_state(goal_id, GoalState.PAUSED)

    async def resume(self, goal_id: str) -> bool:
        return self._set_state(goal_id, GoalState.ACTIVE)

    async def update_meta(self, goal_id: str, meta: dict) -> bool:
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        goal.meta.update(meta)
        goal.updated_at = _now_iso()
        self._save()
        return True

    async def delete(self, goal_id: str) -> bool:
        if goal_id not in self._goals:
            return False
        del self._goals[goal_id]
        self._save()
        return True

    # ─ query ─────────────────────────────────────────────────────────────────

    async def get_active(
        self, limit: int = 10
    ) -> list[Goal]:
        """Return active goals sorted by priority desc."""
        completed_ids = self._completed_ids()
        active = [
            g for g in self._goals.values()
            if g.state == GoalState.ACTIVE and g.is_ready(completed_ids)
        ]
        active.sort(key=lambda g: g.priority, reverse=True)
        return active[:limit]

    async def get_next(
        self
    ) -> Goal | None:
        """Return the single highest-priority executable goal."""
        active = await self.get_active(limit=1)
        return active[0] if active else None

    async def get_all(
        self, state: GoalState | None = None
    ) -> list[Goal]:
        goals = list(self._goals.values())
        if state:
            goals = [g for g in goals if g.state == state]
        return sorted(goals, key=lambda g: (-g.priority, g.created_at))

    async def status_report(self) -> str:
        """Return a human-readable status summary."""
        all_goals = list(self._goals.values())
        by_state: dict[str, list[str]] = {
            s.value: [] for s in GoalState
        }
        for g in all_goals:
            by_state[g.state.value].append(g.summary())

        lines = ["=== NINA Goal Status ==="]
        for state_val, summaries in by_state.items():
            if summaries:
                lines.append(f"\n{state_val.upper()} ({len(summaries)}):")
                for s in summaries[:5]:
                    lines.append(f"  {s}")
        return "\n".join(lines)

    # ─ internal ──────────────────────────────────────────────────────────────

    def _set_state(self, goal_id: str, state: GoalState) -> bool:
        goal = self._goals.get(goal_id)
        if not goal:
            return False
        goal.state      = state
        goal.updated_at = _now_iso()
        self._save()
        return True

    def _unblock_dependents(self, completed_id: str) -> None:
        completed = self._completed_ids()
        for g in self._goals.values():
            if g.state == GoalState.BLOCKED and g.is_ready(completed):
                g.state = GoalState.ACTIVE
                g.updated_at = _now_iso()
                log.info("goal_manager: UNBLOCKED %s", g.summary())

    def _completed_ids(self) -> set[str]:
        return {gid for gid, g in self._goals.items() if g.state == GoalState.COMPLETED}

    def _load(self) -> None:
        if not self._path.exists():
            log.debug("goal_manager: no goals file at %s, starting fresh", self._path)
            return
        try:
            raw = json.loads(self._path.read_text())
            for item in raw.get("goals", []):
                g = Goal.from_dict(item)
                self._goals[g.id] = g
            log.info("goal_manager: loaded %d goals", len(self._goals))
        except Exception as exc:
            log.error("goal_manager: load failed: %s", exc)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {"goals": [g.to_dict() for g in self._goals.values()]}
            self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as exc:
            log.error("goal_manager: save failed: %s", exc)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

goal_manager: "GoalManager" = GoalManager()

