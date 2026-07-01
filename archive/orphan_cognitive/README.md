# Orphaned Cognitive Layer

These modules were created as scaffolding but are **not imported or called** by `core/agent.py`.
The agent uses inline prompt-based Planner/Critic/Verifier/Reflector in `_self_check()` instead.

Archived on: $(date -u +"%Y-%m-%d")

## Files
- `cognitive/` — planner.py, verifier.py, evaluator.py, reflector.py (all orphaned)
- `cognition/` — reflexion.py (orphaned; live version is core/reflexion.py)

## If you want to re-integrate:
Wire via `from core.cognitive.planner import CognitivePlanner` in agent.py's `_self_check()`,
replacing the inline prompt-based planner with the class-based version.
