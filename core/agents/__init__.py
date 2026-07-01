"""
NINA A2A Specialist Multi-Agent Mesh
Lauches specialized subagents communicating via the A2A protocol.
"""
from __future__ import annotations
from .mesh import BaseAgent, A2AMessage, AgentMesh, agent_mesh
from .planner_agent import PlannerAgent
from .research_agent import ResearchAgent
from .coding_agent import CodingAgent
from .memory_agent import MemoryAgent

# Instantiate agent singletons on the mesh
planner_agent = PlannerAgent(agent_mesh)
research_agent = ResearchAgent(agent_mesh)
coding_agent = CodingAgent(agent_mesh)
memory_agent = MemoryAgent(agent_mesh)

__all__ = [
    "BaseAgent",
    "A2AMessage",
    "AgentMesh",
    "agent_mesh",
    "PlannerAgent",
    "ResearchAgent",
    "CodingAgent",
    "MemoryAgent",
    "planner_agent",
    "research_agent",
    "coding_agent",
    "memory_agent",
]
