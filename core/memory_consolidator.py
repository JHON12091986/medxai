"""core/memory_consolidator.py — Letta-style sleep-time memory consolidation.

Runs during idle periods to:
  1. Deduplicate near-identical episodic turns
  2. Score importance of each episodic entry
  3. Promote high-importance entries to semantic memory
  4. Soft-prune (mark, not delete) low-importance stale entries
  5. Extract and upsert facts from conversation history to facts.json

Design rules:
  - Never deletes memory entries — only marks as soft_pruned=True.
  - Consolidation is idempotent: safe to run multiple times.
  - All operations fail open: errors are logged, not raised.
  - Should be called from idleloop.py on a configurable schedule.
  - Respects NINA_CONSOLIDATION_BATCH_SIZE env var.

Usage:
    from core.memory_consolidator import MemoryConsolidator
    consolidator = MemoryConsolidator(memory=layered_memory, router=router)
    report = await consolidator.run()
    print(report.summary())
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.consolidator")

BATCH_SIZE          = int(os.getenv("NINA_CONSOLIDATION_BATCH_SIZE", "50"))
IMPORTANCE_PROMOTE  = 0.75
IMPORTANCE_PRUNE    = 0.20
STALE_DAYS          = 30
SIM_DEDUP_THRESHOLD = 0.92
FACTS_JSON          = Path(os.getenv("NINA_FACTS_JSON", "./data/facts.json"))

IMPORTANCE_SYSTEM = """You are NINA's memory importance scorer.
Given a conversation turn, score its long-term importance (0.0-1.0).

High importance (0.8+): user preferences, key facts, decisions, errors, breakthroughs.
Medium importance (0.5-0.79): useful context, tool results, partial answers.
Low importance (0.0-0.49): greetings, filler, repeated info, trivial chit-chat.

