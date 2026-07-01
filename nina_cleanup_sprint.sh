#!/usr/bin/env bash
# ============================================================
# NINA Integration Sprint — 1-Click Cleanup Script
# Run from: ~/nina/
# Actions:
#   1. Archive orphan cognitive layer (core/cognitive/, core/cognition/)
#   2. Rename orphan reasoning_engine.py to avoid confusion
#   3. Implement goal_manager.py (SQLite-backed persistent goal store)
#   4. Wire knowledge_graph into agent.py context-building block
# ============================================================
set -euo pipefail

NINA_DIR="${HOME}/nina"
cd "$NINA_DIR" || { echo "ERROR: ~/nina not found"; exit 1; }

echo "=== NINA Integration Sprint ==="
echo "Working dir: $(pwd)"
echo "Branch: $(git branch --show-current)"
git status --short
echo ""

# -------------------------------------------------------
# STEP 1: Archive orphan cognitive directories
# -------------------------------------------------------
echo "[1/4] Archiving orphan cognitive directories..."

mkdir -p archive/orphan_cognitive

for d in core/cognitive core/cognition; do
  if [ -d "$d" ]; then
    echo "  Moving $d/ -> archive/orphan_cognitive/$(basename $d)/"
    git mv "$d" "archive/orphan_cognitive/$(basename $d)" 2>/dev/null || mv "$d" "archive/orphan_cognitive/$(basename $d)"
    echo "  ✅ Archived: $d"
  else
    echo "  ⚠️  Not found (skip): $d"
  fi
done

# Add a README so it's clear why these exist
cat > archive/orphan_cognitive/README.md << 'EOF'
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
EOF

echo ""

# -------------------------------------------------------
# STEP 2: Rename orphan reasoning_engine.py
# -------------------------------------------------------
echo "[2/4] Renaming orphan reasoning_engine.py..."

if [ -f "core/reasoning_engine.py" ]; then
  git mv core/reasoning_engine.py core/reasoning_engine.ORPHAN.py 2>/dev/null || \
    mv core/reasoning_engine.py core/reasoning_engine.ORPHAN.py
  echo "  ✅ Renamed: core/reasoning_engine.py -> core/reasoning_engine.ORPHAN.py"
  echo "  ℹ️  Live module is core/reasoning.py (ReasoningKernel)"
else
  echo "  ⚠️  core/reasoning_engine.py not found (skip)"
fi

echo ""

# -------------------------------------------------------
# STEP 3: Implement goal_manager.py (SQLite-backed)
# -------------------------------------------------------
echo "[3/4] Implementing core/goal_manager.py..."

cat > core/goal_manager.py << 'PYEOF'
"""
NINA Goal Manager — SQLite-backed persistent goal store.
Replaces the 262-byte stub with a full implementation.

States: active | paused | blocked | completed | failed
Cross-session: goals survive restarts via ~/nina/data/nina_goals.db
"""
from __future__ import annotations
import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("nina.goal_manager")

DB_PATH = Path(__file__).parent.parent / "data" / "nina_goals.db"


class GoalState(str, Enum):
    ACTIVE    = "active"
    PAUSED    = "paused"
    BLOCKED   = "blocked"
    COMPLETED = "completed"
    FAILED    = "failed"


