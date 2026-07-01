from agents.base import AgentMessage
from agents.planner import PlannerAgent
from agents.reasoner import ReasonerAgent
from agents.executor import ExecutorAgent
from agents.critic import CriticAgent
from agents.archivist import ArchivistAgent
from core.router import HybridRouter

class AgentOrchestrator:
    def __init__(self, router: HybridRouter):
        self.router = router
        self.agents = {
            "archivist": ArchivistAgent(),
            "planner": PlannerAgent(),
            "reasoner": ReasonerAgent(router),
            "executor": ExecutorAgent(router),
            "critic": CriticAgent(router)
        }

    async def run(self, goal: str, messages: list) -> AgentMessage:
        msg = AgentMessage(
            sender="user",
            recipient="archivist",
            intent="start",
            payload={"goal": goal, "messages": messages},
            confidence=1.0,
            inference_cost=0
        )

        max_turns = 10
        turns = 0

        while msg.recipient in self.agents and turns < max_turns:
            agent = self.agents[msg.recipient]
            msg = await agent.process(msg)
            turns += 1

        return msg
