"""
NINA Swarm Engine — asyncio parallel worker pool.
Executes TaskNode DAGs produced by TaskPlanner.
Intelligently routes each node to the optimal NinaGate provider.
Part of NINA Swarm v1.
"""
from __future__ import annotations
import asyncio
import json
import os
import time
from typing import Any, Callable, Dict, List, Optional

from .logger import get_logger
from .task_planner import (
    FeedbackGate, MissionMemory, OODAPhase,
    TaskNode, TaskStatus, TaskType
)

logger = get_logger("nina.swarm")



# ── Provider Map ──────────────────────────────────────────────────────────────
#
# Maps TaskType → (provider_name, model_id, context_window)
# These mirror the NinaGate providers.json config exactly.
#
PROVIDER_MAP: Dict[TaskType, tuple] = {
    TaskType.REASONING:  ("GEMINI",      "gemini-2.5-pro",           1_048_576),
    TaskType.FAST_CODE:  ("GROQ",         "llama-3.3-70b-versatile",  8_192),
    TaskType.LONG_CTX:   ("GEMINI",       "gemini-2.5-flash",         1_048_576),
    TaskType.MICRO:      ("CEREBRAS",      "llama-3.3-70b",            8_192), # Changed from OLLAMA
    TaskType.RESEARCH:   ("PERPLEXITY",   "sonar-pro",                32_768),
    TaskType.CREATIVE:   ("DEEPSEEK",     "deepseek-chat",            65_536),
    TaskType.SYNTHESIS:  ("GEMINI",       "gemini-2.5-pro",           1_048_576),
    TaskType.DIAGNOSTIC: ("GROQ", "llama-3.3-70b-versatile", 8_192),
}

# Fallback chain when primary provider is exhausted / unhealthy
FALLBACK_CHAIN: Dict[str, List[str]] = {
    "GEMINI":      ["OPENROUTER", "MISTRAL", "OLLAMA"],
    "GROQ":        ["CEREBRAS", "FIREWORKS", "OLLAMA"],
    "CEREBRAS":    ["OLLAMA"], # Added fallback for CEREBRAS
    "PERPLEXITY":  ["OPENROUTER", "GEMINI", "OLLAMA"],
    "DEEPSEEK":    ["OPENROUTER", "NOVITA", "OLLAMA"],
    "OLLAMA":      [],  # local — never falls back
}


# ── Telemetry helper ──────────────────────────────────────────────────────────

_TELEM_PATH = os.path.join(os.path.dirname(__file__), "..", "telemetry.jsonl")


