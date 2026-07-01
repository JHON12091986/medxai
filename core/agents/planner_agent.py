"""
NINA Specialist Multi-Agent Mesh - Planner Agent (LT-2)
Decomposes user queries and negotiates task execution with other subagents.
"""
from __future__ import annotations
import logging
from typing import Optional
from .mesh import BaseAgent, A2AMessage, AgentMesh

logger = logging.getLogger("nina.agents.planner")

class PlannerAgent(BaseAgent):
    def __init__(self, mesh: AgentMesh) -> None:
        super().__init__("PlannerAgent", mesh)

    async def _handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        if "plan" in message.subject.lower() or "execute" in message.subject.lower():
            logger.info("PlannerAgent planning execution task...")
            # Automatically negotiate with Research or Coding agents based on keywords
            recipient = "CodingAgent" if "code" in message.content.lower() or "write" in message.content.lower() else "ResearchAgent"
            
            negotiation_msg = A2AMessage(
                sender=self.name,
                recipient=recipient,
                subject="Requesting Task Execution",
                content=f"Please execute task: {message.content}",
                context=message.context
            )
            
            reply = await self.mesh.send_message(negotiation_msg)
            if reply:
                return A2AMessage(
                    sender=self.name,
                    recipient=message.sender,
                    subject="Plan Execution Completed",
                    content=f"Subagent execution complete. Result: {reply.content}",
                    context=reply.context
                )
        return A2AMessage(
            sender=self.name,
            recipient=message.sender,
            subject="Re: " + message.subject,
            content="PlannerAgent stands ready.",
            context=message.context
        )
