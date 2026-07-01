"""
NINA OpenAI Swarm-style Lightweight Agent Handoff Pattern
Allows agents to return tools and handoffs, shifting execution control dynamically.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union

@dataclass
class SwarmAgent:
    name: str
    instructions: str
    tools: List[Callable[..., Any]] = field(default_factory=list)

@dataclass
class SwarmHandoff:
    next_agent: Union[str, SwarmAgent]
    reason: str
    context_update: Dict[str, Any] = field(default_factory=dict)

class SwarmRunner:
    def __init__(self, agents: Dict[str, SwarmAgent], default_agent_name: str) -> None:
        self.agents = agents
        self.default_agent_name = default_agent_name

    def get_agent(self, agent_or_name: Union[str, SwarmAgent]) -> SwarmAgent:
        if isinstance(agent_or_name, SwarmAgent):
            return agent_or_name
        if agent_or_name in self.agents:
            return self.agents[agent_or_name]
        raise ValueError(f"Agent {agent_or_name} not found in runner agents.")

    def run_step(
        self, 
        current_agent_name: str, 
        user_message: str, 
        context: Dict[str, Any]
    ) -> Union[str, SwarmHandoff]:
        """
        Executes a single step. If a handoff is detected (either through tool returns or 
        model instruction), returns a SwarmHandoff object. Otherwise, returns the response string.
        """
        agent = self.get_agent(current_agent_name)
        
        # Simple heuristic or simulated parsing of handoff command
        if "handoff to" in user_message.lower() or "transfer to" in user_message.lower():
            for name, target_agent in self.agents.items():
                if name.lower() in user_message.lower() and name.lower() != current_agent_name.lower():
                    return SwarmHandoff(
                        next_agent=target_agent,
                        reason=f"Explicit request to transfer to {name}",
                        context_update={"previous_agent": current_agent_name}
                    )
        
        return f"Response from {agent.name}: Processed input '{user_message}' using instructions."
