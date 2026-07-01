"""NINA v14.3 — IdleProposalLoop (WIRE 5 / CORE-001)
Blueprint pass 2: added WAL VACUUM schedule (§ IV tension: 'Memory leakage')
Proposal-only mode: Nina analyses, logs a markdown brief, pings Telegram.
High-impact proposals are auto-promoted to jules_backlog.md as READY tasks.
No code generation. Human reviews Medium/Low via Perplexity, injects patch manually.

Pass 2 changes (24 Jun 2026):
  - Added _vacuum_schedule() coroutine: runs PRAGMA wal_checkpoint + VACUUM
    on all SQLite databases in data/ every 6 hours (configurable via
    config.vacuum_interval_h, default=6)
  - _loop() now spawns _vacuum_schedule() as a parallel asyncio.Task on init
"""
import asyncio
import logging
import time
import re
from pathlib import Path
from datetime import datetime

logger     = logging.getLogger("nina.idle")
PROPOSALS_DIR = Path("data/proposals")

ANALYSIS_PROMPTS = [
    ("tool_error_handling",
     "Analyse NINA's tool error handling (tools/*.py). Identify the single weakest point. "
     "Describe: 1) exact file + function, 2) what can go wrong, 3) suggested fix in plain English. "
     "No code. Be specific and concise."),
    ("morning_report",
     "Analyse NINA's morning report (core/nina.py → run_morning_report). Identify one concrete improvement. "
     "Describe: 1) what is missing or fragile, 2) why it matters, 3) suggested fix in plain English. No code."),
    ("provider_routing",
     "Analyse NINA's HybridRouter fallback logic (core/router.py). Identify one failure mode. "
     "Describe: 1) exact scenario where routing silently fails, 2) impact, 3) suggested fix in plain English. No code."),
    ("memory_context",
     "Analyse NINA's memory context building (core/memory.py → build_context). Identify one weakness. "
     "Describe: 1) what context is missed or stale, 2) impact on response quality, 3) suggested fix in plain English. No code."),
    ("scheduler_errors",
     "Analyse NINA's scheduler job error handling (crons/manager.py). Identify one gap. "
     "Describe: 1) which job type can fail silently, 2) what the consequence is, 3) suggested fix in plain English. No code."),
    ("telegram_interface",
     "Analyse NINA's Telegram interface (interfaces/telegram_interface.py). Identify one UX or reliability issue. "
     "Describe: 1) exact command or flow, 2) what breaks or feels rough, 3) suggested fix in plain English. No code."),
    ("config_robustness",
     "Analyse NINA's config loading (core/config.py + core/hotreload.py). Identify one fragility. "
     "Describe: 1) what env var or edge case is unhandled, 2) impact, 3) suggested fix in plain English. No code."),
]

