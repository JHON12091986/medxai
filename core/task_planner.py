"""
NINA Task Planner — OODA recursive task decomposition engine.
Implements: TaskNode DAG, parallel branch detection, FeedbackGate validation.
Part of NINA Swarm v1.
"""
from __future__ import annotations
import os
import re
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ── Enums ────────────────────────────────────────────────────────────────────

class TaskStatus(Enum):
    PENDING   = "pending"
    ACTIVE    = "active"
    DONE      = "done"
    FAILED    = "failed"
    REJECTED  = "rejected"   # FeedbackGate rejection


class TaskType(Enum):
    """Maps to provider selection in SwarmEngine."""
    REASONING   = "reasoning"    # → Gemini 2.5 Pro
    FAST_CODE   = "fast_code"    # → Groq llama-3.3-70b
    LONG_CTX    = "long_ctx"     # → Gemini 2.5 Flash (1M window)
    MICRO       = "micro"        # → Ollama qwen2.5:1.5b (zero cost)
    RESEARCH    = "research"     # → Perplexity sonar-pro
    CREATIVE    = "creative"     # → DeepSeek-chat
    SYNTHESIS   = "synthesis"    # → Gemini 2.5 Pro (merge + contradiction check)
    DIAGNOSTIC  = "diagnostic"   # → shell + file reads, fast provider


# ── OODA Phase Labels ─────────────────────────────────────────────────────────

class OODAPhase(Enum):
    OBSERVE  = "observe"
    ORIENT   = "orient"
    DECIDE   = "decide"
    ACT      = "act"


# ── Core Data Structures ──────────────────────────────────────────────────────

@dataclass
class MissionMemory:
    """
    Compressed context carrier (≤500 tokens).
    Injected into every sub-task so sub-agents never lose the root objective.
    """
    root_goal: str
    key_constraints: List[str] = field(default_factory=list)
    completed_summaries: List[str] = field(default_factory=list)
    token_budget_remaining: int = 40_000

    def compress(self) -> str:
        summaries = " | ".join(self.completed_summaries[-5:])  # last 5 only
        constraints = "; ".join(self.key_constraints)
        return (
            f"ROOT_GOAL: {self.root_goal[:200]}\n"
            f"CONSTRAINTS: {constraints[:150]}\n"
            f"COMPLETED: {summaries[:200]}\n"
            f"TOKEN_BUDGET: {self.token_budget_remaining}"
        )


