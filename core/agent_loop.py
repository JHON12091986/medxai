from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio

# New imports
from core.task_planner import TaskPlanner, MissionMemory, TaskNode, TaskType
from core.swarm_engine import SwarmEngine
from core.task_classifier import ClassifiedTask # Needed for _call_provider_wrapper

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
        # If the intent is not clear, let's treat it as a general reasoning task
        return ThinkResult(intent="reasoning", confidence=0.7, raw_input=input)
    except Exception:
        return ThinkResult(intent="unknown", confidence=0.0, raw_input=input)

def plan(think_result: ThinkResult, available_tools: list[str]) -> PlanResult:
    try:
        steps = [{"action": think_result.intent}]
    except ImportError:
        steps = [{"action": think_result.intent}]

    # If the intent is "unknown" from think, let's try to default to shell
    if think_result.intent == "unknown":
        return PlanResult(steps=[{"action": "shell"}], tool="shell", estimated_tokens=10)

    tool = "shell" # Default tool
    if think_result.intent == "search" and "web" in available_tools:
        tool = "web"
    elif think_result.intent == "execute" and "shell" in available_tools:
        tool = "shell"
    elif available_tools:
        tool = available_tools[0] # Use the first available tool if any

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

    # New method to wrap router._call_provider for SwarmEngine
    async def _call_provider_wrapper(self, provider_name: str, model_id: str, prompt: str) -> Tuple[str, int]:
        messages = [{"role": "user", "content": prompt}]
        
        # Determine a ClassifiedTask.task_type based on the model_id or a generic type.
        if "qwen" in model_id.lower():
            task_type_for_router = "lpu_deterministic" # Local models often for LPU tasks
        elif "llama" in model_id.lower():
            task_type_for_router = "coding" # Llama often used for coding
        elif "gemini" in model_id.lower():
            task_type_for_router = "reasoning" # Gemini for reasoning
        else:
            task_type_for_router = "general" # Default

        dummy_classified_task = ClassifiedTask(
            task_type=task_type_for_router,
            estimated_tokens=len(prompt) // 4, # Rough estimate
            is_read_only=False,
            is_write_only=False
        )

        content, input_tokens, output_tokens, _ = await self.router._call_provider(
            provider_name, messages, dummy_classified_task
        )
        return content, input_tokens + output_tokens


    async def run(self, input: str, context: dict = None) -> ActResult:
        if context is None:
            context = {}

        async def scout_task() -> str:
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
            def _scaffold() -> Any:
                return 'import os\nimport sys\n\n"""\nAuto-generated scaffolding.\n"""\n'
            return await asyncio.to_thread(_scaffold)

        async def cloud_task_orchestrator(scout_future: Any) -> ActResult:
            pre_flight_summary = await scout_future
            local_context = context.copy()
            local_context["pre_flight_summary"] = pre_flight_summary

            t_res = think(input, local_context)
            self.logger.debug(f"THINK: {t_res}")

            task_planner = TaskPlanner()
            mission_memory, task_nodes = task_planner.plan(input, local_context.get("pre_flight_summary", ""))
            self.logger.debug(f"TASK PLAN: Root goal='{mission_memory.root_goal[:50]}...' with {len(task_nodes)} nodes")

            if len(task_nodes) > 1 or (len(task_nodes) == 1 and task_nodes[0].task_type != TaskType.MICRO):
                swarm_engine = SwarmEngine(call_provider=self._call_provider_wrapper)
                
                results_dict = await swarm_engine.execute(task_nodes, mission_memory)
                self.logger.debug(f"SWARM RESULTS: {results_dict}")

                output_text = "\n".join(results_dict.values()) if results_dict else "No results from SwarmEngine."
                ok = bool(results_dict)
                error = None if ok else "SwarmEngine returned no results."
                total_tokens_used = sum(node.tokens_used for node in task_nodes)
                
                a_res = ActResult(
                    ok=ok, 
                    output=output_text, 
                    error=error, 
                    tokens_used=total_tokens_used,
                    pre_flight_summary=pre_flight_summary,
                    scaffold_code=await scaffold_task()
                )
            else:
                p_res = plan(t_res, self.tools)
                self.logger.debug(f"PLAN: {p_res}")
                a_res = act(p_res, local_context)
                self.logger.debug(f"ACT: {a_res}")
                
                a_res.pre_flight_summary = pre_flight_summary
                a_res.scaffold_code = await scaffold_task()

            return a_res

        scout_future = asyncio.create_task(scout_task())
        cloud_future_task = asyncio.create_task(cloud_task_orchestrator(scout_future))
        final_act_result = await cloud_future_task
        return final_act_result
