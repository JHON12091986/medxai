"""swarm/worker_intm.py — Worker node re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Provides the swarm.WorkerINTM callable that wraps run_agent_turn.
All logic lives in core/agent_loop.py — this is a thin shim.
"""
from core.agent_loop import run_agent_turn as WorkerINTM  # type: ignore[import]

__all__ = ["WorkerINTM"]
