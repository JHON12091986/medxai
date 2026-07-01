from agents.base import AgentMessage, BaseAgent
from core.router import HybridRouter
from core.task_classifier import ClassifiedTask

class ReasonerAgent(BaseAgent):
    def __init__(self, router: HybridRouter):
        self.router = router

    async def process(self, msg: AgentMessage) -> AgentMessage:
        goal = msg.payload.get("goal", "")
        messages = msg.payload.get("messages", [])

        task = ClassifiedTask(
            task_type=msg.payload.get("task_type", "research"),
            complexity=msg.payload.get("complexity", "COMPLEX"),
            estimated_tokens=msg.payload.get("estimated_tokens", 1000),
            recommended_tier=msg.payload.get("recommended_tier", "DEEP")
        )

        try:
            plan_content = await self.router.route(goal, messages, task=task)
            confidence = 0.9 # High confidence if successful
        except Exception as e:
            plan_content = f"Failed to reason: {str(e)}"
            confidence = 0.0

        return AgentMessage(
            sender="reasoner",
            recipient="executor",
            intent="execute",
            payload={
                "goal": goal,
                "messages": messages,
                "plan": plan_content
            },
            confidence=confidence,
            inference_cost=0 # Assuming cost tracked in router
        )
