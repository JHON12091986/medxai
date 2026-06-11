"""NINA v12 — AgentLoop (Stage 5)
THINK -> PLAN -> ACT -> OBSERVE -> ADAPT. Variable step budget + global timeout + thermal preflight.
"""
import asyncio, logging, re
from core.router import HybridRouter, ClassifiedTask, STEP_BUDGETS, DEFAULT_MAX_STEPS
from tools import system
from core.capabilities import CapabilityRegistry
_registry = CapabilityRegistry()

logger = logging.getLogger("nina.agent")

class AgentLoop:
    def __init__(self, config, router: HybridRouter, memory, tools: dict):
        self.config = config
        self.router = router
        self.memory = memory
        self.tools  = tools

    def _should_self_check(self, task: ClassifiedTask) -> bool:
        return (getattr(task, "task_type", "") or "").lower() in {
            "research", "coding", "document", "sensitive"
        }

    async def _self_check(self, goal: str, draft: str, task: ClassifiedTask, force_local: bool = False) -> str:
        if not draft or not self._should_self_check(task):
            return draft
        review_prompt = (
            "Review this answer for completeness and accuracy relative to the original question. "
            "If it is complete and accurate, return it unchanged. If not, return a corrected version. "
            f"Original question: {goal}\n\nAnswer: {draft}"
        )
        try:
            reviewed = await self.router.route(
                review_prompt,
                [{"role": "user", "content": review_prompt}],
                task,
                force_local=True,
            )
            reviewed = (reviewed or "").strip()
            if reviewed:
                return reviewed
            return draft
        except Exception as e:
            logger.warning(f"selfcheck_failed: {e}", extra={"log": "agent.log"})
            return draft


    async def run(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
        try:
            return await asyncio.wait_for(
                self._inner(goal, task, session_history),
                timeout=self.config.agent_timeout_s)
        except asyncio.TimeoutError:
            logger.warning(f"agent_loop_timeout goal={goal[:80]!r} exceeded={self.config.agent_timeout_s}s",
                           extra={"log":"agent.log"})
            return f"Task timed out after {self.config.agent_timeout_s}s."

    # F-03c: Bangla language override — injected before routing
    _BANGLA_RANGE = range(0x0980, 0x0A00)
    _BANGLA_RE = re.compile(r"[\u0980-\u09FF]")

    @classmethod
    def _is_bangla(cls, text: str) -> bool:
        return bool(cls._BANGLA_RE.search(text))

    _BANGLA_OVERRIDE = (
        "[LANGUAGE OVERRIDE: User wrote in Bangla. "
        "Your ENTIRE response must be in Bangla. "
        "No English except unavoidable technical terms like API, token, git.]\n\n"
    )

    async def _inner(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
        # AG-LOOP: structured phase logging
        from core.agent_loop import AgentLoop as _AL
        import logging as _log
        _log.getLogger("nina.agent").debug(f"agent input received: {goal!r}")
        session_history = list(session_history)

        ram = await system.get_ram_used_gb()
        if ram >= self.config.ram_guard_gb:
            logger.warning(f"agent_loop_skipped ram={ram:.1f}GB guard={self.config.ram_guard_gb}GB")
            return await self.router.single_turn(goal, session_history)

        temps      = await system.get_temps()
        cput       = temps.get("cpu") or 0
        gput       = temps.get("gpu") or 0
        force_local = False

        if cput >= self.config.thermal_critical_cpu or gput >= self.config.thermal_critical_gpu:
            logger.critical(f"agent_loop_aborted_thermal CPU={cput} GPU={gput}", extra={"log":"agent.log"})
            return f"CRITICAL temp CPU={cput}C GPU={gput}C. Agent loop aborted."

        if cput >= self.config.thermal_guard_cpu or gput >= self.config.thermal_guard_gpu:
            logger.warning(f"thermal_guard CPU={cput} GPU={gput} forcing LOCALFAST")
            force_local = True

        if cput >= self.config.thermal_warn_cpu or gput >= self.config.thermal_warn_gpu:
            logger.warning(f"thermal_warn CPU={cput} GPU={gput}", extra={"log":"nina.log"})

        max_steps  = STEP_BUDGETS.get(task.task_type, DEFAULT_MAX_STEPS)
        context    = await self.memory.build_context(goal)
        # System frame injected once — never repeated in step loop
        # F-03x: Strip redundant instructions if routing through NinaGate (AG-M-10)
        from urllib.parse import urlparse
        api_base = getattr(self.config, "onebrain_api_base", "") or ""
        parsed_url = urlparse(api_base)

        if parsed_url.port == 8080 or "8080" in api_base:
            system_frame = f"Goal: {goal}\nMemory: {context}"
        else:
            system_frame = (
                f"Goal: {goal}\n"
                f"Memory: {context}\n"
                "THINK -> PLAN -> ACT each step.\n"
                "TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status\n"
                "FINAL:answer when done.\n"
                "RULE: live data/prices/news — MUST use TOOL:web first."
            )
        # F-03d: inject Bangla override as a system-role message so providers treat it
        # as a system instruction, not user content (fixes F-03c goal-prepend approach)
        bangla_sys = ([{"role": "system", "content": self._BANGLA_OVERRIDE.strip()}]
                      if self._is_bangla(goal) else [])
        msgs = bangla_sys + [{"role": "user", "content": system_frame}] + session_history.copy()
        scratchpad = []

        for step in range(1, max_steps + 1):
            # Append only incremental scratchpad — no repeated context
            step_prompt = f"[Step {step}/{max_steps}] Scratchpad:\n{chr(10).join(scratchpad[-3:])}"
            msgs.append({"role": "user", "content": step_prompt})
            response = await self.router.route(goal, msgs, task, force_local=force_local)
            msgs.append({"role": "assistant", "content": response})
            logger.info(f"agent_step step={step} task={task.task_type} response={response[:80]!r}",
                        extra={"log":"agent.log"})

            if "FINAL:" in response:
                draft = response.split("FINAL:", 1)[1].strip()
                return await self._self_check(goal, draft, task, force_local=force_local)

            if "TOOL:" in response:
                try:
                    import re as _re
                    # Strip markdown bold/italic and [Step N/M] so MISTRAL's **TOOL:web** works
                    clean_resp = _re.sub(r'[*_`]', '', response)
                    clean_resp = _re.sub(r'^\[Step \d+/\d+\]\s*', '', clean_resp, flags=_re.MULTILINE)

                    match = _re.search(r'TOOL:\s*([^\s:]+)(?:\s+INPUT:\s*([^\n]*)|[ \t]+([^\n]*))?', clean_resp)
                    if not match:
                        raise ValueError("Failed to parse TOOL from response")

                    tool_name = match.group(1).strip(":- ").lower()
                    tool_input = (match.group(2) or match.group(3) or '').strip().strip('\'"')
                    tool = self.tools.get(tool_name)
                    if not _registry.is_healthy(tool_name):
                        obs = f"Tool {tool_name} unavailable (unhealthy)."
                        logger.warning(f"agent_skipped_unhealthy tool={tool_name}")
                    elif tool:
                        obs = await tool.run(tool_input)
                    else:
                        obs = f"Unknown tool: {tool_name}"
                    scratchpad.append(f"[{tool_name}] -> {obs[:300]}")
                except Exception as e:
                    scratchpad.append(f"[tool_error] {e}")

        return response
