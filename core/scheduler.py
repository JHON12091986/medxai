"""
core/scheduler.py — NinaScheduler stub.
Auto-created by nina_fix.sh. Replace with full impl when ready.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger("nina.scheduler")


class NinaScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Dhaka")
        self._jobs: dict = {}
        logger.info("NinaScheduler initialised (stub)")

    async def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("NinaScheduler started")

    async def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("NinaScheduler stopped")

    def add_job(self, func, trigger, job_id: str = None, **kwargs):
        job = self.scheduler.add_job(func, trigger, id=job_id, **kwargs)
        if job_id:
            self._jobs[job_id] = job
        return job

    def remove_job(self, job_id: str) -> None:
        try:
            self.scheduler.remove_job(job_id)
            self._jobs.pop(job_id, None)
        except Exception as e:
            logger.warning("remove_job(%s): %s", job_id, e)

    @property
    def running(self) -> bool:
        return self.scheduler.running
