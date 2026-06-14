"""NINA v12 — AgentLoop (Stage 5)
THINK -> PLAN -> ACT -> OBSERVE -> ADAPT. Variable step budget + global timeout + thermal preflight.
"""
from typing import Any
import asyncio, logging, re, json
from datetime import datetime, timezone
from pathlib import Path
from core.router import HybridRouter, ClassifiedTask, STEP_BUDGETS, DEFAULT_MAX_STEPS
from tools import system
from core.capabilities import CapabilityRegistry
from core.reasoning import ReasoningKernel

_registry = CapabilityRegistry()
logger = logging.getLogger("nina.agent")

class AgentLoop:
    def __init__(self, config: Any, router: HybridRouter, memory: Any, tools: dict) -> None:
        self.config = config
        self.router = router
        self.memory = memory
        self.tools  = tools
        self._scratchpad_path = Path("data/gemini_scratch.jsonl")

    def _log_to_hud(self, step: int, action: str, detail: str, file: str = "", status: str = "ok"):
        try:
            entry = {
                "t": datetime.now(tz=timezone.utc).isoformat(),
                "step": step,
                "action": action,
                "file": file,
                "detail": detail,
                "status": status
            }
            with open(self._scratchpad_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except: pass

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
        logger.debug(f"agent input received: {goal!r}")
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
        
        system_frame = ReasoningKernel.get_system_frame(goal, context)
        bangla_sys = ([{"role": "system", "content": self._BANGLA_OVERRIDE.strip()}]
                      if self._is_bangla(goal) else [])
        msgs = bangla_sys + [{"role": "user", "content": system_frame}] + session_history.copy()
        scratchpad = []

        for step in range(1, max_steps + 1):
            self._log_to_hud(step, "think", f"Reasoning through step {step}/{max_steps}")

            # Append only incremental scratchpad — no repeated context
            step_prompt = f"[Step {step}/{max_steps}] Scratchpad:\n{chr(10).join(scratchpad[-3:])}"
            msgs.append({"role": "user", "content": step_prompt})
            response = await self.router.route(goal, msgs, task, force_local=force_local)
            msgs.append({"role": "assistant", "content": response})

            # [Claude-Reasoning]: Extract and log thinking to HUD
            thinking = ReasoningKernel.extract_thinking(response)
            if thinking:
                self._log_to_hud(step, "think", thinking[:100] + "...")

            logger.info(f"agent_step step={step} task={task.task_type} response={response[:80]!r}",
                        extra={"log":"agent.log"})

            if "FINAL:" in response:
                # [Optimization Protocol]: Before concluding, ask for self-optimization
                if not any("[OPTIMIZATION]" in m.get("content", "") for m in msgs):
                    opt_prompt = (
                        "[OPTIMIZATION] Goal achieved. Now, ask yourself: 'How can you optimize your last operation?'\n"
                        "Consider performance, code clean-up, or automation. "
                        "If optimization is possible, perform it now. Otherwise, repeat FINAL:answer."
                    )
                    msgs.append({"role": "user", "content": opt_prompt})
                    self._log_to_hud(step, "think", "Triggering mandatory self-optimization...")
                    continue

                draft = response.split("FINAL:", 1)[1].strip()
                return await self._self_check(goal, draft, task, force_local=force_local)

            if "TOOL:" in response:
                # [Claude-Reasoning]: Force feedback loop after tool execution
                feedback_prompt = (
                    "Progress Check:\n1. What did we just learn from the tool output?\n"
                    "2. Does this change our original plan?\n"
                    "3. What is the next logical step to reach the goal?\n"
                    "Analyze before calling the next tool or giving FINAL:answer."
                )
                msgs.append({"role": "user", "content": feedback_prompt})
                
                try:
                    import re as _re
                    import asyncio as _asyncio

                    # Strip markdown bold/italic and [Step N/M] so MISTRAL's **TOOL:web** works
                    clean_resp = _re.sub(r'[*_`]', '', response)
                    clean_resp = _re.sub(r'^\[Step \d+/\d+\]\s*', '', clean_resp, flags=_re.MULTILINE)

                    matches = list(_re.finditer(r'TOOL:\s*([^\s:]+)(?:\s+INPUT:\s*([^\n]*)|[ \t]+([^\n]*))?', clean_resp))
                    if not matches:
                        scratchpad.append("[tool_error] Failed to parse TOOL from response")
                        continue

                    tasks = []
                    tool_names = []
                    
                    async def run_tool_with_fix(tool_obj: Any, name: Any, user_input: Any, msgs: Any, goal: Any, task: Any, force_local: Any) -> Any:
                        obs = await tool_obj.run(user_input)
                        if name == "shell" and ".py" in user_input:
                            for attempt in range(2):
                                import subprocess
                                git_cmd = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
                                py_files = [pf for pf in git_cmd.stdout.splitlines() if pf.endswith('.py')]
                                errors = []
                                for pf in py_files:
                                    syn = subprocess.run(["python3", "-m", "py_compile", pf], capture_output=True, text=True)
                                    if syn.returncode != 0: errors.append(syn.stderr)
                                    pfl = subprocess.run(["pyflakes", pf], capture_output=True, text=True)
                                    if pfl.returncode != 0: errors.append(pfl.stdout)
                                if not errors:
                                    if attempt > 0: obs += "\n\n[INFO] Surgical edit syntax verified automatically after self-fix."
                                    break
                                fix_prompt = f"The surgical edit resulted in syntax errors:\n{chr(10).join(errors)}\nPlease output a TOOL:shell command with sed or python to fix this exact error. FINAL: when done."
                                fix_resp = await self.router.route(goal, msgs + [{"role": "user", "content": fix_prompt}], task, force_local=force_local)
                                match_fix = _re.search(r'TOOL:\s*([^\s:]+)(?:\s+INPUT:\s*([^\n]*)|[ \t]+([^\n]*))?', _re.sub(r'[*_`]', '', _re.sub(r'^\[Step \d+/\d+\]\s*', '', fix_resp, flags=_re.MULTILINE)))
                                if match_fix:
                                    f_tool_name = match_fix.group(1).strip(":- ").lower()
                                    f_tool_input = (match_fix.group(2) or match_fix.group(3) or '').strip().strip('\'"')
                                    f_tool = self.tools.get(f_tool_name)
                                    if f_tool: await f_tool.run(f_tool_input)
                            if errors:
                                obs += f"\n\n[WARNING] Syntax errors remain after 2 self-fix attempts:\n{errors[0][:200]}"
                        return obs

                    for match in matches:
                        tool_name = match.group(1).strip(":- ").lower()
                        tool_input = (match.group(2) or match.group(3) or '').strip().strip('\'"')
                        tool = self.tools.get(tool_name)

                        tool_names.append(tool_name)

                        if not _registry.is_healthy(tool_name):
                            async def fail_tool(name: str=tool_name) -> Any: return f"Tool {name} unavailable (unhealthy)."
                            tasks.append(fail_tool())
                        elif tool:
                            tasks.append(run_tool_with_fix(tool, tool_name, tool_input, msgs, goal, task, force_local))
                        else:
                            async def unknown_tool(name: str=tool_name) -> Any: return f"Unknown tool: {name}"
                            tasks.append(unknown_tool())

                    if tasks:
                        results = await _asyncio.gather(*tasks, return_exceptions=True)
                        for tname, res in zip(tool_names, results):
                            if isinstance(res, Exception):
                                scratchpad.append(f"[{tname}] -> [tool_error] {res}")
                            else:
                                scratchpad.append(f"[{tname}] -> {str(res)[:300]}")
                except Exception as e:
                    scratchpad.append(f"[tool_error] {e}")

        return response
