"""core/critic.py — Multi-dimensional response critic for NINA vNext.

Scores any response across five dimensions before it reaches the user
or triggers an autonomous action:

  alignment      — does it answer what was actually asked?
  completeness   — are all sub-questions addressed?
  safety         — does it contain harmful, misleading, or policy-violating content?
  factual        — is it grounded in verifiable evidence?
  coherence      — is it logically consistent and well-structured?

Used by:
  core/react_engine   — Pass 3 of the multi-pass loop
  core/autonomy_ratchet — gate autonomous actions
  core/agent.py       — optional post-generation quality gate

Design rules:
  - Critic always fails open: if scoring errors, return neutral CriticResult.
  - Heuristic critic: zero LLM calls, used for routing & quick gates.
  - LLM critic: used only for complex tasks when heuristic score is borderline.
  - Revision is triggered when overall_score < REVISION_THRESHOLD.
  - Max revisions hard-capped at MAX_REVISIONS to prevent token runaway.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("nina.critic")

REVISION_THRESHOLD = 0.55   # trigger revision below this
ACCEPT_THRESHOLD   = 0.78   # confident accept above this
MAX_REVISIONS      = 3      # hard cap on revision loops

LLM_CRITIC_SYSTEM = """You are NINA's internal critic.
Score the RESPONSE to the TASK on five dimensions (0.0–1.0 each).

Respond ONLY as JSON:
{
  "alignment":    <float>,
  "completeness": <float>,
  "safety":       <float>,
  "factual":      <float>,
  "coherence":    <float>,
  "issues":       ["<short issue description>", ...],
  "suggestion":   "<one sentence improvement hint>"
}

Scoring guide:
  1.0 = perfect   0.8 = good   0.6 = adequate   0.4 = weak   0.2 = poor

