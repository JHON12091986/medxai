"""
core/gap_analysis.py — NINA Gap Analysis Engine

When a user proposes a feature or upgrade, this module intercepts the request,
runs a structured cost-benefit analysis via the router, sends a scored report
to the user via Telegram, and implements a feedback loop before any work begins.

Flow:
  User message → is_feature_request() check
    YES → analyze() → GapReport → send to Telegram → await feedback
    NO  → pass through to normal agent/router
  User replies "yes" / "no" / modified request → _handle_gap_response()
"""

import re
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.router import HybridRouter
    from core.task_classifier import ClassifiedTask

logger = logging.getLogger("nina.gap_analysis")

# ── Trigger detection ─────────────────────────────────────────────────────────

FEATURE_TRIGGERS = [
    "add ", "implement ", "build ", "create ", "integrate ", "enable ",
    "introduce ", "support for", "make nina", "nina should", "can nina",
    "i want nina", "could nina", "new feature", "new capability",
    "hardcode ", "develop ", "upgrade", "extend ", "plug in",
    "hook into", "connect ", "wire up", "attach ", "wrap ",
]

# Phrases that look like feature requests but are really questions/status checks
FEATURE_EXEMPTIONS = [
    "how does", "what does", "what is", "status", "show me",
    "check if", "does nina", "is nina", "list ", "print ",
]

# ── Prompt ────────────────────────────────────────────────────────────────────

_GAP_ANALYSIS_PROMPT = """You are NINA's internal architecture reviewer performing a GAP ANALYSIS.

## Feature Request
{goal}

## Your Task
Analyse this against NINA's current architecture. Be specific about existing modules.
Output EXACTLY these sections, in this order:

### CURRENT STATE
What NINA currently does in this area (2-3 bullets, cite actual files/classes if known).

### TARGET STATE
What the proposed feature would add or change (2-3 bullets).

### GAP
What is missing between current and target. Label it: ADDITIVE | BREAKING | REFACTOR.

### BENEFIT SCORE: X/10
Score + one-sentence justification. Consider: user value, reliability, autonomy gain.

### RISK SCORE: X/10
Score + one-sentence justification. Consider: stability, blast radius, maintenance cost.

### EFFORT ESTIMATE
One of: Low / Medium / High — plus reason in one sentence.

### VERDICT: PROCEED | REVIEW | REJECT
One word verdict, then one sentence rationale.

Keep total response under 350 words. Be direct and technical — no padding.
"""

# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class GapReport:
    goal: str
    current_state: str = ""
    target_state: str = ""
    gap_type: str = "ADDITIVE"
    benefit_score: int = 5
    risk_score: int = 5
    effort: str = "Medium"
    verdict: str = "REVIEW"
    rationale: str = ""
    raw: str = ""

    @property
    def auto_proceed(self) -> bool:
        """Skip user confirmation if high benefit, low risk, and clear PROCEED verdict."""
        return (
            self.verdict == "PROCEED"
            and self.benefit_score >= 7
            and self.risk_score <= 3
        )

    def to_telegram(self) -> str:
        verdict_emoji = {"PROCEED": "✅", "REVIEW": "⚠️", "REJECT": "❌"}.get(self.verdict, "⚠️")
        gap_emoji = {"ADDITIVE": "➕", "BREAKING": "💥", "REFACTOR": "🔄"}.get(self.gap_type, "🔍")
        goal_preview = self.goal[:100] + ("..." if len(self.goal) > 100 else "")

        lines = [
            "🔍 *GAP ANALYSIS*",
            "",
            f"_{goal_preview}_",
            "",
            f"📈 Benefit: `{self.benefit_score}/10`  |  ⚠️ Risk: `{self.risk_score}/10`  |  ⏱ Effort: `{self.effort}`",
            f"{gap_emoji} Change type: `{self.gap_type}`",
            "",
            f"{verdict_emoji} *Verdict: {self.verdict}*",
            f"_{self.rationale}_",
            "",
            "Reply *yes* to proceed · *no* to cancel · or describe modifications",
        ]
        return "\n".join(lines)

    def to_auto_proceed_note(self) -> str:
        return (
            f"✅ *Gap analysis complete — auto-proceeding*\n"
            f"Benefit `{self.benefit_score}/10` · Risk `{self.risk_score}/10` · Effort `{self.effort}`\n"
            f"_{self.rationale}_"
        )

# ── Engine ────────────────────────────────────────────────────────────────────

class GapAnalysisEngine:
    """
    Intercepts feature/upgrade requests, runs structured analysis,
    and gates execution on user confirmation.
    """

    def __init__(self, router: "HybridRouter") -> None:
        self.router = router

    def is_feature_request(self, text: str) -> bool:
        """
        Returns True if the message looks like a feature/upgrade request.
        Excludes status checks and questions.
        """
        t = text.lower().strip()
        if any(exc in t for exc in FEATURE_EXEMPTIONS):
            return False
        return any(kw in t for kw in FEATURE_TRIGGERS)

    async def analyze(self, goal: str, task: "ClassifiedTask") -> GapReport:
        """
        Run gap analysis on a feature request.
        Sends the structured prompt to the router and parses the structured response.
        """
        prompt = _GAP_ANALYSIS_PROMPT.format(goal=goal)
        msgs = [{"role": "user", "content": prompt}]

        try:
            raw = await self.router.route(prompt, msgs, task, force_local=False)
        except Exception as e:
            logger.warning(f"gap_analysis_router_failed: {e}")
            return GapReport(
                goal=goal,
                verdict="REVIEW",
                rationale="Analysis failed — manual review required before proceeding.",
                raw=str(e),
            )

        report = GapReport(goal=goal, raw=raw)
        self._parse(raw, report)
        logger.info(
            f"gap_analysis_done verdict={report.verdict} "
            f"benefit={report.benefit_score} risk={report.risk_score} effort={report.effort}"
        )
        return report

    # ── Parser ─────────────────────────────────────────────────────────────────

    def _parse(self, raw: str, report: GapReport) -> None:
        """Extract structured fields from LLM response."""

        m = re.search(r"BENEFIT SCORE:\s*(\d+)/10", raw, re.IGNORECASE)
        if m:
            report.benefit_score = min(10, max(0, int(m.group(1))))

        m = re.search(r"RISK SCORE:\s*(\d+)/10", raw, re.IGNORECASE)
        if m:
            report.risk_score = min(10, max(0, int(m.group(1))))

        m = re.search(r"EFFORT ESTIMATE[:\s]+(Low|Medium|High)", raw, re.IGNORECASE)
        if m:
            report.effort = m.group(1).capitalize()

        m = re.search(r"\b(ADDITIVE|BREAKING|REFACTOR)\b", raw, re.IGNORECASE)
        if m:
            report.gap_type = m.group(1).upper()

        m = re.search(r"VERDICT[:\s]*(PROCEED|REVIEW|REJECT)", raw, re.IGNORECASE)
        if m:
            report.verdict = m.group(1).upper()

        # Rationale: sentence on the same line as VERDICT, after the keyword
        m = re.search(
            r"VERDICT[:\s]*(?:PROCEED|REVIEW|REJECT)[^\w\n]+(.*?)(?:\n|$)",
            raw, re.IGNORECASE
        )
        if m:
            report.rationale = m.group(1).strip().rstrip(".")
        elif raw:
            # Fallback: last non-empty sentence
            sentences = [s.strip() for s in raw.split(".") if len(s.strip()) > 15]
            report.rationale = sentences[-1] if sentences else "Review the analysis above."
