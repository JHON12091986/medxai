#!/usr/bin/env python3
"""
NinaMCP — stdio MCP server for OpenCode / Cursor / Claude Desktop.

Exposes 4 tools that wrap NINA internals with graceful import guards.
Run via:  python -m ninamcp.server
         (from ~/nina/ with venv active)
"""
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Scrub REPO_ROOT and cwd from sys.path BEFORE importing fastmcp.
# nina/mcp/ shadows the real mcp SDK when ~/nina is in sys.path.
_repo_str = str(REPO_ROOT)
sys.path = [p for p in sys.path if p not in (_repo_str, "", ".")]
sys.path.append(_repo_str)  # append — never prepend

# fastmcp 3.x: top-level `fastmcp` package
try:
    from fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "[ninamcp.server] fastmcp not installed.\nRun: pip install fastmcp-slim[server]",
            file=sys.stderr,
        )
        sys.exit(1)

mcp_server = FastMCP("nina")

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
@mcp_server.tool()
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
@mcp_server.tool()
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
@mcp_server.tool()
async def nina_goals_list(state: str = "active") -> list:
    """
    List NINA goals filtered by state.
    state: 'active' | 'paused' | 'blocked' | 'completed' | 'failed' | 'all'
    """
    if not _GOALS_OK:
        return [{"error": "goal_manager not available"}]
    try:
        goals = _goal_manager.list_goals() if state == "all" else _goal_manager.list_goals(state=state)
        return goals if goals else [{"info": f"No goals with state='{state}'"}]
    except Exception as e:
        return [{"error": str(e)}]


# ---------------------------------------------------------------------------
# Tool 4 — nina_memory_search
# ---------------------------------------------------------------------------
@mcp_server.tool()
async def nina_memory_search(query: str, top_k: int = 5) -> list:
    """
    Search NINA's knowledge graph / memory for context relevant to query.
    Falls back to grepping data/reflections.jsonl if KG not wired.
    """
    if not _MEMORY_OK:
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
    mcp_server.run(transport="stdio")
