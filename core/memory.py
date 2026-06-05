# NINA v12 MemorySystem Stage 5
import asyncio, json, logging, shutil, time
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
        for k, v in self.facts.items():
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
            uid = f"{role}{int(time.time()*1000)}"
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
        self.facts[key] = {"value": val, "ts": time.time()}
        await asyncio.to_thread(
            FACTS_FILE.write_text,
            json.dumps(self.facts, indent=2, ensure_ascii=False)
        )

    async def forget(self, key: str):
        self.facts.pop(key, None)
        await asyncio.to_thread(
            FACTS_FILE.write_text,
            json.dumps(self.facts, indent=2, ensure_ascii=False)
        )

    async def backup(self) -> str:
        ts   = time.strftime("%Y%m%d%H%M%S")
        dest = BACKUP_DIR / f"memory{ts}"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FACTS_FILE, dest / "facts.json") if FACTS_FILE.exists() else None
        shutil.copytree(CHROMA_DIR, dest / "chromadb", dirs_exist_ok=True)
        logger.info(f"memory_backup dest={dest}")
        return str(dest)

    async def wipe_and_reinitialize(self):
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        FACTS_FILE.write_text("{}")
        self.facts = {}
        await self.initialize()

    async def close(self):
        pass

    @property
    def conversation_count(self):
        return self.col.count() if self.col else 0

    @property
    def fact_count(self):
        return len(self.facts)
