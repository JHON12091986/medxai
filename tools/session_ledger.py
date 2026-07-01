import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
import hashlib
import logging

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"
LEDGER_FILE = DATA_DIR / "session_ledger.json"


@dataclass
class SessionLedger:
    tool: str
    task_id: str = ""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    ended_at: str | None = None
    status: str = "active"
    plan: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    mistakes: list[dict] = field(default_factory=list)
    resume_hint: str = ""

    def __post_init__(self):
        # We don't save immediately on init according to instructions "Saves immediately" from nf session start,
        # but _save() should be called manually or in __init__ if required. The instructions say "__init__ ... Loads existing ledger file (creates empty list if missing) ... Never raises".
        # But since we use dataclasses, we'll do the loading logic implicitly or in save.
        pass

    def set_plan(self, steps: list[str]) -> None:
        self.plan = steps
        logger.debug(f"Plan set to: {self.plan}")
        self._save()

    def log_step(self, step: int, action: str, outcome: str, detail: str = "") -> None:
        self.trace.append({
            "step": step,
            "action": action,
            "outcome": outcome,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        if outcome == "failure":
            self._auto_register_mistake(step, action, detail)
        self._save()

    def _auto_register_mistake(self, step: int, action: str, detail: str) -> None:
        fingerprint = hashlib.sha256(f"{action[:40]}:{detail[:40]}".encode()).hexdigest()[:12]

        for mistake in self.mistakes:
            if mistake["fingerprint"] == fingerprint:
                mistake["seen_count"] += 1
                return

        self.mistakes.append({
            "fingerprint": fingerprint,
            "description": detail or f"Failed to execute: {action}",
            "trigger": action,
            "avoid": f"Do not attempt: {action[:80]}",
            "seen_count": 1
        })
        self._save()

    def register_mistake(self, description: str, trigger: str, avoid: str) -> None:
        fingerprint = hashlib.sha256(f"{trigger[:40]}:{description[:40]}".encode()).hexdigest()[:12]

        for mistake in self.mistakes:
            if mistake["fingerprint"] == fingerprint:
                mistake["seen_count"] += 1
                self._save()
                return

        self.mistakes.append({
            "fingerprint": fingerprint,
            "description": description,
            "trigger": trigger,
            "avoid": avoid,
            "seen_count": 1
        })
        self._save()

    def set_resume_hint(self, hint: str) -> None:
        self.resume_hint = hint
        self._save()

    def complete(self, status: str = "completed") -> None:
        self.ended_at = datetime.utcnow().isoformat() + "Z"
        self.status = status
        self._save()

    def _save(self) -> None:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            ledgers = []
            if LEDGER_FILE.exists():
                try:
                    with open(LEDGER_FILE, "r") as f:
                        ledgers = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to read ledger file: {e}")
                    ledgers = []

            # Find and replace, or append
            found = False
            for i, ledger_data in enumerate(ledgers):
                if ledger_data.get("session_id") == self.session_id:
                    ledgers[i] = asdict(self)
                    found = True
                    break

            if not found:
                ledgers.append(asdict(self))

            # Trim to 50
            ledgers = ledgers[-50:]

            # Atomic write
            tmp_file = DATA_DIR / "session_ledger.tmp"
            with open(tmp_file, "w") as f:
                json.dump(ledgers, f, indent=2)
            os.replace(tmp_file, LEDGER_FILE)

        except Exception as e:
            logger.warning(f"Failed to save ledger: {e}")


def get_active_session(tool: str) -> SessionLedger | None:
    if not LEDGER_FILE.exists():
        return None

    try:
        with open(LEDGER_FILE, "r") as f:
            ledgers = json.load(f)

        # Find last session with tool==tool and status=='active'
        for ledger_data in reversed(ledgers):
            if ledger_data.get("tool") == tool and ledger_data.get("status") == "active":
                # Create SessionLedger object
                return SessionLedger(**ledger_data)

    except Exception as e:
        logger.warning(f"Failed to read ledger file in get_active_session: {e}")

    return None


def audit_sessions() -> str:
    from tools.append_log import append_to_log as append_log
    from datetime import timezone

    ledgers = []
    if LEDGER_FILE.exists():
        try:
            with open(LEDGER_FILE, "r") as f:
                ledgers = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read ledger file: {e}")
            ledgers = []

    orphans = []
    sync_failed = []
    ORPHAN_THRESHOLD_HOURS = 2
    now = datetime.now(timezone.utc)

    # Identify orphaned sessions
    for ledger in ledgers:
        status = ledger.get("status")
        if status == "active":
            started_at_str = ledger.get("started_at")
            if started_at_str:
                try:
                    clean_str = started_at_str.replace("Z", "+00:00") if started_at_str.endswith("Z") else started_at_str
                    started_dt = datetime.fromisoformat(clean_str)
                    if started_dt.tzinfo is None:
                        started_dt = started_dt.replace(tzinfo=timezone.utc)
                    
                    if (now - started_dt).total_seconds() > ORPHAN_THRESHOLD_HOURS * 3600:
                        orphans.append(ledger)
                except Exception as e:
                    logger.warning(f"Failed to parse started_at: {started_at_str}, error: {e}")

    # Identify sync-failed sessions
    has_sync_field = False
    for ledger in ledgers:
        if ledger.get("status") != "active":
            if "sync_ok" in ledger:
                has_sync_field = True
                if ledger.get("sync_ok") is False:
                    sync_failed.append(ledger)
            elif "sync_failed" in ledger:
                has_sync_field = True
                if ledger.get("sync_failed") is True:
                    sync_failed.append(ledger)

    # For each orphaned session, correct status, persist, and log the correction
    for orphan in orphans:
        try:
            session_obj = SessionLedger(**orphan)
            session_obj.status = "orphaned"
            session_obj._save()
            try:
                append_log()
            except Exception as e:
                logger.warning(f"Failed to call append_log: {e}")
        except Exception as e:
            logger.warning(f"Failed to correct and save orphan session: {e}")

    # Build and return formatted report
    now_bd_str = datetime.now().strftime('%Y-%m-%d %H:%M BD')
    report = "🔍 Session Ledger Audit\n"
    report += f"Run: {now_bd_str}\n"
    report += f"Orphaned sessions found: {len(orphans)}\n"
    for orphan in orphans:
        report += f"  ⚠️ {orphan.get('session_id')} — open since {orphan.get('started_at')}\n"

    if not has_sync_field:
        report += "Sync-failed sessions: sync_ok field absent\n"
    else:
        report += f"Sync-failed sessions: {len(sync_failed)}\n"
        for sf in sync_failed:
            closed_at = sf.get("ended_at") or sf.get("closed_at") or "unknown"
            report += f"  ❌ {sf.get('session_id')} — closed at {closed_at}\n"

    report += f"\n✅ Audit complete. {len(orphans)} records corrected."
    return report

