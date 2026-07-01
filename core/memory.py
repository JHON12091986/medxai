# NINA v12 MemorySystem Stage 5
from typing import Any, Optional
import asyncio
import json
import logging
import shutil
import time
import uuid
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger("nina.memory")

FACTS_FILE = Path("data/memory/facts.json")
CHROMA_DIR = Path("data/memory/chromadb")
BACKUP_DIR = Path("upgrades/backups")
REMINDERS_FILE = Path("data/reminders.json")

PREF_KEYS = {"name", "language", "timezone", "bank", "email", "role", "style"}

class MemorySystem:
    def __init__(self, db_path: str = "data/memory/knowledge_base.db") -> None:
        self.client = None
        self.col    = None
        self.facts: dict = {}
        self._facts_lock = asyncio.Lock()
        self.reminders: list = []
        self._reminders_lock = asyncio.Lock()
        self.db_path = db_path
        # Avoid creating directory if using in-memory db ":memory:"
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kb_entries (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    source TEXT,
                    ts REAL,
                    tags TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic_memories (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    goal TEXT,
                    reflection TEXT,
                    ts REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS procedural_memories (
                    command_pattern TEXT PRIMARY KEY,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    working_arguments TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    description TEXT,
                    priority INTEGER DEFAULT 3,
                    status TEXT DEFAULT 'active',
                    progress REAL DEFAULT 0.0,
                    created_at REAL,
                    deadline REAL,
                    context_snapshot TEXT
                )
            """)
            conn.commit()
        self._sqlite_conn = None

    def _get_conn(self):
        import sqlite3
        if self._sqlite_conn is None:
            self._sqlite_conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._sqlite_conn

    async def initialize(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        FACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            ef = embedding_functions.OllamaEmbeddingFunction(
                url="http://localhost:11434/api/embeddings",
                model_name="nomic-embed-text"
            )
            self.col = self.client.get_or_create_collection("ninamemory", embedding_function=ef)
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}")
            self.client = None
            self.col = None
        raw = {}
        if FACTS_FILE.exists():
            try:
                raw = json.loads(FACTS_FILE.read_text())
            except Exception as e:
                logger.critical(f"Failed to load facts.json: {e}")
        for k, v in raw.items():
            if isinstance(v, dict) and "value" in v:
                self.facts[k] = v
            else:
                self.facts[k] = {"value": str(v), "ts": 0.0}

        REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if REMINDERS_FILE.exists():
            try:
                self.reminders = json.loads(REMINDERS_FILE.read_text())
            except Exception as e:
                logger.warning(f"Failed to load reminders: {e}")
                self.reminders = []
        else:
            self.reminders = []

        conv_count = self.col.count() if self.col else 0
        logger.info(f"MemorySystem ready conversations={conv_count} facts={len(self.facts)} reminders={len(self.reminders)}")

    async def build_context(self, query: str, n: int = 10, char_budget: Optional[int] = None) -> str:
        docs = []
        try:
            if self.col:
                nresults = min(n, self.col.count())
                if nresults > 0:
                    res = await asyncio.to_thread(
                        self.col.query, query_texts=[query], n_results=nresults,
                        include=["documents", "metadatas"]
                    )
                    raw_docs  = res.get("documents", [[]])[0]
                    raw_metas = res.get("metadatas",  [[]])[0]
                    # Deduplicate by content hash before ranking
                    _seen_hashes = set()
                    _deduped = []
                    for meta, doc in zip(raw_metas, raw_docs):
                        _h = hash(doc[:200])
                        if _h not in _seen_hashes:
                            _seen_hashes.add(_h)
                            _deduped.append((meta, doc))
                    raw_metas = [m for m, _ in _deduped]
                    raw_docs  = [d for _, d in _deduped]
                    paired = sorted(
                        zip(raw_metas, raw_docs),
                        key=lambda x: float(x[0].get("ts", 0)) * 0.7 + float(x[0].get("importance", 0.3)) * 86400 * 7 * 0.3,
                        reverse=True
                    )
                    docs = [d for _, d in paired[:n]]
                    from core.hyperdrive_policy import policy
                    if policy.is_enabled():
                        from core.hyperdrive_context import optimizer
                        chunks = [{"content": d} for d in docs]
                        reranked_chunks = optimizer.rerank_relevance(chunks, query)
                        docs = [optimizer.mask_observations(c["content"]) for c in reranked_chunks]
        except Exception:
            docs = []

        # ── F-02: personal_context — fixed top section, always injected ─────
        def get_val(key: Any, default: Any="unknown") -> Any:
            fact = self.facts.get(key)
            if fact is None:
                return default
            val = fact.get("value", default) if isinstance(fact, dict) else fact
            return val if val != "" else default

        def format_list(val: Any) -> Any:
            if isinstance(val, list):
                return ", ".join(val)
            if isinstance(val, str):
                return val
            return str(val)

        pc_block = (
            "--- PERSONAL CONTEXT ---\n"
            f"Name: {get_val('name')}\n"
            f"Role: {get_val('role')}\n"
            f"Organization: {get_val('organization')}\n"
            f"Location: {get_val('location')}\n"
            f"Timezone: {get_val('timezone')}\n"
            f"Priorities: {format_list(get_val('priorities', []))}\n"
            f"Preferences: {format_list(get_val('preferences', []))}\n"
            "--- END PERSONAL CONTEXT ---"
        )

        parts = [pc_block]
        goals_ctx = await self.goal_resume_context()
        if goals_ctx:
            parts.append(goals_ctx)

        from core.hyperdrive_policy import policy
        if policy.is_enabled():
            from core.hyperdrive_goals import goals_manager
            hd_goals_ctx = goals_manager.serialize_state_capsule("default")
            if hd_goals_ctx:
                parts.append(hd_goals_ctx)

        if docs:
            # Simple truncation (prevents context overflow)
            limit = char_budget if char_budget is not None else 12000
            budget = limit - len(pc_block)
            if budget < 500:
                budget = 500
            context_str = "\n".join(docs)
            if len(context_str) > budget:
                context_str = context_str[:budget] + "... [truncated]"
            parts.append("Recent context:\n" + context_str)

        return "\n\n".join(parts)


    def get_facts(self) -> dict:
        return self.facts

    async def save_turn(self, role: str, content: str) -> None:
        try:
            if not self.col:
                return
            uid = f"{role}{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
            
            # Compute importance score
            base = 0.5 if role == "user" else 0.45
            if role == "assistant" and len(content) > 200:
                base = 0.55   # substantive assistant replies are valuable context
            
            content_lower = content.lower()
            keywords = ["remember", "important", "urgent", "critical"]
            tool_noise = ["traceback", "tool_call", "error:", "exception:", "stderr"]
            if any(kw in content_lower for kw in keywords):
                base = min(1.0, base + 0.3)
            elif any(kw in content_lower for kw in tool_noise):
                base = max(0.1, base - 0.2)  # Demote tool error noise
            
            if len(content) > 500:
                base = min(1.0, base + 0.1)
                
            importance = round(base, 2)
            
            await asyncio.to_thread(
                self.col.add,
                documents=[content],
                ids=[uid],
                metadatas=[{"role": role, "ts": time.time(), "importance": importance}]
            )
        except Exception as e:
            logger.warning(f"memory_save_failed err={e}")

    async def remember(self, text: str) -> None:
        parts = text.split(":", 1)
        key = parts[0].strip()
        val = parts[1].strip() if len(parts) == 2 else text
        async with self._facts_lock:
            self.facts[key] = {"value": val, "ts": time.time()}
            tmp = FACTS_FILE.with_suffix(".tmp")
            await asyncio.to_thread(
                tmp.write_text,
                json.dumps(self.facts, indent=2, ensure_ascii=False)
            )
            tmp.replace(FACTS_FILE)

    async def forget(self, key: str) -> None:
        async with self._facts_lock:
            self.facts.pop(key, None)
            tmp = FACTS_FILE.with_suffix(".tmp")
            await asyncio.to_thread(
                tmp.write_text,
                json.dumps(self.facts, indent=2, ensure_ascii=False)
            )
            tmp.replace(FACTS_FILE)

    async def backup(self) -> str:
        ts   = time.strftime("%Y%m%d%H%M%S")
        dest = BACKUP_DIR / f"memory{ts}"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FACTS_FILE, dest / "facts.json") if FACTS_FILE.exists() else None
        shutil.copytree(CHROMA_DIR, dest / "chromadb", dirs_exist_ok=True)
        logger.info(f"memory_backup dest={dest}")
        return str(dest)

    async def add_reminder(self, text: str, due_time: float) -> str:
        rem_id = f"rem_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        reminder = {
            "id": rem_id,
            "text": text,
            "due_time": due_time,
            "status": "pending",
            "created_at": time.time()
        }
        async with self._reminders_lock:
            self.reminders.append(reminder)
            await self._save_reminders()
        return rem_id

    async def get_due_reminders(self, now: float) -> list:
        async with self._reminders_lock:
            return [
                r for r in self.reminders
                if r.get("status") == "pending" and r.get("due_time", 0) <= now
            ]

    async def mark_reminder_done(self, rem_id: str) -> None:
        async with self._reminders_lock:
            for r in self.reminders:
                if r.get("id") == rem_id:
                    r["status"] = "done"
                    break
            await self._save_reminders()

    async def _save_reminders(self) -> None:
        tmp = REMINDERS_FILE.with_suffix(".tmp")
        await asyncio.to_thread(
            tmp.write_text,
            json.dumps(self.reminders, indent=2, ensure_ascii=False)
        )
        tmp.replace(REMINDERS_FILE)

    async def wipe_and_reinitialize(self) -> None:
        async with self._facts_lock:
            for root, dirs, files in os.walk(CHROMA_DIR, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except OSError:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except OSError:
                        pass
            try:
                os.rmdir(CHROMA_DIR)
            except OSError:
                pass
            FACTS_FILE.write_text("{}")
            self.facts = {}
            await self.initialize()

    def _sqlite_add_entry(self, entry_id: str, text: str, source: str, ts: float, tags_str: str):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO kb_entries (id, text, source, ts, tags) VALUES (?, ?, ?, ?, ?)",
                (entry_id, text, source, ts, tags_str)
            )
            conn.commit()

    def _sqlite_search(self, tag: str = None, query: str = None, limit: int = 5) -> list[dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        if query and tag:
            cursor.execute(
                "SELECT id, text, source, ts, tags FROM kb_entries WHERE text LIKE ? AND tags LIKE ? ORDER BY ts DESC LIMIT ?",
                (f"%{query}%", f"%{tag}%", limit)
            )
        elif query:
            cursor.execute(
                "SELECT id, text, source, ts, tags FROM kb_entries WHERE text LIKE ? ORDER BY ts DESC LIMIT ?",
                (f"%{query}%", limit)
            )
        elif tag:
            cursor.execute(
                "SELECT id, text, source, ts, tags FROM kb_entries WHERE tags LIKE ? ORDER BY ts DESC LIMIT ?",
                (f"%{tag}%", limit)
            )
        else:
            cursor.execute(
                "SELECT id, text, source, ts, tags FROM kb_entries ORDER BY ts DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "text": r[1],
                "source": r[2],
                "ts": r[3],
                "tags": r[4].split(",") if r[4] else []
            })
        return results

    async def kb_add_entry(self, tags: list[str], text: str, source: str = "manual") -> str:
        """
        Adds a new entry to the personal knowledge base.
        F-08 primitive.
        """
        entry_id = f"kb_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        tags_str = ",".join(tags) if tags else ""
        ts = time.time()
        try:
            await asyncio.to_thread(self._sqlite_add_entry, entry_id, text, source, ts, tags_str)
            
            if self.col:
                metadata = {
                    "type": "kb_entry",
                    "source": source,
                    "ts": ts,
                    "tags": tags_str
                }
                await asyncio.to_thread(
                    self.col.add,
                    documents=[text],
                    ids=[entry_id],
                    metadatas=[metadata]
                )
            return entry_id
        except Exception as e:
            logger.warning(f"kb_add_entry failed: {e}")
            return ""

    async def kb_search(self, tag: str = None, query: str = None, limit: int = 5) -> list[dict]:
        """
        Searches the personal knowledge base by tag and/or text match.
        F-08 primitive.
        """
        results = []
        seen_ids = set()

        try:
            sqlite_results = await asyncio.to_thread(self._sqlite_search, tag, query, limit)
            if sqlite_results:
                for r in sqlite_results:
                    results.append(r)
                    seen_ids.add(r["id"])
        except Exception as e:
            logger.warning(f"kb_search SQLite failed: {e}")
        try:
            if not self.col:
                return results
            nresults = min(limit, self.col.count())
            if nresults == 0:
                return results

            if query:
                res = await asyncio.to_thread(
                    self.col.query,
                    query_texts=[query],
                    n_results=nresults,
                    where={"type": "kb_entry"},
                    include=["documents", "metadatas"]
                )
                raw_docs = res.get("documents", [[]])[0]
                raw_metas = res.get("metadatas", [[]])[0]
                raw_ids = res.get("ids", [[]])[0]

                for i, m, d in zip(raw_ids, raw_metas, raw_docs):
                    if tag and tag not in m.get("tags", "").split(","):
                        continue
                    if i not in seen_ids:
                        results.append({"id": i, "text": d, "tags": m.get("tags", "").split(","), "source": m.get("source", "unknown"), "ts": m.get("ts", 0.0)})
                        seen_ids.add(i)
            else:
                # If no text query, we have to fetch entries. Chroma's get() supports where.
                res = await asyncio.to_thread(
                    self.col.get,
                    where={"type": "kb_entry"},
                    include=["documents", "metadatas"]
                )
                raw_docs = res.get("documents", [])
                raw_metas = res.get("metadatas", [])
                raw_ids = res.get("ids", [])

                for i, m, d in zip(raw_ids, raw_metas, raw_docs):
                    if tag and tag not in m.get("tags", "").split(","):
                        continue
                    if i not in seen_ids:
                        results.append({"id": i, "text": d, "tags": m.get("tags", "").split(","), "source": m.get("source", "unknown"), "ts": m.get("ts", 0.0)})
                        seen_ids.add(i)

                # Sort by timestamp desc and limit
                results.sort(key=lambda x: x["ts"], reverse=True)
                results = results[:limit]
        except Exception as e:
            logger.warning(f"kb_search failed: {e}")

        # Final sort and limit just in case it came from the query branch without truncation
        results.sort(key=lambda x: x["ts"], reverse=True)
        return results[:limit]

    def _sqlite_episodic_add(self, entry_id: str, session_id: str, goal: str, reflection: str, ts: float) -> None:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO episodic_memories (id, session_id, goal, reflection, ts) VALUES (?, ?, ?, ?, ?)",
                (entry_id, session_id, goal, reflection, ts)
            )
            conn.commit()

    def _sqlite_episodic_search(self, query: str = None, limit: int = 5) -> list[dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        if query:
            cursor.execute(
                "SELECT id, session_id, goal, reflection, ts FROM episodic_memories WHERE goal LIKE ? OR reflection LIKE ? ORDER BY ts DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
        else:
            cursor.execute(
                "SELECT id, session_id, goal, reflection, ts FROM episodic_memories ORDER BY ts DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        return [{"id": r[0], "session_id": r[1], "goal": r[2], "reflection": r[3], "ts": r[4]} for r in rows]

    def _sqlite_procedural_record(self, command_pattern: str, success: bool, args: str) -> None:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT success_count, failure_count FROM procedural_memories WHERE command_pattern = ?", (command_pattern,))
            row = cursor.fetchone()
            if row:
                sc, fc = row
                if success:
                    sc += 1
                else:
                    fc += 1
                cursor.execute(
                    "UPDATE procedural_memories SET success_count = ?, failure_count = ?, working_arguments = ? WHERE command_pattern = ?",
                    (sc, fc, args if success else args, command_pattern)
                )
            else:
                cursor.execute(
                    "INSERT INTO procedural_memories (command_pattern, success_count, failure_count, working_arguments) VALUES (?, ?, ?, ?)",
                    (command_pattern, 1 if success else 0, 0 if success else 1, args)
                )
            conn.commit()

    def _sqlite_procedural_get(self, command_pattern: str) -> dict | None:
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT command_pattern, success_count, failure_count, working_arguments FROM procedural_memories WHERE command_pattern = ?", (command_pattern,))
            row = cursor.fetchone()
            if row:
                return {
                    "command_pattern": row[0],
                    "success_count": row[1],
                    "failure_count": row[2],
                    "working_arguments": row[3]
                }
            return None

    async def episodic_add(self, session_id: str, goal: str, reflection: str) -> str:
        entry_id = f"epi_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        ts = time.time()
        await asyncio.to_thread(self._sqlite_episodic_add, entry_id, session_id, goal, reflection, ts)
        if self.col:
            try:
                await asyncio.to_thread(
                    self.col.add,
                    documents=[f"{goal}\n{reflection}"],
                    ids=[entry_id],
                    metadatas=[{"type": "episodic", "session_id": session_id,
                                "goal": goal[:200], "ts": ts, "importance": 0.7}]
                )
            except Exception as _e:
                logger.warning(f"episodic chroma write failed: {_e}")
        return entry_id

    async def save_reflection(
        self,
        session_id: str,
        goal: str,
        outcome: str,           # "success" | "partial" | "failure"
        what_worked: str,
        what_failed: str,
        improvement_note: str
    ) -> str:
        reflection = (
            f"OUTCOME: {outcome}\n"
            f"WHAT WORKED: {what_worked}\n"
            f"WHAT FAILED: {what_failed}\n"
            f"IMPROVEMENT: {improvement_note}"
        )
        return await self.episodic_add(session_id=session_id, goal=goal, reflection=reflection)

    async def get_relevant_reflections(self, query: str, limit: int = 3) -> str:
        results = await self.episodic_search(query=query, limit=limit)
        if not results:
            return ""
        lines = ["--- PAST REFLECTIONS ---"]
        for r in results:
            lines.append(f"Goal: {r['goal']}")
            lines.append(r['reflection'])
            lines.append("---")
        return "\n".join(lines)

    async def episodic_search(self, query: str = None, limit: int = 5) -> list[dict]:
        # Try ChromaDB semantic search first
        if self.col and query:
            try:
                nresults = min(limit, self.col.count())
                if nresults > 0:
                    res = await asyncio.to_thread(
                        self.col.query,
                        query_texts=[query],
                        n_results=nresults,
                        where={"type": "episodic"},
                        include=["documents", "metadatas"]
                    )
                    metas = res.get("metadatas", [[]])[0]
                    if metas:
                        return [{"id": "", "session_id": m.get("session_id",""),
                                 "goal": m.get("goal",""), "reflection": "",
                                 "ts": m.get("ts", 0)} for m in metas]
            except Exception as _e:
                logger.warning(f"episodic chroma search failed: {_e}")
        # Fallback to SQLite LIKE search
        return await asyncio.to_thread(self._sqlite_episodic_search, query, limit)

    async def procedural_record(self, command_pattern: str, success: bool, args: str = "") -> None:
        await asyncio.to_thread(self._sqlite_procedural_record, command_pattern, success, args)

    async def procedural_get(self, command_pattern: str) -> dict | None:
        return await asyncio.to_thread(self._sqlite_procedural_get, command_pattern)

    async def goal_add(self, description: str, priority: int = 3, deadline: float = None) -> str:
        goal_id = f"goal_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        async with self._facts_lock:
            await asyncio.to_thread(
                self._goal_add_sync, goal_id, description, priority,
                time.time(), deadline or 0.0
            )
        return goal_id

    def _goal_add_sync(self, goal_id, description, priority, created_at, deadline):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO goals (id, description, priority, status, progress, created_at, deadline) VALUES (?, ?, ?, 'active', 0.0, ?, ?)",
                (goal_id, description, priority, created_at, deadline)
            )
            conn.commit()

    async def goal_list(self, status: str = "active") -> list[dict]:
        import sqlite3
        def _list():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, description, priority, status, progress, created_at, deadline FROM goals WHERE status = ? ORDER BY priority ASC, created_at ASC",
                    (status,)
                )
                return [{"id": r[0], "description": r[1], "priority": r[2], "status": r[3], "progress": r[4], "created_at": r[5], "deadline": r[6]} for r in cursor.fetchall()]
        return await asyncio.to_thread(_list)

    async def goal_done(self, goal_id: str) -> None:
        import sqlite3
        def _done():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE goals SET status = 'done' WHERE id = ?", (goal_id,))
                conn.commit()
        await asyncio.to_thread(_done)

    async def goal_resume_context(self) -> str:
        goals = await self.goal_list(status="active")
        if not goals:
            return ""
        lines = ["--- ACTIVE GOALS ---"]
        for g in goals:
            lines.append(f"[{g['id']}] (P{g['priority']}) {g['description']}")
        lines.append("--- END GOALS ---")
        return "\n".join(lines)

    async def close(self) -> None:
        pass

    @property
    def conversation_count(self) -> Any:
        return self.col.count() if self.col else 0

    @property
    def fact_count(self) -> Any:
        return len(self.facts)

class MemoryHealth:
    @classmethod
    def check(cls) -> dict:
        health = {
            "chromadb_ok": False,
            "facts_ok": False,
            "collection_count": 0,
            "last_error": None
        }

        # Check facts.json
        try:
            if FACTS_FILE.exists():
                json.loads(FACTS_FILE.read_text())
            health["facts_ok"] = True
        except Exception as e:
            health["last_error"] = str(e)

        # Check ChromaDB
        try:
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            col = client.get_collection("ninamemory")
            health["collection_count"] = col.count()
            health["chromadb_ok"] = True
        except Exception as e:
            if health["last_error"]:
                health["last_error"] += f" | {e}"
            else:
                health["last_error"] = str(e)

        try:
            from core.observability import get_hub
            get_hub().emit_log()
        except ImportError:
            pass

        return health
