"""core/confidence_scorer.py — Confidence and evidence scorer for NINA vNext.

Attaches an uncertainty signal (0.0–1.0 confidence) to any response or
decision. Used by:
  - core/critic.py         — weight revision decisions
  - core/autonomy_ratchet  — gate autonomous actions on confidence
  - core/react_engine      — FINISH step confidence check
  - Telegram interface     — optionally surface uncertainty to user

Two scoring modes:
  1. Heuristic (no LLM call): fast, signal-based, used for routing decisions.
  2. LLM-assisted (optional): model self-reports confidence in structured JSON.

Design rules:
  - Never block output — scorer fails open at confidence=0.5.
  - Confidence < LOW_CONFIDENCE_THRESHOLD triggers a disclaimer injection.
  - All scores are logged for observability.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("nina.confidence")

LOW_CONFIDENCE_THRESHOLD  = 0.40
HIGH_CONFIDENCE_THRESHOLD = 0.80

# Hedging phrases that strongly signal low confidence
_HEDGE_PHRASES = [
    "i'm not sure", "i am not sure", "not certain", "might be", "may be",
    "possibly", "perhaps", "i think", "i believe", "could be", "unclear",
    "unsure", "i don't know", "i do not know", "cannot confirm",
    "unverified", "speculation", "approximately", "roughly", "estimate",
]

# Confident phrasing signals
_CONFIDENT_PHRASES = [
    "confirmed", "verified", "according to", "source:", "reference:",
    "documented", "established", "proven", "definitively", "certainly",
]

# Factual claim markers that raise stakes (require higher confidence)
_FACTUAL_MARKERS = [
    "the answer is", "the result is", "the value is", "equals", "costs",
    "the date is", "located at", "founded in", "born in", "died in",
]

LLM_CONFIDENCE_SYSTEM = """You are NINA's confidence assessor.
Given a response and task, estimate how confident NINA should be in this response.

Respond STRICTLY as JSON:
{
  "confidence": <float 0.0-1.0>,
  "evidence_quality": "none|weak|moderate|strong",
  "reasoning": "<one sentence max>"
}

Rules:
- 0.9+ only for verified facts with clear sources
- 0.7-0.89 for well-reasoned responses with partial evidence
- 0.5-0.69 for plausible but uncertain responses
- Below 0.5 for speculative or potentially incorrect responses
Return only the JSON."""


@dataclass
class ConfidenceResult:
    confidence: float          # 0.0 - 1.0
    evidence_quality: str      # none | weak | moderate | strong
    reasoning: str = ""
    method: str = "heuristic"  # heuristic | llm
    low: bool = False
    high: bool = False
    error: str = ""

    def __post_init__(self):
        self.low  = self.confidence < LOW_CONFIDENCE_THRESHOLD
        self.high = self.confidence >= HIGH_CONFIDENCE_THRESHOLD

    def disclaimer(self) -> str:
        """Return a disclaimer string to append if confidence is low."""
        if self.low:
            return (
                f"\n\n⚠️ _Confidence: {self.confidence:.0%} — "
                "this response may be uncertain or incomplete._"
            )
        return ""

    def summary(self) -> str:
        return (
            f"confidence={self.confidence:.2f} evidence={self.evidence_quality} "
            f"low={self.low} method={self.method}"
        )


class ConfidenceScorer:
    """Confidence scorer. Instantiate once, reuse across requests."""

    def __init__(self, router: Any = None):
        """
        Args:
            router: Optional NINA router for LLM-assisted scoring.
                    If None, heuristic-only mode is used.
        """
        self.router = router

    def score_heuristic(self, text: str, task: str = "") -> ConfidenceResult:
        """Fast heuristic confidence scoring — no LLM call."""
        t = text.lower()
        score = 0.70  # neutral base

        # hedge signals → reduce confidence
        hedge_count = sum(1 for p in _HEDGE_PHRASES if p in t)
        score -= hedge_count * 0.07

        # confident signals → boost
        conf_count = sum(1 for p in _CONFIDENT_PHRASES if p in t)
        score += conf_count * 0.05

        # factual claims without evidence → slight penalty
        if any(m in t for m in _FACTUAL_MARKERS):
            if not any(p in t for p in _CONFIDENT_PHRASES):
                score -= 0.05

        # length heuristic — very short responses are often uncertain
        word_count = len(text.split())
        if word_count < 10:
            score -= 0.10
        elif word_count > 80:
            score += 0.05

        # error / failure words
        if any(w in t for w in ["error", "failed", "could not", "unable to"]):
            score -= 0.10

        score = max(0.05, min(0.95, score))
        eq = _evidence_quality(score)
        result = ConfidenceResult(
            confidence=round(score, 3),
            evidence_quality=eq,
            method="heuristic",
        )
        log.debug("confidence heuristic: %s", result.summary())
        return result

    async def score(self, text: str, task: str = "") -> ConfidenceResult:
        """Score confidence — uses LLM if router available, else heuristic."""
        heuristic = self.score_heuristic(text, task)
        if not self.router:
            return heuristic

        # Only call LLM for borderline cases (save tokens on clear cases)
        if heuristic.confidence > 0.85 or heuristic.confidence < 0.25:
            return heuristic

        try:
            result = await self._llm_score(text, task)
            # Blend: LLM 60%, heuristic 40%
            blended = round(result.confidence * 0.6 + heuristic.confidence * 0.4, 3)
            result.confidence = blended
            result.low  = blended < LOW_CONFIDENCE_THRESHOLD
            result.high = blended >= HIGH_CONFIDENCE_THRESHOLD
            result.method = "llm+heuristic"
            log.info("confidence llm: %s", result.summary())
            return result
        except Exception as exc:
            log.warning("confidence: LLM scoring failed, using heuristic: %s", exc)
            return heuristic

    async def _llm_score(self, text: str, task: str) -> ConfidenceResult:
        user_content = (
            f"TASK: {task[:300]}\n\nRESPONSE:\n{text[:800]}\n\nAssess confidence."
        )
        messages = [
            {"role": "system", "content": LLM_CONFIDENCE_SYSTEM},
            {"role": "user",   "content": user_content},
        ]
        if hasattr(self.router, "chat"):
            raw = await self.router.chat(messages, model="local")
        else:
            raw = await self.router.complete(
                "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages),
                model="local",
            )
        return _parse_llm_confidence(raw)


# ── helpers ────────────────────────────────────────────────────────────────────

def _evidence_quality(score: float) -> str:
    if score >= 0.80: return "strong"
    if score >= 0.60: return "moderate"
    if score >= 0.40: return "weak"
    return "none"


def _parse_llm_confidence(raw: str) -> ConfidenceResult:
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("No JSON in confidence response")
    data = json.loads(m.group(0))
    c = float(data.get("confidence", 0.5))
    return ConfidenceResult(
        confidence=round(max(0.0, min(1.0, c)), 3),
        evidence_quality=str(data.get("evidence_quality", "weak")),
        reasoning=str(data.get("reasoning", "")),
        method="llm",
    )
