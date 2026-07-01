"""core/contradiction_detector.py — Cross-memory contradiction detection for NINA vNext.

Detects semantic contradictions between incoming claims and existing
memory stores (episodic, semantic, facts.json, knowledge graph).

Pipeline:
  1. Embed the new claim using ChromaDB's default embedder.
  2. Retrieve top-K most similar existing memory entries.
  3. Fast heuristic filter: skip obvious non-contradictions.
  4. LLM arbitration: ask the router to adjudicate conflicts.
  5. Return ConflictReport with severity + resolution recommendation.

Design rules:
  - Non-blocking: runs as advisory check, never blocks writes.
  - Fail open: detection errors return empty ConflictReport.
  - LLM arbitration is optional; heuristic-only mode is the default.
  - Severity levels: NONE, LOW, MEDIUM, HIGH, CRITICAL.

Usage:
    from core.contradiction_detector import ContradictionDetector
    detector = ContradictionDetector(memory=layered_memory)
    report = await detector.check("NINA uses PostgreSQL for memory")
    if report.has_conflicts():
        print(report.summary())
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.contradiction")

FACTS_JSON  = Path(os.getenv("NINA_FACTS_JSON", "./data/facts.json"))
TOP_K       = int(os.getenv("NINA_CONTRADICTION_TOP_K", "8"))
SIM_FLOOR   = 0.60   # min cosine similarity to consider a candidate
LLM_TRIGGER = 0.72   # above this similarity, escalate to LLM

ARBITRATOR_SYSTEM = """You are NINA's memory consistency arbiter.
You are given a NEW CLAIM and a list of EXISTING MEMORY entries.
For each existing entry that genuinely contradicts the new claim, output a JSON object.
If there are no contradictions, output {"contradictions": []}.

Output format:
{
  "contradictions": [
    {
      "existing": "<exact existing entry text>",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "explanation": "<one sentence>",
      "resolution": "UPDATE_EXISTING|KEEP_EXISTING|NEEDS_REVIEW"
    }
  ]
}

Severity guide:
  CRITICAL — direct factual conflict on a key system fact
  HIGH     — strong contradiction on an important preference or setting
  MEDIUM   — partial or contextual conflict
  LOW      — minor inconsistency or possible ambiguity

