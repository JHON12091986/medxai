"""swarm/planner_intj.py — Planner node re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Provides the swarm.PlannerINTJ alias for CoordinatorAgent.
All logic lives in core/coordinator_agent.py — this is a thin shim.
"""
from core.coordinator_agent import CoordinatorAgent as PlannerINTJ

__all__ = ["PlannerINTJ"]
