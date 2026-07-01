#!/usr/bin/env python3
"""
NinaMCP — stdio MCP server for OpenCode / Cursor / Claude Desktop.

Exposes 4 tools that wrap NINA internals with graceful import guards.
Run via:  python -m mcp.nina_mcp_server
         (from ~/nina/ with venv active)

Port: stdio (no TCP port — OpenCode spawns this as a subprocess)
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Ensure repo root is on path when invoked as `python -m mcp.nina_mcp_server`
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print(
        "[nina_mcp_server] fastmcp not installed.\n"
        "Run: pip install fastmcp",
        file=sys.stderr,
    )
    sys.exit(1)

mcp = FastMCP("nina")

# ---------------------------------------------------------------------------
# Optional imports — graceful degradation if modules not yet wired
# ---------------------------------------------------------------------------
try:
    from core.goal_manager import goal_manager as _goal_manager
    _GOALS_OK = True
except Exception:
    _GOALS_OK = False

try:
    from core.knowledge_graph import KnowledgeGraph as _KG
    _kg = _KG()
    _MEMORY_OK = True
except Exception:
    _MEMORY_OK = False


# ---------------------------------------------------------------------------
# Tool 1 — nina_ask
# ---------------------------------------------------------------------------
@mcp.tool()
async def nina_ask(goal: str) -> str:
    """
    Send a goal/task to NINA's agent loop and return the response.
    Use this to delegate coding tasks, research, or system actions to NINA.
    """
    try:
        from core.agent import AgentLoop
        loop = AgentLoop()
        result = await loop.run(goal)
        return result if isinstance(result, str) else json.dumps(result)
    except Exception as e:
        return f"[nina_ask error] {e}"


# ---------------------------------------------------------------------------
# Tool 2 — nina_status
# ---------------------------------------------------------------------------
@mcp.tool()
async def nina_status() -> dict:
    """
    Returns NINA system health: NinaGate provider states, Ollama health,
    goal_manager status, and uptime. Safe to call at any time.
    """
    import httpx
    status: dict = {
        "ts": time.time(),
        "ninagate": "unknown",
        "ollama": "unknown",
        "goals_module": _GOALS_OK,
        "memory_module": _MEMORY_OK,
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get("http://localhost:8080/health")
            if r.status_code == 200:
                data = r.json()
                status["ninagate"] = "ok"
                status["ollama"] = "ok" if data.get("local_ollama") else "unavailable"
            else:
                status["ninagate"] = f"http_{r.status_code}"
    except Exception as e:
        status["ninagate"] = f"unreachable: {e}"

    if _GOALS_OK:
        try:
            active = _goal_manager.list_goals(state="active")
            status["active_goals"] = len(active)
        except Exception:
            status["active_goals"] = "error"

    return status


# ---------------------------------------------------------------------------
# Tool 3 — nina_goals_list
# ---------------------------------------------------------------------------
@mcp.tool()
async def nina_goals_list(state: str = "active") -> list:
    """
    List NINA goals filtered by state.
    state: 'active' | 'paused' | 'blocked' | 'completed' | 'failed' | 'all'
    Returns a list of goal dicts with id, title, priority, state, dependencies.
    """
    if not _GOALS_OK:
        return [{"error": "goal_manager not available — run: nina goals install"}]
    try:
        if state == "all":
            goals = _goal_manager.list_goals()
        else:
            goals = _goal_manager.list_goals(state=state)
        return goals if goals else [{"info": f"No goals with state='{state}'"}]
    except Exception as e:
        return [{"error": str(e)}]


# ---------------------------------------------------------------------------
# Tool 4 — nina_memory_search
# ---------------------------------------------------------------------------
@mcp.tool()
async def nina_memory_search(query: str, top_k: int = 5) -> list:
    """
    Search NINA's knowledge graph / memory store for context relevant to query.
    Returns top_k matching entries with content and metadata.
    Use before writing code to retrieve prior decisions, patterns, or notes.
    """
    if not _MEMORY_OK:
        # Fallback: grep logs/reflections for the query string
        results = []
        reflections_path = REPO_ROOT / "data" / "reflections.jsonl"
        if reflections_path.exists():
            try:
                with open(reflections_path) as f:
                    for line in f:
                        if query.lower() in line.lower():
                            try:
                                results.append(json.loads(line))
                            except Exception:
                                results.append({"raw": line.strip()})
                            if len(results) >= top_k:
                                break
            except Exception:
                pass
        return results or [{"info": "knowledge_graph not available, no reflections matched"}]
    try:
        results = _kg.query(query, top_k=top_k)
        return results if results else [{"info": "No matches found"}]
    except Exception as e:
        return [{"error": str(e)}]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
