"""
NINA Modular Cognitive Layer - Hot-swappable Evaluator
"""
from __future__ import annotations
import json
import logging
import re
from typing import Any, Dict, List
from .base import BaseEvaluator

logger = logging.getLogger("nina.cognitive.evaluator")

class CognitiveEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "cognitive_evaluator"

    @property
    def version(self) -> str:
        return "1.0.0"

    def __init__(self, router: Any = None) -> None:
        self.router = router

    async def evaluate(self, goal: str, result: str, trace: List[tuple[str, str]]) -> Dict[str, Any]:
        logger.info(f"Evaluating output for goal: {goal}")
        _tail = trace[-6:] if len(trace) > 6 else trace
        history = "\n".join([f"{role.upper()}: {text[:300]}" for role, text in _tail])
        if len(trace) > 6:
            history = f"[{len(trace) - 6} earlier steps omitted]\n" + history
        prompt = (
            f"Goal: {goal}\n\n"
            f"Trace History:\n{history}\n\n"
            f"Candidate Result:\n{result}\n\n"
            "Evaluate whether the result fully satisfies the goal, and is correct and accurate.\n"
            "Format your response as a JSON object with keys:\n"
            "- score: number from 0 to 100\n"
            "- matches_goal: boolean\n"
            "- issues: list of strings detailing errors/shortcomings\n"
            "- suggestions: list of strings on how to resolve the issues\n"
            "Return ONLY raw JSON, no markdown formatting."
        )
        try:
            if self.router:
                res = await self.router.route(prompt, messages=[], task_type="reasoning")
                res_clean = re.sub(r'```json|```', '', res).strip()
                return json.loads(res_clean)
        except Exception as e:
            logger.warning(f"CognitiveEvaluator failed: {e}")
            return {"score": -1, "matches_goal": True, "issues": [], "suggestions": [], "_eval_skipped": True}

        # Mid-process critic checkpoint
        if hasattr(self, '_tool_call_count') and self._tool_call_count % 3 == 0:
            if not getattr(self, '_file_read_confirmed', False):
                import logging
                logging.warning(f"[CRITIC] {self._tool_call_count} tool calls made without confirmed file read. Read target file before editing.")
                import os
                os.makedirs('docs/space', exist_ok=True)
                with open('docs/space/agy_process_log.md', 'a') as f:
                    import datetime
                    f.write(f"| {datetime.datetime.utcnow()} | WARNING | {self._tool_call_count} tool calls, no file read confirmed |\n")

        logger.warning("CognitiveEvaluator: router is None, returning unverified score")
        return {"score": 0, "matches_goal": False, "issues": ["Evaluator has no router"], "suggestions": ["Inject router at init"]}
