# NINA v12 MemorySystem Stage 5
import asyncio, json, logging, shutil, time, uuid
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger("nina.memory")

FACTS_FILE = Path("data/memory/facts.json")
CHROMA_DIR = Path("data/memory/chromadb")
BACKUP_DIR = Path("upgrades/backups")

PREF_KEYS = {"name", "language", "timezone", "bank", "email", "role", "style"}

class MemorySystem:
    def __init__(self):
        self.client = None
        self.col    = None
        self.facts: dict = {}
        self._facts_lock = asyncio.Lock()

    async def initialize(self):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        FACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="nomic-embed-text"
        )
        self.col = self.client.get_or_create_collection("ninamemory", embedding_function=ef)
        raw = json.loads(FACTS_FILE.read_text()) if FACTS_FILE.exists() else {}
        for k, v in raw.items():
            if isinstance(v, dict) and "value" in v:
                self.facts[k] = v
            else:
                self.facts[k] = {"value": str(v), "ts": 0.0}
        logger.info(f"MemorySystem ready conversations={self.col.count()} facts={len(self.facts)}")

    async def build_context(self, query: str, n: int = 5) -> str:
        try:
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
            else:
                docs = []
        except Exception:
            docs = []

        # ── F-02: personal_context — fixed top section, always injected ─────
        # Facts are already loaded into self.facts by initialize(); read from
        # memory instead of hitting disk on every build_context call (R-83).
        _pc: dict = self.facts.get("personal_context", {})

        prefs, recents = [], []
        for k, v in list(self.facts.items()):
            if k == "personal_context":
                continue
            val   = v["value"] if isinstance(v, dict) else str(v)
            ts    = v.get("ts", 0.0) if isinstance(v, dict) else 0.0
            entry = f"{k}: {val}"
            if k.lower() in PREF_KEYS:
                prefs.append(entry)
            else:
                recents.append((ts, entry))

        recents.sort(key=lambda x: x[0], reverse=True)
        recent_lines = [e for _, e in recents[:7]]

        parts = []
        if _pc:
            block = "\n".join(f"  {k}: {v}" for k, v in _pc.items())
            parts.append(f"[Owner]\n{block}")
        if prefs or recent_lines:
            facts_block = "\n".join(prefs + recent_lines)
            parts.append(f"Facts:\n{facts_block}")
        if docs:
            parts.append("Recent context:\n" + "\n".join(docs))

        return "\n\n".join(parts) if parts else "(none)"

    async def save_turn(self, role: str, content: str):
        try:
            uid = f"{role}{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
            await asyncio.to_thread(
                self.col.add,
                documents=[content],
                ids=[uid],
                metadatas=[{"role": role, "ts": time.time()}]
            )
        except Exception as e:
            logger.warning(f"memory_save_failed err={e}")

    async def remember(self, text: str):
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

    async def forget(self, key: str):
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

    async def wipe_and_reinitialize(self):
        async with self._facts_lock:
            shutil.rmtree(CHROMA_DIR, ignore_errors=True)
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
        await asyncio.to_thread(
            self.col.add,
            documents=[text],
            ids=[entry_id],
            metadatas=[metadata]
        )
        return entry_id

    async def kb_search(self, tag: str = None, query: str = None, limit: int = 5) -> list[dict]:
        """
        Searches the personal knowledge base by tag and/or text match.
        F-08 primitive.
        """
        results = []
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

        return results

    async def close(self):
        pass

    @property
    def conversation_count(self):
        return self.col.count() if self.col else 0

    @property
    def fact_count(self):
        return len(self.facts)
