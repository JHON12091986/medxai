"""
NINA ReAct Reasoning Engine (SI-1 / CORE-002)
Features a structured thinking/critique loop: Think -> Act -> Observe -> Critique.
Decoupled into hot-swappable cognitive modules (LT-1).
"""
from __future__ import annotations
import logging
import json
import re
from typing import Any, Dict, List
from dataclasses import dataclass

from .cognitive import (
    registry, CognitivePlanner, CognitiveReflector,
    CognitiveEvaluator, CognitiveVerifier
)

logger = logging.getLogger("nina.core.reasoning_engine")

@dataclass
class Action:
    type: str  # "TOOL" or "FINAL_ANSWER"
    name: str  # Tool name (e.g. "read_file") or empty
    content: str  # Action arguments or final answer text

@dataclass
class ReasoningResult:
    answer: str
    trace: List[tuple[str, str]]

class ReasoningEngine:
    def __init__(self, dispatcher: Any = None, router: Any = None) -> None:
        self.dispatcher = dispatcher
        self.router = router
        
        # Initialize default cognitive modules (LT-1)
        self.planner = CognitivePlanner(router=self.router)
        self.reflector = CognitiveReflector(router=self.router)
        self.evaluator = CognitiveEvaluator(router=self.router)
        self.verifier = CognitiveVerifier(router=self.router)
        self._current_task_type: str = "quick"
        self._current_tier: str = "LOCALFAST"
        
        # Register standard cognitive modules
        if not registry.has("cognitive_planner"):
            registry.register(self.planner)
        if not registry.has("cognitive_reflector"):
            registry.register(self.reflector)
        if not registry.has("cognitive_evaluator"):
            registry.register(self.evaluator)
        if not registry.has("cognitive_verifier"):
            registry.register(self.verifier)

    def hot_swap_module(self, module_name: str, module_instance: Any) -> None:
        """Dynamically swap a cognitive module at runtime."""
        logger.info(f"Hot-swapping cognitive module '{module_name}'")
        if hasattr(module_instance, "name") and module_instance.name != module_name:
            raise ValueError(
                f"hot_swap_module name mismatch: caller said '{module_name}' "
                f"but module.name is '{module_instance.name}'"
            )
        registry.register(module_instance)
        if module_name == "cognitive_planner":
            self.planner = module_instance
        elif module_name == "cognitive_reflector":
            self.reflector = module_instance
        elif module_name == "cognitive_evaluator":
            self.evaluator = module_instance
        elif module_name == "cognitive_verifier":
            self.verifier = module_instance

    async def reason(self, goal: str, context_str: str = "", max_steps: int = 5) -> ReasoningResult:
        scratchpad: List[tuple[str, str]] = []
        logger.info(f"ReasoningEngine initiated for goal: {goal}")
        # Inherit task tier from caller if set before reason() is called
        _think_tier = getattr(self, "_current_tier", "LOCALFAST")
        _think_task_type = getattr(self, "_current_task_type", "quick")
        
        # Generate initial high-level task decomposition plan using modular planner
        plan_context = {"context_str": context_str}
        try:
            initial_plan = await self.planner.generate_plan(goal, plan_context)
            logger.debug(f"Generated cognitive plan: {initial_plan}")
        except Exception as e:
            logger.warning(f"Modular planning failed, falling back: {e}")
            initial_plan = []
        
        for step in range(max_steps):
            # 1. THINK: generate thought + proposed action
            _use_plan = initial_plan if step < 2 else []  # drop stale plan after step 2
            # Cap context injection to 800 chars after step 0 to prevent prompt bloat
            _ctx_cap = 800 if step > 0 else 3000
            _ctx_trimmed = context_str[:_ctx_cap] + ("…[trimmed]" if len(context_str) > _ctx_cap else "")
            if _use_plan:
                _plan_text = "\n".join([f"Step {i+1}: {t.get('label','')} — {t.get('description','')}" for i, t in enumerate(_use_plan)])
                think_context = f"{_ctx_trimmed}\n\nPLAN:\n{_plan_text}"
            else:
                think_context = _ctx_trimmed
            thought, action = await self._think(goal, scratchpad, think_context, task_tier=_think_tier, task_type=_think_task_type)
            scratchpad.append(("thought", thought))
            
            if action.type == "FINAL_ANSWER":
                # Verify final answer quality using modular evaluator & verifier
                try:
                    # Skip evaluator on step 0 — no trace to evaluate yet, trust direct answer
                    if step == 0:
                        eval_res = {"score": -1, "matches_goal": True, "issues": [], "suggestions": [], "_eval_skipped": True}
                    else:
                        eval_res = await self.evaluator.evaluate(goal, action.content, scratchpad)
                    raw_score = eval_res.get("score", None)
                    if raw_score is None:
                        logger.warning("Evaluator returned no score key — skipping quality gate")
                        score = 100  # neutral: do not force loop on missing score
                    else:
                        try:
                            score = int(raw_score)
                        except (TypeError, ValueError):
                            score = 0
                    logger.info(f"Modular Evaluator score: {score}")
                    if score != -1 and score < 60:
                        logger.warning(f"Evaluator score {score} below threshold — forcing loop continuation.")
                        scratchpad.append(("thought", f"Answer quality score {score}/100 is too low. Must gather more evidence and try again."))
                        continue
                    
                    is_valid = await self.verifier.verify(
                        action.content,
                        metadata={"task_type": getattr(self, "_current_task_type", ""), "goal": goal}
                    )
                    if not is_valid:
                        logger.warning("Verifier flagged final answer as invalid — continuing loop for correction.")
                        scratchpad.append(("thought", "Answer failed verification. Must re-examine evidence and try again."))
                        continue
                except Exception as e:
                    logger.warning(f"Modular validation failed: {e}")
                
                logger.info(f"ReasoningEngine finalized at step {step}: {action.content[:50]}...")
                return ReasoningResult(answer=action.content, trace=scratchpad)
            
            # 2. ACT: execute tool
            scratchpad.append(("action", f"{action.name}: {action.content}"))
            observation = await self._act(action)
            
            # 3. OBSERVE: capture output
            scratchpad.append(("observation", observation))
            
            # 4. CRITIQUE: critic checks quality via modular reflector
            try:
                reflection_raw = await self.reflector.reflect(goal, scratchpad)
                try:
                    import json as _json, re as _re
                    ref_clean = _re.sub(r'```json|```', '', reflection_raw).strip()
                    ref_data = _json.loads(ref_clean)
                    if ref_data.get("should_revise"):
                        scratchpad.append(("revision", ref_data.get("reason", reflection_raw)))
                except Exception:
                    # Only trigger revision on unambiguous positive signals
                    _lower_ref = reflection_raw.lower()
                    _should = (
                        "should revise" in _lower_ref
                        or "must revise" in _lower_ref
                        or "needs revision" in _lower_ref
                        or ("error" in _lower_ref and "no error" not in _lower_ref)
                    )
                    if _should:
                        scratchpad.append(("revision", reflection_raw))
            except Exception as e:
                logger.warning(f"Modular reflection failed, using standard critique: {e}")
                critique = await self._critique(goal, scratchpad)
                if critique.get("should_revise"):
                    scratchpad.append(("revision", critique.get("suggestion", "")))
        
        # Find the last FINAL_ANSWER attempt in scratchpad, not the last revision
        _final_candidates = [text for role, text in scratchpad if role == "thought" and len(text) > 40]
        _obs_candidates = [text for role, text in scratchpad if role == "observation" and not text.startswith("[")]
        final_answer = (
            _obs_candidates[-1] if _obs_candidates else
            _final_candidates[-1] if _final_candidates else
            scratchpad[-1][1] if scratchpad else "No answer generated."
        )
        logger.warning(f"ReasoningEngine exhausted max_steps — returning best available: {final_answer[:60]}")
        return ReasoningResult(answer=final_answer, trace=scratchpad)

    async def _think(self, goal: str, scratchpad: List[tuple[str, str]], context_str: str, task_tier: str = "LOCALFAST", task_type: str = "quick") -> tuple[str, Action]:
        # Inject only last 6 scratchpad entries, truncated to 350 chars each
        _recent = scratchpad[-6:]
        history = "\n".join([f"{role.upper()}: {text[:350]}" for role, text in _recent])
        prompt = (
            f"Goal: {goal}\n"
            f"Context:\n{context_str}\n\n"
            f"Execution History:\n{history}\n\n"
            "Generate the next step. If you have enough information to solve the goal, formulate the final answer.\n"
            "Format your response as a JSON object with keys:\n"
            "- thought: Your internal reasoning process.\n"
            "- action_type: Either 'TOOL' or 'FINAL_ANSWER'.\n"
            "- action_name: If 'TOOL', specify the tool name (e.g., 'read_file'). Otherwise, leave empty.\n"
            "- action_content: If 'TOOL', specify the tool input/argument. If 'FINAL_ANSWER', specify the final answer text.\n"
            "Return ONLY raw JSON, no markdown formatting."
        )
        try:
            if self.dispatcher:
                plan = self.dispatcher.dispatch(prompt, force_tier=task_tier)
                res = await plan.execute()
            elif self.router:
                res = await self.router.route(prompt, messages=[], task_type=task_type)
            else:
                res = '{"thought": "Direct proceed", "action_type": "FINAL_ANSWER", "action_name": "", "action_content": "No backend available"}'
            
            res_clean = re.sub(r'```json|```', '', res).strip()
            data = json.loads(res_clean)
            thought = data.get("thought", "Proceeding to next step")
            a_type = data.get("action_type", "FINAL_ANSWER")
            a_name = data.get("action_name", "")
            a_content = data.get("action_content", "")
            return thought, Action(type=a_type, name=a_name, content=a_content)
        except Exception as e:
            logger.warning(f"ReasoningEngine _think failed: {e}")
            return f"Error during thinking phase: {e}", Action(type="FINAL_ANSWER", name="", content=f"Failed due to error: {e}")

    async def _act(self, action: Action) -> str:
        logger.info(f"Executing tool action: {action.name}")
        if not self.dispatcher:
            return f"[no dispatcher] would have called {action.name}({action.content})"
        try:
            plan = self.dispatcher.dispatch(
                action.content,
                tool_hint=action.name,
                force_tier="LOCALFAST"
            )
            result = await plan.execute()
            return str(result) if result else "[tool returned empty]"
        except Exception as e:
            logger.warning(f"_act tool execution failed: {e}")
            return f"[TOOL_FAILED:{action.name}] {e} — Do NOT treat this as evidence. Retry with a different approach or tool."

    async def _critique(self, goal: str, scratchpad: List[tuple[str, str]]) -> Dict[str, Any]:
        # Critique only needs the last action + observation (2 entries)
        _recent_critique = scratchpad[-2:]
        history = "\n".join([f"{role.upper()}: {text[:400]}" for role, text in _recent_critique])
        prompt = (
            f"Goal: {goal}\n\n"
            f"History:\n{history}\n\n"
            "Review the last action and observation. Are we in a loop, did the tool fail, or is the quality low?\n"
            "Format your response as a JSON object with keys:\n"
            "- should_revise: boolean (true if we need to adjust course)\n"
            "- suggestion: string (guidance for the next thought, if should_revise is true)\n"
            "Return ONLY raw JSON, no markdown formatting."
        )
        try:
            if self.dispatcher:
                plan = self.dispatcher.dispatch(prompt, force_tier="BALANCED")
                res = await plan.execute()
            elif self.router:
                res = await self.router.route(prompt, messages=[], task_type="quick")
            else:
                return {"should_revise": False, "suggestion": ""}
            
            res_clean = re.sub(r'```json|```', '', res).strip()
            data = json.loads(res_clean)
            return {
                "should_revise": data.get("should_revise", False),
                "suggestion": data.get("suggestion", "")
            }
        except Exception as e:
            logger.warning(f"Critique failed: {e}")
            return {"should_revise": False, "suggestion": ""}

