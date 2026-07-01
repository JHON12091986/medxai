# ruff: noqa: E402
"""
NINA v12 — TaskScheduler (Stage 5)
11 core jobs. APScheduler-based.
"""
import functools # verified
import logging
from crons.backup_jobs import run_memory_backup, run_py_backup
from tools.market import check_alerts
# Jules pipeline is now managed by ninajulesgithub.service (standalone daemon)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Hard constraint (cron.lambda_coroutine_drop): Do not use lambda wrappers for async job callables.
# Lambda wrappers drop coroutine execution. Use functools.partial or pass the coroutine directly.

logger = logging.getLogger("nina.scheduler")


import asyncio
import signal
import time
import json
from datetime import datetime, timezone

from crons.registry import CronJob
CRON_JOB = CronJob(
    id='manager',
    name='Manager',
    schedule='0 * * * *',
    module='crons.manager',
    description='APScheduler manager for legacy tasks'
)

from pathlib import Path
import traceback
import os

_job_metrics = {}
_active_scheduler = None
DATA_DIR = Path(__file__).parent.parent.resolve() / "data"

def get_job_metrics():
    return _job_metrics

def save_cron_health(scheduler=None):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        health_file = DATA_DIR / "cron_health.json"
        
        output_metrics = {}
        for job_id, metrics in _job_metrics.items():
            output_metrics[job_id] = dict(metrics)
            if scheduler and scheduler._sched:
                job = scheduler._sched.get_job(job_id)
                if job:
                    output_metrics[job_id]["next_run"] = str(job.next_run_time).split(".")[0] if job.next_run_time else "None"
                    output_metrics[job_id]["schedule"] = str(job.trigger) if job.trigger else "None"
                else:
                    output_metrics[job_id]["next_run"] = metrics.get("next_run", "None")
                    output_metrics[job_id]["schedule"] = metrics.get("schedule", "None")
            else:
                output_metrics[job_id]["next_run"] = metrics.get("next_run", "None")
                output_metrics[job_id]["schedule"] = metrics.get("schedule", "None")

        tmp_file = DATA_DIR / "cron_health.tmp"
        with open(tmp_file, "w") as f:
            json.dump(output_metrics, f, indent=2)
        os.replace(tmp_file, health_file)
    except Exception as e:
        logger.warning(f"Failed to save cron health metrics: {e}")

