import json
import time
import logging
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    logger = logging.getLogger("nina.observability")

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"

@dataclass
class NinaMetrics:
    uptime_seconds: float = 0.0
    tasks_total: int = 0
    tasks_ok: int = 0
    tasks_fail: int = 0
    router_calls: int = 0
    last_sync_ts: str = ""
    last_health_check_ts: str = ""
    active_providers: list[str] = None
    error_rate: float = 0.0
    memory_mb: float = 0.0

    def __post_init__(self) -> None:
        if self.active_providers is None:
            self.active_providers = []

class ObservabilityHub:
    def __init__(self) -> None:
        self.metrics = NinaMetrics()
        self.start_time = time.time()

    def record_task(self, ok: bool) -> None:
        self.metrics.tasks_total += 1
        if ok:
            self.metrics.tasks_ok += 1
        else:
            self.metrics.tasks_fail += 1
        self.metrics.error_rate = self.metrics.tasks_fail / self.metrics.tasks_total if self.metrics.tasks_total > 0 else 0.0

    def record_router_call(self) -> None:
        self.metrics.router_calls += 1

    def set_sync_ts(self) -> None:
        # Format: ISO8601
        from datetime import datetime, timezone
        self.metrics.last_sync_ts = datetime.now(timezone.utc).isoformat()

    def set_health_ts(self) -> None:
        from datetime import datetime, timezone
        self.metrics.last_health_check_ts = datetime.now(timezone.utc).isoformat()

    def set_active_providers(self, names: list[str]) -> None:
        self.metrics.active_providers = names

    def get_status(self) -> HealthStatus:
        if self.metrics.error_rate > 0.5:
            return HealthStatus.CRITICAL
        elif self.metrics.error_rate > 0.2:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def to_dict(self) -> dict:
        self.metrics.uptime_seconds = time.time() - self.start_time
        data = asdict(self.metrics)
        data["status"] = self.get_status().value
        return data

    def emit_log(self) -> None:
        logger.info(json.dumps(self.to_dict()))

_hub = None

def get_hub() -> ObservabilityHub:
    global _hub
    if _hub is None:
        _hub = ObservabilityHub()
    return _hub
