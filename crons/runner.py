import dataclasses
import datetime
import importlib
import json
import os
import time
from typing import List, Optional

from crons.registry import CronJob, CronRegistry

@dataclasses.dataclass
class CronResult:
    id: str
    ok: bool
    duration_ms: float
    error: Optional[str]
    ran_at: str

class CronRunner:
    def __init__(self):
        self.registry = CronRegistry()
        self.results_file = os.path.join("data", "cron_results.json")

    def run_job(self, job: CronJob) -> CronResult:
        start_time = time.perf_counter()
        ran_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        ok = False
        error_str = None

        try:
            mod = importlib.import_module(job.module)
            if hasattr(mod, "run"):
                mod.run()
            else:
                raise ValueError(f"Module {job.module} does not have a run() function.")
            ok = True
        except Exception as e:
            ok = False
            error_str = str(e)
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000.0

        return CronResult(
            id=job.id,
            ok=ok,
            duration_ms=duration_ms,
            error=error_str,
            ran_at=ran_at
        )

    def log_result(self, result: CronResult) -> None:
        os.makedirs(os.path.dirname(self.results_file), exist_ok=True)
        with open(self.results_file, "a") as f:
            f.write(json.dumps(dataclasses.asdict(result)) + "\n")

    def run_all_enabled(self) -> List[CronResult]:
        results = []
        for job in self.registry.get_enabled():
            result = self.run_job(job)
            self.log_result(result)
            results.append(result)

        try:
            from core.observability import get_hub
            hub = get_hub()
            hub.emit_log(
                "cron_runner_completed",
                metadata={"total_ran": len(results), "successes": sum(1 for r in results if r.ok)}
            )
        except Exception:
            pass

        return results