def _wrap_job(job_id, func):
    if job_id not in _job_metrics:
        _job_metrics[job_id] = {
            "duration_seconds": 0.0,
            "last_run": None,
            "last_success": None,
            "last_failure": None,
            "fail_count": 0,
            "status": "PENDING",
            "last_error": None
        }

    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False
        error_msg = None
        now_str = datetime.now(timezone.utc).isoformat().split(".")[0] + "Z"
        _job_metrics[job_id]["last_run"] = now_str
        try:
            if asyncio.iscoroutinefunction(func) or (isinstance(func, functools.partial) and asyncio.iscoroutinefunction(func.func)):
                res = await func(*args, **kwargs)
            else:
                res = func(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    res = await res
            success = True
            return res
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Job {job_id} failed: {traceback.format_exc()}")
            raise
        finally:
            duration = time.time() - start_time
            _job_metrics[job_id]["duration_seconds"] = round(duration, 3)
            if success:
                _job_metrics[job_id]["last_success"] = now_str
                _job_metrics[job_id]["status"] = "SUCCESS"
                _job_metrics[job_id]["last_error"] = None
            else:
                _job_metrics[job_id]["last_failure"] = now_str
                _job_metrics[job_id]["status"] = "FAILED"
                _job_metrics[job_id]["fail_count"] += 1
                _job_metrics[job_id]["last_error"] = error_msg

            # Save metrics persistently
            save_cron_health(_active_scheduler)

            logger.info(json.dumps({
                "event": "job_run",
                "job": job_id,
                "duration": duration,
                "success": success,
                "error": error_msg
            }), extra={"cron_module": "cron", "job_id": job_id})

    return wrapper

async def _model_discovery_job(nina_os):
    # Wait 30s before the first run. The IntervalTrigger doesn't run immediately on start usually,
    # or if we schedule it now it might, but doing an asyncio.sleep(30) in the job itself is one way.
    # Actually, the requirement specifically says "startup delay via asyncio.sleep(30)".
    # Let's add a sleep if it's not the first run? No, just sleep(30) then discover_all() inside the job?
    # Wait, if we sleep 30s on every interval run, that's fine. It's just a background job.
    await asyncio.sleep(30)
    await nina_os.router._model_discovery.discover_all()

async def _cache_purge_job(nina_os):
    nina_os.router.cache.purge_expired()

async def _jules_watchdog_job():
    try:
        from tools.jules import check_pipeline_watchdog
        await check_pipeline_watchdog()
    except Exception as e:
        logger.error(f"Jules pipeline watchdog job failed: {e}")

async def _ooda_cycle_job():
    try:
        from tools import nina_ooda
        await nina_ooda.ooda_cycle()
    except Exception as e:
        logger.error(f"OODA cycle job failed: {e}")

async def _cicd_cycle_job():
    try:
        from tools import nina_cicd
        await nina_cicd.run_cicd_cycle()
    except Exception as e:
        logger.error(f"CICD cycle job failed: {e}")

async def check_heartbeats(nina_os):
    import pathlib
    import json
    import datetime
    repo_root = pathlib.Path(__file__).parent.parent.resolve()
    hb_file = repo_root / "data" / "heartbeats.json"
    if not hb_file.exists():
        return
    try:
        with open(hb_file, "r") as f:
            data = json.load(f)
    except Exception:
        return
        
    now = datetime.datetime.utcnow()
    for name, ts_str in data.items():
        age = None
        unresponsive = False
        if ts_str is None:
            unresponsive = True
            age = "unknown"
        else:
            try:
                clean_ts = ts_str.rstrip('Z')
                ts = datetime.datetime.fromisoformat(clean_ts)
                age = (now - ts).total_seconds()
                if age > 300:
                    unresponsive = True
            except Exception:
                unresponsive = True
                age = "unknown"
                
        if unresponsive:
            msg = f"🚨 NINA Heartbeat Alert\nService `{name}` missed heartbeats for {age}s!\nStatus: UNRESPONSIVE."
            try:
                await nina_os.telegram.send_message(msg)
            except Exception as e:
                logger.error(f"Failed to send heartbeat alert: {e}")
                
            # Trigger immediate autonomous self-healing via OODA cycle
            try:
                from tools import nina_ooda
                logger.info(f"Unresponsive service `{name}` detected. Triggering immediate self-healing OODA cycle...")
                asyncio.create_task(nina_ooda.ooda_cycle())
            except Exception as oe:
                logger.error(f"Failed to trigger self-healing OODA cycle: {oe}")

async def _session_ledger_audit_job():
    try:
        from tools.session_ledger import audit_sessions
        audit_sessions()
    except Exception as e:
        logger.error(f"Session ledger audit job failed: {e}")

async def _daily_discoverability_wiring_audit_job():
    try:
        import subprocess
        res = subprocess.run(
            ["bash", "agy_task.sh", ".jules/tasks/daily_discoverability_wiring_audit.md"],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            logger.error(f"daily_discoverability_wiring_audit_job failed: {res.stderr}")
    except Exception as e:
        logger.error(f"daily_discoverability_wiring_audit_job failed: {e}")

class TaskScheduler:
    def __init__(self, nina_os):
        global _active_scheduler
        self.nina = nina_os
        self._sched = AsyncIOScheduler(timezone="Asia/Dhaka")
        _active_scheduler = self

    def add(self, func, trigger, id, **kwargs):
        existing_job = self._sched.get_job(id)
        if existing_job:
            logger.info(f"Job {id} already exists. Rescheduling...")
            return self._sched.reschedule_job(id, trigger=trigger)
        return self._sched.add_job(_wrap_job(id, func), trigger, id=id, **kwargs)

    def start(self):
        n = self.nina
        add = self.add

        add(n.run_morning_report,    CronTrigger(hour=9,  minute=0,  timezone="Asia/Dhaka"), id="morning_report")
        add(n.run_heartbeat,         IntervalTrigger(hours=1),                               id="heartbeat")
        add(functools.partial(_cache_purge_job, n), CronTrigger(hour=3, minute=5, timezone="Asia/Dhaka"), id="cache_purge")
        add(n.run_cost_report,       CronTrigger(hour=23, minute=0,  timezone="Asia/Dhaka"), id="cost_report")
        add(n.run_circuit_breaker_stats, CronTrigger(hour=4,  minute=20, timezone="Asia/Dhaka"), id="circuit_breaker_stats")
        add(n.router.reset_daily, CronTrigger(hour=0, minute=1, second=0,
                                              timezone="UTC"),                                  id="rate_limit_reset")
        add(n.run_idle_summary,      IntervalTrigger(minutes=30),                            id="idle_summary")
        add(n.run_log_rotation,      CronTrigger(hour=4,  minute=0,  timezone="Asia/Dhaka"), id="log_rotation")
        add(n.run_provider_health,   IntervalTrigger(hours=6),                               id="provider_health")
        add(n.run_provider_hunter,   CronTrigger(hour=2,  minute=0,  timezone="Asia/Dhaka"), id="provider_hunter")
        add(n.run_thermal_health,    IntervalTrigger(minutes=5),                             id="thermal_health")
        add(functools.partial(run_memory_backup, n), CronTrigger(hour=2, minute=30, timezone="Asia/Dhaka"), id="memory_backup")
        add(functools.partial(run_py_backup, n),     CronTrigger(hour=3, minute=0,  timezone="Asia/Dhaka"), id="py_backup")
        from core.reminders import check_and_fire
        add(functools.partial(check_and_fire, send_fn=n.telegram.send_message), IntervalTrigger(minutes=1), id="reminder_check")
        add(functools.partial(check_alerts, n), CronTrigger(hour="10-14", minute="*/30", day_of_week="sun-thu", timezone="Asia/Dhaka"), id="market_monitor")

        # GAP-06 — Orchestrator + Kernel Wiring
        try:
            from core.gap_scanner.scanner import GapScanner as _GapScanner
            self._gap_scanner = _GapScanner(
                telemetry_path="telemetry.jsonl",
                register_path="docs/space/nina_error_register.md",
                backlog_path="docs/space/jules_backlog.md"
            )
            add(
                self._gap_scanner.run_cycle,
                trigger=IntervalTrigger(minutes=5),
                id="gap_scanner",
                replace_existing=True,
                max_instances=1,
                misfire_grace_time=60
            )
        except Exception as e:
            logger.error(f"Failed to start GapScanner: {e}")

        # Ensure core crons are started:


        add(functools.partial(_model_discovery_job, n), IntervalTrigger(hours=24), id="model_discovery")
        add(n.pipeline._expire_pending,            IntervalTrigger(minutes=15), id="expire_pending")
        add(_jules_watchdog_job,                   IntervalTrigger(minutes=15), id="jules_watchdog")
        add(_ooda_cycle_job,                       IntervalTrigger(minutes=30), id="nina_ooda_cycle")
        add(_cicd_cycle_job,                       IntervalTrigger(minutes=60), id="nina_cicd_cycle")
        add(functools.partial(check_heartbeats, n), IntervalTrigger(minutes=5), id="heartbeat_watchdog")
        add(functools.partial(run_hourly_quota_suggestion, n), IntervalTrigger(hours=1), id="hourly_quota_suggestion")
        add(functools.partial(run_autonomous_evolution_cycle, n), IntervalTrigger(minutes=15), id="autonomous_evolution")
        add(_session_ledger_audit_job,             IntervalTrigger(hours=2), id="session_ledger_audit")
        add(_stale_pr_cleanup_job,                 IntervalTrigger(hours=24), id="stale_pr_cleanup")
        add(_daily_discoverability_wiring_audit_job, CronTrigger(hour=2, minute=0, timezone="Asia/Dhaka"), id="daily_wiring_audit")

        add(functools.partial(_jules_audit_job, n), CronTrigger(day_of_week="sun", hour=0, minute=0, timezone="Asia/Dhaka"), id="jules_audit")
        add(functools.partial(_healthcheck_job, n), IntervalTrigger(hours=6), id="nina_healthcheck")

        # Initialize metric entries for all jobs so they exist immediately on start
        for job in self._sched.get_jobs():
            if job.id not in _job_metrics:
                _job_metrics[job.id] = {
                    "duration_seconds": 0.0,
                    "last_run": None,
                    "last_success": None,
                    "last_failure": None,
                    "fail_count": 0,
                    "status": "PENDING",
                    "last_error": None
                }
        save_cron_health(self)

        self._sched.start()
        logger.info(f"Scheduler started — {len(self._sched.get_jobs())} jobs", extra={"cron_module": "cron", "job_id": "manager"})
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._handle_shutdown_signal, sig)
        except (NotImplementedError, RuntimeError) as e:
            logger.warning(f"Could not setup signal handlers: {e}", extra={"cron_module": "cron", "job_id": "manager"})

    def _handle_shutdown_signal(self, sig):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...", extra={"cron_module": "cron", "job_id": "manager"})
        self.shutdown(wait=False)
        # Cancel all running tasks to release locks and terminate the event loop
        for task in asyncio.all_tasks():
            task.cancel()

    def shutdown(self, wait=False):
        self._sched.shutdown(wait=wait)

    def next_job_time(self, job_id: str) -> str:
        job = self._sched.get_job(job_id)
        return str(job.next_run_time) if job else "unknown"

    @property
    def job_count(self): return len(self._sched.get_jobs())

async def run_hourly_quota_suggestion(nina_os):
    """
    Intelligently monitors quotas (Gemini, Groq, and Jules session counts)
    and lists of ready tasks from jules_backlog.md to deliver hourly
    proactive suggestions to Telegram.
    """
    try:
        from tools.jules import load_registry, send_telegram
        from tools.ninaflash_core import get_backlog_tasks
        
        # 1. Check Jules tasks today
        reg = load_registry()
        completed_today_count = 0
        active_count = 0
        now_utc = datetime.now(timezone.utc)
        start_of_today = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for s in reg.values():
            status = s.get("status")
            created_str = s.get("created_at")
            if created_str:
                try:
                    created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    if created_dt >= start_of_today:
                        if status in ("COMPLETED", "FAILED", "DUPLICATE"):
                            completed_today_count += 1
                        elif status in ("IN_PROGRESS", "AWAITING_USER_FEEDBACK"):
                            active_count += 1
                except Exception:
                    pass
                    
        # Total daily jules session target limit is 100
        jules_limit = 100
        used_jules = completed_today_count + active_count
        remaining_jules = max(0, jules_limit - used_jules)
        
        # 2. Extract READY tasks from jules_backlog
        all_tasks = get_backlog_tasks()
        ready_tasks = [t for t in all_tasks if t.get("status") == "READY"]
        
        # 3. Retrieve LLM Provider Health & Quotas
        provider_status_lines = []
        for pid in ["GEMINI", "GROQ"]:
            h = nina_os.router.health.get(pid)
            if h:
                usage = nina_os.router.quota_router.get_provider_usage(pid)
                reqs = h.requests_today
                # Visual bar representation
                filled = min(5, int(usage * 5))
                bar = "▓" * filled + "░" * (5 - filled)
                provider_status_lines.append(f"📡 *{pid}*: {bar} {usage*100:.0f}% ({reqs} reqs)")
                
        # 4. Formulate the hourly recommendation message
        lines = [
            "📊 *NINA Hourly Quota & Suggestion Update*",
            f"• *Jules Daily Quota*: `{used_jules}/{jules_limit}` used ({remaining_jules} left)",
            f"• *Active Jules Sessions*: `{active_count}` active",
        ]
        
        if provider_status_lines:
            lines.append("• *LLM Quotas*:\n  " + "\n  ".join(provider_status_lines))
            
        lines.append("")
        
        if ready_tasks:
            lines.append(f"💡 *READY Tasks Waiting ({len(ready_tasks)} total)*:")
            # Suggest the top 3 ready tasks
            for t in ready_tasks[:3]:
                # Format: B-NNN: Title (files)
                cleaned_title = t.get("title", "Untitled").strip()
                lines.append(f"  - `{t['id']}`: {cleaned_title}")
                
            lines.append("")
            lines.append(f"🚀 *Suggestion*: Let's leverage our remaining `{remaining_jules}` Jules quota slots! Run standard dispatcher on `{ready_tasks[0]['id']}` or use `/goal` to kickstart a new task.")
        else:
            lines.append("💡 *Suggestion*: All backlog tasks are completed or pending. Excellent work! Why not define a new feature or goal using `/goal` to keep Jules productive?")
            
        await send_telegram("\n".join(lines))
        logger.info("Hourly quota suggestion delivered to Telegram.")
    except Exception as e:
        logger.error(f"Failed to generate hourly quota suggestion: {e}")

async def run_autonomous_evolution_cycle(nina_os):
    """
    Fully autonomous self-directed evolution routine (OODA betterment cycle).
    Runs every 15 minutes, checks system errors, identifies needed improvements,
    generates structured specs, adds them to the backlog, and triggers Jules.
    """
    try:
        from tools.jules import load_registry, send_telegram, goal_to_backlog
        from tools.ninaflash_core import REPO_ROOT
        
        # 1. Safety Threshold check: stop if we are near Jules daily limit (e.g. 95/100)
        reg = load_registry()
        completed_today_count = 0
        active_count = 0
        now_utc = datetime.now(timezone.utc)
        start_of_today = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        for s in reg.values():
            status = s.get("status")
            created_str = s.get("created_at")
            if created_str:
                try:
                    created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    if created_dt >= start_of_today:
                        if status in ("COMPLETED", "FAILED", "DUPLICATE"):
                            completed_today_count += 1
                        elif status in ("IN_PROGRESS", "AWAITING_USER_FEEDBACK"):
                            active_count += 1
                except Exception:
                    pass
        
        if (completed_today_count + active_count) >= 95:
            logger.warning("Autonomous Evolution Cycle skipped: Daily Jules limit threshold (95/100) reached.")
            return

        # Do not stack up too many simultaneous active sessions
        if active_count >= 3:
            logger.info("Autonomous Evolution Cycle skipped: 3 or more active Jules sessions already running.")
            return

        # 2. Gather Context: Read error register
        err_path = REPO_ROOT / "docs/space/nina_error_register.md"
        error_context = ""
        if err_path.exists():
            # Get open errors
            lines = err_path.read_text(encoding="utf-8").splitlines()
            open_errs = [line for line in lines if "OPEN" in line or "🔵" in line or "🔴" in line or "🟠" in line]
            if open_errs:
                error_context = "\n".join(open_errs[:5])

        # 3. Consult LLM router for a betterment specification
        brainstorm_prompt = (
            "You are NINA's top-level Autonomous Evolution Architect.\n"
            "Analyze the following context from NINA's system state and determine the single most valuable improvement "
            "we can build right now to improve reliability, speed, or developer experience.\n\n"
            f"### Active Open Error Register:\n{error_context or 'None'}\n\n"
            "### Rules:\n"
            "1. Output a clear, single line description of the improvement (maximum 80 characters).\n"
            "2. Followed by a concise, high-quality, comprehensive 3-paragraph task specification that Jules can understand.\n"
            "3. State exactly which files to edit.\n"
            "4. Start your response directly with the line: 'BETTERMENT_TITLE: <title>' and then 'BETTERMENT_SPEC: <spec>'"
        )
        
        from core.quota_dispatcher import QuotaDispatcher
        dispatcher = QuotaDispatcher(nina_os.router)
        plan = dispatcher.dispatch(brainstorm_prompt, force_tier="DEEP")
        response = await plan.execute()

        import types
        if isinstance(response, types.AsyncGeneratorType):
            acc = []
            async for chunk in response:
                acc.append(chunk)
            response = "".join(acc)

        if isinstance(response, tuple):
            response_str = str(response[0])
        elif isinstance(response, Exception):
            response_str = str(response)
        elif not isinstance(response, str):
            response_str = str(response)
        else:
            response_str = response

        # Check for provider failure
        if "⚠️ All providers are currently unavailable" in response_str or "All providers are currently unavailable" in response_str or response_str.startswith("⚠️"):
            logger.warning(f"Autonomous Evolution Cycle skipped: router returned error: {response_str}")
            return


        # Parse response
        title = "Auto Betterment Task"
        spec = ""
        if "⚠️ All providers are currently unavailable" in response_str or "All providers are currently unavailable" in response_str or "failing validation" in response_str:
            logger.warning("Autonomous Evolution Cycle skipped: All LLM providers are currently failing.")
            return

        if "BETTERMENT_TITLE:" in response_str:
            try:
                parts = response_str.split("BETTERMENT_SPEC:", 1)
                title_part = parts[0].replace("BETTERMENT_TITLE:", "").strip()
                spec_part = parts[1].strip() if len(parts) > 1 else ""
                if title_part:
                    title = title_part
                if spec_part:
                    spec = spec_part
            except Exception:
                pass
        
        if not spec:
            spec = response_str.strip()

        # Check for matching error_id and duplicates on GitHub
        error_id = None
        if err_path.exists():
            try:
                err_lines = err_path.read_text(encoding="utf-8").splitlines()
                for el in err_lines:
                    if any(term in el for term in ("OPEN", "🔵", "🔴", "🟠")):
                        parts = [p.strip() for p in el.split("|") if p.strip()]
                        if parts:
                            eid = parts[0]
                            if eid in title or eid in spec:
                                error_id = eid
                                break
            except Exception as e:
                logger.error(f"Error parsing error register for dedup: {e}")

        if error_id:
            attempts_file = DATA_DIR / "jules_attempts.json"
            attempts = {}
            if attempts_file.exists():
                try:
                    attempts = json.loads(attempts_file.read_text())
                except Exception:
                    pass
            count = attempts.get(error_id, 0)
            if count >= 3:
                logger.warning(f"Jules task skipped: max attempts (3) reached for error_id: {error_id}")
                return

            import subprocess
            res = subprocess.run(["gh", "pr", "list", "--state", "open", "--json", "title,body,number"], capture_output=True, text=True)
            if res.returncode == 0:
                try:
                    prs = json.loads(res.stdout)
                    duplicate_found = False
                    for pr in prs:
                        t_val = pr.get("title") or ""
                        b_val = pr.get("body") or ""
                        if error_id in t_val or error_id in b_val:
                            duplicate_found = True
                            break
                    if duplicate_found:
                        logger.info(f"Jules task skipped: open PR already exists for {error_id}")
                        return
                except Exception as e:
                    logger.error(f"Failed to check GitHub PRs: {e}")

            attempts[error_id] = count + 1
            try:
                attempts_file.write_text(json.dumps(attempts, indent=2))
            except Exception:
                pass

        # 4. Save to backlog and dispatch to Jules automatically!
        await send_telegram(f"🤖 *Autonomous Evolution Triggered*\n\nNINA identified a system betterment opportunity:\n*Title:* `{title}`\n\nStarting fully autonomous design and implementation...")
        await goal_to_backlog(f"[{title}] {spec}", auto_dispatch=True)
        
    except Exception as e:
        logger.error(f"Autonomous Evolution Cycle failed: {e}")

async def _stale_pr_cleanup_job():
    try:
        import subprocess
        import json
        from datetime import datetime
        try:
            from rapidfuzz import fuzz
        except ImportError:
            class fuzz:
                @staticmethod
                def ratio(s1, s2):
                    import difflib
                    return difflib.SequenceMatcher(None, s1, s2).ratio() * 100

        res = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title,createdAt,url"],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            logger.error(f"stale_pr_cleanup: gh command failed: {res.stderr}")
            return

        prs = json.loads(res.stdout)
        closed_count = 0
        for i in range(len(prs)):
            for j in range(i + 1, len(prs)):
                pr1 = prs[i]
                pr2 = prs[j]
                
                ratio = fuzz.ratio(pr1["title"].lower(), pr2["title"].lower())
                if ratio >= 85:
                    try:
                        d1 = datetime.fromisoformat(pr1["createdAt"].replace("Z", "+00:00"))
                        d2 = datetime.fromisoformat(pr2["createdAt"].replace("Z", "+00:00"))
                    except Exception:
                        d1 = pr1["number"]
                        d2 = pr2["number"]
                    
                    if d1 < d2:
                        older = pr1
                        newer = pr2
                    else:
                        older = pr2
                        newer = pr1
                    
                    logger.info(f"stale_pr_cleanup: closing older duplicate PR #{older['number']} in favor of #{newer['number']}")
                    comment_msg = f"Closing older duplicate of #{newer['number']} (title fuzzy match {ratio:.1f}% >= 85%)."
                    
                    subprocess.run(["gh", "pr", "comment", str(older["number"]), "--body", comment_msg])
                    subprocess.run(["gh", "pr", "close", str(older["number"])])
                    closed_count += 1
                    
        logger.info(f"stale_pr_cleanup complete. Closed {closed_count} older duplicate PRs.")
    except Exception as e:
        logger.error(f"stale_pr_cleanup job failed: {e}")

async def _jules_audit_job(nina_os):
    try:
        import subprocess
        import json
        from datetime import datetime, timedelta, timezone
        
        res = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "100", "--json", "number,state,createdAt,labels"],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            logger.error(f"jules_audit: gh command failed: {res.stderr}")
            return
            
        prs = json.loads(res.stdout)
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        
        recent_prs = []
        for pr in prs:
            try:
                created_dt = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                if created_dt >= seven_days_ago:
                    recent_prs.append(pr)
            except Exception:
                pass
                
        total = len(recent_prs)
        if total == 0:
            merge_rate = 0.0
            duplicate_rate = 0.0
            merged_count = 0
            duplicate_count = 0
        else:
            merged_count = sum(1 for pr in recent_prs if pr["state"] == "MERGED")
            duplicate_count = sum(
                1 for pr in recent_prs 
                if any(label.get("name") == "duplicate" for label in pr.get("labels", []))
            )
            merge_rate = (merged_count / total) * 100
            duplicate_rate = (duplicate_count / total) * 100
            
        report_path = Path(__file__).parent.parent.resolve() / "docs/space/jules_weekly_audit.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# Jules Weekly Audit Report
