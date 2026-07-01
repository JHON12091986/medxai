"""core/react_engine.py — ReAct (Reason + Act) reasoning engine for NINA vNext.

Implements a bounded multi-pass Reason→Act→Observe loop:

  Pass 1: THINK   — decompose task, identify subtasks, choose tools
  Pass 2: ACT     — execute tool calls or generate sub-responses
  Pass 3: OBSERVE — collect results, run critic, check confidence
  Pass 4: REFLECT — if revision needed, regenerate with critique context
  Pass 5: FINISH  — assemble final response with reflection storage

Key design decisions:
  - Max loop iterations: MAX_ITERATIONS (default 4) — hard token budget.
  - Critic gates every ACT output before FINISH.
  - Confidence scorer gates final FINISH step.
  - Reflection is stored to layered_memory after every completed task.
  - All steps produce OTel spans when otel_tracer is wired in.
  - Falls back gracefully to single-pass if sub-components are unavailable.

Usage:
    from core.react_engine import ReActEngine
    engine = ReActEngine(router=router, tools=tools, memory=memory)
    result = await engine.run(task="Explain transformer attention")
    print(result.response)
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("nina.react")

MAX_ITERATIONS        = 4
THINK_SYSTEM          = """You are NINA's planner. Given a task, produce a concise execution plan.

Format:
THOUGHT: <reasoning about the task>
PLAN:
- <step 1>
- <step 2>
...
TOOLS_NEEDED: <comma-separated tool names, or NONE>
COMPLEXITY: <low|medium|high>"""

ACT_SYSTEM            = """You are NINA. Execute the following plan step and produce the best possible response.
Be specific, accurate, and complete. If you need information you don't have, say so explicitly."""

REFLECT_SYSTEM        = """You are NINA's reflection module.
Given the task, original response, and critic feedback, produce an improved response.
Address all identified issues. Be direct and complete."""

FINISH_REFLECTION_TPL = """Task: {task}
Outcome: {outcome}
Critic score: {score:.2f}
Issues resolved: {issues}
What worked: {worked}
What to improve: {improve}
"""


@dataclass
class ReActResult:
    response:       str
    task_id:        str
    iterations:     int     = 1
    critic_score:   float   = 0.0
    confidence:     float   = 0.0
    tools_used:     list    = field(default_factory=list)
    reflection_id:  str     = ""
    success:        bool    = True
    error:          str     = ""
    elapsed_ms:     float   = 0.0


