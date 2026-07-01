"""
NINA CrewAI-style Role-Based Agent Crew & Shared Memory Buffer Pattern
Enables declarative teams of specialized agents with shared context and memory pools.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class CrewAgent:
    name: str
    role: str
    goal: str
    backstory: str

@dataclass
class CrewTask:
    description: str
    expected_output: str
    assigned_agent: str
    output: Optional[str] = None
    completed: bool = False

class Crew:
    def __init__(self, agents: List[CrewAgent], tasks: List[CrewTask]) -> None:
        self.agents = {agent.name: agent for agent in agents}
        self.tasks = tasks
        self.shared_memory: Dict[str, Any] = {}

    def set_shared_memory(self, key: str, value: Any) -> None:
        """
        Sets a key-value pair inside the shared memory buffer.
        """
        self.shared_memory[key] = value

    def get_shared_memory(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a value from the shared memory buffer.
        """
        return self.shared_memory.get(key, default)

    def execute_sequential(self, task_executor: Any) -> List[CrewTask]:
        """
        Executes crew tasks sequentially, automatically feeding context through the 
        shared memory buffer.
        """
        for task in self.tasks:
            agent = self.agents.get(task.assigned_agent)
            if not agent:
                raise ValueError(f"Task assigned to unknown agent: {task.assigned_agent}")

            # Context injection: inject shared memory keys
            context_string = "\n".join(f"{k}: {v}" for k, v in self.shared_memory.items())
            full_prompt = f"Role: {agent.role}\nGoal: {agent.goal}\nContext:\n{context_string}\nTask:\n{task.description}"
            
            # Execute
            result = task_executor(full_prompt)
            task.output = result
            task.completed = True
            
            # Save to shared memory for downstream tasks
            self.set_shared_memory("last_task_output", result)
            self.set_shared_memory(f"task_{self.tasks.index(task)}_result", result)
            
        return self.tasks
