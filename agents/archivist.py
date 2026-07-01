from agents.base import AgentMessage, BaseAgent

class ArchivistAgent(BaseAgent):
    async def process(self, msg: AgentMessage) -> AgentMessage:
        # In a real implementation this would read from memory/
        # For now, just pass the message along with a placeholder or no context

        # We could inject context into the messages here.
        # Right now we just act as a pass-through to planner.

        return AgentMessage(
            sender="archivist",
            recipient="planner",
            intent="plan",
            payload=msg.payload,
            confidence=1.0,
            inference_cost=0
        )
