"""crons/memory_consolidation.py — Nightly memory consolidation for NINA vNext.

Runs as an APScheduler background job. Reads episodic turns from ChromaDB,
identifies high-importance memories, summarises clusters into semantic facts,
flags potential contradictions, and prunes low-value old turns.

How to register in your existing scheduler (crons/scheduler.py or similar):

    from crons.memory_consolidation import run_consolidation
    scheduler.add_job(
        run_consolidation,
        trigger="cron",
        hour=3,
        minute=0,
        id="memory_consolidation",
        replace_existing=True,
    )

Environment / config expected:
    NINA_CHROMA_PATH  — path to ChromaDB persist dir (default: ./data/chroma)
    NINA_FACTS_JSON   — path to facts.json (default: ./data/facts.json)
    NINA_MEMORY_COLLECTION  — ChromaDB collection name (default: nina_memory)

Design rules:
- All DB writes are append-safe — no destructive deletes on first pass.
- Contradiction detection flags only; does not auto-resolve.
- Summarisation uses local lightweight model to avoid cloud cost.
- Idempotent: re-running on same data produces same output.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.memory_consolidation")

# ── config ─────────────────────────────────────────────────────────────────

CHROMA_PATH = Path(os.getenv("NINA_CHROMA_PATH", "./data/chroma"))
FACTS_JSON  = Path(os.getenv("NINA_FACTS_JSON",  "./data/facts.json"))
COLLECTION  = os.getenv("NINA_MEMORY_COLLECTION", "nina_memory")

# Turns older than WINDOW_DAYS with score below PRUNE_SCORE_THRESHOLD
# are candidates for soft-pruning (metadata flag, not physical delete).
WINDOW_DAYS           = 30
PRUNE_SCORE_THRESHOLD = 0.3
SUMMARY_CLUSTER_SIZE  = 20   # number of episodic turns to summarise into one fact
MIN_TURNS_FOR_SUMMARY = 50   # don't consolidate unless we have this many turns


# ── entry point ───────────────────────────────────────────────────────────

async def run_consolidation(router: Any = None) -> dict:
    """Main consolidation job. Called by APScheduler.

    Args:
        router: Optional NINA router for LLM summarisation calls.
                If None, skips LLM summarisation (structure-only pass).

    Returns:
        Summary dict with stats for logging.
    """
    log.info("memory_consolidation: starting")
    stats: dict[str, int] = {
        "turns_scanned": 0,
        "facts_written": 0,
        "contradictions_flagged": 0,
        "turns_soft_pruned": 0,
    }

    try:
        import chromadb
    except ImportError:
        log.error("memory_consolidation: chromadb not installed; skipping")
        return stats

    # ─ open chroma collection ───────────────────────────────────────────
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    try:
        coll = client.get_collection(COLLECTION)
    except Exception:
        log.warning("memory_consolidation: collection '%s' not found; skipping", COLLECTION)
        return stats

    total = coll.count()
    stats["turns_scanned"] = total
    log.info("memory_consolidation: %d total turns in collection", total)

    if total < MIN_TURNS_FOR_SUMMARY:
        log.info(
            "memory_consolidation: below threshold (%d < %d); skipping summarisation",
            total, MIN_TURNS_FOR_SUMMARY,
        )
        return stats

    # ─ fetch candidate turns (oldest, not yet consolidated) ─────────────
    results = coll.get(
        where={"consolidated": {"$ne": True}},
        limit=SUMMARY_CLUSTER_SIZE * 5,
        include=["documents", "metadatas"],
    )
    docs      = results.get("documents") or []
    metas     = results.get("metadatas") or []
    ids       = results.get("ids") or []

    if not docs:
        log.info("memory_consolidation: no unconsolidated turns found")
        return stats

    # ─ importance scoring (heuristic) ────────────────────────────────
    scored: list[tuple[float, int]] = []
    for i, doc in enumerate(docs):
        score = _importance_score(doc, metas[i] if i < len(metas) else {})
        scored.append((score, i))
    scored.sort(reverse=True)

    # ─ soft-prune low-score old turns ─────────────────────────────────
    prune_ids = [
        ids[idx] for sc, idx in scored
        if sc < PRUNE_SCORE_THRESHOLD and idx < len(ids)
    ]
    if prune_ids:
        try:
            coll.update(
                ids=prune_ids,
                metadatas=[{"soft_pruned": True, "pruned_at": _now_iso()}] * len(prune_ids),
            )
            stats["turns_soft_pruned"] = len(prune_ids)
            log.info("memory_consolidation: soft-pruned %d low-value turns", len(prune_ids))
        except Exception as exc:
            log.warning("memory_consolidation: soft-prune failed: %s", exc)

    # ─ cluster high-value turns for summarisation ──────────────────────
    high_value_indices = [idx for sc, idx in scored if sc >= PRUNE_SCORE_THRESHOLD]
    clusters = [
        high_value_indices[i:i + SUMMARY_CLUSTER_SIZE]
        for i in range(0, len(high_value_indices), SUMMARY_CLUSTER_SIZE)
    ]

    for cluster_indices in clusters:
        cluster_docs = [docs[i] for i in cluster_indices if i < len(docs)]
        cluster_ids  = [ids[i]  for i in cluster_indices if i < len(ids)]

        summary = await _summarise_cluster(cluster_docs, router)
        if not summary:
            continue

        # ─ write semantic fact to facts.json ────────────────────────────
        _append_fact(summary, source_ids=cluster_ids)
        stats["facts_written"] += 1

        # mark cluster turns as consolidated
        try:
            coll.update(
                ids=cluster_ids,
                metadatas=[{"consolidated": True, "consolidated_at": _now_iso()}]
                          * len(cluster_ids),
            )
        except Exception as exc:
            log.warning("memory_consolidation: mark-consolidated failed: %s", exc)

    # ─ contradiction detection (simple heuristic) ─────────────────────
    contradictions = _detect_contradictions(docs)
    if contradictions:
        _write_contradiction_flags(contradictions)
        stats["contradictions_flagged"] = len(contradictions)
        log.warning(
            "memory_consolidation: %d potential contradictions flagged",
            len(contradictions),
        )

    log.info("memory_consolidation: done — %s", stats)
    return stats


# ── helpers ─────────────────────────────────────────────────────────────────

def _importance_score(doc: str, meta: dict) -> float:
    """Heuristic importance score 0.0-1.0 based on content signals."""
    score = 0.5
    text = doc.lower()

    # Recency boost
    ts = meta.get("timestamp", "")
    if ts:
        try:
            age_days = (datetime.now(timezone.utc) -
                        datetime.fromisoformat(ts.replace("Z", "+00:00"))).days
            if age_days < 7:
                score += 0.2
            elif age_days > WINDOW_DAYS:
                score -= 0.2
        except Exception:
            pass

    # Content signal boosts
    importance_signals = [
        "remember", "important", "always", "never", "prefer", "favourite",
        "goal", "task", "deadline", "error", "fix", "bug", "critical", "must",
    ]
    for sig in importance_signals:
        if sig in text:
            score += 0.05

    # Role: assistant answers score lower than user instructions
    if meta.get("role") == "user":
        score += 0.1

    return max(0.0, min(1.0, score))


async def _summarise_cluster(
    docs: list[str], router: Any
) -> str:
    """Summarise a cluster of episodic turns into a single semantic fact."""
    if not router:
        # Fallback: concatenate first sentence of each doc
        snippets = [d.split(".")[0][:120] for d in docs[:5]]
        return " | ".join(snippets)

    combined = "\n---\n".join(d[:400] for d in docs)
    prompt = (
        "Below are conversation turns from NINA's memory.\n"
        "Write ONE concise semantic fact (max 3 sentences) that captures the "
        "most important reusable knowledge from these turns. "
        "Focus on user preferences, recurring patterns, and actionable insights.\n\n"
        f"{combined}\n\nFact:"
    )
    try:
        if hasattr(router, "complete"):
            summary = await router.complete(prompt, model="local")
        elif hasattr(router, "chat"):
            summary = await router.chat(
                [{"role": "user", "content": prompt}], model="local"
            )
        else:
            return ""
        return summary.strip()[:500]
    except Exception as exc:
        log.warning("memory_consolidation: summarisation failed: %s", exc)
        return ""


def _append_fact(fact_text: str, source_ids: list[str]) -> None:
    """Append a new semantic fact to facts.json."""
    FACTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    facts: list[dict] = []
    if FACTS_JSON.exists():
        try:
            facts = json.loads(FACTS_JSON.read_text())
        except Exception:
            facts = []

    entry = {
        "fact": fact_text,
        "source": "memory_consolidation",
        "source_ids": source_ids[:5],
        "created_at": _now_iso(),
        "type": "semantic",
    }
    facts.append(entry)
    FACTS_JSON.write_text(json.dumps(facts, indent=2, ensure_ascii=False))


def _detect_contradictions(docs: list[str]) -> list[tuple[int, int, str]]:
    """Simple heuristic: flag pairs where one doc negates another."""
    NEGATION_PAIRS = [
        (r"always\s+(\w+)",  r"never\s+\1"),
        (r"prefer\s+(\w+)",  r"dislike\s+\1"),
        (r"enable\s+(\w+)",  r"disable\s+\1"),
        (r"like\s+(\w+)",    r"hate\s+\1"),
    ]
    flagged: list[tuple[int, int, str]] = []
    for i, doc_a in enumerate(docs):
        for j, doc_b in enumerate(docs):
            if j <= i:
                continue
            for pat_a, pat_b in NEGATION_PAIRS:
                m = re.search(pat_a, doc_a, re.IGNORECASE)
                if m:
                    pat_b_filled = pat_b.replace("\\1", re.escape(m.group(1)))
                    if re.search(pat_b_filled, doc_b, re.IGNORECASE):
                        flagged.append((i, j, m.group(0)))
    return flagged


def _write_contradiction_flags(flags: list[tuple[int, int, str]]) -> None:
    """Write contradiction flags to data/contradiction_flags.json."""
    flag_path = FACTS_JSON.parent / "contradiction_flags.json"
    existing: list[dict] = []
    if flag_path.exists():
        try:
            existing = json.loads(flag_path.read_text())
        except Exception:
            existing = []
    for a_idx, b_idx, pattern in flags:
        existing.append({
            "doc_a_index": a_idx,
            "doc_b_index": b_idx,
            "pattern": pattern,
            "flagged_at": _now_iso(),
            "resolved": False,
        })
    flag_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
