"""
NINA agent namespace — canonical home for all agent modules.

All agent sub-packages live under agents/:
  agents/agy/        — Agy orchestration agent
  agents/gemini/     — Gemini CLI agent bridge
  agents/jules/      — Jules task-execution agent
  agents/ninamcp/    — Nina MCP server agent
  agents/opencode/   — OpenCode agent
  agents/perplexity/ — Perplexity research agent

The legacy agent/ directory has been removed (MEGA-09).
DO NOT create or import from agent/ (singular). Use agents/ (plural) exclusively.

Import convention:
    from agents.jules import ...    ✓
    from agents.gemini import ...   ✓
    from agent import ...           ✗  (old namespace — deleted)
"""
# Public surface — import the top-level router if it exists,
# otherwise this init is a clean namespace marker.
try:
    from agents.router import route_message  # noqa: F401
except ImportError:
    # router not yet implemented — namespace is still usable
    pass

from agents.base import AgentMessage, BaseAgent
from agents.planner import PlannerAgent
from agents.reasoner import ReasonerAgent
from agents.executor import ExecutorAgent
from agents.critic import CriticAgent
from agents.archivist import ArchivistAgent
from agents.orchestrator import AgentOrchestrator

__all__ = [
    "route_message",
    "AgentMessage", "BaseAgent",
    "PlannerAgent", "ReasonerAgent", "ExecutorAgent",
    "CriticAgent", "ArchivistAgent", "AgentOrchestrator"
]
