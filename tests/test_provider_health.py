import pytest
import time
import json
from unittest.mock import AsyncMock, patch

from tools.provider_health import ProviderWindow, ProviderHealthTracker

def test_provider_window_basic():
    w = ProviderWindow(name="test-prov")
    assert w.name == "test-prov"
    assert len(w.calls) == 0
    assert w.ok_rate == 1.0
    assert w.avg_latency_ms == 0.0
    assert w.call_count_window == 0

    # Record some calls
    w.record(ok=True, latency_ms=100.0)
    assert w.consecutive_successes == 1
    assert w.consecutive_failures == 0
    assert w.ok_rate == 1.0
    assert w.avg_latency_ms == 100.0

    w.record(ok=False, latency_ms=0.0, error="Timeout")
    assert w.consecutive_successes == 0
    assert w.consecutive_failures == 1
    assert w.ok_rate == 0.5
    assert w.avg_latency_ms == 50.0
    assert w.last_error == "Timeout"

    # Consecutive successes reset failures
    w.record(ok=True, latency_ms=120.0)
    assert w.consecutive_successes == 1
    assert w.consecutive_failures == 0
    assert w.last_error == ""

def test_provider_window_time_window():
    w = ProviderWindow(name="test-prov")
    now = time.time()
    
    # Mock calls in the past (beyond 10 minutes window)
    w.calls.append({"ts": now - 700, "ok": True, "latency_ms": 50.0})
    # Mock call within window
    w.calls.append({"ts": now - 300, "ok": False, "latency_ms": 100.0})
    
    assert w.call_count_window == 1
    assert w.ok_rate == 0.0
    assert w.avg_latency_ms == 100.0

@pytest.mark.asyncio
async def test_provider_tracker_alert_and_persist(tmp_path):
    # Use temporary state path
    test_state_file = tmp_path / "provider_health.json"
    
    with patch("tools.provider_health._STATE_PATH", test_state_file):
        tracker = ProviderHealthTracker()
        mock_notify = AsyncMock()
        tracker.set_notify(mock_notify)

        # Record 2 failures (no alert yet, threshold is 3)
        await tracker.record("prov-1", ok=False, latency_ms=0.0, error="Err1")
        await tracker.record("prov-1", ok=False, latency_ms=0.0, error="Err2")
        assert mock_notify.call_count == 0

        # 3rd failure triggers degraded alert
        await tracker.record("prov-1", ok=False, latency_ms=0.0, error="Err3")
        assert mock_notify.call_count == 1
        assert "degraded" in mock_notify.call_args[0][0]
        assert "prov-1" in mock_notify.call_args[0][0]

        # 4th failure doesn't alert again (prevents spam)
        await tracker.record("prov-1", ok=False, latency_ms=0.0, error="Err4")
        assert mock_notify.call_count == 1

        # Recovery alert
        await tracker.record("prov-1", ok=True, latency_ms=50.0)
        assert mock_notify.call_count == 2
        assert "recovered" in mock_notify.call_args[0][0]

        # Check state persistence
        assert test_state_file.exists()
        saved_data = json.loads(test_state_file.read_text())
        assert "prov-1" in saved_data
        assert saved_data["prov-1"]["consecutive_failures"] == 0
        assert saved_data["prov-1"]["last_error"] == ""

        # Test loading from state
        new_tracker = ProviderHealthTracker()
        assert "prov-1" in new_tracker.health_summary()

def test_tracker_sync_record(tmp_path):
    test_state_file = tmp_path / "provider_health_sync.json"
    with patch("tools.provider_health._STATE_PATH", test_state_file):
        tracker = ProviderHealthTracker()
        tracker.record_sync("prov-sync", ok=True, latency_ms=80.0)
        
        summary = tracker.health_summary()
        assert "prov-sync" in summary
        assert summary["prov-sync"]["avg_latency_ms"] == 80.0
