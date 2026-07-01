"""NINA v13 — AgentLoop (Stage 5 + Orchestrator Wire)
THINK -> PLAN -> ACT -> OBSERVE -> ADAPT. Variable step budget + global timeout + thermal preflight.
Orchestrator wire: agents/orchestrator.py is called at the top of _inner() for eligible tasks.
If confidence >= 0.85 the orchestrated result is returned directly, otherwise falls through to
the existing ReAct pipeline unchanged.
"""
from typing import Any
import asyncio
import logging
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from core.router import HybridRouter, STEP_BUDGETS, DEFAULT_MAX_STEPS
from core.task_classifier import ClassifiedTask
from tools import system
from core.capabilities import CapabilityRegistry
from core.reasoning import ReasoningKernel, ToolFirstReflex, MissionMemoryCarrier
from core.circuit_breaker import BehavioralCircuitBreaker
from core.reflexion import ReflexionEngine
from core.goal_manager import GoalManager

def _sanitize_tool_call(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"(?<![\\\])\'", '"', raw)
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw

def parse_tool_call(raw: str) -> dict | None:
    try:
        if not isinstance(raw, str):
            logger.warning(f"Tool grammar parse failed: input is not a string | type={type(raw).__name__}")
            return None
        parsed = json.loads(_sanitize_tool_call(raw))
    except (ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as e:
        logger.warning(f"Tool grammar parse failed after sanitize: {e} | raw={str(raw)[:120]}")
        parsed = None
    if parsed is None:
        return None
    return parsed

_registry = CapabilityRegistry()
logger = logging.getLogger("nina.agent")

class AgentLoop:
    _CHAINED_RE = re.compile(r"then|after|next|step|sequence|first|and also", re.IGNORECASE)

    def __init__(self, config: Any, router: HybridRouter, memory: Any, tools: dict) -> None:
        self.config = config
        self.router = router
        from core.quota_dispatcher import QuotaDispatcher
        self.dispatcher = QuotaDispatcher(self.router)
        self.router.dispatcher = self.dispatcher
        self.memory = memory
        self.tools  = tools
        self._scratchpad_path = Path("data/gemini_scratch.jsonl")
        self.nina = None
        cost_limit = getattr(config, "circuit_breaker_cost_limit", 0.25) if config else 0.25
        if not isinstance(cost_limit, (int, float)):
            cost_limit = 0.25
        max_tool_calls = getattr(config, "circuit_breaker_max_tool_calls", 6) if config else 6
        if not isinstance(max_tool_calls, (int, float)):
            max_tool_calls = 6
        self.circuit_breaker = BehavioralCircuitBreaker(cost_limit=cost_limit, max_tool_calls_per_run=max_tool_calls)
        self._file_cache = {}
        self._debug_phase = "FINDINGS"
        self.goal_manager = GoalManager()
        # Lazy-init orchestrator — imported here to avoid circular import at module load
        self._orchestrator = None

    def _get_orchestrator(self):
        if self._orchestrator is None:
            try:
                from agents.orchestrator import AgentOrchestrator
                self._orchestrator = AgentOrchestrator(self.router)
            except Exception as e:
                logger.warning(f"orchestrator_init_failed (non-fatal): {e}")
        return self._orchestrator

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
            with open(self._scratchpad_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            # Bounded log rotation to prevent HUD I/O stalls on large files
            if self._scratchpad_path.exists() and self._scratchpad_path.stat().st_size > 50000:
                with open(self._scratchpad_path, "r", encoding="utf-8", errors="ignore") as rf:
                    lines = rf.readlines()
                if len(lines) > 200:
                    with open(self._scratchpad_path, "w", encoding="utf-8") as wf:
                        wf.writelines(lines[-100:])
        except Exception:
            pass

    def pre_task_snapshot(self, file_paths: list[str]) -> None:
        if not hasattr(self, "_file_cache"):
            self._file_cache = {}
        for fp in file_paths:
            if not fp or not isinstance(fp, str):
                continue
            # Basic validation that it's a real path
            if "/" in fp or "." in fp:
                p = Path(fp)
                if not p.is_absolute():
                    p = Path("/home/aibony/nina") / p
                if p.exists() and p.is_file():
                    try:
                        self._file_cache[fp] = p.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass

    def _get_available_tools(self) -> list[str]:
        return list(self.tools.keys())

    def _pre_self_check(self, task: str, tools_required: list[str] = None) -> dict:
        """
        Returns {"ok": True} if ready, or
        {"ok": False, "reason": str, "suggestion": str} if not.
        """
        issues = []

        # Check 1: context window — warn if task string > 6000 chars
        if len(task) > 6000:
            issues.append("Task length exceeds safe context window (6000 chars)")

        # Check 2: required tools available
        if tools_required:
            available = self._get_available_tools()  # use existing method
            missing = [t for t in tools_required if t not in available]
            if missing:
                issues.append(f"Required tools not available: {missing}")

        # Check 3: router health — call router.is_available() if it exists,
        #           else skip this check silently
        try:
            if hasattr(self, 'router') and not self.router.is_available():
                issues.append("Router reports no available providers")
        except Exception:
            pass  # non-fatal

        if issues:
            return {
                "ok": False,
                "reason": "; ".join(issues),
                "suggestion": "Simplify the task or check provider quota."
            }
        return {"ok": True}

    def _should_self_check(self, task: ClassifiedTask) -> bool:
        t_type = (getattr(task, "task_type", "") or "").lower()
        s_type = (getattr(task, "_semantic_type", "") or "").lower()
        _check_types = {"research", "coding", "diagnostic", "sensitive"}
        return t_type in _check_types or s_type in _check_types

    async def _self_check(self, goal: str, draft: str, task: ClassifiedTask, force_local: bool = False) -> str:
        t_type = (getattr(task, "task_type", "") or "").lower()
        if not draft or not self._should_self_check(task):
            return draft

        _draft_limit = 8000 if (getattr(task, "complexity", "") in ("COMPLEX", "MASSIVE")) else 3000

        logger.info("Initiating Phase II: Bounded Multi-Pass Reasoning Engine (ReAct/OODA Upgrade)")
        current_draft = draft
        max_passes = 3
        depth = 0
        token_budget = 40000  # Hard token budget limit for the critique loop
        accumulated_tokens = 0

        # Stage 1: PLANNER (Decomposes the goal and validation objectives)
        planner_prompt = (
            f"Goal: {goal}\n\n"
            f"Initial Draft/Solution to verify:\n{draft[:_draft_limit]}\n\n"
            "You are NINA's cognitive Planner. Decompose this goal and solution into specific validation criteria.\n"
            "Identify:\n"
            "1. Core requirements and potential syntax/import concerns.\n"
            "2. Safety boundaries (no destructive commands, no leaked secrets).\n"
            "3. Necessary verification tests or checks.\n"
            "Output a structured plan for the Critic and Verifier."
        )
        plan_str = ""
        try:
            plan = self.dispatcher.dispatch(planner_prompt, force_tier="LOCALFAST" if force_local else ("FAST" if t_type not in ("research", "coding", "diagnostic") else None))
            plan_str = await plan.execute()
            accumulated_tokens += len(planner_prompt + plan_str) / 4.0
            logger.info("Planner Stage: Completed verification roadmap.")
        except Exception as e:
            logger.warning(f"Planner Stage failed: {e}")
            plan_str = "Perform standard syntax and safety checks."

        # Keep running critique loops until pass or depth/budget exceeded
        while depth < max_passes and accumulated_tokens < token_budget:
            depth += 1
            logger.info(f"Deliberative Critique Pass {depth}/{max_passes}")

            # Stage 3: CRITIC (Verifies syntax, safety, and imports)
            critic_issues = []
            has_syntax_error = False

            if "```python" in current_draft:
                blocks = re.findall(r'```python\s*(.*?)\s*```', current_draft, re.DOTALL)
                for i, code_block in enumerate(blocks):
                    try:
                        compile(code_block.strip(), f"<string_check_{i}>", "exec")
                    except Exception as e:
                        has_syntax_error = True
                        critic_issues.append(f"Python Syntax/Compilation Error in block {i+1}: {e}")

            # Run LLM Critic for semantic, safety, imports, and principle checks
            critic_prompt = (
                f"Goal: {goal}\n\n"
                f"Verification Plan:\n{plan_str}\n\n"
                f"Current Draft:\n{current_draft[:_draft_limit]}\n\n"
                "You are NINA's cognitive Critic. Review the draft against the original goal, the plan, and safety standards.\n"
                "Specifically check:\n"
                "- Imports: Are any imported modules missing or invalid?\n"
                "- Safety: Does it violate security boundaries or contain harmful actions?\n"
                "- Logic: Is there any contradiction or incorrect reasoning?\n"
                "- Read-first: Did the solution read/check the actual file or git history BEFORE theorizing? "
                "If it made assumptions without reading source, mark REVISE.\n\n"
                f"Detected programmatic issues: {critic_issues if critic_issues else 'None'}\n\n"
                "Output PASS if the response is excellent, complete, accurate, safe, and syntactically correct.\n"
                "Otherwise, output REVISE: <detailed corrective feedback for the Generator>."
            )
            
            critic_feedback = ""
            try:
                plan = self.dispatcher.dispatch(critic_prompt, force_tier="LOCALFAST" if force_local else ("FAST" if t_type not in ("research", "coding", "diagnostic") else None))
                critic_feedback = await plan.execute()
                # Gate 1: constitutional validation
                _passed, _violations = ReasoningKernel.validate_output(current_draft)
                if not _passed:
                    critic_feedback = "REVISE: Constitutional violations detected: " + "; ".join(_violations)
                    is_pass = False
                accumulated_tokens += len(critic_prompt + critic_feedback) / 4.0
                logger.info(f"Critic Stage Feedback: {critic_feedback[:100]}...")
            except Exception as e:
                logger.warning(f"Critic Stage failed: {e}")
                critic_feedback = "PASS"

            # Check if Critic passed
            critic_clean = critic_feedback.strip()
            is_pass = critic_clean.startswith("PASS") or "PASS" in critic_clean[:10]
            if is_pass and not has_syntax_error:
                logger.info("Critic Stage: PASS achieved.")
                
                # Stage 4: VERIFIER (Runs test suites or semantic checks)
                verifier_prompt = (
                    f"Goal: {goal}\n\n"
                    f"Approved Draft:\n{current_draft[:_draft_limit]}\n\n"
                    "You are NINA's cognitive Verifier. Run final logical validation on this approved draft.\n"
                    "Verify if any edge cases are missed, or if there are any logical fallacies.\n"
                    "Output VERIFIED if everything is perfect, or REVISE: <corrective instructions> if a logical gap remains."
                )
                try:
                    plan = self.dispatcher.dispatch(verifier_prompt, force_tier="LOCALFAST" if force_local else ("FAST" if t_type not in ("research", "coding", "diagnostic") else None))
                    verifier_feedback = await plan.execute()
                    accumulated_tokens += len(verifier_prompt + verifier_feedback) / 4.0
                    logger.info(f"Verifier Stage Feedback: {verifier_feedback[:100]}...")
                    if verifier_feedback.strip().startswith("VERIFIED") or "VERIFIED" in verifier_feedback.strip()[:10]:
                        logger.info("Verifier Stage: VERIFIED achieved.")
                        break
                    else:
                        critic_feedback = verifier_feedback  # Treat verifier rejection as critique for next revision
                        is_pass = False  # explicitly mark as needing revision so loop continues correctly
                except Exception as e:
                    logger.warning(f"Verifier Stage failed: {e}")
                    break
            
            # If rejected, run Stage 2: GENERATOR (drafts corrections based on critique feedback)
            revision_instructions = critic_feedback
            if has_syntax_error and critic_issues:
                revision_instructions = "FIX SYNTAX ERRORS:\n" + "\n".join(critic_issues) + f"\n\nOther feedback:\n{critic_feedback}"

            generator_prompt = (
                f"Goal: {goal}\n\n"
                f"Current Draft:\n{current_draft[:_draft_limit]}\n\n"
                f"Verification Roadmap:\n{plan_str}\n\n"
                f"Corrective Feedback:\n{revision_instructions}\n\n"
                "You are NINA's cognitive Generator. Revise the current draft to address all the corrective feedback and syntax errors.\n"
                "Output the complete corrected response. Wrap any updated python code in standard ```python ... ``` blocks."
            )
            try:
                plan = self.dispatcher.dispatch(generator_prompt, force_tier="LOCALFAST" if force_local else ("FAST" if t_type not in ("research", "coding", "diagnostic") else None))
                current_draft = await plan.execute()
                accumulated_tokens += len(generator_prompt + current_draft) / 4.0
                logger.info("Generator Stage: Completed revised draft generation.")
            except Exception as e:
                logger.warning(f"Generator Stage failed: {e}")
                break

        # Stage 5: REFLECTOR (Saves post-mortem learnings)
        try:
            logger.info("Reflector Stage: Generating and storing post-mortem reflection.")
            trace_steps = [
                "Planner: Created verification plan.",
                f"Critique Passes: {depth} completed.",
                f"Tokens consumed in critique: {accumulated_tokens}.",
            ]
            success = (depth < max_passes) or ("VERIFIED" in current_draft)
            await ReflexionEngine.generate_reflection(
                dispatcher=self.dispatcher,
                memory=self.memory,
                goal=goal,
                trace=trace_steps,
                success=success,
            )
        except Exception as e:
            logger.warning(f"Reflector Stage failed to store reflection: {e}")

        return current_draft

    async def run(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
        try:
            res = await asyncio.wait_for(
                self._inner(goal, task, session_history),
                timeout=self.config.agent_timeout_s)
            
            # QW-2: two-pass critic for complex responses
            try:
                # Skip QW-2 if _self_check already ran (avoids double critique pipeline)
                _already_checked = self._should_self_check(task)
                task_len = len(res) if isinstance(res, str) else 0
                is_complex = not _already_checked and (task_len > 300 or any(
                    kw in (goal or "").lower()
                    for kw in ["code", "write", "create", "fix", "analyze", "plan", "explain", "how to"]
                ))
                if is_complex:
                    critic_prompt = (
                        "You are a strict critic. Review this response for quality.\n\n"
                        f"ORIGINAL TASK: {(goal or '')[:300]}\n\n"
                        f"RESPONSE TO REVIEW:\n{res[:1500]}\n\n"
                        "Rate on three criteria (each 0-10):\n"
                        "1. ACCURACY: factually correct and complete?\n"
                        "2. CLARITY: well structured and clear?\n"
                        "3. TASK_FIT: does it actually answer the task?\n\n"
                        "If ANY score < 6, output REVISE: <one specific improvement instruction>.\n"
                        "If all scores >= 6, output PASS.\n"
                        "Output ONLY: PASS or REVISE: <instruction>"
                    )
                    _critic_plan = self.dispatcher.dispatch(critic_prompt, force_tier="LOCALFAST")
                    critic_result = await _critic_plan.execute()
                    if isinstance(critic_result, str) and critic_result.strip().startswith("REVISE:"):
                        revision_instruction = critic_result.replace("REVISE:", "").strip()
                        revision_prompt = (
                            "Improve your previous response based on this specific feedback:\n"
                            f"{revision_instruction}\n\n"
                            f"Original task: {(goal or '')[:300]}\n"
                            f"Original response: {res[:1500]}\n\n"
                            "Provide an improved response only. Do not explain what you changed."
                        )
                        revised = await self.router.route(
                            revision_prompt,
                            messages=[],
                            task_type="general"
                        )
                        if revised and len(revised) > 50:
                            res = revised
                            logger.info("critic_revision_applied")
            except Exception as e:
                logger.warning(f"critic_pass_failed err={e}")
                # never block — original response still used

            # QW-1: store reflection for complex tasks
            try:
                if len(res) > 600 and any(kw in (goal or "").lower() for kw in ["code", "fix", "write", "analyze", "debug", "diagnose", "create", "explain"]):
                    import time
                    reflection_prompt = (
                        "In one sentence each, answer:\n"
                        "1. What worked well in this response?\n"
                        "2. What could have been better?\n"
                        "3. One improvement for next time.\n"
                        "Format: WORKED: ... | FAILED: ... | IMPROVE: ..."
                    )
                    _ref_plan = self.dispatcher.dispatch(reflection_prompt, context=goal[:200])
                    ref_resp = await _ref_plan.execute()
                    parts = ref_resp.split("|")
                    worked = parts[0].replace("WORKED:", "").strip() if len(parts) > 0 else "n/a"
                    failed = parts[1].replace("FAILED:", "").strip() if len(parts) > 1 else "n/a"
                    improve = parts[2].replace("IMPROVE:", "").strip() if len(parts) > 2 else "n/a"
                    await self.memory.save_reflection(
                        session_id=str(int(time.time())),
                        goal=goal[:200],
                        outcome="success",
                        what_worked=worked,
                        what_failed=failed,
                        improvement_note=improve
                    )
            except Exception:
                pass  # never block the response
                
            return res
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

    def _search_index_by_terms(self, goal: str) -> list:
        index_path = Path("docs/space/nina_index.json")
        if not index_path.exists():
            return []
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            stopwords = {"the", "and", "for", "you", "that", "this", "with", "from", "your", "how", "what", "which", "are", "have", "please", "should", "need", "needed"}
            words = [w.strip("?,.:;\"'()") for w in goal.lower().split()]
            keywords = [w for w in words if len(w) > 3 and w not in stopwords]
            
            if not keywords:
                return []
            
            matches = []
            for file_obj in data.get("files", []):
                path = file_obj.get("path", "")
                summary = file_obj.get("summary", "").lower()
                path_lower = path.lower()
                
                score = 0
                for kw in keywords:
                    if kw in path_lower:
                        score += 3
                    if kw in summary:
                        score += 1
                
                if score > 0:
                    matches.append((score, path))
            
            matches.sort(reverse=True, key=lambda x: x[0])
            return [Path(p) for _, p in matches]
        except Exception:
            return []

    def _compress_markdown(self, text: str, keywords: list) -> str:
        lines = text.splitlines()
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                result.append(line)
            elif any(kw in line.lower() for kw in keywords):
                result.append(line)
        
        compressed = "\n".join(result)
        if len(compressed) < 200:
            return text[:1500]
        return compressed

    _BANGLA_OVERRIDE = (
        "[LANGUAGE OVERRIDE: User wrote in Bangla. "
        "Your ENTIRE response must be in Bangla. "
        "No English except unavoidable technical terms like API, token, git.]\n\n"
    )

    async def _inner(self, goal: str, task: ClassifiedTask, session_history: list) -> str:
        logger.debug(f"agent input received: {goal!r}")

        # ── ORCHESTRATOR WIRE ──────────────────────────────────────────────────
        # Attempt agent-chain routing before the full ReAct pipeline.
        # Only runs for non-surgical, non-diagnostic, non-command goals.
        # Falls through silently on any failure — existing pipeline is unaffected.
        _is_command = isinstance(goal, str) and (
            goal.startswith("/") or goal.startswith("SURGICAL:")
        )
        _task_type = (getattr(task, "task_type", "") or "").lower()
        _is_diagnostic = _task_type == "diagnostic"

        if not _is_command and not _is_diagnostic:
            try:
                _orch = self._get_orchestrator()
                if _orch is not None:
                    _orch_result = await asyncio.wait_for(
                        _orch.run(goal, list(session_history)),
                        timeout=min(30, getattr(self.config, "agent_timeout_s", 120) // 2)
                    )
                    if (
                        _orch_result is not None
                        and hasattr(_orch_result, "confidence")
                        and _orch_result.confidence >= 0.85
                        and isinstance(_orch_result.payload.get("response"), str)
                        and len(_orch_result.payload["response"]) > 20
                    ):
                        logger.info(
                            f"orchestrator_fast_path: confidence={_orch_result.confidence:.2f} "
                            f"sender={_orch_result.sender}"
                        )
                        return _orch_result.payload["response"]
                    else:
                        logger.debug(
                            f"orchestrator_fallthrough: confidence="
                            f"{getattr(_orch_result, 'confidence', 'n/a')} — continuing ReAct pipeline"
                        )
            except asyncio.TimeoutError:
                logger.debug("orchestrator_timeout — continuing ReAct pipeline")
            except Exception as _orch_exc:
                logger.warning(f"orchestrator_wire_failed (non-fatal): {_orch_exc}")
        # ── END ORCHESTRATOR WIRE ──────────────────────────────────────────────

        session_history = list(session_history)
        trace = []
        self.circuit_breaker.session_cost = 0.0
        self.circuit_breaker.tool_call_count = 0
        self.circuit_breaker.consecutive_failures = 0
        self.circuit_breaker.state = "CLOSED"

        # PROMPT 19 — pre_task_snapshot candidates in goal
        candidates = re.findall(r'\b[a-zA-Z0-9_/.-]+\.[a-zA-Z0-9_-]+\b', goal)
        if candidates:
            self.pre_task_snapshot(candidates)

        # PROMPT 17 — MEMORY ANCHOR reading
        anchor_parts = []
        for fn in ["perplexity_handoff.md", "nina_error_register.md", "jules_backlog.md", "nina_runbook.md"]:
            fp = Path(f"/home/aibony/nina/docs/space/{fn}")
            if fp.exists():
                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                    anchor_parts.append(f"=== {fn} ===\n{content}")
                except Exception:
                    pass
        anchor_text = "\n\n".join(anchor_parts) if anchor_parts else ""

        # F-08 Command Routing
        if goal.startswith("/remember"):
            val = goal[len("/remember"):].strip()
            if hasattr(self, "memory") and self.memory:
                await self.memory.kb_add_entry(tags=["agent"], text=val)
                return f"✅ Remembered: '{val}'"

        if goal.startswith("/recall"):
            query = goal[len("/recall"):].strip()
            if hasattr(self, "memory") and self.memory:
                results = await self.memory.kb_search(query=query)
                if results:
                    lines = [f"• {r['text']} (source: {r.get('source', 'unknown')})" for r in results]
                    return "🧠 *Personal Knowledge Base matches*:\n" + "\n".join(lines)
                else:
                    return f"Nothing found for '{query}'."

        # F-06 Reminder Intent Parsing
        lower_goal = goal.lower()
        if any(kw in lower_goal for kw in ["remind me", "set reminder", "remind me at"]):
            text = ""
            remind_at = ""
            m1 = re.search(r"(?:remind me|set reminder)\s+((?:tomorrow|today|tonight|in \d+ \w+|at \d+(?::\d+)?\w*|\d+(?::\d+)?\w*)(?:\s+at\s+\d+(?::\d+)?\w*)?)?\s+to\s+(.+)", lower_goal)
            m2 = re.search(r"(?:remind me|set reminder)\s+(?:to\s+)?(.+?)\s+(tomorrow|today|tonight|in \d+ \w+|at \d+(?::\d+)?\w*|\d+(?::\d+)?\w*)$", lower_goal)
            if m1:
                remind_at = m1.group(1).strip() if m1.group(1) else ""
                text = m1.group(2).strip()
            elif m2:
                text = m2.group(1).strip()
                remind_at = m2.group(2).strip()
            else:
                m3 = re.search(r"(?:remind me|set reminder)\s+(?:to\s+)?(.+?)\s+(?:at|in|on)\s+(.+)", lower_goal)
                if m3:
                    text = m3.group(1).strip()
                    remind_at = m3.group(2).strip()
                else:
                    text = goal
                    remind_at = "in 5 minutes"

            idx = goal.lower().find(text.lower())
            if idx != -1:
                text = goal[idx:idx+len(text)].strip()

            if hasattr(self, "nina") and self.nina:
                return await self.nina.add_reminder(text, remind_at)

        # PROMPT 20 — SURGICAL: bypass steps 1-11
        is_surgical = False
        if isinstance(goal, str) and goal.startswith("SURGICAL:"):
            is_surgical = True
        elif isinstance(task, str) and task.startswith("SURGICAL:"):
            is_surgical = True

        force_local = False

        if is_surgical:
            max_steps = STEP_BUDGETS.get(getattr(task, "task_type", "general"), DEFAULT_MAX_STEPS)
            system_frame = ReasoningKernel.get_system_frame(goal, "")
            bangla_sys = ([{"role": "system", "content": self._BANGLA_OVERRIDE.strip()}]
                          if self._is_bangla(goal) else [])
            msgs = bangla_sys + [{"role": "user", "content": system_frame}] + session_history.copy()
            scratchpad = []
            _mission_summaries = []
        else:
            # F-01 Pre-Execution Rule-based Self-Check Pass
            task_type_str = (getattr(task, "task_type", "") or "").lower()
            semantic_type_str = (getattr(task, "_semantic_type", "") or "").lower()
            
            is_f01_complex = (
                "```" in goal
                or len(goal) > 1500
                or task_type_str in ("code", "coding", "multi_step")
                or semantic_type_str in ("code", "coding", "multi_step")
            )

            if is_f01_complex:
                detected_tools = [t for t in self.tools.keys() if t in goal.lower()]
                check = self._pre_self_check(goal, tools_required=detected_tools)
                if not check["ok"]:
                    logger.warning(f"Self-check failed: {check['reason']}")
                    return f"⚠️ Self-check: {check['reason']}\n💡 {check['suggestion']}"

            # F-01 Complexity Self-Check Pass
            COMPLEX_TASK_TOKEN_THRESHOLD = 300
            is_complex = False
            token_count = len(goal.split())
            # [Performance] Pre-compiled regex search avoids string allocation (.lower()) and python-level generator iteration in hot loop
            has_chained = bool(self._CHAINED_RE.search(goal))
            suspected_tools = [t for t in self.tools if t in goal.lower()]
            has_multiple_tools = len(suspected_tools) > 1

            if has_multiple_tools or has_chained or token_count > COMPLEX_TASK_TOKEN_THRESHOLD or (task and getattr(task, "complexity", "") in ("COMPLEX", "MASSIVE")):
                is_complex = True

            if is_complex:
                self_check_prompt = (
                    f"Analyze this goal: '{goal}'\n"
                    "Return a JSON object with keys:\n"
                    "- intent: a brief string summarizing the core user intent\n"
                    "- tools: a list of tool names likely needed (choose from: " + ", ".join(self.tools.keys()) + ")\n"
                    "- steps: estimated number of steps (integer)\n"
                    "- ambiguous: boolean, true if the intent is highly ambiguous (no clear tool match and no clear text response path)\n"
                    "- detected_intent: if ambiguous, a short 3-5 word phrase of what you think they want, to ask for confirmation.\n"
                    "Return ONLY raw JSON, no markdown formatting."
                )
                try:
                    plan = self.dispatcher.dispatch(self_check_prompt, force_tier="LOCALFAST")
                    check_res_str = await plan.execute()
                    check_res_str = re.sub(r'```json|```', '', check_res_str).strip()
                    check_data = json.loads(check_res_str)
                    intent = check_data.get("intent", "Unknown")
                    tools_planned = check_data.get("tools", [])
                    steps_count = check_data.get("steps", 1)
                    ambiguous = check_data.get("ambiguous", False)
                    detected_intent = check_data.get("detected_intent", "proceed")

                    logger.info(f"Self-check: intent={intent}, tools={tools_planned}, steps={steps_count}")

                    if ambiguous:
                        return f"I want to make sure I understood — are you asking me to {detected_intent}? Reply yes to proceed."
                except Exception as e:
                    logger.warning(f"Self-check error: {e}")

            ram = await system.get_ram_used_gb()
            if ram >= self.config.ram_guard_gb:
                logger.warning(f"agent_loop_skipped ram={ram:.1f}GB guard={self.config.ram_guard_gb}GB")
                return await self.router.single_turn(goal, session_history)

            # DIAGNOSTIC fast-path: skip System2 + self-check overhead for simple diagnostic queries
            task_type_str_inner = (getattr(task, "task_type", "") or "").lower()
            if task_type_str_inner == "diagnostic":
                system_frame = ReasoningKernel.get_system_frame(goal, locals().get('base_context', ''), mode="diagnostic")
                system_frame = (
                    "[DIAGNOSTIC MODE]\nBefore theorizing:\n"
                    "1. Run: git log --all --full-history -- <suspected file>\n"
                    "2. Check nina_error_register.md for matching OPEN rows\n"
                    "3. Read the actual file/script before forming a hypothesis\n\n"
                ) + system_frame
                msgs = [{"role": "user", "content": system_frame}] + session_history.copy()
                if anchor_text:
                    msgs.insert(0, {"role": "system", "content": f"[MEMORY ANCHOR]\n{anchor_text.strip()}"})
                plan = self.dispatcher.dispatch(goal, context=str(msgs))
                return await plan.execute()

            temps      = await system.get_temps()
            cput       = temps.get("cpu") or 0
            gput       = temps.get("gpu") or 0

            if cput >= self.config.thermal_critical_cpu or gput >= self.config.thermal_critical_gpu:
                logger.critical(f"agent_loop_aborted_thermal CPU={cput} GPU={gput}", extra={"log":"agent.log"})
                return f"CRITICAL temp CPU={cput}C GPU={gput}C. Agent loop aborted."

            if cput >= self.config.thermal_guard_cpu or gput >= self.config.thermal_guard_gpu:
                logger.warning(f"thermal_guard CPU={cput} GPU={gput} forcing LOCALFAST")
                force_local = True

            if cput >= self.config.thermal_warn_cpu or gput >= self.config.thermal_warn_gpu:
                logger.warning(f"thermal_warn CPU={cput} GPU={gput}", extra={"log":"nina.log"})

            max_steps  = STEP_BUDGETS.get(task.task_type, DEFAULT_MAX_STEPS)
            char_budget = 12000
            n_docs = 20
            try:
                from core.hyperdrive_policy import policy
                if policy.is_enabled() and 'task' in locals() and task:
                    hd_tier = policy.estimate_required_tier(task)
                    if hd_tier == "LOCALFAST":
                        char_budget = 3500
                        n_docs = 10
                    elif hd_tier == "FAST":
                        char_budget = 12000
                        n_docs = 20
                    elif hd_tier in ("DEEP", "LARGE"):
                        char_budget = 40000
                        n_docs = 40
            except Exception as e:
                logger.warning(f"Failed to estimate context budget: {e}")

            base_context = await self.memory.build_context(goal, n=n_docs, char_budget=char_budget)

            past_reflections_str = ""
            try:
                if hasattr(self, "memory") and self.memory:
                    past_reflections = await self.memory.episodic_search(query=goal, limit=3)
                    if past_reflections:
                        ref_lines = [f"- Goal: {r['goal']}\n  Reflection: {r['reflection']}" for r in past_reflections]
                        past_reflections_str = "\n\n[PAST POST-MORTEM REFLECTIONS]\n" + "\n".join(ref_lines)
            except Exception as e:
                logger.warning(f"Failed to query episodic memories: {e}")

            # 1. Document-to-Skill / Context Enrichment (Metacognition)
            enriched_context = ""
            try:
                related_docs = self._search_index_by_terms(goal)
                stopwords = {"the", "and", "for", "you", "that", "this", "with", "from", "your", "how", "what", "which", "are", "have"}
                goal_keywords = [w.strip("?,.:;\"'()") for w in goal.lower().split()]
                goal_keywords = [w for w in goal_keywords if len(w) > 3 and w not in stopwords]
                
                seen_snippets = set()
                for doc_path in related_docs[:2]:
                    if doc_path.name in ("agent.py", "router.py"):
                        continue
                    if doc_path.exists() and doc_path.is_file():
                        raw_content = doc_path.read_text(encoding="utf-8", errors="ignore")
                        if doc_path.suffix == ".py":
                            from tools.context_pruner import prune_content
                            compressed = prune_content(raw_content, ".py")
                        elif doc_path.suffix == ".md":
                            compressed = self._compress_markdown(raw_content, goal_keywords)
                        else:
                            compressed = raw_content[:1000]
                        _doc_snippet = compressed[:200]
                        if _doc_snippet not in seen_snippets and _doc_snippet not in (base_context + past_reflections_str):
                            seen_snippets.add(_doc_snippet)
                            enriched_context += f"\n--- Reference Manual: {doc_path.name} ---\n{compressed}\n"
            except Exception as e:
                logger.warning(f"context_enrichment_failed: {e}")

            # [WIRED] knowledge_graph context enrichment
            graphrag_context = ""
            try:
                from core.knowledge_graph import KnowledgeGraph
                _kg = KnowledgeGraph()
                kg_results = _kg.query(goal, top_k=5)
                if kg_results:
                    graphrag_context = "\n\n[KNOWLEDGE GRAPH]\n" + "\n".join(
                        f"- {r}" if isinstance(r, str) else str(r)
                        for r in kg_results
                    )
            except Exception as _kg_err:
                logger.debug(f"knowledge_graph_query_failed: {_kg_err}")

            # [WIRED] goal_manager context enrichment (ARCH-3)
            goal_manager_context = ""
            try:
                self.goal_manager.register(goal)
                gm_active = self.goal_manager.get_active_context()
                if gm_active:
                    goal_manager_context = f"\n\n[GOAL MANAGER]\n{gm_active}"
            except Exception as _gm_err:
                logger.warning(f"goal_manager_context_failed: {_gm_err}")

            context = base_context + enriched_context + graphrag_context + goal_manager_context + past_reflections_str

            # 2. System 2 Thinking (Pre-Compute Planning Blueprint)
            blueprint = ""
            if self._should_self_check(task):
                try:
                    self._log_to_hud(0, "think", "System 2: Pausing to compute planning blueprint...")
                    planning_prompt = (
                        f"Goal: {goal}\n\nContext:\n{context}\n\n"
                        "System 2 Reflection: Pause and compute a complex logical chain to achieve this goal. "
                        "Draft a detailed step-by-step blueprint. Identify prerequisites, potential risks, and testing steps."
                    )
                    # Thermal guard: reduce step budget but don't degrade planning quality
                    plan = self.dispatcher.dispatch(planning_prompt, force_tier="LOCALFAST" if force_local else None)
                    blueprint = await plan.execute()
                except Exception as e:
                    logger.warning(f"system2_thinking_failed: {e}")

            system_frame = ReasoningKernel.get_system_frame(goal, context)
            if blueprint:
                system_frame += f"\n\n[SYSTEM 2 PLANNING BLUEPRINT]\n{blueprint}"
            bangla_sys = ([{"role": "system", "content": self._BANGLA_OVERRIDE.strip()}]
                          if self._is_bangla(goal) else [])
            msgs = bangla_sys + [{"role": "user", "content": system_frame}] + session_history.copy()
            scratchpad = []
            _mission_summaries: list[str] = []

        for step in range(1, max_steps + 1):
            self._log_to_hud(step, "think", f"Reasoning through step {step}/{max_steps}")

            # PROMPT 25 — SESSION_SUMMARY every 20 messages
            if len(msgs) >= 20 and len(msgs) % 20 == 0:
                logger.info("Triggering SESSION_SUMMARY compression...")
                to_compress = msgs[1:-3]
                if to_compress:
                    compress_prompt = (
                        "Summarize the following agent conversation history concisely. "
                        "Preserve key findings, actions taken, and status. Keep it under 500 characters:\n\n"
                        + "\n".join([f"{m['role']}: {m['content'][:300]}" for m in to_compress])
                    )
                    try:
                        summary_plan = self.dispatcher.dispatch(compress_prompt, force_tier="LOCALFAST")
                        summary_text = await summary_plan.execute()
                        summary_msg = {"role": "system", "content": f"[SESSION_SUMMARY]\n{summary_text.strip()}"}
                        # Preserve msgs[0] (Memory Anchor), the summary, and the last 3 messages (current task context)
                        msgs = [msgs[0], summary_msg] + msgs[-3:]
                        logger.info("Session history compressed successfully.")
                    except Exception as e:
                        logger.warning(f"Session history compression failed: {e}")

            # Append only incremental scratchpad — no repeated context
            _raw_step = f"[Step {step}/{max_steps}] Scratchpad:\n{chr(10).join(scratchpad[-3:])}"
            step_prompt = MissionMemoryCarrier.wrap(
                prompt=_raw_step,
                root_goal=goal,
                completed_summaries=_mission_summaries,
                constraints=[]
            )
            _tf_should, _tf_tool = ToolFirstReflex.check(step_prompt or goal)
            if _tf_should and _tf_tool and _tf_tool in self.tools:
                logger.info(f"tool_first_reflex: suggesting tool={_tf_tool} before generation")
                _suggested_cmd = ToolFirstReflex.suggest_command(step_prompt or goal)
                _hint = f"[TOOL-FIRST HINT: use TOOL:{_tf_tool}" + (f" INPUT:{_suggested_cmd}" if _suggested_cmd else "") + "]\n"
                step_prompt = _hint + step_prompt

            # PROMPT 22 — PINNED_CONTEXT prepended to step_prompt
            pinned_data = {
                "current_task": goal,
                "file_cache_keys": list(self._file_cache.keys()) if hasattr(self, "_file_cache") else [],
                "last_3_tool_results": scratchpad[-3:] if scratchpad else [],
                "active_errors": anchor_text[:300] if anchor_text else "",
            }
            pinned_context_str = f"[PINNED_CONTEXT]\n{json.dumps(pinned_data, ensure_ascii=False)}\n\n"
            step_prompt = pinned_context_str + (step_prompt or "")

            msgs.append({"role": "user", "content": step_prompt})
            if anchor_text and len(msgs) == 2:
                msgs.insert(0, {"role": "system", "content": f"[MEMORY ANCHOR]\n{anchor_text.strip()}"})

            plan = self.dispatcher.dispatch(goal, context=str(msgs), force_tier="LOCALFAST" if force_local else None)
            response = await plan.execute()

            if not response or not isinstance(response, str):
                scratchpad.append(f"[Step {step}] Empty or invalid response.")
                continue

            self._log_to_hud(step, "observe", response[:120])
            scratchpad.append(f"[Step {step}] {response[:300]}")
            msgs.append({"role": "assistant", "content": response})

            # Tool execution
            tool_match = re.search(r'TOOL:\s*(\w+)\s+INPUT:\s*(\{.*?\}|\[.*?\]|".*?"|\S+)', response, re.DOTALL)
            if tool_match:
                tool_name = tool_match.group(1).strip()
                tool_input_raw = tool_match.group(2).strip()

                cb_result = self.circuit_breaker.check(estimated_cost=0.01)
                if cb_result != "ALLOW":
                    scratchpad.append(f"[Step {step}] Circuit breaker: {cb_result}")
                    break

                if tool_name in self.tools:
                    try:
                        parsed_input = parse_tool_call(tool_input_raw)
                        if parsed_input is None:
                            parsed_input = tool_input_raw
                        tool_fn = self.tools[tool_name]
                        if asyncio.iscoroutinefunction(tool_fn):
                            tool_result = await tool_fn(parsed_input)
                        else:
                            tool_result = tool_fn(parsed_input)
                        self.circuit_breaker.record_success()
                        result_str = str(tool_result)[:500]
                        self._log_to_hud(step, "act", f"Tool={tool_name}", file=str(parsed_input)[:80], status="ok")
                        scratchpad.append(f"[Tool:{tool_name}] {result_str}")
                        msgs.append({"role": "user", "content": f"[TOOL_RESULT:{tool_name}]\n{result_str}"})
                    except Exception as e:
                        self.circuit_breaker.record_failure()
                        err_str = f"Tool {tool_name} error: {e}"
                        self._log_to_hud(step, "act", err_str, status="error")
                        scratchpad.append(err_str)
                        msgs.append({"role": "user", "content": f"[TOOL_ERROR:{tool_name}]\n{err_str}"})
                else:
                    scratchpad.append(f"[Step {step}] Unknown tool: {tool_name}")

            # Terminal signal
            if "FINAL_ANSWER:" in response or response.strip().startswith("FINAL_ANSWER:"):
                final = re.sub(r".*?FINAL_ANSWER:\s*", "", response, flags=re.DOTALL).strip()
                self._log_to_hud(step, "final", final[:120])
                result = await self._self_check(goal, final, task, force_local=force_local)
                _mission_summaries.append(f"Step {step}: Completed — {final[:100]}")
                return result

        # Fallback: synthesize from scratchpad
        if scratchpad:
            synthesis_prompt = (
                f"Original goal: {goal}\n\n"
                f"Steps taken:\n" + "\n".join(scratchpad[-5:]) +
                "\n\nSynthesize the best final answer from the above steps."
            )
            try:
                synth_plan = self.dispatcher.dispatch(synthesis_prompt, force_tier="LOCALFAST" if force_local else None)
                final_synthesis = await synth_plan.execute()
                result = await self._self_check(goal, final_synthesis, task, force_local=force_local)
                return result
            except Exception as e:
                logger.warning(f"synthesis_failed: {e}")

        return msgs[-1]["content"] if msgs and msgs[-1].get("role") == "assistant" else "Agent loop completed without a final answer."