Respond ONLY as JSON: {"importance": <float>, "reason": "<5 words max>"}"""

EXTRACT_FACTS_SYSTEM = """You are NINA's fact extractor.
From the conversation snippet, extract durable facts about the user or system.
Return ONLY a JSON array of strings (facts), max 5 items.
Example: ["User prefers dark mode", "Project uses Python 3.14"]
If no durable facts, return []. Return only the JSON array."""


@dataclass
class ConsolidationReport:
    scored:      int   = 0
    promoted:    int   = 0
    pruned:      int   = 0
    deduped:     int   = 0
    facts_added: int   = 0
    errors:      int   = 0
    elapsed_ms:  float = 0.0

    def summary(self) -> str:
        return (
            f"Consolidation: scored={self.scored} promoted={self.promoted} "
            f"pruned={self.pruned} deduped={self.deduped} "
            f"facts_added={self.facts_added} errors={self.errors} "
            f"elapsed={self.elapsed_ms:.0f}ms"
        )


class MemoryConsolidator:
    """Sleep-time memory consolidation engine."""

    def __init__(self, memory: Any, router: Any = None):
        self.memory = memory
        self.router = router

    async def run(self) -> ConsolidationReport:
        """Run a full consolidation pass. Safe to call repeatedly."""
        import time
        t0     = time.time()
        report = ConsolidationReport()
        for step in (self._score_and_promote, self._deduplicate, self._extract_facts):
            try:
                await step(report)
            except Exception as exc:
                log.error("consolidator: step %s failed: %s", step.__name__, exc)
                report.errors += 1
        report.elapsed_ms = (time.time() - t0) * 1000
        log.info("consolidator: %s", report.summary())
        return report

    # ── score & promote ────────────────────────────────────────────────

    async def _score_and_promote(self, report: ConsolidationReport) -> None:
        coll = self._episodic_coll()
        if coll is None:
            return
        count = coll.count()
        if count == 0:
            return
        results = coll.get(limit=BATCH_SIZE, include=["documents", "metadatas", "ids"])
        docs  = results.get("documents") or []
        metas = results.get("metadatas") or []
        ids   = results.get("ids") or []
        for doc, meta, doc_id in zip(docs, metas, ids):
            if meta and meta.get("importance", 0) > 0.01:
                continue
            try:
                importance = await self._score_importance(doc)
                importance = _apply_age_penalty(importance, meta)
                new_meta = dict(meta or {})
                new_meta["importance"] = importance
                if importance >= IMPORTANCE_PROMOTE:
                    await self._promote_to_semantic(doc, new_meta)
                    report.promoted += 1
                if importance < IMPORTANCE_PRUNE:
                    new_meta["soft_pruned"] = True
                    report.pruned += 1
                coll.update(ids=[doc_id], metadatas=[new_meta])
                report.scored += 1
            except Exception as exc:
                log.warning("consolidator: score %s failed: %s", doc_id, exc)
                report.errors += 1

    async def _promote_to_semantic(self, text: str, meta: dict) -> None:
        from core.layered_memory import MemoryLayer
        new_meta = {k: v for k, v in meta.items()
                    if k in ("importance", "role", "session_id")}
        new_meta["type"]   = "promoted_episodic"
        new_meta["source"] = "consolidation"
        await self.memory.write(text, layer=MemoryLayer.SEMANTIC, metadata=new_meta)

    # ── deduplication ──────────────────────────────────────────────────

    async def _deduplicate(self, report: ConsolidationReport) -> None:
        coll = self._episodic_coll()
        if coll is None:
            return
        count = coll.count()
        if count < 2:
            return
        results = coll.get(
            limit=min(BATCH_SIZE, count),
            include=["documents", "metadatas", "ids"],
        )
        docs  = results.get("documents") or []
        metas = results.get("metadatas") or []
        ids   = results.get("ids") or []
        seen: set[str] = set()
        for doc, meta, doc_id in zip(docs, metas, ids):
            if doc_id in seen:
                continue
            try:
                sim = coll.query(
                    query_texts=[doc],
                    n_results=min(3, count),
                    include=["ids", "distances"],
                )
                sim_ids   = (sim.get("ids")       or [[]])[0]
                sim_dists = (sim.get("distances") or [[]])[0]
                for sid, dist in zip(sim_ids, sim_dists):
                    if sid == doc_id or sid in seen:
                        continue
                    if (1.0 - float(dist)) >= SIM_DEDUP_THRESHOLD:
                        idx = ids.index(sid) if sid in ids else -1
                        dup_meta = dict(metas[idx] if idx >= 0 else {})
                        dup_meta["soft_pruned"] = True
                        dup_meta["dedup_of"]    = doc_id
                        coll.update(ids=[sid], metadatas=[dup_meta])
                        seen.add(sid)
                        report.deduped += 1
            except Exception as exc:
                log.debug("consolidator: dedup query failed: %s", exc)

    # ── fact extraction ────────────────────────────────────────────────

    async def _extract_facts(self, report: ConsolidationReport) -> None:
        if not self.router:
            return
        coll = self._episodic_coll()
        if coll is None:
            return
        count = coll.count()
        if count == 0:
            return
        results = coll.get(limit=min(20, count), include=["documents"])
        docs = results.get("documents") or []
        if not docs:
            return
        snippet = "\n".join(docs[-10:])[:1500]
        facts = await self._llm_extract_facts(snippet)
        if facts:
            _save_facts(facts)
            report.facts_added += len(facts)
            log.info("consolidator: extracted %d facts", len(facts))

    # ── LLM helpers ────────────────────────────────────────────────────

    async def _score_importance(self, text: str) -> float:
        heuristic = _heuristic_importance(text)
        if not self.router or heuristic > 0.85 or heuristic < 0.15:
            return heuristic
        try:
            import re
            import json as _json
            messages = [
                {"role": "system", "content": IMPORTANCE_SYSTEM},
                {"role": "user",   "content": text[:600]},
            ]
            raw = await self._llm(messages)
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                data = _json.loads(m.group(0))
                score = float(data.get("importance", heuristic))
                return round(max(0.0, min(1.0, score * 0.6 + heuristic * 0.4)), 3)
        except Exception as exc:
            log.debug("consolidator: LLM importance failed: %s", exc)
        return heuristic

    async def _llm_extract_facts(self, snippet: str) -> list[str]:
        try:
            import re
            import json as _json
            messages = [
                {"role": "system", "content": EXTRACT_FACTS_SYSTEM},
                {"role": "user",   "content": snippet},
            ]
            raw = await self._llm(messages)
            m = re.search(r"\[.*\]", raw, re.DOTALL)
            if m:
                facts = _json.loads(m.group(0))
                return [str(f)[:200] for f in facts if f][:5]
        except Exception as exc:
            log.debug("consolidator: LLM fact extract failed: %s", exc)
        return []

    async def _llm(self, messages: list[dict]) -> str:
        if hasattr(self.router, "chat"):
            return await self.router.chat(messages, model="local")
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
        return await self.router.complete(prompt, model="local")

    def _episodic_coll(self):
        return getattr(self.memory, "_chroma_episodic", None)


# ── helpers ────────────────────────────────────────────────────────────

def _heuristic_importance(text: str) -> float:
    t = text.lower()
    score = 0.4
    for w in ["prefer", "always", "never", "error", "bug", "breakthrough",
              "decided", "remember", "important", "critical", "deadline", "goal"]:
        if w in t:
            score += 0.10
    for w in ["hello", "hi ", "thanks", "okay", "ok ", "sure", "yes", "no",
              "lol", ":)", "got it", "understood"]:
        if w in t:
            score -= 0.08
    words = len(text.split())
    if words < 5:
        score -= 0.15
    elif words > 40:
        score += 0.10
    return round(max(0.0, min(1.0, score)), 3)


def _apply_age_penalty(importance: float, meta: dict) -> float:
    if not meta:
        return importance
    created = meta.get("created_at") or meta.get("timestamp") or ""
    if not created:
        return importance
    try:
        ts  = datetime.fromisoformat(created.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - ts).days
        if age > STALE_DAYS:
            penalty = min(0.25, (age - STALE_DAYS) / 100 * 0.05)
            return round(max(0.0, importance - penalty), 3)
    except Exception:
        pass
    return importance


def _save_facts(new_facts: list[str]) -> None:
    FACTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    existing: list = []
    if FACTS_JSON.exists():
        try:
            data = json.loads(FACTS_JSON.read_text())
            existing = data if isinstance(data, list) else data.get("facts", [])
        except Exception:
            existing = []
    existing_set = {f.lower() for f in existing}
    added = [f for f in new_facts if f.lower() not in existing_set]
    FACTS_JSON.write_text(json.dumps(existing + added, indent=2, ensure_ascii=False))
