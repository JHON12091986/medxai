import pytest
import time
from core.observability import get_hub, ObservabilityHub, HealthStatus, NinaMetrics
from unittest.mock import patch

@pytest.fixture
def hub():
    """Return a fresh Hub instance for testing."""
    return ObservabilityHub()

def test_hub_singleton():
    hub1 = get_hub()
    hub2 = get_hub()
    assert hub1 is hub2

def test_record_task(hub):
    # Happy path
    hub.record_task(ok=True)
    assert hub.metrics.tasks_total == 1
    assert hub.metrics.tasks_ok == 1
    assert hub.metrics.tasks_fail == 0
    assert hub.metrics.error_rate == 0.0

    # Failure path
    hub.record_task(ok=False)
    assert hub.metrics.tasks_total == 2
    assert hub.metrics.tasks_ok == 1
    assert hub.metrics.tasks_fail == 1
    assert hub.metrics.error_rate == 0.5

def test_record_router_call(hub):
    hub.record_router_call()
    hub.record_router_call()
    assert hub.metrics.router_calls == 2

def test_set_sync_ts(hub):
    hub.set_sync_ts()
    assert hub.metrics.last_sync_ts != ""
    # Basic ISO check
    assert "T" in hub.metrics.last_sync_ts

def test_set_health_ts(hub):
    hub.set_health_ts()
    assert hub.metrics.last_health_check_ts != ""
    assert "T" in hub.metrics.last_health_check_ts

def test_set_active_providers(hub):
    hub.set_active_providers(["GEMINI", "OPENAI"])
    assert hub.metrics.active_providers == ["GEMINI", "OPENAI"]

def test_get_status(hub):
    # Healthy
    hub.record_task(ok=True)
    assert hub.get_status() == HealthStatus.HEALTHY

    # Degraded (> 0.2)
    hub.record_task(ok=False)
    hub.record_task(ok=True)
    hub.record_task(ok=True)
    # 1 fail / 4 total = 0.25
    assert hub.get_status() == HealthStatus.DEGRADED

    # Critical (> 0.5)
    hub.record_task(ok=False)
    hub.record_task(ok=False)
    hub.record_task(ok=False)
    # 3 fails / 7 total = 0.42 (still degraded)
    hub.record_task(ok=False)
    # 4 fails / 8 total = 0.57
    assert hub.get_status() == HealthStatus.CRITICAL

def test_to_dict(hub):
    hub.record_task(ok=True)
    hub.set_sync_ts()
    hub.set_active_providers(["LOCAL"])
    
    data = hub.to_dict()
    assert data["tasks_total"] == 1
    assert data["status"] == "HEALTHY"
    assert data["active_providers"] == ["LOCAL"]
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], float)

def test_emit_log(hub):
    import json
    hub.record_task(ok=True)
    
    # Patch the actual logger used in core.observability
    with patch("core.observability.logger") as mock_logger:
        hub.emit_log()
        
    assert mock_logger.info.called
    log_arg = mock_logger.info.call_args[0][0]
    parsed = json.loads(log_arg)
    assert parsed["tasks_total"] == 1
    assert parsed["status"] == "HEALTHY"
