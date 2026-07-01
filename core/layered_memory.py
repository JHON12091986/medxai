"""core/layered_memory.py — Unified layered memory facade for NINA vNext.

Provides a single read/write API over four memory stores:

  Working memory   — current session context (in-process dict, no DB)
  Episodic memory  — per-turn conversation history (ChromaDB)
  Semantic memory  — consolidated facts & knowledge (facts.json + ChromaDB)
  Procedural memory— reusable skill/tool recipes (JSON file)

Replaces the flat, scattered ChromaDB calls across core/agent.py with
a typed, priority-aware retrieval interface.

Usage:
    from core.layered_memory import LayeredMemory, MemoryLayer
    mem = LayeredMemory()

    # Write
    await mem.write("user likes dark mode", layer=MemoryLayer.SEMANTIC)
    await mem.write_episodic(turn_id="t001", role="user", text="Hello NINA")
    await mem.write_procedural(skill_name="web_search", recipe={...})

    # Read — searches all layers, ranked by relevance + importance
    results = await mem.search("user preferences UI", top_k=5)

    # Working memory (current session)
    mem.working["active_goal"] = "research AI memory"
    goal = mem.working.get("active_goal")

All methods fail open: errors are logged, not raised, so a memory
failure never crashes the main agent loop.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.layered_memory")

CHROMA_PATH       = Path(os.getenv("NINA_CHROMA_PATH",     "./data/chroma"))
FACTS_JSON        = Path(os.getenv("NINA_FACTS_JSON",      "./data/facts.json"))
PROCEDURES_JSON   = Path(os.getenv("NINA_PROCEDURES_JSON", "./data/procedures.json"))
EPISODIC_COLL     = os.getenv("NINA_MEMORY_COLLECTION",    "nina_memory")
SEMANTIC_COLL     = "nina_semantic"
PROCEDURAL_COLL   = "nina_procedural"


class MemoryLayer(str, Enum):
    WORKING    = "working"
    EPISODIC   = "episodic"
    SEMANTIC   = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryResult:
    text: str
    layer: MemoryLayer
    score: float = 0.0          # relevance score (higher = more relevant)
    importance: float = 0.5     # importance score from episodic_scorer
    metadata: dict = field(default_factory=dict)
    id: str = ""

    def __lt__(self, other: "MemoryResult") -> bool:
        return self.score < other.score


class LayeredMemory:
    """Unified memory facade over all four NINA memory layers."""

    def __init__(self, use_chroma: bool = True):
        # Working memory: plain dict, session-scoped, never persisted
        self.working: dict[str, Any] = {}

        self._chroma_episodic  = None
        self._chroma_semantic  = None
        self._chroma_procedural = None

        if use_chroma:
            self._init_chroma()

    # ─ init ─────────────────────────────────────────────────────────────────

    def _init_chroma(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            self._chroma_episodic   = client.get_or_create_collection(
                EPISODIC_COLL,   metadata={"hnsw:space": "cosine"})
            self._chroma_semantic   = client.get_or_create_collection(
                SEMANTIC_COLL,   metadata={"hnsw:space": "cosine"})
            self._chroma_procedural = client.get_or_create_collection(
                PROCEDURAL_COLL, metadata={"hnsw:space": "cosine"})
            log.info("layered_memory: chroma collections ready")
        except Exception as exc:
            log.warning("layered_memory: chroma init failed: %s", exc)

    # ─ write ────────────────────────────────────────────────────────────────

    async def write(
        self,
        text: str,
        layer: MemoryLayer = MemoryLayer.SEMANTIC,
        metadata: dict | None = None,
        doc_id: str | None = None,
    ) -> str:
        """Write a text entry to the specified memory layer.

        Returns the doc_id of the written entry.
        """
        doc_id = doc_id or _new_id(layer)
        meta   = {"layer": layer.value, "created_at": _now_iso(), **(metadata or {})}

        coll = self._coll_for(layer)
        if coll is None:
            log.debug("layered_memory: write skipped (no chroma) layer=%s", layer)
            return doc_id

        try:
            coll.add(ids=[doc_id], documents=[text], metadatas=[meta])
            log.debug("layered_memory: wrote id=%s layer=%s", doc_id, layer)
        except Exception as exc:
            # Duplicate id — update instead
            try:
                coll.update(ids=[doc_id], documents=[text], metadatas=[meta])
            except Exception as exc2:
                log.warning("layered_memory: write failed: %s / %s", exc, exc2)
        return doc_id

    async def write_episodic(
        self,
        text: str,
        role: str = "user",
        turn_id: str | None = None,
        session_id: str = "",
        extra_meta: dict | None = None,
    ) -> str:
        """Convenience: write a conversation turn to episodic memory."""
        meta = {
            "role": role,
            "session_id": session_id,
            "timestamp": _now_iso(),
            **(extra_meta or {}),
        }
        return await self.write(
            text, layer=MemoryLayer.EPISODIC, metadata=meta, doc_id=turn_id
        )

    async def write_procedural(
        self,
        skill_name: str,
        recipe: dict,
        description: str = "",
    ) -> str:
        """Write a skill/tool recipe to procedural memory."""
        text = description or json.dumps(recipe, ensure_ascii=False)[:500]
        doc_id = f"proc_{skill_name}"
        meta = {"skill_name": skill_name, "recipe_json": json.dumps(recipe)[:800]}
        # Also persist to JSON file for backup
        _append_procedure(skill_name, recipe, description)
        return await self.write(
            text, layer=MemoryLayer.PROCEDURAL, metadata=meta, doc_id=doc_id
        )

    # ─ read / search ────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        top_k: int = 5,
        layers: list[MemoryLayer] | None = None,
        min_importance: float = 0.0,
    ) -> list[MemoryResult]:
        """Search across specified memory layers, ranked by relevance.

        Args:
            query:          Semantic search query.
            top_k:          Total results to return across all layers.
            layers:         Layers to search. Defaults to all except WORKING.
            min_importance: Filter out results below this importance score.

        Returns:
            Sorted list of MemoryResult (highest relevance first).
        """
        if layers is None:
            layers = [MemoryLayer.EPISODIC, MemoryLayer.SEMANTIC, MemoryLayer.PROCEDURAL]

        all_results: list[MemoryResult] = []
        per_layer_k = max(top_k, 3)  # fetch a bit more, then merge

        for layer in layers:
            results = await self._search_layer(query, layer, n=per_layer_k)
            all_results.extend(results)

        # Apply importance filter & sort by score desc
        all_results = [
            r for r in all_results if r.importance >= min_importance
        ]
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:top_k]

    async def search_text(
        self, query: str, top_k: int = 5, layers: list[MemoryLayer] | None = None
    ) -> str:
        """Search and return results as plain text for prompt injection."""
        results = await self.search(query, top_k=top_k, layers=layers)
        if not results:
            return ""
        lines = []
        for r in results:
            lines.append(f"[{r.layer.value.upper()}] {r.text[:300]}")
        return "\n".join(lines)

    async def get_procedural(
        self, skill_name: str
    ) -> dict | None:
        """Retrieve a procedural recipe by skill name."""
        doc_id = f"proc_{skill_name}"
        if self._chroma_procedural is None:
            return _load_procedure(skill_name)
        try:
            res = self._chroma_procedural.get(
                ids=[doc_id], include=["metadatas"]
            )
            metas = res.get("metadatas") or []
            if metas:
                recipe_str = metas[0].get("recipe_json", "{}")
                return json.loads(recipe_str)
        except Exception as exc:
            log.warning("layered_memory: get_procedural failed: %s", exc)
        return _load_procedure(skill_name)

    # ─ internal ──────────────────────────────────────────────────────────────

    def _coll_for(self, layer: MemoryLayer):
        return {
            MemoryLayer.EPISODIC:   self._chroma_episodic,
            MemoryLayer.SEMANTIC:   self._chroma_semantic,
            MemoryLayer.PROCEDURAL: self._chroma_procedural,
        }.get(layer)

    async def _search_layer(
        self, query: str, layer: MemoryLayer, n: int
    ) -> list[MemoryResult]:
        coll = self._coll_for(layer)
        if coll is None:
            return []
        try:
            count = coll.count()
            if count == 0:
                return []
            res = coll.query(
                query_texts=[query],
                n_results=min(n, count),
                include=["documents", "metadatas", "distances"],
            )
            docs      = (res.get("documents")  or [[]])[0]
            metas     = (res.get("metadatas")  or [[]])[0]
            distances = (res.get("distances")  or [[]])[0]

            results = []
            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance →0.0 (identical) → 1.0 (opposite)
                # Convert to relevance score: 1.0 = identical
                relevance = max(0.0, 1.0 - float(dist))
                importance = _importance_from_meta(meta)
                results.append(MemoryResult(
                    text=doc,
                    layer=layer,
                    score=relevance,
                    importance=importance,
                    metadata=meta or {},
                ))
            return results
        except Exception as exc:
            log.warning("layered_memory: search layer=%s failed: %s", layer, exc)
            return []


# ── helpers ─────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _new_id(layer: MemoryLayer) -> str:
    return f"{layer.value}_{uuid.uuid4().hex[:12]}"

def _importance_from_meta(meta: dict) -> float:
    """Extract or estimate importance from chroma metadata."""
    if not meta:
        return 0.5
    # If consolidation/episodic scorer wrote a score
    if "importance" in meta:
        try:
            return float(meta["importance"])
        except Exception:
            pass
    # Soft-pruned entries are de-prioritised
    if meta.get("soft_pruned"):
        return 0.1
    # Semantic facts are high value
    if meta.get("type") == "semantic":
        return 0.8
    return 0.5

def _append_procedure(skill_name: str, recipe: dict, description: str) -> None:
    PROCEDURES_JSON.parent.mkdir(parents=True, exist_ok=True)
    procs: dict = {}
    if PROCEDURES_JSON.exists():
        try:
            procs = json.loads(PROCEDURES_JSON.read_text())
        except Exception:
            procs = {}
    procs[skill_name] = {
        "description": description,
        "recipe": recipe,
        "updated_at": _now_iso(),
    }
    PROCEDURES_JSON.write_text(json.dumps(procs, indent=2, ensure_ascii=False))

def _load_procedure(skill_name: str) -> dict | None:
    if not PROCEDURES_JSON.exists():
        return None
    try:
        procs = json.loads(PROCEDURES_JSON.read_text())
        return procs.get(skill_name)
    except Exception:
        return None
