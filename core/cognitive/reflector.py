"""
NINA Modular Cognitive Layer - Hot-swappable Reflector
"""
from __future__ import annotations
import logging
from typing import Any, List
from .base import BaseReflector

logger = logging.getLogger("nina.cognitive.reflector")

class CognitiveReflector(BaseReflector):
    @property
    def name(self) -> str:
        return "cognitive_reflector"

    @property
    def version(self) -> str:
        return "1.0.0"

    def __init__(self, router: Any = None) -> None:
        self.router = router

    async def reflect(self, goal: str, execution_trace: List[tuple[str, str]]) -> str:
        logger.info(f"Generating modular reflection for: {goal}")
        _recent_trace = execution_trace[-6:]  # reflector only needs last 3 act/observe pairs
        trace_text = "\n".join([f"{role.upper()}: {text[:250]}" for role, text in _recent_trace])
        prompt = (
            "Review the execution history for the goal below.\n"
            "Check: (1) Is the agent going in circles? (2) Did any tool return an error? "
            "(3) Is the approach fundamentally wrong?\n"
            "Respond ONLY as JSON: {\"should_revise\": true/false, \"reason\": \"one sentence\"}\n"
            f"Goal: {goal}\n\nHistory:\n{trace_text}"
        )
        try:
            if self.router:
                res = await self.router.route(prompt, messages=[], task_type="reasoning")
                import json as _json, re as _re
                raw = (res or "").strip()
                _clean = _re.sub(r'```json|```', '', raw).strip()
                _parsed = _json.loads(_clean)
                if "should_revise" not in _parsed:
                    raise ValueError("missing should_revise key")
                return _json.dumps(_parsed)
        except Exception as e:
            logger.warning(f"CognitiveReflector failed or returned invalid JSON: {e}")
            
        return '{"should_revise": false, "reason": "Reflector unavailable, failed or returned non-JSON."}'