class IdleProposalLoop:
    def __init__(self, config, router, telegram, pipeline=None):
        self.config        = config
        self.router        = router
        from core.quota_dispatcher import QuotaDispatcher
        self.dispatcher = QuotaDispatcher(self.router)
        if self.router:
            self.router.dispatcher = self.dispatcher
        self.telegram      = telegram
        # pipeline retained in signature for compat but never used
        self._last_user_ts: float = time.time()
        self._task: asyncio.Task | None = None
        self._vacuum_task: asyncio.Task | None = None
        _idx_file = Path("data/proposal_index.txt")
        try:
            self._prompt_index = int(_idx_file.read_text().strip())
        except Exception:
            self._prompt_index = 0
        PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        self._task = asyncio.create_task(self._loop(), name="nina.idle.proposals")
        self._vacuum_task = asyncio.create_task(
            self._vacuum_schedule(), name="nina.idle.wal_vacuum"
        )
        logger.info("IdleProposalLoop initialized (proposal-only + WAL vacuum)")

    def record_user_message(self):
        self._last_user_ts = time.time()

    def _is_idle(self) -> bool:
        return (time.time() - self._last_user_ts) / 60 >= self.config.idle_threshold_min

    def _is_quota_safe(self) -> bool:
        """Return False if all cloud providers are rate-limited or unavailable.
        Falls back to True (safe) if router state cannot be inspected, so
        we never block proposals due to an instrumentation error.
        """
        try:
            if not self.router:
                return False
            available = self.router.get_available_providers()
            if available is not None:
                return len(available) > 0
            cb = getattr(self.router, "circuit_breakers", None)
            if cb and isinstance(cb, dict):
                open_count = sum(1 for s in cb.values() if getattr(s, "is_open", False))
                total = len(cb)
                if total > 0 and open_count >= total:
                    return False
            return True
        except Exception as e:
            logger.debug(f"quota_safe_check_failed (non-blocking) {e}")
            return True

    # ------------------------------------------------------------------ #
    #  WAL VACUUM SCHEDULE  (Blueprint § IV — memory leakage tension fix) #
    # ------------------------------------------------------------------ #

    async def _vacuum_schedule(self) -> None:
        """Run PRAGMA wal_checkpoint(TRUNCATE) + VACUUM on every SQLite db
        in data/ every vacuum_interval_h hours (default 6).

        This resolves the blueprint §IV open tension:
        'Long-running warm memory (SQLite) — are old rows being vacuumed?'
        """
        interval_h = getattr(self.config, "vacuum_interval_h", 6)
        interval_s = interval_h * 3600
        # Stagger first run by 10 minutes to avoid contention at boot
        await asyncio.sleep(600)
        while True:
            try:
                dbs = list(Path("data").glob("**/*.db")) + list(Path("data").glob("**/*.sqlite"))
                if not dbs:
                    logger.info("wal_vacuum no sqlite dbs found — skipping")
                else:
                    for db_path in dbs:
                        try:
                            await asyncio.to_thread(_sqlite_vacuum, db_path)
                            logger.info("wal_vacuum done path=%s", db_path)
                        except Exception as exc:
                            logger.warning("wal_vacuum_failed path=%s err=%s", db_path, exc)
                    logger.info(
                        "wal_vacuum cycle_complete dbs=%d next_in=%dh",
                        len(dbs), interval_h
                    )
            except Exception as exc:
                logger.warning("wal_vacuum_schedule_error %s", exc)
            await asyncio.sleep(interval_s)

    async def _loop(self):
        while True:
            try:
                await asyncio.sleep(60)
                from tools.heartbeat import write_heartbeat; write_heartbeat("nina.service")
                if not self._is_idle():
                    continue
                import psutil
                ram_gb = psutil.virtual_memory().used / (1024 ** 3)
                if ram_gb >= self.config.ram_guard_gb:
                    logger.warning(f"idle_loop_skipped RAM={ram_gb:.1f}GB")
                    continue
                if not self._is_quota_safe():
                    logger.info("idle_loop_skipped all_providers_exhausted — waiting for quota reset")
                    continue
                logger.info("idle_loop_tick generating proposal brief")
                await self._generate_proposal()
                await asyncio.sleep(self.config.idle_report_min * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"idle_loop_error {e}")
                await asyncio.sleep(300)

    async def _promote_to_backlog(self, topic: str, analysis: str, impact: str) -> bool:
        """
        WIRE 5: Auto-promote High-impact proposals to jules_backlog.md as READY tasks.
        Only 'High' impact triggers promotion. Medium/Low remain pending for human review.
        """
        if impact.lower() != "high":
            return False
        backlog_path = Path("docs/space/jules_backlog.md")
        if not backlog_path.exists():
            logger.warning("idle_promote_skipped backlog_not_found")
            return False
        task_id = f"IDLE-{datetime.now().strftime('%Y%m%d-%H%M')}"
        category = topic.replace('_', ' ').title()
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        card = f"""
---

### {task_id} | Auto-Promoted by IdleLoop | {category}

**Status:** READY
**Impact:** {impact}
**Source:** idleloop auto-promotion — {ts}
**Topic:** {topic}

**Analysis:**
{analysis}

**Acceptance Criteria (Jules must verify):**
- Implement the highest-priority suggestion from the analysis above
- Touch only the file(s) explicitly named in the analysis
- Do NOT touch: `core/router.py`, `core/nina.py`, `guardian_engine.py`, `interfaces/telegram_interface.py`
- Guardian must PASS before PR is opened
- Add a log statement proving the fix is active at runtime

"""
        try:
            with open(backlog_path, "a") as f:
                f.write(card)
            logger.info(f"promoted to READY: task_id={task_id} topic={topic}")
            logger.info(f"idle_promoted_to_backlog task_id={task_id} topic={topic} impact={impact}")
            
            # Wire to native task queue
            try:
                from core.task_manager import TaskQueue, TaskSpec
                _tq = TaskQueue()
                _spec = TaskSpec(
                    task_id=task_id,
                    title=category,
                    body=analysis,
                    priority="P3",
                    tier="BACKLOG",
                    source="idleloop",
                    status="PENDING",
                    created_at=datetime.now().isoformat(),
                    dispatched_at="",
                    done_at="",
                    pr_number=0,
                    idempotency_key="",  # computed in __post_init__
                    tags=["idle", "backlog", topic],
                    target_files=[],
                    depends_on=[]
                )
                _tq.enqueue(_spec)
            except Exception as _e:
                logger.warning(f"idle_queue_enqueue_failed {_e}")

            return True
        except Exception as e:
            logger.warning(f"idle_promote_failed {e}")
            return False

    async def _generate_proposal(self):
        topic, prompt = ANALYSIS_PROMPTS[self._prompt_index % len(ANALYSIS_PROMPTS)]
        self._prompt_index += 1
        try:
            Path("data/proposal_index.txt").write_text(str(self._prompt_index))
        except Exception:
            pass
        try:

            # Ground the LLM with actual file list to prevent hallucination
            real_files = sorted(str(p.relative_to(Path("."))) for p in Path(".").rglob("*.py")
                if not any(x in str(p) for x in ["venv", ".venv", "__pycache__", "archive"]))
            file_list = "\n".join(real_files[:40])
            format_instructions = (
                "FORMAT REQUIREMENT:\n"
                "1) First line must be exactly 'IMPACT: High', 'IMPACT: Medium', or 'IMPACT: Low'.\n"
                "2) Followed by a short bullet list of candidate improvements.\n"
                "Keep it concise and do not include code."
            )
            grounded_prompt = f"{prompt}\n\nIMPORTANT: NINA's actual Python files are:\n{file_list}\nOnly reference files from this list.\n\n{format_instructions}"
            msgs = [{"role": "user", "content": grounded_prompt}]
            plan = self.dispatcher.dispatch(grounded_prompt, context=str(msgs))
            analysis = await plan.execute()
            logger.info(f"proposal detected: topic={topic}")

            impact = "Unknown"
            clean_analysis = analysis.strip()

            # Extract and remove impact line if present
            match = re.search(r"^IMPACT:\s*(High|Medium|Low)", clean_analysis, re.IGNORECASE | re.MULTILINE)
            if match:
                impact = match.group(1).title()
                clean_analysis = re.sub(r"(?i)^IMPACT:\s*(High|Medium|Low)\s*\n+", "", clean_analysis).strip()

            # Determine task_id up front so it's available for Telegram notification
            task_id = f"IDLE-{datetime.now().strftime('%Y%m%d-%H%M')}"

            # Append to single rolling daily file
            today = datetime.now().strftime("%Y-%m-%d")
            out   = PROPOSALS_DIR / f"{today}_proposals.md"
            ts    = datetime.now().strftime("%H:%M:%S")
            category = topic.replace('_', ' ').title()

            # WIRE 5: status line reflects promotion outcome
            promoted = await self._promote_to_backlog(topic, clean_analysis, impact)
            status_line = "auto-promoted to backlog ✅" if promoted else "pending — awaiting human review"

            entry = f"""
---

## [{ts}] {category} | Impact: {impact}

**Candidate Improvements:**
{clean_analysis}

**Status:** {status_line}
"""
            with open(out, "a") as f:
                if not out.exists() or out.stat().st_size == 0:
                    f.write(f"# NINA Daily Proposals — {today}\n")
                f.write(entry)
            logger.info(f"idle_proposal_appended topic={topic} file={out.name}")

            # WIRE 5: Telegram notification on successful promotion
            if promoted:
                logger.info(f"idle_backlog_promoted topic={topic} task_id={task_id}")
                if self.telegram:
                    try:
                        await self.telegram.send_message(
                            f"🧠 IdleLoop promoted a task to backlog\n"
                            f"*Topic:* {category}\n"
                            f"*Impact:* {impact}\n"
                            f"*Task ID:* {task_id}"
                        )
                    except Exception:
                        pass  # non-critical

        except Exception as e:
            logger.warning(f"idle_proposal_failed {e}")

    async def manually_promote_latest(self) -> str:
        """Manually promote the most recent pending proposal regardless of impact level.
        Callable from Telegram: /idle promote
        """
        files = sorted(PROPOSALS_DIR.glob("*.md"), reverse=True)
        if not files:
            return "No proposals found."
        latest = files[0]
        try:
            text = latest.read_text(encoding="utf-8")
        except Exception as e:
            return f"Could not read {latest.name}: {e}"

        # Extract last proposal block (after final ---)
        blocks = re.split(r"\n---\n", text)
        last_block = blocks[-1].strip() if blocks else ""
        if not last_block:
            return f"No proposal blocks found in {latest.name}."

        # Extract topic/category from heading
        heading_match = re.search(r"## \[.*?\] (.+?) \| Impact:", last_block)
        topic_raw = heading_match.group(1).strip() if heading_match else "unknown"
        topic = topic_raw.lower().replace(" ", "_")

        # Extract analysis (Candidate Improvements block)
        analysis_match = re.search(r"\*\*Candidate Improvements:\*\*\n(.+?)\n\n\*\*Status:", last_block, re.DOTALL)
        analysis = analysis_match.group(1).strip() if analysis_match else last_block

        # Force High to bypass the impact guard
        promoted = await self._promote_to_backlog(topic, analysis, "High")
        if promoted:
            return f"✅ Manually promoted `{topic_raw}` from {latest.name} to Jules backlog."
        return "❌ Promotion failed — check that docs/space/jules_backlog.md exists."

    async def show_idle_queue(self) -> str:
        files = sorted(PROPOSALS_DIR.glob("*.md"), reverse=True)[:10]
        if not files:
            return "No proposals yet."
        lines = [f"📋 Last {len(files)} proposals:"]
        for f in files:
            lines.append(f"• `{f.name}`")
        return "\n".join(lines)


def _sqlite_vacuum(db_path: Path) -> None:
    """Synchronous SQLite WAL checkpoint + VACUUM.
    Wrapped in asyncio.to_thread() — must not be called on the event loop.
    """
    import sqlite3
    conn = sqlite3.connect(str(db_path), timeout=10)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("VACUUM")
        conn.commit()
    finally:
        conn.close()


# Alias so core/nina.py import stays unchanged
IdleUpgradeLoop = IdleProposalLoop
