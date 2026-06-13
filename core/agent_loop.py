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
    pre_flight_summary: Optional[str] = None
    scaffold_code: Optional[str] = None

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
    def __init__(self, router: Any, tools: list[str]) -> None:
        self.router = router
        self.tools = tools
        self.logger = logging.getLogger("nina.agent")

    async def run(self, input: str, context: dict = None) -> ActResult:
        if context is None:
            context = {}

        import asyncio

        async def scout_task() -> str:
            # Run blocking file operations in a thread pool
            def _scout() -> Any:
                try:
                    import glob
                    files = glob.glob("**/*.py", recursive=True)[:3]
                    summary = []
                    for f in files:
                        with open(f, "r") as file_obj:
                            summary.append(f"File {f}: {len(file_obj.read())} bytes")
                    return "Pre-Flight Summary:\n" + "\n".join(summary)
                except Exception as e:
                    return f"Pre-Flight Summary failed: {e}"
            return await asyncio.to_thread(_scout)

        async def scaffold_task() -> str:
            # Start local tool scaffolding (imports, docstrings)
            def _scaffold() -> Any:
                return 'import os\nimport sys\n\n"""\nAuto-generated scaffolding.\n"""\n'
            return await asyncio.to_thread(_scaffold)

        async def cloud_task(scout_future: Any) -> ActResult:
            # We must wait for the scout to provide the summary to the agent
            pre_flight_summary = await scout_future

            # Inject the pre_flight_summary into the context
            local_context = context.copy()
            local_context["pre_flight_summary"] = pre_flight_summary

            def _cloud() -> Any:
                t_res = think(input, local_context)
                self.logger.debug(f"THINK: {t_res}")
                p_res = plan(t_res, self.tools)
                self.logger.debug(f"PLAN: {p_res}")
                a_res = act(p_res, local_context)
                self.logger.debug(f"ACT: {a_res}")
                return a_res
            return await asyncio.to_thread(_cloud)

        scout_future = asyncio.create_task(scout_task())
        scaffold_future = asyncio.create_task(scaffold_task())
        cloud_future = asyncio.create_task(cloud_task(scout_future))

        results = await asyncio.gather(cloud_future, scaffold_future)

        a_res = results[0]
        a_res.pre_flight_summary = scout_future.result()
        a_res.scaffold_code = results[1]
        return a_res
