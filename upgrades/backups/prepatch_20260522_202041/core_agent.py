"""NINA v12 — AgentLoop (Stage 5)
THINK -> PLAN -> ACT -> OBSERVE -> ADAPT. Variable step budget + global timeout + thermal preflight.
"""
import asyncio, logging, time
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

    async def run(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
        try:
            return await asyncio.wait_for(
                self._inner(goal, task, session_history),
                timeout=self.config.agent_timeout_s)
        except asyncio.TimeoutError:
            logger.warning(f"agent_loop_timeout goal={goal[:80]!r} exceeded={self.config.agent_timeout_s}s",
                           extra={"log":"agent.log"})
            return f"Task timed out after {self.config.agent_timeout_s}s."

    async def _inner(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
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
        system_frame = (
            f"Goal: {goal}\n"
            f"Memory: {context}\n"
            "THINK -> PLAN -> ACT each step.\n"
            "TOOL:web INPUT:query | TOOL:browser INPUT:url | TOOL:shell INPUT:cmd | TOOL:system INPUT:status\n"
            "FINAL:answer when done.\n"
            "RULE: live data/prices/news — MUST use TOOL:web first."
        )
        msgs = [{"role": "user", "content": system_frame}] + session_history.copy()
        scratchpad = []

        for step in range(1, max_steps + 1):
            # Append only incremental scratchpad — no repeated context
            step_prompt = f"[Step {step}/{max_steps}] Scratchpad:\n{chr(10).join(scratchpad[-3:])}"
            msgs.append({"role": "user", "content": step_prompt})
            response = await self.router.route(goal, msgs, task, force_local_fast=force_local)
            msgs.append({"role": "assistant", "content": response})
            logger.info(f"agent_step step={step} task={task.task_type} response={response[:80]!r}",
                        extra={"log":"agent.log"})

            if "FINAL:" in response:
                return response.split("FINAL:", 1)[1].strip()

            if "TOOL:" in response:
                try:
                    tool_name  = response.split("TOOL:")[1].split()[0].lower()
                    tool_input = response.split("INPUT:")[1].strip() if "INPUT:" in response else ""
                    tool       = self.tools.get(tool_name)
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
