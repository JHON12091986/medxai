from agents.base import AgentMessage, BaseAgent
from core.task_classifier import classify_task

class PlannerAgent(BaseAgent):
    async def process(self, msg: AgentMessage) -> AgentMessage:
        task_str = msg.payload.get("goal", "")
        history = msg.payload.get("messages", [])

        classified = classify_task(task_str, history)

        # Decide who to route to based on task type and complexity
        if classified.task_type in ["coding", "research", "diagnostic"]:
            recipient = "reasoner"
            intent = "plan"
        else:
            recipient = "executor"
            intent = "execute"

        return AgentMessage(
            sender="planner",
            recipient=recipient,
            intent=intent,
            payload={
                "goal": task_str,
                "messages": history,
                "task_type": classified.task_type,
                "complexity": classified.complexity,
                "recommended_tier": classified.recommended_tier,
                "estimated_tokens": classified.estimated_tokens
            },
            confidence=1.0,
            inference_cost=0
        )
