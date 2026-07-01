"""
NINA A2A Specialist Multi-Agent Mesh (LT-2)
Implements protocol-based inter-agent negotiations and message passing.
"""
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("nina.agents.mesh")

@dataclass
class A2AMessage:
    sender: str
    recipient: str
    subject: str
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None


class BaseAgent:
    def __init__(self, name: str, mesh: 'AgentMesh') -> None:
        self.name = name
        self.mesh = mesh
        self.mesh.register_agent(self)

    async def receive_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Process incoming A2A message."""
        logger.info(f"[{self.name}] received message from [{message.sender}] regarding '{message.subject}'")
        return await self._handle_message(message)

    async def _handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        raise NotImplementedError


class AgentMesh:
    def __init__(self) -> None:
        self.agents: Dict[str, BaseAgent] = {}
        self.message_history: List[A2AMessage] = []

    def register_agent(self, agent: BaseAgent) -> None:
        self.agents[agent.name] = agent
        logger.info(f"Agent [{agent.name}] registered to the mesh.")

    async def send_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        self.message_history.append(message)
        if message.recipient not in self.agents:
            logger.warning(f"Recipient agent [{message.recipient}] not found in mesh.")
            return None
        
        recipient_agent = self.agents[message.recipient]
        try:
            return await recipient_agent.receive_message(message)
        except Exception as e:
            logger.error(f"Error handling message from [{message.sender}] to [{message.recipient}]: {e}")
            return None

# Global shared agent mesh
agent_mesh = AgentMesh()
