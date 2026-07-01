from agents.base import AgentMessage, BaseAgent
from core.router import HybridRouter
from core.task_classifier import ClassifiedTask

class ExecutorAgent(BaseAgent):
    def __init__(self, router: HybridRouter):
        self.router = router

    async def process(self, msg: AgentMessage) -> AgentMessage:
        goal = msg.payload.get("goal", "")
        plan = msg.payload.get("plan", None)
        messages = msg.payload.get("messages", [])

        if plan:
           goal_with_plan = f"Goal: {goal}\nPlan:\n{plan}"
        else:
           goal_with_plan = goal

        task = ClassifiedTask(
            task_type=msg.payload.get("task_type", "quick"),
            complexity=msg.payload.get("complexity", "SIMPLE"),
            recommended_tier=msg.payload.get("recommended_tier", "FAST")
        )

        try:
            content = await self.router.route(goal_with_plan, messages, task=task)
            confidence = 0.9
        except Exception as e:
            content = f"Failed to execute: {str(e)}"
            confidence = 0.0

        return AgentMessage(
            sender="executor",
            recipient="critic",
            intent="review",
            payload={
                "goal": goal,
                "messages": messages,
                "content": content,
                "task_type": task.task_type
            },
            confidence=confidence,
            inference_cost=0
        )
