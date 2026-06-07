"""
NINA v12 — TaskScheduler (Stage 5)
11 core jobs. APScheduler-based.
"""
import functools
import logging
from crons.backup_jobs import run_memory_backup, run_py_backup
from tools.market import run_market_monitor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Hard constraint (cron.lambda_coroutine_drop): Do not use lambda wrappers for async job callables.
# Lambda wrappers drop coroutine execution. Use functools.partial or pass the coroutine directly.

logger = logging.getLogger("nina.scheduler")


import asyncio

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

class TaskScheduler:
    def __init__(self, nina_os):
        self.nina = nina_os
        self._sched = AsyncIOScheduler(timezone="Asia/Dhaka")

    def start(self):
        n = self.nina
        add = self._sched.add_job

        add(n.run_morning_report,    CronTrigger(hour=9,  minute=0,  timezone="Asia/Dhaka"), id="morning_report")
        add(n.run_heartbeat,         IntervalTrigger(hours=1),                               id="heartbeat")
        add(functools.partial(_cache_purge_job, n), CronTrigger(hour=3, minute=5, timezone="Asia/Dhaka"), id="cache_purge")
        add(n.run_cost_report,       CronTrigger(hour=23, minute=0,  timezone="Asia/Dhaka"), id="cost_report")
        add(n.router.reset_daily_counters, CronTrigger(hour=0, minute=1, second=0,
                                           timezone="UTC"),                                  id="rate_limit_reset")
        add(n.run_idle_summary,      IntervalTrigger(minutes=30),                            id="idle_summary")
        add(n.run_log_rotation,      CronTrigger(hour=4,  minute=0,  timezone="Asia/Dhaka"), id="log_rotation")
        add(n.run_provider_health,   IntervalTrigger(hours=6),                               id="provider_health")
        add(n.run_provider_hunter,   CronTrigger(hour=2,  minute=0,  timezone="Asia/Dhaka"), id="provider_hunter")
        add(n.run_thermal_health,    IntervalTrigger(minutes=5),                             id="thermal_health")
        add(functools.partial(run_memory_backup, n), CronTrigger(hour=2, minute=30, timezone="Asia/Dhaka"), id="memory_backup")
        add(functools.partial(run_py_backup, n),     CronTrigger(hour=3, minute=0,  timezone="Asia/Dhaka"), id="py_backup")
        add(n.run_reminder_check,    IntervalTrigger(minutes=15),                            id="reminder_check")
        add(functools.partial(run_market_monitor, n), CronTrigger(hour="10-14", minute="*/30", timezone="Asia/Dhaka"), id="market_monitor")

        add(functools.partial(_model_discovery_job, n), IntervalTrigger(hours=24), id="model_discovery")
        add(n.pipeline._expire_pending,            IntervalTrigger(minutes=15), id="expire_pending")
        self._sched.start()
        logger.info(f"Scheduler started — {len(self._sched.get_jobs())} jobs", extra={"module": "cron", "job_id": "manager"})

    def shutdown(self, wait=False):
        self._sched.shutdown(wait=wait)

    def next_job_time(self, job_id: str) -> str:
        job = self._sched.get_job(job_id)
        return str(job.next_run_time) if job else "unknown"

    @property
    def job_count(self): return len(self._sched.get_jobs())
