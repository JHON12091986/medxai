"""
NINA Modular Cognitive Layer - Hot-swappable Planner
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict, List
from .base import BasePlanner

logger = logging.getLogger("nina.cognitive.planner")

class CognitivePlanner(BasePlanner):
    @property
    def name(self) -> str:
        return "cognitive_planner"

    @property
    def version(self) -> str:
        return "1.0.0"

    def __init__(self, router: Any = None) -> None:
        self.router = router

    async def generate_plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        logger.info(f"Generating plan for: {goal}")
        _ctx_safe = {k: (v[:300] if isinstance(v, str) else v) for k, v in context.items()
                     if k in ("task_type", "user", "pre_flight_summary", "intent", "session_id", "context_str")}
        prompt = (
            f"Goal: {goal}\n"
            f"Context: {json.dumps(_ctx_safe)}\n\n"
            "Decompose this goal into small, sequential, evidence-based tasks.\n"
            "RULES:\n"
            "1. If the goal is diagnostic (why/broken/deleted/missing): FIRST task must be 'read source file or run git log', SECOND task must be 'check nina_error_register.md'. Never theorize before reading evidence.\n"
            "2. If the goal is coding: FIRST task must be 'read target file fully'.\n"
            "3. Never create a task called 'Understand the problem' or 'Propose solution' without a preceding read/observe task.\n"
            "Respond with a raw JSON list of tasks, where each task has keys: 'id', 'label', 'description', 'dependencies' (list of IDs).\n"
            "Respond ONLY with raw valid JSON."
        )
        try:
            if self.router:
                res = await self.router.route(prompt, messages=[], task_type="reasoning")
                import re
                res_clean = re.sub(r'```json|```', '', res).strip()
                return json.loads(res_clean)
        except json.JSONDecodeError as e:
            logger.warning(f"CognitivePlanner JSON parse failed: {e} | raw: {res_clean[:200] if 'res_clean' in locals() else ''}")
        except Exception as e:
            logger.warning(f"CognitivePlanner router failed: {e}")
            
        logger.warning("CognitivePlanner: falling back to single-task plan")
        _goal_lower = goal.lower()
        _is_diagnostic = any(k in _goal_lower for k in ("why", "deleted", "missing", "broken", "disappeared", "not found", "error"))
        if _is_diagnostic:
            return [
                {"id": "t1", "label": "Read source", "description": "Run git log --all --full-history or cat on the suspected file BEFORE any hypothesis.", "dependencies": [], "_fallback": True},
                {"id": "t2", "label": "Check error register", "description": "cat docs/space/nina_error_register.md and look for matching OPEN rows.", "dependencies": ["t1"], "_fallback": True},
            ]
        return [{"id": "t1", "label": "Execute goal", "description": goal, "dependencies": [], "_fallback": True}]
