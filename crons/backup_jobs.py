
"""NINA v12 — Backup jobs"""
import logging, time, zipfile
from pathlib import Path

from crons.registry import CronJob
CRON_JOB = CronJob(
    id='backup_jobs',
    name='Backup Jobs',
    schedule='30 2 * * *',
    module='crons.backup_jobs',
    description='Runs memory and python codebase backups'
)

logger = logging.getLogger("nina.scheduler")

BACKUP_ROOT = Path("upgrades/backups")

async def run_memory_backup(nina_os):
    try:
        path = await nina_os.memory.backup()
        logger.info(f"memory_backup_ok dest={path}", extra={"cron_module": "cron", "job_id": "memory_backup"})
    except Exception as e:
        logger.warning(f"memory_backup_failed {e}", extra={"cron_module": "cron", "job_id": "memory_backup"})

async def run_py_backup(nina_os):
    try:
        ts = time.strftime("%Y%m%d%H%M%S")
        dest = BACKUP_ROOT / f"py_{ts}.zip"
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(".")
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in root.rglob("*.py"):
                if not any(x in f.parts for x in (".venv", "venv", "backups")):
                    zf.write(f)
        logger.info(f"py_backup_ok dest={dest}", extra={"cron_module": "cron", "job_id": "py_backup"})
    except Exception as e:
        logger.warning(f"py_backup_failed {e}", extra={"cron_module": "cron", "job_id": "py_backup"})

def run():
    import asyncio
    async def _main():
        class _MinimalMemory:
            async def backup(self):
                dest = BACKUP_ROOT / f"mem_stub_{int(time.time())}.zip"
                BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
                zipfile.ZipFile(dest, "w").close()
                return str(dest)
        class _MinimalNinaOS:
            def __init__(self):
                self.memory = _MinimalMemory()
        
        nina_stub = _MinimalNinaOS()
        await run_memory_backup(nina_stub)
        await run_py_backup(nina_stub)

    asyncio.run(_main())