class ReActEngine:
    """Bounded ReAct reasoning engine.

    Args:
        router:   NINA router (required — provides LLM access)
        tools:    Optional tool dispatcher (provides tool execution)
        memory:   Optional LayeredMemory instance
        critic:   Optional Critic instance
        scorer:   Optional ConfidenceScorer instance
        tracer:   Optional NinaTracer instance
        max_iter: Override MAX_ITERATIONS
    """

    def __init__(
        self,
        router:   Any,
        tools:    Any  = None,
        memory:   Any  = None,
        critic:   Any  = None,
        scorer:   Any  = None,
        tracer:   Any  = None,
        max_iter: int  = MAX_ITERATIONS,
    ):
        self.router   = router
        self.tools    = tools
        self.memory   = memory
        self.critic   = critic
        self.scorer   = scorer
        self.tracer   = tracer
        self.max_iter = max_iter

    async def run(
        self,
        task: str,
        context: str = "",
        task_id: str | None = None,
        use_tools: bool = True,
    ) -> ReActResult:
        """Run the ReAct loop for a task.

        Args:
            task:      The user task or sub-task string.
            context:   Optional prior context (memory, conversation history).
            task_id:   Stable ID for this task (used for revision tracking).
            use_tools: Whether to allow tool calls in the ACT step.

        Returns:
            ReActResult with final response and metadata.
        """
        task_id   = task_id or uuid.uuid4().hex[:12]
        t_start   = time.time()
        iteration = 0
        response  = ""
        critic_result = None
        tools_used: list[str] = []

        log.info("react: START task_id=%s task=%s...", task_id, task[:80])

        # ── THINK (Pass 1) ────────────────────────────────────────────────────
        plan = await self._think(task, context)
        log.debug("react: THINK plan=%s", plan[:200])

        # ── ACT → OBSERVE → REFLECT loop ─────────────────────────────────────
        while iteration < self.max_iter:
            iteration += 1

            # ACT (Pass 2)
            response, used = await self._act(task, plan, context, response, use_tools)
            tools_used.extend(used)

            # OBSERVE / CRITIQUE (Pass 3)
            if self.critic:
                critic_result = await self.critic.critique(
                    response, task=task, task_id=task_id
                )
                log.debug(
                    "react: OBSERVE iter=%d critic=%s",
                    iteration, critic_result.summary()
                )

                # Accept early if good enough
                if critic_result.accept:
                    log.info("react: ACCEPT iter=%d score=%.2f", iteration, critic_result.overall)
                    break

                # Revise if warranted and under cap
                if self.critic.should_revise(critic_result, task_id):
                    log.info(
                        "react: REVISE iter=%d score=%.2f issues=%s",
                        iteration, critic_result.overall, critic_result.issues
                    )
                    response = await self._reflect(
                        task, response, critic_result.revision_prompt()
                    )
                    continue  # re-critique revised response
                else:
                    break  # revision cap hit or no revision needed
            else:
                break  # no critic, single pass

        # ── CONFIDENCE (Pass 4 gate) ──────────────────────────────────────────
        confidence = 0.70
        if self.scorer:
            score_result = await self.scorer.score(response, task)
            confidence   = score_result.confidence
            if score_result.low:
                response += score_result.disclaimer()

        critic_score = critic_result.overall if critic_result else 0.70

        # ── REFLECT & STORE (Pass 5) ──────────────────────────────────────────
        reflection_id = ""
        if self.memory:
            reflection_id = await self._store_reflection(
                task, response, critic_score, critic_result
            )

        elapsed = (time.time() - t_start) * 1000
        log.info(
            "react: FINISH task_id=%s iter=%d critic=%.2f conf=%.2f elapsed=%.0fms",
            task_id, iteration, critic_score, confidence, elapsed
        )

        return ReActResult(
            response=response,
            task_id=task_id,
            iterations=iteration,
            critic_score=critic_score,
            confidence=confidence,
            tools_used=list(set(tools_used)),
            reflection_id=reflection_id,
            success=True,
            elapsed_ms=elapsed,
        )

    # ── internal steps ────────────────────────────────────────────────────────

    async def _think(self, task: str, context: str) -> str:
        """THINK step: produce a plan for the task."""
        user_content = f"Context:\n{context[:500]}\n\nTask: {task}" if context else f"Task: {task}"
        messages = [
            {"role": "system", "content": THINK_SYSTEM},
            {"role": "user",   "content": user_content},
        ]
        try:
            return await self._llm(messages, model="fast")
        except Exception as exc:
            log.warning("react: THINK failed: %s", exc)
            return f"THOUGHT: Direct response\nPLAN:\n- Answer directly\nTOOLS_NEEDED: NONE\nCOMPLEXITY: low"

    async def _act(
        self,
        task: str,
        plan: str,
        context: str,
        prior_response: str,
        use_tools: bool,
    ) -> tuple[str, list[str]]:
        """ACT step: execute plan and produce a response."""
        tools_used: list[str] = []

        # Tool calls if applicable
        tool_results = ""
        if use_tools and self.tools and "NONE" not in plan.upper().split("TOOLS_NEEDED:")[-1][:50]:
            tool_names = _extract_tool_names(plan)
            for tname in tool_names[:3]:  # cap at 3 tool calls per ACT
                try:
                    result = await self._call_tool(tname, task)
                    tool_results += f"\n[{tname} result]: {str(result)[:400]}"
                    tools_used.append(tname)
                except Exception as exc:
                    tool_results += f"\n[{tname} error]: {exc}"

        revision_note = ""
        if prior_response:
            revision_note = f"\nPrior attempt (improve this):\n{prior_response[:600]}"

        user_content = (
            f"Task: {task}\n"
            f"Plan:\n{plan[:600]}\n"
            f"{f'Context: {context[:300]}' if context else ''}"
            f"{tool_results}"
            f"{revision_note}"
        )
        messages = [
            {"role": "system", "content": ACT_SYSTEM},
            {"role": "user",   "content": user_content},
        ]
        try:
            response = await self._llm(messages, model="default")
            return response, tools_used
        except Exception as exc:
            log.error("react: ACT failed: %s", exc)
            return f"Error generating response: {exc}", tools_used

    async def _reflect(
        self, task: str, response: str, revision_prompt: str
    ) -> str:
        """REFLECT step: revise response based on critic feedback."""
        messages = [
            {"role": "system", "content": REFLECT_SYSTEM},
            {"role": "user",   "content":
                f"Task: {task}\n\n"
                f"Original response:\n{response[:800]}\n\n"
                f"Critic feedback: {revision_prompt}\n\n"
                "Produce an improved response:"},
        ]
        try:
            return await self._llm(messages, model="default")
        except Exception as exc:
            log.warning("react: REFLECT failed: %s", exc)
            return response  # fall back to original

    async def _store_reflection(
        self,
        task: str,
        response: str,
        critic_score: float,
        critic_result: Any,
    ) -> str:
        """Store task reflection to layered memory for future reuse."""
        issues_str   = "; ".join(getattr(critic_result, "issues", [])[:3])
        suggestion   = getattr(critic_result, "suggestion", "")
        worked       = "Response met quality threshold" if critic_score >= ACCEPT_THRESHOLD else "Partial quality"
        improve      = suggestion or "Increase factual grounding"

        reflection_text = FINISH_REFLECTION_TPL.format(
            task=task[:200],
            outcome=response[:200],
            score=critic_score,
            issues=issues_str or "none",
            worked=worked,
            improve=improve,
        )
        try:
            from core.layered_memory import MemoryLayer
            doc_id = await self.memory.write(
                reflection_text,
                layer=MemoryLayer.EPISODIC,
                metadata={"type": "reflection", "critic_score": str(critic_score)},
            )
            log.debug("react: reflection stored id=%s", doc_id)
            return doc_id
        except Exception as exc:
            log.warning("react: reflection storage failed: %s", exc)
            return ""

    async def _llm(
        self, messages: list[dict], model: str = "default"
    ) -> str:
        """Call the router with a message list."""
        if hasattr(self.router, "chat"):
            return await self.router.chat(messages, model=model)
        # Fallback: concatenate messages
        prompt = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )
        return await self.router.complete(prompt, model=model)

    async def _call_tool(self, tool_name: str, task: str) -> Any:
        """Dispatch a tool call via the tools dispatcher."""
        if not self.tools:
            raise RuntimeError("No tools dispatcher available")
        if hasattr(self.tools, "call"):
            return await self.tools.call(tool_name, task=task)
        if hasattr(self.tools, "run"):
            return await self.tools.run(tool_name, task)
        raise RuntimeError(f"Tools dispatcher has no 'call' or 'run' method")


# ── constants ─────────────────────────────────────────────────────────────────
ACCEPT_THRESHOLD = 0.78  # mirror from critic for local use

# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_tool_names(plan: str) -> list[str]:
    """Parse TOOLS_NEEDED line from a THINK plan."""
    for line in plan.splitlines():
        if "TOOLS_NEEDED:" in line.upper():
            raw = line.split(":", 1)[-1].strip()
            if raw.upper() == "NONE" or not raw:
                return []
            return [t.strip().lower() for t in raw.split(",") if t.strip()]
    return []