Generated at: {now.isoformat()}

## Summary (Last 7 Days)
- **Total PRs Created:** {total}
- **Merged PRs:** {merged_count} (Merge Rate: {merge_rate:.2f}%)
- **Duplicate PRs:** {duplicate_count} (Duplicate Rate: {duplicate_rate:.2f}%)

"""
        report_path.write_text(report_content, encoding="utf-8")
        logger.info(f"jules_audit: Report written to {report_path}")
        
        if duplicate_rate > 20.0:
            alert_msg = f"⚠️ *Jules Weekly Audit Alert*\nDuplicate PR rate is high: `{duplicate_rate:.1f}%` ({duplicate_count}/{total} PRs in last 7 days)!"
            try:
                await nina_os.telegram.send_message(alert_msg)
            except Exception as te:
                logger.error(f"jules_audit: Failed to send Telegram alert: {te}")
                
    except Exception as e:
        logger.error(f"jules_audit job failed: {e}")

async def _healthcheck_job(nina_os):
    try:
        import psutil
        import json
        from pathlib import Path
        
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        cpu_ram_ok = cpu < 90.0 and ram.percent < 95.0
        
        disk = psutil.disk_usage('/')
        disk_ok = disk.percent < 90.0
        
        cron_ok = len(get_job_metrics()) > 0
        
        hb_file = Path(__file__).parent.parent.resolve() / "data" / "heartbeats.json"
        heartbeats_ok = True
        if hb_file.exists():
            try:
                with open(hb_file, "r") as f:
                    hb_data = json.load(f)
                import datetime
                now = datetime.datetime.utcnow()
                for name, ts_str in hb_data.items():
                    if ts_str:
                        clean_ts = ts_str.rstrip('Z')
                        ts = datetime.datetime.fromisoformat(clean_ts)
                        if (now - ts).total_seconds() > 300:
                            heartbeats_ok = False
                            break
            except Exception:
                heartbeats_ok = False
                
        api_ok = True
        for pid in ["GEMINI", "GROQ"]:
            h = nina_os.router.health.get(pid)
            if h and getattr(h, "degraded", False):
                api_ok = False
                break
                
        failures = 0
        if not cpu_ram_ok:
            failures += 1
        if not disk_ok:
            failures += 1
        if not cron_ok:
            failures += 1
        if not heartbeats_ok:
            failures += 1
        if not api_ok:
            failures += 1
        
        if failures == 0:
            health = "green"
        elif failures <= 2:
            health = "yellow"
        else:
            health = "red"
            
        state_file = Path("/home/aibony/nina/docs/space/nina_state.json")
        if state_file.exists():
            try:
                state_data = json.loads(state_file.read_text(encoding="utf-8"))
                old_health = state_data.get("system_health", "unknown")
                state_data["system_health"] = health
                state_file.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
                
                if health in ("yellow", "red") or (old_health != health and health != "green"):
                    msg = f"🏥 *NINA System Health Notification*\n\nStatus: *{health.upper()}*\nFailed Conditions: `{failures}/5`\n- CPU/RAM: {'✅' if cpu_ram_ok else '❌'}\n- Disk: {'✅' if disk_ok else '❌'}\n- Cron: {'✅' if cron_ok else '❌'}\n- Heartbeats: {'✅' if heartbeats_ok else '❌'}\n- API: {'✅' if api_ok else '❌'}"
                    try:
                        await nina_os.telegram.send_message(msg)
                    except Exception as te:
                        logger.error(f"healthcheck: Failed to send Telegram: {te}")
            except Exception as e:
                logger.error(f"healthcheck: Failed to update state file: {e}")
                
    except Exception as e:
        logger.error(f"healthcheck job failed: {e}")

def run():
    class _MinimalNinaOS:
        class Router:
            class ModelDiscovery:
                async def discover_all(self): pass
            class Cache:
                def purge_expired(self): pass
            class Health:
                def get(self, *args, **kwargs):
                    class H:
                        degraded = False
                        requests_today = 0
                    return H()
            class QuotaRouter:
                def get_provider_usage(self, *args, **kwargs): return 0.0
            def __init__(self):
                self._model_discovery = self.ModelDiscovery()
                self.cache = self.Cache()
                self.health = self.Health()
                self.quota_router = self.QuotaRouter()
            async def reset_daily(self): pass
        
        class Telegram:
            async def send_message(self, *args, **kwargs): pass
            
        class Pipeline:
            async def _expire_pending(self): pass

        def __init__(self):
            self.router = self.Router()
            self.telegram = self.Telegram()
            self.pipeline = self.Pipeline()

        async def run_morning_report(self): pass
        async def run_heartbeat(self): pass
        async def run_cost_report(self): pass
        async def run_circuit_breaker_stats(self): pass
        async def run_idle_summary(self): pass
        async def run_log_rotation(self): pass
        async def run_provider_health(self): pass
        async def run_provider_hunter(self): pass
        async def run_thermal_health(self): pass

    async def _main():
        nina_stub = _MinimalNinaOS()
        scheduler = TaskScheduler(nina_stub)
        scheduler.start()
        while True:
            await asyncio.sleep(3600)

    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
