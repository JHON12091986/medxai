# NINA v12 MemorySystem Stage 5
from typing import Any
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
    def __init__(self) -> None:
        self.client = None
        self.col    = None
        self.facts: dict = {}
        self._facts_lock = asyncio.Lock()
        self.reminders: list = []
        self._reminders_lock = asyncio.Lock()

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

    async def build_context(self, query: str, n: int = 5) -> str:
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
                    paired = sorted(
                        zip(raw_metas, raw_docs),
                        key=lambda x: float(x[0].get("ts", 0)),
                        reverse=True
                    )
                    docs = [d for _, d in paired[:5]]
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
        if docs:
            # Simple truncation to stay under 4000 total (prevents context overflow)
            budget = 3800 - len(pc_block)
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
            await asyncio.to_thread(
                self.col.add,
                documents=[content],
                ids=[uid],
                metadatas=[{"role": role, "ts": time.time()}]
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

    async def kb_add_entry(self, tags: list[str], text: str, source: str = "manual") -> str:
        """
        Adds a new entry to the personal knowledge base.
        F-08 primitive.
        """
        entry_id = f"kb_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
        metadata = {
            "type": "kb_entry",
            "source": source,
            "ts": time.time(),
            "tags": ",".join(tags) if tags else ""
        }
        try:
            if not self.col:
                return ""
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
        try:
            if not self.col:
                return results
            nresults = min(limit, self.col.count())
            if nresults == 0:
                return results

            if query:
                if tag:
                    # We can't do string containment natively in basic Chroma without contains operator if not supported,
                    # but we'll try an exact tag match or just fetch and filter. For simplicity and reliability,
                    # we fetch by type and filter below if needed, or if we assume strict tag equality we could use it.
                    pass
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
                    results.append({"id": i, "text": d, "tags": m.get("tags", "").split(","), "source": m.get("source", "unknown"), "ts": m.get("ts", 0.0)})
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
                    results.append({"id": i, "text": d, "tags": m.get("tags", "").split(","), "source": m.get("source", "unknown"), "ts": m.get("ts", 0.0)})

                # Sort by timestamp desc and limit
                results.sort(key=lambda x: x["ts"], reverse=True)
                results = results[:limit]
        except Exception as e:
            logger.warning(f"kb_search failed: {e}")

        return results

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