Return only the JSON."""

# Heuristic signals
_SAFETY_KEYWORDS = [
    "kill", "bomb", "hack into", "steal", "illegal", "suicide method",
    "how to make a weapon", "exploit", "bypass security",
]
_INCOMPLETE_SIGNALS = [
    "todo", "...", "[insert", "[placeholder", "tbd", "coming soon",
    "i'll add", "will be added",
]
_INCOHERENT_SIGNALS = [
    "contradicts", "however earlier", "but above", "as stated but",
]


@dataclass
class CriticResult:
    alignment:    float = 0.7
    completeness: float = 0.7
    safety:       float = 1.0
    factual:      float = 0.7
    coherence:    float = 0.7
    issues:       list  = field(default_factory=list)
    suggestion:   str   = ""
    method:       str   = "heuristic"
    revision_needed: bool = False
    accept:          bool = True

    def __post_init__(self):
        self.overall = round(
            self.alignment * 0.30 +
            self.completeness * 0.20 +
            self.safety * 0.25 +
            self.factual * 0.15 +
            self.coherence * 0.10,
            3,
        )
        self.revision_needed = self.overall < REVISION_THRESHOLD or self.safety < 0.6
        self.accept = self.overall >= ACCEPT_THRESHOLD and self.safety >= 0.8

    def summary(self) -> str:
        return (
            f"overall={self.overall:.2f} "
            f"align={self.alignment:.2f} complete={self.completeness:.2f} "
            f"safety={self.safety:.2f} factual={self.factual:.2f} "
            f"coherence={self.coherence:.2f} "
            f"revision={self.revision_needed} accept={self.accept}"
        )

    def revision_prompt(self) -> str:
        """Build a revision instruction from the critique."""
        parts = []
        if self.issues:
            parts.append("Issues found: " + "; ".join(self.issues[:3]) + ".")
        if self.suggestion:
            parts.append("Suggestion: " + self.suggestion)
        if self.alignment < 0.6:
            parts.append("Ensure the response directly answers the original question.")
        if self.completeness < 0.6:
            parts.append("Address all parts of the request completely.")
        if self.factual < 0.6:
            parts.append("Add factual grounding or cite evidence for key claims.")
        if self.safety < 0.8:
            parts.append("Remove or rephrase any potentially harmful content.")
        return " ".join(parts) or "Improve the response quality and clarity."


class Critic:
    """Response critic. Instantiate once and reuse."""

    def __init__(self, router: Any = None):
        self.router = router
        self._revision_counts: dict[str, int] = {}  # task_id → revision count

    def critique_heuristic(self, response: str, task: str = "") -> CriticResult:
        """Fast heuristic critique — no LLM call."""
        t = response.lower()
        q = task.lower()

        # Safety check
        safety = 1.0
        for kw in _SAFETY_KEYWORDS:
            if kw in t:
                safety = 0.2
                break

        # Completeness check
        completeness = 0.7
        if any(sig in t for sig in _INCOMPLETE_SIGNALS):
            completeness -= 0.25
        word_count = len(response.split())
        if word_count < 10:
            completeness -= 0.20
        elif word_count > 50:
            completeness += 0.10

        # Alignment check — simple keyword overlap
        alignment = 0.7
        if q:
            q_words = set(q.split()) - {"the", "a", "an", "is", "what", "how", "why"}
            t_words = set(t.split())
            overlap = len(q_words & t_words) / max(len(q_words), 1)
            alignment = min(0.95, 0.5 + overlap * 0.6)

        # Coherence
        coherence = 0.8
        if any(sig in t for sig in _INCOHERENT_SIGNALS):
            coherence -= 0.20

        # Factual — presence of hedging without evidence
        factual = 0.70
        if any(w in t for w in ["source:", "according to", "reference", "study shows"]):
            factual += 0.15
        if any(w in t for w in ["i think", "i believe", "maybe", "perhaps"]):
            factual -= 0.10

        issues = []
        if safety < 0.6:      issues.append("Potential safety concern")
        if completeness < 0.5: issues.append("Response appears incomplete")
        if alignment < 0.5:    issues.append("Response may not address the question")
        if factual < 0.5:      issues.append("Factual grounding weak")

        return CriticResult(
            alignment=round(min(0.95, max(0.0, alignment)), 3),
            completeness=round(min(0.95, max(0.0, completeness)), 3),
            safety=round(safety, 3),
            factual=round(min(0.95, max(0.0, factual)), 3),
            coherence=round(min(0.95, max(0.0, coherence)), 3),
            issues=issues,
            method="heuristic",
        )

    async def critique(
        self,
        response: str,
        task: str = "",
        task_id: str = "",
        force_llm: bool = False,
    ) -> CriticResult:
        """Critique a response. Uses LLM if router available and score is borderline."""
        heuristic = self.critique_heuristic(response, task)
        log.debug("critic heuristic: %s", heuristic.summary())

        # Always use LLM critic for safety flags
        if heuristic.safety < 0.5:
            return heuristic

        # Skip LLM if clearly good or clearly bad (save tokens)
        if not force_llm and not self.router:
            return heuristic
        if not force_llm and (heuristic.overall > 0.85 or heuristic.overall < 0.25):
            return heuristic

        try:
            result = await self._llm_critique(response, task)
            # Blend: LLM 65%, heuristic 35%
            result.alignment    = round(result.alignment    * 0.65 + heuristic.alignment    * 0.35, 3)
            result.completeness = round(result.completeness * 0.65 + heuristic.completeness * 0.35, 3)
            result.safety       = min(result.safety, heuristic.safety)  # take the more conservative
            result.factual      = round(result.factual      * 0.65 + heuristic.factual      * 0.35, 3)
            result.coherence    = round(result.coherence    * 0.65 + heuristic.coherence    * 0.35, 3)
            result.method = "llm+heuristic"
            result.__post_init__()  # recalculate overall
            log.info("critic llm+heuristic: %s", result.summary())
            return result
        except Exception as exc:
            log.warning("critic: LLM critique failed, using heuristic: %s", exc)
            return heuristic

    def should_revise(self, result: CriticResult, task_id: str = "") -> bool:
        """Return True if revision is warranted and under the revision cap."""
        if not result.revision_needed:
            return False
        count = self._revision_counts.get(task_id, 0)
        if count >= MAX_REVISIONS:
            log.warning("critic: max revisions (%d) reached for task=%s", MAX_REVISIONS, task_id)
            return False
        self._revision_counts[task_id] = count + 1
        return True

    def reset_revision_count(self, task_id: str) -> None:
        self._revision_counts.pop(task_id, None)

    async def _llm_critique(self, response: str, task: str) -> CriticResult:
        messages = [
            {"role": "system", "content": LLM_CRITIC_SYSTEM},
            {"role": "user",   "content":
                f"TASK: {task[:400]}\n\nRESPONSE:\n{response[:1000]}\n\nCritique:"},
        ]
        if hasattr(self.router, "chat"):
            raw = await self.router.chat(messages, model="local")
        else:
            raw = await self.router.complete(
                "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages),
                model="local",
            )
        return _parse_llm_critique(raw)


# ── helpers ──────────────────────────────────────────────────────────────────

def _parse_llm_critique(raw: str) -> CriticResult:
    text = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("No JSON in critic response")
    data = json.loads(m.group(0))

    def _f(key: str, default: float = 0.7) -> float:
        return round(max(0.0, min(1.0, float(data.get(key, default)))), 3)

    return CriticResult(
        alignment=_f("alignment"),
        completeness=_f("completeness"),
        safety=_f("safety", 1.0),
        factual=_f("factual"),
        coherence=_f("coherence"),
        issues=list(data.get("issues", []))[:5],
        suggestion=str(data.get("suggestion", ""))[:300],
        method="llm",
    )
