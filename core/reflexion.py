"""core/reflexion.py — Reflexion-style verbal reinforcement learning for NINA vNext.

After each task execution, Reflexion:
1. Evaluates outcome (success / failure / partial).
2. Generates a verbal reflection: what worked, what failed, what to do differently.
3. Stores the structured reflection to disk (data/reflexion_store.json).
4. Optionally indexes the reflection in ChromaDB episodic collection for retrieval.

Design based on: Shinn et al. (2023) Reflexion: Language Agents with
Verbal Reinforcement Learning.

Usage:
    from core.reflexion import Reflexion
    r = Reflexion(router=router)
    await r.reflect(
        task="Build a stock screener script",
        outcome="partial",
        trace_text=react_trace.to_reflexion_text(),
        output_snippet=final_answer[:500],
    )

    # Recall past reflections before attempting similar task:
    memories = await r.recall(task="write a python script")
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

log = logging.getLogger("nina.reflexion")

STORE_PATH = Path(os.getenv("NINA_REFLEXION_STORE", "./data/reflexion_store.json"))
CHROMA_PATH = Path(os.getenv("NINA_CHROMA_PATH", "./data/chroma"))
REFLEXION_COLLECTION = "nina_reflexion"
MAX_STORE_ENTRIES = 2000  # rotate oldest when exceeded

Outcome = Literal["success", "failure", "partial"]

REFLEXION_SYSTEM = """You are NINA's internal Reflexion module.
Given a task, its outcome, and an execution trace, produce a concise verbal reflection.

Respond in STRICT JSON:
{
  "what_worked": "<1-2 sentences or empty string>",
  "what_failed": "<1-2 sentences or empty string>",
  "improvement": "<1-2 actionable sentences for next attempt>",
  "skill_tags": ["<tag1>", "<tag2>"],
  "confidence": <float 0.0-1.0>
}