Return ONLY the JSON object. No prose."""


class Severity(str, Enum):
    NONE     = "NONE"
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_str(cls, s: str) -> "Severity":
        try:
            return cls(s.upper())
        except ValueError:
            return cls.NONE

    def weight(self) -> int:
        return {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}[self.value]


@dataclass
class Conflict:
    existing:    str
    new_claim:   str
    severity:    Severity = Severity.NONE
    explanation: str      = ""
    resolution:  str      = "NEEDS_REVIEW"   # UPDATE_EXISTING | KEEP_EXISTING | NEEDS_REVIEW
    similarity:  float    = 0.0
    source:      str      = ""               # which memory store


@dataclass
class ConflictReport:
    new_claim:  str
    conflicts:  list[Conflict] = field(default_factory=list)
    checked_at: str = field(default_factory=lambda: __import__(
        "datetime").datetime.utcnow().isoformat())

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def max_severity(self) -> Severity:
        if not self.conflicts:
            return Severity.NONE
        return max(self.conflicts, key=lambda c: c.severity.weight()).severity

    def summary(self) -> str:
        if not self.conflicts:
            return f"No contradictions found for: {self.new_claim[:60]}"
        lines = [f"Contradictions ({len(self.conflicts)}) for: {self.new_claim[:60]}"]
        for c in self.conflicts:
            lines.append(
                f"  [{c.severity.value}] existing='{c.existing[:60]}' "
                f"| {c.explanation[:80]} | resolution={c.resolution}"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "new_claim":  self.new_claim,
            "checked_at": self.checked_at,
            "max_severity": self.max_severity().value,
            "conflicts": [
                {
                    "existing":    c.existing,
                    "severity":    c.severity.value,
                    "explanation": c.explanation,
                    "resolution":  c.resolution,
                    "similarity":  round(c.similarity, 3),
                    "source":      c.source,
                }
                for c in self.conflicts
            ],
        }


class ContradictionDetector:
    """Cross-memory contradiction detection engine."""

    def __init__(
        self,
        memory: Any,
        router: Any = None,
        knowledge_graph: Any = None,
        use_llm: bool = True,
    ):
        self.memory          = memory
        self.router          = router
        self.kg              = knowledge_graph
        self.use_llm         = use_llm and router is not None

    async def check(
        self,
        new_claim: str,
        top_k: int = TOP_K,
    ) -> ConflictReport:
        """Check a new claim against all memory stores.

        Args:
            new_claim: The statement to validate.
            top_k:     Max candidates to retrieve per store.

        Returns:
            ConflictReport with detected conflicts.
        """
        report = ConflictReport(new_claim=new_claim)
        candidates: list[tuple[str, float, str]] = []  # (text, similarity, source)

        # Gather candidates from all stores
        candidates += await self._candidates_from_memory(new_claim, top_k)
        candidates += await self._candidates_from_facts(new_claim, top_k)
        candidates += await self._candidates_from_kg(new_claim, top_k)

        # Filter by similarity floor
        candidates = [(t, s, src) for t, s, src in candidates
                      if s >= SIM_FLOOR and t.strip() != new_claim.strip()]
        if not candidates:
            return report

        # Deduplicate by text
        seen: set[str] = set()
        deduped = []
        for t, s, src in sorted(candidates, key=lambda x: -x[1]):
            if t not in seen:
                deduped.append((t, s, src))
                seen.add(t)

        # Heuristic pre-filter
        heuristic_hits = [
            (t, s, src) for t, s, src in deduped
            if _heuristic_contradiction(new_claim, t)
        ]

        # LLM arbitration for high-similarity or heuristic hits
        llm_candidates = [
            (t, s, src) for t, s, src in deduped
            if s >= LLM_TRIGGER or (t, s, src) in heuristic_hits
        ][:top_k]

        if self.use_llm and llm_candidates:
            conflicts = await self._llm_arbitrate(new_claim, llm_candidates)
            report.conflicts.extend(conflicts)
        else:
            # Heuristic-only path
            for text, sim, src in heuristic_hits[:top_k]:
                report.conflicts.append(Conflict(
                    existing=text,
                    new_claim=new_claim,
                    severity=Severity.LOW,
                    explanation="Heuristic similarity conflict",
                    resolution="NEEDS_REVIEW",
                    similarity=sim,
                    source=src,
                ))

        if report.has_conflicts():
            log.info(
                "contradiction: %d conflict(s) for '%s' — max=%s",
                len(report.conflicts), new_claim[:50],
                report.max_severity().value,
            )
        return report

    # ── candidate retrieval ────────────────────────────────────────────

    async def _candidates_from_memory(
        self, query: str, top_k: int
    ) -> list[tuple[str, float, str]]:
        """Retrieve similar entries from LayeredMemory."""
        results = []
        from core.layered_memory import MemoryLayer
        for layer in (MemoryLayer.EPISODIC, MemoryLayer.SEMANTIC):
            try:
                hits = await self.memory.search(
                    query, layer=layer, top_k=top_k // 2 or 3
                )
                for hit in hits:
                    text = hit.get("text") or hit.get("document") or ""
                    dist = hit.get("distance", 1.0)
                    sim  = max(0.0, 1.0 - float(dist))
                    if text:
                        results.append((text, sim, layer.value))
            except Exception as exc:
                log.debug("contradiction: memory search (%s) failed: %s", layer, exc)
        return results

    async def _candidates_from_facts(
        self, query: str, top_k: int
    ) -> list[tuple[str, float, str]]:
        """Search facts.json for relevant entries."""
        if not FACTS_JSON.exists():
            return []
        try:
            data  = json.loads(FACTS_JSON.read_text())
            facts = data if isinstance(data, list) else data.get("facts", [])
        except Exception:
            return []
        q = query.lower()
        results = []
        for fact in facts:
            text = str(fact)
            sim  = _token_overlap_sim(q, text.lower())
            if sim >= SIM_FLOOR * 0.8:  # looser floor for keyword match
                results.append((text, sim, "facts.json"))
        return sorted(results, key=lambda x: -x[1])[:top_k]

    async def _candidates_from_kg(
        self, query: str, top_k: int
    ) -> list[tuple[str, float, str]]:
        """Search knowledge graph entities."""
        if not self.kg:
            return []
        try:
            entities = await self.kg.search_entities(query, top_k=top_k)
            results  = []
            for entity in entities:
                text = entity.description or entity.name
                sim  = _token_overlap_sim(query.lower(), text.lower())
                results.append((text, max(sim, 0.65), "knowledge_graph"))
            return results
        except Exception as exc:
            log.debug("contradiction: kg search failed: %s", exc)
            return []

    # ── LLM arbitration ────────────────────────────────────────────────

    async def _llm_arbitrate(
        self,
        new_claim: str,
        candidates: list[tuple[str, float, str]],
    ) -> list[Conflict]:
        """Ask LLM to identify genuine contradictions."""
        existing_block = "\n".join(
            f"- [{src}] {text[:200]}" for text, _sim, src in candidates
        )
        messages = [
            {"role": "system", "content": ARBITRATOR_SYSTEM},
            {"role": "user",   "content":
             f"NEW CLAIM:\n{new_claim}\n\nEXISTING MEMORY:\n{existing_block}"},
        ]
        try:
            raw = await self._llm(messages)
            m   = re.search(r"\{.*\}", raw, re.DOTALL)
            if not m:
                return []
            data = json.loads(m.group(0))
            conflicts = []
            for item in data.get("contradictions", []):
                existing  = str(item.get("existing", ""))
                sim_entry = next(
                    (s for t, s, _ in candidates if t[:100] in existing or existing[:100] in t),
                    0.70,
                )
                source = next(
                    (src for t, _s, src in candidates
                     if t[:100] in existing or existing[:100] in t),
                    "unknown",
                )
                conflicts.append(Conflict(
                    existing=existing,
                    new_claim=new_claim,
                    severity=Severity.from_str(item.get("severity", "LOW")),
                    explanation=str(item.get("explanation", ""))[:200],
                    resolution=str(item.get("resolution", "NEEDS_REVIEW")),
                    similarity=sim_entry,
                    source=source,
                ))
            return conflicts
        except Exception as exc:
            log.debug("contradiction: LLM arbitration failed: %s", exc)
            return []

    async def _llm(self, messages: list[dict]) -> str:
        if hasattr(self.router, "chat"):
            return await self.router.chat(messages, model="local")
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
        return await self.router.complete(prompt, model="local")


# ── helper functions ───────────────────────────────────────────────────

def _heuristic_contradiction(claim_a: str, claim_b: str) -> bool:
    """Cheap heuristic: look for negation or antonym signals."""
    negations = [" not ", " no ", " never ", " don't ", " doesn't ",
                 " isn't ", " aren't ", " won't ", " can't "]
    a, b = claim_a.lower(), claim_b.lower()
    # Check if one negates a key noun/verb from the other
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    overlap  = tokens_a & tokens_b - {"the", "a", "an", "is", "are", "was",
                                       "it", "to", "of", "in", "for", "and"}
    if len(overlap) < 2:
        return False
    for neg in negations:
        if (neg in a and neg not in b) or (neg not in a and neg in b):
            return True
    return False


def _token_overlap_sim(a: str, b: str) -> float:
    """Jaccard similarity on word tokens."""
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union        = tokens_a | tokens_b
    return len(intersection) / len(union)