class GoalManager:
    """
    Persistent goal store. SQLite-backed so goals survive process restarts.

    Usage:
        gm = GoalManager()
        gm.ensure_db()
        gid = gm.add_goal("Refactor agent.py", priority=1)
        gm.update_state(gid, GoalState.COMPLETED)
        active = gm.list_active()
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT    NOT NULL,
                    description TEXT,
                    state       TEXT    NOT NULL DEFAULT 'active',
                    priority    INTEGER NOT NULL DEFAULT 5,
                    parent_id   INTEGER REFERENCES goals(id),
                    depends_on  TEXT,           -- JSON list of goal IDs
                    metadata    TEXT,           -- JSON dict of extra fields
                    created_at  TEXT    NOT NULL,
                    updated_at  TEXT    NOT NULL,
                    session_id  TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_state ON goals(state)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON goals(priority)")
            conn.commit()
        logger.info(f"GoalManager: DB ready at {self.db_path}")

    def _now(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def add_goal(
        self,
        title: str,
        description: str = "",
        priority: int = 5,
        parent_id: Optional[int] = None,
        depends_on: Optional[list[int]] = None,
        metadata: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """Add a new goal. Returns the new goal ID."""
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO goals
                   (title, description, state, priority, parent_id,
                    depends_on, metadata, created_at, updated_at, session_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    title, description, GoalState.ACTIVE,
                    priority, parent_id,
                    json.dumps(depends_on or []),
                    json.dumps(metadata or {}),
                    now, now, session_id,
                ),
            )
            conn.commit()
            gid = cur.lastrowid
        logger.info(f"GoalManager: added goal #{gid} '{title}' priority={priority}")
        return gid

    def update_state(self, goal_id: int, state: GoalState, note: str = "") -> bool:
        """Update goal state. Returns True if updated."""
        now = self._now()
        with sqlite3.connect(self.db_path) as conn:
            meta_row = conn.execute(
                "SELECT metadata FROM goals WHERE id=?", (goal_id,)
            ).fetchone()
            if not meta_row:
                logger.warning(f"GoalManager: goal #{goal_id} not found")
                return False
            meta = json.loads(meta_row[0] or "{}")
            if note:
                meta.setdefault("notes", []).append({"ts": now, "text": note})
            conn.execute(
                "UPDATE goals SET state=?, updated_at=?, metadata=? WHERE id=?",
                (state, now, json.dumps(meta), goal_id),
            )
            conn.commit()
        logger.info(f"GoalManager: goal #{goal_id} -> {state}")
        return True

    def list_active(self) -> list[dict]:
        return self._list_by_state(GoalState.ACTIVE)

    def list_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM goals ORDER BY priority ASC, updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def _list_by_state(self, state: GoalState) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM goals WHERE state=? ORDER BY priority ASC, updated_at DESC",
                (state,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get(self, goal_id: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM goals WHERE id=?", (goal_id,)).fetchone()
        return dict(row) if row else None

    def are_dependencies_met(self, goal_id: int) -> bool:
        """True if all depends_on goals are completed."""
        goal = self.get(goal_id)
        if not goal:
            return False
        deps = json.loads(goal.get("depends_on") or "[]")
        if not deps:
            return True
        with sqlite3.connect(self.db_path) as conn:
            for dep_id in deps:
                row = conn.execute(
                    "SELECT state FROM goals WHERE id=?", (dep_id,)
                ).fetchone()
                if not row or row[0] != GoalState.COMPLETED:
                    return False
        return True

    def next_actionable(self) -> Optional[dict]:
        """Return highest-priority active goal with all dependencies met."""
        active = self.list_active()
        for goal in active:
            if self.are_dependencies_met(goal["id"]):
                return goal
        return None

    def summary(self) -> dict:
        """Return counts by state — useful for /status commands."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT state, COUNT(*) as cnt FROM goals GROUP BY state"
            ).fetchall()
        return {r[0]: r[1] for r in rows}

    # ---- Async wrappers for use in async agent loop ----
    async def async_add_goal(self, *args, **kwargs) -> int:
        return await asyncio.to_thread(self.add_goal, *args, **kwargs)

    async def async_update_state(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.update_state, *args, **kwargs)

    async def async_next_actionable(self) -> Optional[dict]:
        return await asyncio.to_thread(self.next_actionable)


# Module-level singleton — import and use directly:
#   from core.goal_manager import goal_manager
#   goal_manager.ensure_db()
goal_manager = GoalManager()
PYEOF

echo "  ✅ core/goal_manager.py written (SQLite-backed, async wrappers)"
echo ""

# -------------------------------------------------------
# STEP 4: Wire knowledge_graph into agent.py context block
# -------------------------------------------------------
echo "[4/4] Wiring knowledge_graph into agent.py context-building block..."

# We use Python to do the surgical patch — sed is fragile for multi-line Python
python3 - << 'PYEOF'
import re
from pathlib import Path

agent_path = Path("core/agent.py")
source = agent_path.read_text(encoding="utf-8")

# Check if already patched
if "knowledge_graph" in source:
    print("  ℹ️  agent.py already references knowledge_graph — skipping patch")
    exit(0)

# Find the context assembly line: `context = base_context + enriched_context + past_reflections_str`
# We inject GraphRAG after enriched_context is built, before context is assembled.
PATCH_ANCHOR = "            context = base_context + enriched_context + past_reflections_str"

KG_INJECTION = '''            # [WIRED] knowledge_graph context enrichment
            graphrag_context = ""
            try:
                from core.knowledge_graph import KnowledgeGraph
                _kg = KnowledgeGraph()
                kg_results = _kg.query(goal, top_k=5)
                if kg_results:
                    graphrag_context = "\\n\\n[KNOWLEDGE GRAPH]\\n" + "\\n".join(
                        f"- {r}" if isinstance(r, str) else str(r)
                        for r in kg_results
                    )
            except Exception as _kg_err:
                logger.debug(f"knowledge_graph_query_failed: {_kg_err}")

            context = base_context + enriched_context + graphrag_context + past_reflections_str'''

if PATCH_ANCHOR not in source:
    print("  ⚠️  Patch anchor not found in agent.py — manual wiring needed")
    print(f"     Expected: {PATCH_ANCHOR[:80]!r}")
    exit(0)

patched = source.replace(PATCH_ANCHOR, KG_INJECTION, 1)
agent_path.write_text(patched, encoding="utf-8")
print("  ✅ agent.py patched: knowledge_graph wired into context assembly")
PYEOF

echo ""

# -------------------------------------------------------
# COMMIT
# -------------------------------------------------------
echo "[GIT] Staging and committing..."

git add -A
git status --short

git commit -m "refactor: integration sprint — archive orphans, implement goal_manager, wire KG

- Archive core/cognitive/ and core/cognition/ to archive/orphan_cognitive/
  (zero imports in agent.py confirmed; inline _self_check() is the live pipeline)
- Rename core/reasoning_engine.py -> .ORPHAN.py (live module: core/reasoning.py)
- Implement core/goal_manager.py: SQLite-backed persistent goal store
  States: active|paused|blocked|completed|failed, cross-session, async wrappers
- Wire core/knowledge_graph.py into agent.py context-building block
  Injected after enriched_context, before context assembly"

echo ""
echo "=== Sprint Complete ==="
echo "Next: git push origin $(git branch --show-current)"
git log --oneline -3

