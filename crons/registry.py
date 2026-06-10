"""
Cron findings from audit:
- backup_jobs.py:
  - Jobs: 2
  - Description: Runs memory backups and Python codebase backups.
  - IDs: memory_backup, py_backup (inside APScheduler manager, not in file)
  - Schedule: memory backup at 2:30 AM, Python backup at 3:00 AM (Asia/Dhaka).
- manager.py:
  - Jobs: 16 scheduled using APScheduler.
  - Description: The main orchestrator that schedules all jobs. Not a standalone cron script.
"""

import dataclasses
import glob
import importlib
import os
import sys
from typing import List, Optional

@dataclasses.dataclass
class CronJob:
    id: str
    name: str
    schedule: str
    module: str
    enabled: bool = True
    description: str = ""

class CronRegistry:
    _instance = None
    _jobs: dict[str, CronJob] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CronRegistry, cls).__new__(cls)
            cls._jobs = {}
        return cls._instance

    def register(self, job: CronJob) -> None:
        if job.id in self._jobs:
            raise ValueError(f"Duplicate cron ID: {job.id}")
        self._jobs[job.id] = job

    def get(self, id: str) -> Optional[CronJob]:
        return self._jobs.get(id)

    def get_all(self) -> List[CronJob]:
        return list(self._jobs.values())

    def get_enabled(self) -> List[CronJob]:
        return [job for job in self._jobs.values() if job.enabled]

    def disable(self, id: str) -> None:
        if id in self._jobs:
            self._jobs[id].enabled = False

    def enable(self, id: str) -> None:
        if id in self._jobs:
            self._jobs[id].enabled = True

registry = CronRegistry()

def _auto_register():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for filepath in glob.glob(os.path.join(base_dir, "*.py")):
        filename = os.path.basename(filepath)
        if filename in ("__init__.py", "registry.py", "runner.py"):
            continue

        module_name = f"crons.{filename[:-3]}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "CRON_JOB") and isinstance(mod.CRON_JOB, CronJob):
                registry.register(mod.CRON_JOB)
            else:
                registry.register(CronJob(
                    id=filename[:-3],
                    name=filename[:-3].replace("_", " ").title(),
                    schedule="0 * * * *",
                    module=module_name,
                    description=f"Auto-registered {filename}"
                ))
        except Exception as e:
            # Note: We continue if a cron module fails to load,
            # as it shouldn't crash the entire registry import.
            print(f"Failed to auto-register {module_name}: {e}", file=sys.stderr)

_auto_register()
