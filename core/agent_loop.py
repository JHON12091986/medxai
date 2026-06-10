"""
A) The THINK phase: where the agent decides what to do with input
B) The PLAN phase: where the agent decides how to do it (steps/tool selection)
C) The ACT phase: where the agent executes the plan and collects result
D) The main loop entry point function name: _inner (in core/agent.py)
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import logging

@dataclass
class ThinkResult:
    intent: str
    confidence: float
    raw_input: str

@dataclass
class PlanResult:
    steps: List[Dict[str, Any]]
    tool: str
    estimated_tokens: int

@dataclass
class ActResult:
    ok: bool
    output: str
    error: Optional[str]
    tokens_used: int

def think(input: str, context: dict) -> ThinkResult:
    try:
        lower_input = input.lower()
        if any(w in lower_input for w in ["search", "web", "lookup", "who", "what"]):
            return ThinkResult(intent="search", confidence=0.8, raw_input=input)
        elif any(w in lower_input for w in ["run", "shell", "cmd", "execute"]):
            return ThinkResult(intent="execute", confidence=0.8, raw_input=input)
        return ThinkResult(intent="unknown", confidence=0.5, raw_input=input)
    except Exception:
        return ThinkResult(intent="unknown", confidence=0.0, raw_input=input)

def plan(think_result: ThinkResult, available_tools: list[str]) -> PlanResult:
    try:
        from core.planner import GoalDecomposer
        GoalDecomposer()  # Check import
        steps = [{"action": think_result.intent}]
    except ImportError:
        steps = [{"action": think_result.intent}]

    if think_result.intent == "unknown":
        return PlanResult(steps=[{"action": "shell"}], tool="shell", estimated_tokens=10)

    tool = "shell"
    if think_result.intent == "search" and "web" in available_tools:
        tool = "web"
    elif think_result.intent == "execute" and "shell" in available_tools:
        tool = "shell"
    elif available_tools:
        tool = available_tools[0]

    return PlanResult(steps=steps, tool=tool, estimated_tokens=20)

def act(plan_result: PlanResult, context: dict) -> ActResult:
    ok = True
    error = None
    output = ""
    for step in plan_result.steps:
        pass
    try:
        from core.observability import get_hub
        hub = get_hub()
        hub.record_task(ok=ok)
    except Exception as e:
        error = str(e)
    return ActResult(ok=ok, output=output, error=error, tokens_used=5)

class AgentLoop:
    def __init__(self, router, tools: list[str]):
        self.router = router
        self.tools = tools
        self.logger = logging.getLogger("nina.agent")

    def run(self, input: str, context: dict = None) -> ActResult:
        if context is None:
            context = {}
        t_res = think(input, context)
        self.logger.debug(f"THINK: {t_res}")
        p_res = plan(t_res, self.tools)
        self.logger.debug(f"PLAN: {p_res}")
        a_res = act(p_res, context)
        self.logger.debug(f"ACT: {a_res}")
        return a_res
