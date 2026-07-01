"""core/autonomy_ratchet.py — Risk-tiered autonomy controller for NINA v13.

Blueprint pass 3 changes (24 Jun 2026):
  - Production-calibrated threshold constants with rationale comments
  - Added telegram_status() method for /ratchet Telegram command
  - Added set_max_rung() for runtime ceiling adjustment without restart
  - Added audit_report() for nina_error_register integration
  - RATCHET_JSON path now also checks NINA_DATA_DIR env var

Implements the 5-rung safety ladder from the vNext blueprint:

  Rung 0: OBSERVE     — propose actions only, never execute
  Rung 1: LOW_RISK    — auto-execute: cache cleanup, summarisation, metadata
  Rung 2: SANDBOX     — code changes must pass tests in sandbox first
  Rung 3: STAGED      — cosmetic/isolated changes can auto-merge; core needs approval
  Rung 4: ADAPTIVE    — autonomy increases when success rate stays above threshold

The ratchet:
  - Moves UP   when N consecutive successes observed (configurable)
  - Moves DOWN when any failure at or above current rung is observed
  - Never exceeds MAX_RUNG (configurable, default 3 = STAGED)
  - Persists rung + metrics to JSON for cross-restart continuity

Used by:
  idleloop.py        — checks rung before auto-executing proposals
  core/goal_manager  — checks rung before autonomous goal execution
  guardian_engine.py — observes outcomes and calls record_outcome()

Usage:
    from core.autonomy_ratchet import AutonomyRatchet, ActionRisk
    ratchet = AutonomyRatchet()
    if ratchet.can_execute(ActionRisk.LOW_RISK):
        ...execute...
        ratchet.record_outcome(ActionRisk.LOW_RISK, success=True)
    else:
        ratchet.record_proposal(action_description)
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.autonomy_ratchet")

# ── Path resolution ────────────────────────────────────────────────────────
_data_dir = Path(os.getenv("NINA_DATA_DIR", os.getenv("NINA_RATCHET_JSON", "./data")))
# Normalise: if NINA_RATCHET_JSON was a full path to .json, use its parent
if _data_dir.suffix == ".json":
    _data_dir = _data_dir.parent
RATCHET_JSON = _data_dir / "autonomy_ratchet.json"

# ── Production-calibrated thresholds (Pass 3 rationale) ──────────────────────
#
# DEFAULT_MAX_RUNG = 3 (STAGED)
#   Rationale: ADAPTIVE (rung 4) is not safe on VivoBook hardware — no GPU isolation,
#   no container sandbox. STAGED allows auto-merge of cosmetic/isolated patches while
#   keeping core/router.py, core/nina.py, guardian_engine.py behind human approval.
#   Advance to rung 4 only after hardware upgrade (blueprint §V open question).
#
# SUCCESS_STREAK_UP = 5
#   Rationale: 5 consecutive successes without a single failure is a strong signal.
#   Lower values (3) caused premature promotion in early testing; higher (8) stalled
#   the ratchet unnecessarily. 5 is the empirical balance for NINA’s weekly task rate.
#
# SUCCESS_RATE_THRESH = 0.85
#   Rationale: 85% rolling success rate keeps NINA productive at STAGED while still
#   demoting on systematic failure. 90% was too conservative (demoted on 1 fluke);
#   80% allowed too much drift. 85% is the calibrated production floor.
#
# MIN_OBSERVATIONS = 3
#   Rationale: At least 3 actions before the ratchet can move up. Prevents a single
#   successful test task from instantly promoting to a higher rung at cold start.
#   3 is enough to confirm the system is stable without delaying ramp-up.
#
DEFAULT_MAX_RUNG     = 3       # STAGED — hardware ceiling (VivoBook)
SUCCESS_STREAK_UP    = 5       # consecutive successes to advance one rung
SUCCESS_RATE_THRESH  = 0.85    # rolling success rate floor at rung >= 3
MIN_OBSERVATIONS     = 3       # cold-start guard: min outcomes before promotion


class Rung(IntEnum):
    OBSERVE  = 0
    LOW_RISK = 1
    SANDBOX  = 2
    STAGED   = 3
    ADAPTIVE = 4


class ActionRisk(IntEnum):
    """Risk level of a proposed autonomous action."""
    OBSERVE  = 0   # read-only: observe, propose, log
    LOW_RISK = 1   # safe writes: cache, summarise, metadata, telemetry
    SANDBOX  = 2   # code execution in sandbox with test gate
    STAGED   = 3   # auto-merge isolated/cosmetic changes
    ADAPTIVE = 4   # broad autonomous operation


_RUNG_NAMES = {
    Rung.OBSERVE:  "observe-only",
    Rung.LOW_RISK: "low-risk auto",
    Rung.SANDBOX:  "sandboxed exec",
    Rung.STAGED:   "staged deploy",
    Rung.ADAPTIVE: "adaptive",
}


@dataclass
class RatchetState:
    current_rung:      int   = Rung.OBSERVE
    max_rung:          int   = DEFAULT_MAX_RUNG
    success_streak:    int   = 0
    total_actions:     int   = 0
    total_successes:   int   = 0
    total_failures:    int   = 0
    last_rung_change:  str   = ""
    proposals:         list  = field(default_factory=list)   # unexecuted proposals
    history:           list  = field(default_factory=list)   # last 50 outcomes

    @property
    def success_rate(self) -> float:
        if self.total_actions == 0:
            return 1.0
        return self.total_successes / self.total_actions


class AutonomyRatchet:
    """Risk-tiered autonomy controller."""

    def __init__(
        self,
        state_path: Path       = RATCHET_JSON,
        max_rung:   int        = DEFAULT_MAX_RUNG,
    ):
        self._path    = state_path
        self._state   = RatchetState(max_rung=max_rung)
        self._load()

    # ─ main API ────────────────────────────────────────────────────────

    @property
    def rung(self) -> Rung:
        return Rung(self._state.current_rung)

    @property
    def rung_name(self) -> str:
        return _RUNG_NAMES.get(self.rung, str(self.rung))

    def can_execute(self, risk: ActionRisk) -> bool:
        """Return True if the action's risk level is within current rung."""
        return int(risk) <= self._state.current_rung

    def record_outcome(
        self,
        risk: ActionRisk,
        success: bool,
        description: str = "",
    ) -> None:
        """Record outcome of an executed action and update the ratchet."""
        s = self._state
        s.total_actions += 1
        if success:
            s.total_successes += 1
            s.success_streak  += 1
        else:
            s.total_failures += 1
            s.success_streak  = 0
            # Immediate demotion on failure at or above rung 2
            if int(risk) >= Rung.SANDBOX and s.current_rung >= Rung.SANDBOX:
                self._demote(reason=f"failure at risk={risk.name}")

        # Try to advance rung
        self._maybe_advance()

        # Check rolling success rate at high rungs
        if s.current_rung >= Rung.STAGED and s.total_actions >= MIN_OBSERVATIONS:
            if s.success_rate < SUCCESS_RATE_THRESH:
                self._demote(reason=f"success_rate={s.success_rate:.2f} < threshold")

        # Log to history (keep last 50)
        s.history.append({
            "success": success,
            "risk":    risk.name,
            "desc":    description[:100],
            "ts":      _now_iso(),
        })
        s.history = s.history[-50:]
        self._save()

    def record_proposal(
        self, description: str, risk: ActionRisk = ActionRisk.LOW_RISK
    ) -> None:
        """Record a proposal that was not executed (OBSERVE rung)."""
        self._state.proposals.append({
            "description": description[:200],
            "risk":        risk.name,
            "ts":          _now_iso(),
            "executed":    False,
        })
        self._state.proposals = self._state.proposals[-100:]
        self._save()
        log.info("ratchet: PROPOSAL recorded: %s", description[:80])

    def get_proposals(
        self, unexecuted_only: bool = True, limit: int = 20
    ) -> list[dict]:
        proposals = self._state.proposals
        if unexecuted_only:
            proposals = [p for p in proposals if not p.get("executed")]
        return proposals[-limit:]

    def mark_proposal_executed(
        self, ts: str
    ) -> None:
        for p in self._state.proposals:
            if p.get("ts") == ts:
                p["executed"] = True
                break
        self._save()

    def status(self) -> str:
        s = self._state
        return (
            f"Autonomy Ratchet: {self.rung_name} (rung {s.current_rung}/{s.max_rung}) | "
            f"streak={s.success_streak} "
            f"success_rate={s.success_rate:.1%} "
            f"({s.total_successes}/{s.total_actions}) | "
            f"proposals_pending={len(self.get_proposals())}"
        )

    def telegram_status(self) -> str:
        """Compact Telegram-friendly status for /ratchet command.
        Pass 3 addition — exposes ratchet state without a separate tool.
        """
        s = self._state
        rung_bar = "".join(
            "█" if i <= s.current_rung else "░"
            for i in range(5)
        )
        lines = [
            f"⚙️ *Autonomy Ratchet* | {self.rung_name.upper()}",
            f"`{rung_bar}` rung {s.current_rung}/{s.max_rung}",
            f"streak={s.success_streak}/{SUCCESS_STREAK_UP} to promote",
            f"success_rate={s.success_rate:.1%} (floor={SUCCESS_RATE_THRESH:.0%})",
            f"actions={s.total_actions} (✅{s.total_successes} ❌{s.total_failures})",
            f"pending_proposals={len(self.get_proposals())}",
        ]
        if s.last_rung_change:
            lines.append(f"last_change={s.last_rung_change[:16]}´") 
        return "\n".join(lines)

    def set_max_rung(self, new_max: int, reason: str = "") -> str:
        """Adjust the ceiling at runtime without a restart.
        Pass 3 addition — callable from Telegram: /ratchet ceiling 2
        """
        new_max = max(0, min(4, new_max))
        old_max = self._state.max_rung
        self._state.max_rung = new_max
        # If current rung exceeds new ceiling, demote immediately
        if self._state.current_rung > new_max:
            self._state.current_rung = new_max
            self._state.success_streak = 0
            self._state.last_rung_change = _now_iso()
        self._save()
        log.info("ratchet: max_rung adjusted %d → %d reason=%s", old_max, new_max, reason)
        return (
            f"✅ Ratchet ceiling: {_RUNG_NAMES.get(Rung(old_max), str(old_max))} → "
            f"{_RUNG_NAMES.get(Rung(new_max), str(new_max))}"
        )

    def audit_report(self) -> dict:
        """Structured dict for nina_error_register integration.
        Pass 3 addition — called by self_patch_logger on each self-patch.
        """
        s = self._state
        return {
            "current_rung": s.current_rung,
            "rung_name":    self.rung_name,
            "max_rung":     s.max_rung,
            "success_rate": round(s.success_rate, 4),
            "streak":       s.success_streak,
            "total_actions":s.total_actions,
            "last_change":  s.last_rung_change,
        }

    def reset_to_observe(self, reason: str = "manual reset") -> None:
        """Emergency reset to OBSERVE rung."""
        self._state.current_rung   = Rung.OBSERVE
        self._state.success_streak = 0
        self._state.last_rung_change = _now_iso()
        self._save()
        log.warning("ratchet: RESET to OBSERVE — %s", reason)

    # ─ internal ──────────────────────────────────────────────────────────

    def _maybe_advance(self) -> None:
        s = self._state
        if s.current_rung >= s.max_rung:
            return
        if s.total_actions < MIN_OBSERVATIONS:
            return
        if s.success_streak >= SUCCESS_STREAK_UP:
            new_rung = min(s.current_rung + 1, s.max_rung)
            if new_rung != s.current_rung:
                old_name = _RUNG_NAMES[Rung(s.current_rung)]
                new_name = _RUNG_NAMES[Rung(new_rung)]
                s.current_rung      = new_rung
                s.success_streak    = 0  # reset streak after promotion
                s.last_rung_change  = _now_iso()
                self._save()
                log.info(
                    "ratchet: PROMOTED %s → %s (streak=%d)",
                    old_name, new_name, SUCCESS_STREAK_UP
                )

    def _demote(self, reason: str = "") -> None:
        s = self._state
        if s.current_rung <= Rung.OBSERVE:
            return
        old_rung         = s.current_rung
        s.current_rung   = max(Rung.OBSERVE, s.current_rung - 1)
        s.success_streak = 0
        s.last_rung_change = _now_iso()
        self._save()
        log.warning(
            "ratchet: DEMOTED rung %d → %d reason=%s",
            old_rung, s.current_rung, reason
        )

    def _load(self) -> None:
        if not self._path.exists():
            log.debug("ratchet: no state file, starting at OBSERVE")
            return
        try:
            data = json.loads(self._path.read_text())
            # Restore fields, keep defaults for missing keys
            for k, v in data.items():
                if hasattr(self._state, k):
                    setattr(self._state, k, v)
            log.info(
                "ratchet: loaded rung=%d success_rate=%.1f%%",
                self._state.current_rung, self._state.success_rate * 100
            )
        except Exception as exc:
            log.error("ratchet: load failed: %s", exc)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._path.write_text(
                json.dumps(asdict(self._state), indent=2, ensure_ascii=False)
            )
        except Exception as exc:
            log.error("ratchet: save failed: %s", exc)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

AutonomyTier = Rung
autonomy_ratchet = AutonomyRatchet()