Only return the JSON object."""


@dataclass
class ReflexionEntry:
    task: str
    outcome: str
    what_worked: str
    what_failed: str
    improvement: str
    skill_tags: list[str] = field(default_factory=list)
    confidence: float = 0.5
    trace_snippet: str = ""
    output_snippet: str = ""
    created_at: str = ""
    error: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_recall_text(self) -> str:
        """Human-readable recall summary injected into future prompts."""
        return (
            f"[Reflexion: {self.outcome.upper()}] Task: {self.task[:100]}\n"
            f"  Worked: {self.what_worked[:120]}\n"
            f"  Failed: {self.what_failed[:120]}\n"
            f"  Improve: {self.improvement[:150]}"
        )


class Reflexion:
    """Verbal reinforcement learning via post-task reflection."""

    def __init__(self, router: Any = None, use_chroma: bool = True):
        """
        Args:
            router:     NINA router for LLM reflection generation.
                        If None, uses heuristic fallback (no LLM call).
            use_chroma: Index reflections in ChromaDB for semantic recall.
        """
        self.router = router
        self.use_chroma = use_chroma
        self._chroma_coll = None
        if use_chroma:
            self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            self._chroma_coll = client.get_or_create_collection(
                REFLEXION_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
            log.debug("reflexion: chroma collection ready")
        except Exception as exc:
            log.warning("reflexion: chroma init failed: %s", exc)
            self._chroma_coll = None

    async def reflect(
        self,
        task: str,
        outcome: Outcome,
        trace_text: str = "",
        output_snippet: str = "",
    ) -> ReflexionEntry:
        """Generate and store a verbal reflection after task execution."""
        entry = await self._generate_reflection(
            task=task,
            outcome=outcome,
            trace_text=trace_text,
            output_snippet=output_snippet,
        )
        self._store(entry)
        if self._chroma_coll:
            self._index_in_chroma(entry)
        log.info(
            "reflexion: stored [%s] for task: %s... tags=%s",
            outcome, task[:60], entry.skill_tags,
        )
        return entry

    async def recall(
        self,
        task: str,
        n_results: int = 3,
        outcome_filter: Outcome | None = None,
    ) -> list[ReflexionEntry]:
        """Retrieve past reflections relevant to a task.

        Args:
            task:           Query task description.
            n_results:      Number of past reflections to return.
            outcome_filter: If set, only return reflections with this outcome.

        Returns:
            List of ReflexionEntry sorted by relevance (most relevant first).
        """
        if self._chroma_coll:
            return self._recall_from_chroma(
                task, n_results=n_results, outcome_filter=outcome_filter
            )
        return self._recall_from_file(
            task, n_results=n_results, outcome_filter=outcome_filter
        )

    async def recall_text(
        self, task: str, n_results: int = 3
    ) -> str:
        """Recall as formatted text for injection into prompts."""
        entries = await self.recall(task, n_results=n_results)
        if not entries:
            return ""
        return "\n".join(e.to_recall_text() for e in entries)

    # ─ generation ─────────────────────────────────────────────────────

    async def _generate_reflection(
        self, task: str, outcome: str, trace_text: str, output_snippet: str
    ) -> ReflexionEntry:
        if not self.router:
            return _heuristic_reflection(
                task, outcome, trace_text, output_snippet
            )
        user_content = (
            f"TASK: {task}\n"
            f"OUTCOME: {outcome}\n"
            f"TRACE (truncated):\n{trace_text[:1200]}\n"
            f"OUTPUT SNIPPET:\n{output_snippet[:400]}\n"
            "Generate the reflection JSON."
        )
        messages = [
            {"role": "system", "content": REFLEXION_SYSTEM},
            {"role": "user",   "content": user_content},
        ]
        try:
            if hasattr(self.router, "chat"):
                raw = await self.router.chat(messages, model="local")
            else:
                prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
                raw = await self.router.complete(prompt, model="local")

            data = _parse_reflection_json(raw)
            return ReflexionEntry(
                task=task, outcome=outcome,
                what_worked=data.get("what_worked", ""),
                what_failed=data.get("what_failed", ""),
                improvement=data.get("improvement", ""),
                skill_tags=data.get("skill_tags", []),
                confidence=float(data.get("confidence", 0.5)),
                trace_snippet=trace_text[:300],
                output_snippet=output_snippet[:300],
            )
        except Exception as exc:
            log.warning("reflexion: LLM generation failed: %s", exc)
            return _heuristic_reflection(task, outcome, trace_text, output_snippet)

    # ─ storage ─────────────────────────────────────────────────────────

    def _store(self, entry: ReflexionEntry):
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        entries: list[dict] = []
        if STORE_PATH.exists():
            try:
                entries = json.loads(STORE_PATH.read_text())
            except Exception:
                entries = []
        entries.append(asdict(entry))
        # rotate
        if len(entries) > MAX_STORE_ENTRIES:
            entries = entries[-MAX_STORE_ENTRIES:]
        STORE_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False))

    def _index_in_chroma(self, entry: ReflexionEntry):
        if not self._chroma_coll:
            return
        try:
            doc_text = entry.to_recall_text()
            doc_id = f"refl_{entry.created_at.replace(':', '-').replace('+', '_')}"
            self._chroma_coll.add(
                ids=[doc_id],
                documents=[doc_text],
                metadatas=[{
                    "outcome": entry.outcome,
                    "confidence": entry.confidence,
                    "tags": ",".join(entry.skill_tags),
                    "created_at": entry.created_at,
                }],
            )
        except Exception as exc:
            log.warning("reflexion: chroma index failed: %s", exc)

    # ─ recall ──────────────────────────────────────────────────────────────

    def _recall_from_chroma(
        self,
        task: str,
        n_results: int,
        outcome_filter: str | None,
    ) -> list[ReflexionEntry]:
        try:
            where = {"outcome": outcome_filter} if outcome_filter else None
            res = self._chroma_coll.query(
                query_texts=[task],
                n_results=min(n_results, self._chroma_coll.count() or 1),
                where=where,
                include=["documents", "metadatas"],
            )
            docs  = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            entries = []
            for doc, meta in zip(docs, metas):
                entries.append(ReflexionEntry(
                    task=task,
                    outcome=meta.get("outcome", "unknown"),
                    what_worked="",
                    what_failed="",
                    improvement=doc,
                    skill_tags=meta.get("tags", "").split(","),
                    confidence=float(meta.get("confidence", 0.5)),
                    created_at=meta.get("created_at", ""),
                ))
            return entries
        except Exception as exc:
            log.warning("reflexion: chroma recall failed: %s", exc)
            return []

    def _recall_from_file(
        self,
        task: str,
        n_results: int,
        outcome_filter: str | None,
    ) -> list[ReflexionEntry]:
        if not STORE_PATH.exists():
            return []
        try:
            raw_list = json.loads(STORE_PATH.read_text())
        except Exception:
            return []
        task_lower = task.lower()
        filtered = [
            r for r in raw_list
            if (not outcome_filter or r.get("outcome") == outcome_filter)
            and task_lower[:30] in r.get("task", "").lower()
        ]
        filtered = filtered[-n_results:]  # most recent first
        return [
            ReflexionEntry(**{k: v for k, v in r.items() if k in ReflexionEntry.__dataclass_fields__})
            for r in reversed(filtered)
        ]


# ── helpers ─────────────────────────────────────────────────────────────────

import re


def _parse_reflection_json(raw: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


def _heuristic_reflection(
    task: str, outcome: str, trace_text: str, output_snippet: str
) -> ReflexionEntry:
    worked  = "Task completed." if outcome == "success" else ""
    failed  = "Task did not complete." if outcome == "failure" else ""
    improve = "Review trace for tool errors or missing context."
    return ReflexionEntry(
        task=task, outcome=outcome,
        what_worked=worked, what_failed=failed, improvement=improve,
        skill_tags=[], confidence=0.4,
        trace_snippet=trace_text[:200],
        output_snippet=output_snippet[:200],
    )


# ── Compatibility shim — agent.py imports ReflexionEngine ────────────────────

class ReflexionEngine:
    """Static façade so agent.py can call ReflexionEngine.generate_reflection().

    agent.py uses:
        from core.reflexion import ReflexionEngine
        await ReflexionEngine.generate_reflection(dispatcher, memory, goal, trace, success)

    This wraps the existing Reflexion class without changing its behaviour.
    """

    @staticmethod
    async def generate_reflection(
        dispatcher: Any,
        memory: Any,
        goal: str,
        trace: list,
        success: bool,
    ) -> None:
        try:
            r = Reflexion(router=None)
            outcome: Outcome = "success" if success else "failure"
            trace_text = "\n".join(str(s) for s in trace)
            entry = await r.reflect(task=goal, outcome=outcome, trace_text=trace_text)
            if hasattr(memory, "save_reflection"):
                await memory.save_reflection(
                    session_id=entry.created_at,
                    goal=goal,
                    outcome=outcome,
                    what_worked=entry.what_worked,
                    what_failed=entry.what_failed,
                    improvement_note=entry.improvement,
                )
        except Exception as exc:
            log.warning("ReflexionEngine.generate_reflection failed: %s", exc)