@dataclass
class TaskNode:
    """
    A single node in the OODA task DAG.
    Each node is itself an OODA loop — observe→orient→decide→act.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    label: str = ""
    prompt: str = ""
    task_type: TaskType = TaskType.REASONING
    status: TaskStatus = TaskStatus.PENDING
    ooda_phase: OODAPhase = OODAPhase.OBSERVE
    depth: int = 0                        # 0 = root, 1 = sub-task, 2 = micro-task
    dependencies: List[str] = field(default_factory=list)   # task IDs that must complete first
    children: List["TaskNode"] = field(default_factory=list)
    result: Optional[str] = None
    feedback_score: float = 1.0           # 0.0–1.0; below threshold triggers re-dispatch
    mission_memory: Optional[MissionMemory] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    provider_used: Optional[str] = None
    tokens_used: int = 0
    retry_count: int = 0
    max_retries: int = 2
    sla_seconds: float = 60.0

    def is_ready(self, completed_ids: set) -> bool:
        """True if all dependencies are resolved."""
        return all(dep in completed_ids for dep in self.dependencies)

    def mark_done(self, result: str, provider: str, tokens: int):
        self.result = result
        self.status = TaskStatus.DONE
        self.completed_at = time.time()
        self.provider_used = provider
        self.tokens_used = tokens
        self.ooda_phase = OODAPhase.ACT

    def mark_failed(self, reason: str):
        self.status = TaskStatus.FAILED
        self.result = f"[FAILED] {reason}"
        self.completed_at = time.time()

    def to_telemetry(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "status": self.status.value,
            "phase": self.ooda_phase.value,
            "depth": self.depth,
            "provider": self.provider_used,
            "tokens": self.tokens_used,
            "score": self.feedback_score,
            "elapsed": round(time.time() - self.created_at, 1) if self.completed_at is None
                       else round(self.completed_at - self.created_at, 1),
        }


# ── FeedbackGate ──────────────────────────────────────────────────────────────

class FeedbackGate:
    """
    Validates sub-task results before they are merged into the parent.
    Applies Constitutional checks, sycophancy detection, contradiction flagging.
    Does NOT blindly accept outputs — re-dispatches if quality is below threshold.
    """

    SYCOPHANCY_PHRASES = [
        "great idea", "absolutely", "certainly", "of course", "you're right",
        "as you suggested", "as you mentioned", "i agree completely",
        "that's a great point", "excellent question",
    ]

    THRESHOLD = 0.65  # feedback_score below this → reject + re-queue

    @staticmethod
    def score(node: TaskNode, result: str) -> float:
        score = 1.0

        # Penalise empty or trivially short results
        if len(result.strip()) < 50:
            score -= 0.4

        # Penalise obvious sycophancy
        lower = result.lower()
        sycophancy_hits = sum(1 for p in FeedbackGate.SYCOPHANCY_PHRASES if p in lower)
        score -= min(sycophancy_hits * 0.1, 0.3)

        # Penalise if root goal keyword not mentioned at all
        if node.mission_memory:
            root_keywords = node.mission_memory.root_goal.lower().split()[:5]
            hits = sum(1 for kw in root_keywords if kw in lower)
            if hits == 0:
                score -= 0.2

        return max(0.0, min(1.0, score))

    @classmethod
    def validate(cls, node: TaskNode) -> bool:
        """
        Returns True if result passes, False if it should be re-dispatched.
        Updates node.feedback_score in place.
        """
        if node.result is None:
            node.feedback_score = 0.0
            return False

        node.feedback_score = cls.score(node, node.result)
        if node.feedback_score < cls.THRESHOLD:
            node.status = TaskStatus.REJECTED
            return False
        return True

    @staticmethod
    def detect_contradictions(nodes: List[TaskNode]) -> List[tuple]:
        """
        Lightweight contradiction detection between parallel results.
        Returns list of (node_id_a, node_id_b, snippet) pairs that conflict.
        """
        contradictions = []
        results = [(n.id, n.result or "") for n in nodes if n.result]

        negation_pairs = [("will", "will not"), ("is", "is not"), ("can", "cannot"),
                          ("should", "should not"), ("true", "false")]
        for i, (id_a, res_a) in enumerate(results):
            for id_b, res_b in results[i+1:]:
                for pos, neg in negation_pairs:
                    if pos in res_a.lower() and neg in res_b.lower():
                        contradictions.append((id_a, id_b, f"{pos} vs {neg}"))
        return contradictions


# ── Task Planner (OODA Orchestrator) ─────────────────────────────────────────

class TaskPlanner:
    """
    Master OODA orchestrator.
    Given a root goal, decomposes it into a TaskNode DAG.
    Identifies parallelisable branches vs. sequential dependencies.
    Returns the DAG ready for SwarmEngine execution.
    """

    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.gate = FeedbackGate()

    # ── OBSERVE phase ──────────────────────────────────────────────────────────

    def observe(self, goal: str, context: str = "") -> MissionMemory:
        """Parse the goal and build MissionMemory."""
        constraints = []
        if "never" in goal.lower():
            constraints.append("hard exclusion present — check for 'never' clauses")
        if "deadline" in goal.lower() or "urgent" in goal.lower():
            constraints.append("time-sensitive task — prefer fast providers")
        if len(goal) > 500:
            constraints.append("complex goal — may need depth>1 decomposition")

        return MissionMemory(
            root_goal=goal[:300],
            key_constraints=constraints,
        )

    # ── ORIENT phase ──────────────────────────────────────────────────────────

    def orient(self, goal: str, mission: MissionMemory) -> TaskType:
        """Classify the root task type for provider selection."""
        g = goal.lower()
        if any(k in g for k in ["research", "search", "find", "look up", "web"]):
            return TaskType.RESEARCH
        if any(k in g for k in ["write", "story", "poem", "creative", "design"]):
            return TaskType.CREATIVE
        if any(k in g for k in ["format", "lint", "docstring", "rename", "comment"]):
            return TaskType.MICRO
        if any(k in g for k in ["refactor", "implement", "build", "create", "code", "fix"]):
            return TaskType.FAST_CODE
        if any(k in g for k in ["why", "why is", "why does", "why did", "deleted", "missing", "broken", "not working", "failed", "error"]):
            return TaskType.DIAGNOSTIC
        if any(k in g for k in ["analyse", "analyze", "reason", "explain", "how"]):
            return TaskType.REASONING
        if len(goal) > 800 or "entire" in g or "all" in g:
            return TaskType.LONG_CTX
        return TaskType.REASONING

    # ── DECIDE phase ──────────────────────────────────────────────────────────

    def decide(self, goal: str, mission: MissionMemory,
               root_type: TaskType, depth: int = 0) -> List[TaskNode]:
        """
        Decompose goal into parallel + sequential sub-tasks.
        Returns a flat list of TaskNodes with dependency wiring.
        Sub-tasks at depth>0 inherit MissionMemory.
        """
        if depth >= self.max_depth:
            # Leaf node — execute directly
            return [TaskNode(
                label=f"leaf:{goal[:40]}",
                prompt=goal,
                task_type=root_type,
                depth=depth,
                mission_memory=mission,
            )]

        # Heuristic decomposition — in production this can itself be an LLM call
        nodes = []
        segments = self._split_goal(goal)
        prev_id = None

        for i, seg in enumerate(segments):
            t = TaskNode(
                label=f"sub-{i}:{seg[:40]}",
                prompt=self._build_prompt(seg, mission),
                task_type=self.orient(seg, mission),
                depth=depth + 1,
                mission_memory=mission,
                dependencies=[prev_id] if (prev_id and self._is_sequential(seg)) else [],
            )
            # Recurse for complex segments
            if len(seg) > 200 and depth < self.max_depth - 1:
                t.children = self.decide(seg, mission, t.task_type, depth + 1)
            nodes.append(t)
            if self._is_sequential(seg):
                prev_id = t.id

        return nodes

    # ── ACT phase (entry point) ────────────────────────────────────────────────

    def plan(self, goal: str, context: str = "") -> tuple[MissionMemory, List[TaskNode]]:
        """
        Full OODA cycle. Returns (MissionMemory, [TaskNode list]).
        Pass the list to SwarmEngine.execute().
        """
        mission = self.observe(goal, context)
        root_type = self.orient(goal, mission)
        nodes = self.decide(goal, mission, root_type, depth=0)

        # Emit telemetry event
        self._emit_telemetry("plan_ready", {
            "root_goal": mission.root_goal[:80],
            "task_count": len(nodes),
            "root_type": root_type.value,
        })
        return mission, nodes

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _split_goal(self, goal: str) -> List[str]:
        """Split goal on numbered steps, bullets, semicolons, or natural breaks."""
        import re
        # Try numbered list first
        parts = re.split(r'\n\s*\d+[\.\)]\s+', goal)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
        # Try bullet points
        parts = re.split(r'\n\s*[-*•]\s+', goal)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]
        # Try semicolons
        if ';' in goal:
            return [p.strip() for p in goal.split(';') if p.strip()]
        # Prose diagnostic: inject evidence-gathering prefix tasks
        lower = goal.lower()
        if any(k in lower for k in ["why", "deleted", "missing", "broken", "not working", "failed", "error"]):
            return [
                "Run: git log --all --full-history --oneline -- . | head -30",
                "Run: grep -r 'nexus_discoveries\\|SPACE_FILES\\|rm\\|delete' nina_sync.sh docs/ --include='*.sh' --include='*.md' -l 2>/dev/null | head -20",
                f"Read docs/space/nina_error_register.md and find any OPEN rows related to: {goal[:100]}",
                f"Based on all evidence gathered above, answer: {goal}",
            ]
        # Default: single task
        return [goal]

    _SEQ_RE = re.compile(r"then|after|finally|next|once|when done|following|subsequently|last", re.IGNORECASE)

    def _is_sequential(self, segment: str) -> bool:
        """Detect if segment implies ordering (then, after, finally, etc.)."""
        # [Performance] Pre-compiled regex search avoids string allocation (.lower()) and python-level generator iteration in hot loop
        return bool(self._SEQ_RE.search(segment))

    def _build_prompt(self, segment: str, mission: MissionMemory) -> str:
        return f"[MISSION CONTEXT]\n{mission.compress()}\n\n[TASK]\n{segment}"

    # Helper to write telemetry in a non-blocking way
    def _write_telemetry_entry(self, entry_str: str, path: str):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a") as f:
                f.write(entry_str + "\n")
        except Exception:
            pass

    def _emit_telemetry(self, event: str, data: Dict[str, Any]):
        import json
        import os
        import threading # Import threading
        entry = {"event": event, "ts": time.time(), **data}
        entry_str = json.dumps(entry)
        path = os.path.join(os.path.dirname(__file__), "..", "telemetry.jsonl")
        
        # Offload to a thread to prevent blocking the main thread
        threading.Thread(target=self._write_telemetry_entry, args=(entry_str, path)).start()
