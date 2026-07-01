"""core/coordinator_agent.py — Specialist subagent mesh + task dispatcher.

The Coordinator is NINA's internal multi-agent orchestrator:
  - Maintains a registry of specialist agents (Research, Coding,
    Memory, Guard, Execution, General)
  - Receives a decomposed task plan from ReActEngine and dispatches
    subtasks to the best-fit agent
  - Supports sequential, parallel fan-out, and conditional routing
  - Synthesises results from multiple agents into a unified response
  - Tracks per-agent health (success rate, latency, last error)

Design rules:
  - Agents are async callables: async def run(task, context) -> AgentResult
  - Coordinator never blocks: all dispatch is async with timeouts
  - Failures are isolated: one agent error does not abort others
  - Health registry drives routing preference (not just capability)
  - All dispatch is logged with OTel-compatible span metadata

Usage:
    from core.coordinator_agent import CoordinatorAgent, AgentRole
    coord = CoordinatorAgent(router=router, tools=tools, memory=memory)
    coord.auto_register()
    result = await coord.dispatch("Research the MCP protocol spec",
                                  role=AgentRole.RESEARCH)
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable

log = logging.getLogger("nina.coordinator")

DEFAULT_TIMEOUT = int(60)
MAX_PARALLEL    = int(6)


class AgentRole(str, Enum):
    RESEARCH   = "research"
    CODING     = "coding"
    MEMORY     = "memory"
    GUARD      = "guard"
    EXECUTION  = "execution"
    GENERAL    = "general"
    PLANNER    = "planner"


@dataclass
class AgentResult:
    role:      AgentRole
    success:   bool
    output:    str        = ""
    error:     str        = ""
    latency_ms: float     = 0.0
    metadata:  dict       = field(default_factory=dict)

    def to_context_block(self) -> str:
        if not self.success:
            return f"[{self.role.value.upper()} ERROR] {self.error}"
        return f"[{self.role.value.upper()}]\n{self.output}"


@dataclass
class AgentHealth:
    role:        AgentRole
    total:       int   = 0
    successes:   int   = 0
    avg_latency: float = 0.0
    last_error:  str   = ""
    available:   bool  = True

    @property
    def success_rate(self) -> float:
        return self.successes / self.total if self.total else 1.0

    def record(self, result: AgentResult) -> None:
        self.total += 1
        if result.success:
            self.successes += 1
        else:
            self.last_error = result.error
        # Exponential moving average
        alpha = 0.2
        self.avg_latency = (alpha * result.latency_ms
                            + (1 - alpha) * self.avg_latency)


AgentCallable = Callable[[str, dict], Awaitable[AgentResult]]


class CoordinatorAgent:
    """Routes tasks to specialist subagents and synthesises results."""

    def __init__(
        self,
        router: Any     = None,
        tools: Any      = None,
        memory: Any     = None,
        react_engine: Any = None,
    ):
        self._router = router
        self._tools  = tools
        self._memory = memory
        self._react  = react_engine
        self._agents:  dict[AgentRole, AgentCallable] = {}
        self._health:  dict[AgentRole, AgentHealth]   = {}

    # ── registration ───────────────────────────────────────────────────

    def register(
        self,
        role: AgentRole,
        fn: AgentCallable,
    ) -> None:
        """Register a specialist agent callable."""
        self._agents[role] = fn
        self._health[role] = AgentHealth(role=role)
        log.debug("coordinator: registered agent '%s'", role.value)

    def auto_register(self) -> int:
        """Register all built-in specialist agents.

        Returns number of agents registered.
        """
        builtins: list[tuple[AgentRole, AgentCallable]] = [
            (AgentRole.RESEARCH,  self._research_agent),
            (AgentRole.CODING,    self._coding_agent),
            (AgentRole.MEMORY,    self._memory_agent),
            (AgentRole.GUARD,     self._guard_agent),
            (AgentRole.EXECUTION, self._execution_agent),
            (AgentRole.GENERAL,   self._general_agent),
        ]
        for role, fn in builtins:
            self.register(role, fn)
        log.info("coordinator: auto-registered %d agents", len(builtins))
        return len(builtins)

    # ── dispatch ────────────────────────────────────────────────────────

    async def dispatch(
        self,
        task: str,
        role: AgentRole = AgentRole.GENERAL,
        context: dict | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> AgentResult:
        """Dispatch a single task to the best available agent for the role."""
        ctx = context or {}
        agent = self._agents.get(role) or self._agents.get(AgentRole.GENERAL)
        if not agent:
            return AgentResult(
                role=role, success=False,
                error="No agent registered for role and no GENERAL fallback",
            )
        return await self._run_agent(role, agent, task, ctx, timeout)

    async def dispatch_parallel(
        self,
        subtasks: list[tuple[str, AgentRole]],
        context: dict | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> list[AgentResult]:
        """Dispatch multiple subtasks in parallel, respecting MAX_PARALLEL.

        Args:
            subtasks: List of (task_text, role) pairs.
            context:  Shared context dict passed to all agents.
            timeout:  Per-subtask timeout in seconds.

        Returns:
            List of AgentResult in the same order as subtasks.
        """
        ctx  = context or {}
        sem  = asyncio.Semaphore(MAX_PARALLEL)
        results: list[AgentResult | None] = [None] * len(subtasks)

        async def run_one(idx: int, task: str, role: AgentRole) -> None:
            async with sem:
                results[idx] = await self.dispatch(task, role, ctx, timeout)

        await asyncio.gather(
            *[run_one(i, t, r) for i, (t, r) in enumerate(subtasks)],
            return_exceptions=True,
        )
        return [
            r if r is not None else AgentResult(
                role=AgentRole.GENERAL, success=False,
                error="dispatch_parallel: slot never filled"
            )
            for r in results
        ]

    async def synthesise(
        self,
        original_task: str,
        results: list[AgentResult],
    ) -> str:
        """Merge outputs from multiple agents into a unified response."""
        if not results:
            return ""
        successful = [r for r in results if r.success]
        if not successful:
            errors = "; ".join(r.error for r in results)
            return f"All agents failed: {errors}"
        if len(successful) == 1:
            return successful[0].output

        # Multi-result synthesis via LLM
        blocks = "\n\n".join(r.to_context_block() for r in successful)
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are NINA's synthesis engine. "
                    "Merge the following specialist agent outputs into a single "
                    "coherent response that best answers the original task. "
                    "Preserve important details; remove redundancy."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"ORIGINAL TASK:\n{original_task}\n\n"
                    f"AGENT OUTPUTS:\n{blocks}"
                ),
            },
        ]
        if self._router:
            try:
                if hasattr(self._router, "chat"):
                    return await self._router.chat(prompt_messages)
                prompt = "\n".join(
                    f"{m['role'].upper()}: {m['content']}" for m in prompt_messages
                )
                return await self._router.complete(prompt)
            except Exception as exc:
                log.warning("coordinator: synthesis LLM failed: %s", exc)
        return "\n\n".join(r.output for r in successful)

    def health_report(self) -> dict:
        """Return health stats for all registered agents."""
        return {
            role.value: {
                "success_rate": round(h.success_rate, 3),
                "avg_latency_ms": round(h.avg_latency, 1),
                "total_calls": h.total,
                "available": h.available,
                "last_error": h.last_error[-100:] if h.last_error else "",
            }
            for role, h in self._health.items()
        }

    # ── internal runner ─────────────────────────────────────────────────

    async def _run_agent(
        self,
        role: AgentRole,
        fn: AgentCallable,
        task: str,
        context: dict,
        timeout: int,
    ) -> AgentResult:
        t0 = time.time()
        try:
            result = await asyncio.wait_for(fn(task, context), timeout=timeout)
            result.latency_ms = (time.time() - t0) * 1000
        except asyncio.TimeoutError:
            result = AgentResult(
                role=role, success=False,
                error=f"Timeout after {timeout}s",
                latency_ms=(time.time() - t0) * 1000,
            )
        except Exception as exc:
            result = AgentResult(
                role=role, success=False,
                error=str(exc),
                latency_ms=(time.time() - t0) * 1000,
            )
        if role in self._health:
            self._health[role].record(result)
        log.debug(
            "coordinator: agent=%s success=%s latency=%.0fms",
            role.value, result.success, result.latency_ms,
        )
        return result

    # ── built-in specialist agents ──────────────────────────────────────

    async def _research_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """Research agent: web search + memory retrieval."""
        output_parts: list[str] = []

        # Memory retrieval
        if self._memory:
            try:
                from core.layered_memory import MemoryLayer
                hits = await self._memory.search(
                    task, layer=MemoryLayer.SEMANTIC, top_k=5
                )
                if hits:
                    texts = [h.get("text") or h.get("document", "") for h in hits]
                    output_parts.append(
                        "Memory:\n" + "\n".join(f"- {t[:200]}" for t in texts if t)
                    )
            except Exception as exc:
                log.debug("research_agent: memory failed: %s", exc)

        # Tool: web_search
        if self._tools and hasattr(self._tools, "web_search"):
            try:
                result = await self._tools.web_search(task)
                output_parts.append(f"Web:\n{str(result)[:800]}")
            except Exception as exc:
                log.debug("research_agent: web_search failed: %s", exc)

        # LLM synthesis
        if self._router and output_parts:
            context_text = "\n\n".join(output_parts)
            messages = [
                {"role": "system", "content": "You are NINA's research specialist. Synthesise the context to answer the task concisely."},
                {"role": "user",   "content": f"TASK: {task}\n\nCONTEXT:\n{context_text}"},
            ]
            try:
                output = await self._router.chat(messages) if hasattr(self._router, "chat") \
                    else await self._router.complete(f"TASK: {task}\n\n{context_text}")
                return AgentResult(role=AgentRole.RESEARCH, success=True, output=output)
            except Exception as exc:
                return AgentResult(role=AgentRole.RESEARCH, success=False, error=str(exc))

        output = "\n\n".join(output_parts) or f"No research results for: {task}"
        return AgentResult(role=AgentRole.RESEARCH, success=bool(output_parts), output=output)

    async def _coding_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """Coding agent: delegates to ReActEngine or Jules pipeline."""
        if self._react:
            try:
                result = await self._react.run(task=task, context=str(context))
                return AgentResult(
                    role=AgentRole.CODING,
                    success=result.success,
                    output=result.response,
                    error=result.error if not result.success else "",
                )
            except Exception as exc:
                return AgentResult(role=AgentRole.CODING, success=False, error=str(exc))
        if self._router:
            try:
                prompt = f"You are a coding specialist. Complete this task:\n{task}"
                messages = [{"role": "user", "content": prompt}]
                output = await self._router.chat(messages) if hasattr(self._router, "chat") \
                    else await self._router.complete(prompt)
                return AgentResult(role=AgentRole.CODING, success=True, output=output)
            except Exception as exc:
                return AgentResult(role=AgentRole.CODING, success=False, error=str(exc))
        return AgentResult(role=AgentRole.CODING, success=False,
                           error="No router or react_engine available")

    async def _memory_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """Memory agent: search and summarise across all memory layers."""
        if not self._memory:
            return AgentResult(role=AgentRole.MEMORY, success=False,
                               error="No memory instance")
        try:
            from core.layered_memory import MemoryLayer
            all_hits: list[str] = []
            for layer in (MemoryLayer.WORKING, MemoryLayer.EPISODIC,
                          MemoryLayer.SEMANTIC, MemoryLayer.PROCEDURAL):
                hits = await self._memory.search(task, layer=layer, top_k=3)
                for h in hits:
                    t = h.get("text") or h.get("document", "")
                    if t:
                        all_hits.append(f"[{layer.value}] {t[:300]}")
            if not all_hits:
                return AgentResult(role=AgentRole.MEMORY, success=True,
                                   output="No relevant memory found.")
            return AgentResult(
                role=AgentRole.MEMORY, success=True,
                output="\n".join(all_hits[:12]),
            )
        except Exception as exc:
            return AgentResult(role=AgentRole.MEMORY, success=False, error=str(exc))

    async def _guard_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """Guard agent: safety and policy check."""
        violations: list[str] = []
        t = task.lower()
        blocked = ["rm -rf", "drop table", "delete from", "format c:",
                   "sudo rm", "os.system", "__import__"]
        for b in blocked:
            if b in t:
                violations.append(f"Blocked pattern: '{b}'")
        if violations:
            return AgentResult(
                role=AgentRole.GUARD, success=False,
                error="Safety violation: " + "; ".join(violations),
                metadata={"blocked": True},
            )
        return AgentResult(
            role=AgentRole.GUARD, success=True,
            output="Safety check passed.",
            metadata={"blocked": False},
        )

    async def _execution_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """Execution agent: runs tool calls from context."""
        if self._tools:
            try:
                if hasattr(self._tools, "execute"):
                    result = await self._tools.execute(task)
                    return AgentResult(role=AgentRole.EXECUTION, success=True,
                                       output=str(result)[:1000])
            except Exception as exc:
                return AgentResult(role=AgentRole.EXECUTION, success=False,
                                   error=str(exc))
        return AgentResult(role=AgentRole.EXECUTION, success=False,
                           error="No tool executor available")

    async def _general_agent(
        self, task: str, context: dict
    ) -> AgentResult:
        """General-purpose agent: direct LLM call."""
        if not self._router:
            return AgentResult(role=AgentRole.GENERAL, success=False,
                               error="No router available")
        try:
            ctx_str = str(context)[:400] if context else ""
            messages = [
                {"role": "system", "content": "You are NINA, a helpful AI assistant."},
                {"role": "user",   "content": f"{task}\n\n{ctx_str}".strip()},
            ]
            output = await self._router.chat(messages) if hasattr(self._router, "chat") \
                else await self._router.complete(task)
            return AgentResult(role=AgentRole.GENERAL, success=True, output=output)
        except Exception as exc:
            return AgentResult(role=AgentRole.GENERAL, success=False, error=str(exc))