def _emit(event: str, data: Dict[str, Any]):
    entry = {"event": event, "ts": time.time(), **data}
    try:
        with open(_TELEM_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ── SwarmEngine ────────────────────────────────────────────────────────────────

class SwarmEngine:
    """
    Executes a list of TaskNodes with maximum parallelism.
    Respects dependency ordering (DAG topology).
    Routes each task to the best NinaGate provider.
    Applies FeedbackGate after every result.
    Emits live telemetry to telemetry.jsonl for the TUI daemon.
    """

    def __init__(
        self,
        call_provider: Callable[[str, str, str], tuple[str, int]],
        max_parallel: int = 8,
    ):
        """
        Args:
            call_provider: async fn(provider_name, model_id, prompt)
                           → (response_text, tokens_used)
                           Implemented externally — wraps the NinaGate HTTP client.
            max_parallel:  max concurrent LLM calls (default 8).
        """
        self._call = call_provider
        self._sem = asyncio.Semaphore(max_parallel)
        self._gate = FeedbackGate()
        self._completed: set = set()
        self._results: Dict[str, str] = {}

    # ── Public entry point ───────────────────────────────────────────────────────

    async def execute(
        self,
        nodes: List[TaskNode],
        mission: MissionMemory,
        on_progress: Optional[Callable[[TaskNode], None]] = None,
    ) -> Dict[str, str]:
        """
        Execute all TaskNodes.
        Returns dict of {task_id: result_text}.
        """
        self._completed = set()
        self._results = {}

        _emit("swarm_start", {
            "node_count": len(nodes),
            "root_goal": mission.root_goal[:80],
        })

        # Keep looping until all nodes are terminal
        remaining = list(nodes)
        while remaining:
            # Find all nodes ready to run in this wave
            ready = [
                n for n in remaining
                if n.status == TaskStatus.PENDING and n.is_ready(self._completed)
            ]

            if not ready:
                # No progress possible — check for stuck nodes
                stuck = [n for n in remaining if n.status not in
                         (TaskStatus.DONE, TaskStatus.FAILED)]
                if stuck:
                    for n in stuck:
                        n.mark_failed("dependency deadlock")
                        _emit("node_deadlock", n.to_telemetry())
                break

            # Fire all ready nodes in parallel
            await asyncio.gather(
                *[self._run_node(n, on_progress) for n in ready]
            )

            # Move completed/failed nodes out of remaining
            remaining = [
                n for n in remaining
                if n.status not in (TaskStatus.DONE, TaskStatus.FAILED)
            ]

        # Contradiction check across all parallel results
        done_nodes = [n for n in nodes if n.status == TaskStatus.DONE]
        contradictions = FeedbackGate.detect_contradictions(done_nodes)
        if contradictions:
            _emit("contradictions_detected", {"pairs": contradictions})

        _emit("swarm_done", {
            "done": len([n for n in nodes if n.status == TaskStatus.DONE]),
            "failed": len([n for n in nodes if n.status == TaskStatus.FAILED]),
            "total_tokens": sum(n.tokens_used for n in nodes),
        })

        return self._results

    # ── Node execution ───────────────────────────────────────────────────────────

    async def _run_node(self, node: TaskNode,
                        on_progress: Optional[Callable] = None):
        async with self._sem:
            node.status = TaskStatus.ACTIVE
            node.ooda_phase = OODAPhase.ACT
            _emit("node_start", node.to_telemetry())

            provider, model, ctx_window = PROVIDER_MAP.get(
                node.task_type, ("GEMINI", "gemini-2.5-flash", 1_048_576)
            )

            # Truncate prompt to fit context window (rough 4-char/token estimate)
            max_chars = ctx_window * 3
            prompt = node.prompt[:max_chars]

            # Attempt with fallbacks
            for attempt_provider, attempt_model in self._provider_chain(provider, model):
                try:
                    sla_timeout = getattr(node, "sla_seconds", 60.0)
                    try:
                        result, tokens = await asyncio.wait_for(
                            self._call(attempt_provider, attempt_model, prompt),
                            timeout=sla_timeout
                        )
                    except asyncio.TimeoutError:
                        node.mark_failed(f"Subtask SLA Exceeded ({sla_timeout}s timeout)")
                        logger.warning(f"[SLA] Node {getattr(node, 'id', '?')} timed out after {sla_timeout}s")
                        return
                    node.mark_done(result, attempt_provider, tokens)

                    # FeedbackGate validation
                    if not self._gate.validate(node):
                        if node.retry_count < node.max_retries:
                            node.retry_count += 1
                            node.result = None
                            node.status = TaskStatus.ACTIVE
                            _emit("node_rejected", {**node.to_telemetry(), "score": node.feedback_score})
                            # Try next provider in chain immediately — do not re-queue
                            continue
                        else:
                            node.mark_failed("FeedbackGate: max retries exceeded")
                    break

                except (asyncio.TimeoutError, Exception) as exc:
                    error_msg = f"Timeout ({attempt_provider}) " if isinstance(exc, asyncio.TimeoutError) else str(exc)
                    _emit("node_error", {"id": node.id, "error": error_msg,
                                         "provider": attempt_provider})
                    continue
            else:
                _emit("node_exhausted", {**node.to_telemetry(), "retries": node.retry_count})
                node.mark_failed("all providers exhausted")

            # Register result
            if node.status == TaskStatus.DONE and node.result:
                self._results[node.id] = node.result
                self._completed.add(node.id)
                # Update mission memory with summary
                if node.mission_memory:
                    summary = node.result[:120].replace("\n", " ")
                    node.mission_memory.completed_summaries.append(
                        f"{node.label}: {summary}"
                    )

            _emit("node_done", node.to_telemetry())
            if on_progress:
                on_progress(node)

    # ── Provider fallback chain ──────────────────────────────────────────────────────

    def _provider_chain(self, primary: str, primary_model: str):
        """Yield (provider, model) tuples: primary first, then fallbacks."""
        yield primary, primary_model
        for fallback_name in FALLBACK_CHAIN.get(primary, []):
            # Use default model for fallback provider
            fb_model = self._default_model(fallback_name)
            yield fallback_name, fb_model

    @staticmethod
    def _default_model(provider: str) -> str:
        defaults = {
            "OPENROUTER":  "auto",
            "MISTRAL":     "mistral-large-latest",
            "CEREBRAS":    "llama-3.3-70b",
            "FIREWORKS":   "llama-v3p1-405b",
            "NOVITA":      "llama-3.1-70b",
            "OLLAMA":      "qwen2.5:7b",
        }
        return defaults.get(provider, "auto")


# ── Synthesis helper ──────────────────────────────────────────────────────────────

def build_synthesis_prompt(nodes: List[TaskNode], mission: MissionMemory) -> str:
    """
    Merges all completed sub-task results into a single synthesis prompt.
    Flags contradictions in the prompt so the synthesis model can resolve them.
    """
    contradictions = FeedbackGate.detect_contradictions(
        [n for n in nodes if n.status == TaskStatus.DONE]
    )

    parts = [f"[SYNTHESIS REQUEST]\nRoot goal: {mission.root_goal}\n"]
    parts.append("\n[SUB-TASK RESULTS]")
    for n in nodes:
        if n.status == TaskStatus.DONE and n.result:
            parts.append(f"\n## {n.label} (via {n.provider_used})")
            parts.append(n.result[:1500])

    if contradictions:
        parts.append("\n[CONTRADICTIONS DETECTED — RESOLVE EXPLICITLY]")
        for id_a, id_b, snippet in contradictions:
            parts.append(f"- Conflict between task {id_a} and {id_b}: '{snippet}'")

    parts.append("\n[INSTRUCTION] Synthesise all results into a coherent final answer. "
                 "Resolve contradictions explicitly. Do NOT average — reason through them.")
    return "\n".join(parts)
