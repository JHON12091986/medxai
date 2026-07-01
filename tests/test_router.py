import pytest
import time
from unittest.mock import AsyncMock, patch

from core.router import CircuitBreaker, HybridRouter, ClassifiedTask, ProviderHealth
from core.config import NinaConfig

@pytest.fixture
def dummy_config():
    return NinaConfig(
        telegram_bot_token="dummy",
        telegram_chat_id="dummy",
        authorized_user_id="123",
        groq_api_key="mock_key",
        gemini_api_key="mock_key"
    )

@pytest.fixture
def router(dummy_config):
    return HybridRouter(dummy_config)

def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker()
    assert cb.state == "CLOSED"
    assert cb.can_attempt() is True

    # 3 Failures should open the circuit
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_attempt() is False

    cb.open_until = time.time() - 1
    assert cb.can_attempt() is True
    assert cb.state == "HALF_OPEN"

    cb.record_success()
    assert cb.state == "CLOSED"

def test_circuit_breaker_half_open_to_open():
    cb = CircuitBreaker()
    cb.failures = [time.time()] * 3
    cb.state = "OPEN"
    cb.open_until = time.time() - 1
    
    assert cb.can_attempt() is True
    assert cb.state == "HALF_OPEN"

    cb.record_failure()
    assert cb.state == "OPEN"

@pytest.mark.asyncio
async def test_router_route_basic(router):
    task = ClassifiedTask("quick", 100, False, False)
    # Mock _call_provider to simulate a successful response
    # We must patch it on the INSTANCE
    router._call_provider = AsyncMock(return_value=("Success", 10, 10, 50.0))
    
    # Force a dummy provider into ALL_PROVIDERS and TIER_PREFERENCE_ORDER and health
    with patch("core.quota_router.TIER_PREFERENCE_ORDER", {"FAST": [["TEST"]]}):
        with patch("core.router.ALL_PROVIDERS", {"TEST": {"model": "m", "base_url": "u", "key_field": None}}):
            router.health["TEST"] = ProviderHealth()
            resp = await router.route("Hello", [], task)
            assert resp == "Success"
            assert router.health["TEST"].success_count == 1

@pytest.mark.asyncio
async def test_router_fallback(router):
    task = ClassifiedTask("quick", 100, False, False)
    
    async def mock_call(pid, msgs, t):
        if pid == "FAIL": raise Exception("Down")
        return "Recovered", 5, 5, 20.0
    
    router._call_provider = AsyncMock(side_effect=mock_call)
    
    # Mock ALL_PROVIDERS and TIER_PREFERENCE_ORDER with two providers. Order them to ensure FAIL is tried first.
    with patch("core.quota_router.TIER_PREFERENCE_ORDER", {"FAST": [["FAIL", "OK"]]}):
        with patch("core.router.ALL_PROVIDERS", {
            "FAIL": {"model": "m1", "base_url": "u1", "key_field": None},
            "OK": {"model": "m2", "base_url": "u2", "key_field": None}
        }):
            # Setup health for both
            router.health["FAIL"] = ProviderHealth()
            router.health["OK"] = ProviderHealth()
            # Give FAIL a slightly better score to ensure it's picked first in available.sort()
            router.health["FAIL"].success_count = 10 
            
            resp = await router.route("Goal", [], task)
            assert resp == "Recovered"
            assert router.health["FAIL"].failure_count == 1
            assert router.health["OK"].success_count == 1

def test_provider_health_scoring():
    h = ProviderHealth()
    assert h.health_score == 1.0
    h.record_failure()
    assert h.health_score < 1.0

def test_cache_logic(router):
    router.cache.set("prompt", "response", 100, messages=[{"r": "u"}])
    assert router.cache.get("prompt", messages=[{"r": "u"}]) == "response"

def test_get_models_status(router):
    router.health = {"TEST": ProviderHealth()}
    status = router.get_models_status()
    assert "Provider" in status

@pytest.mark.asyncio
async def test_router_stream_no_providers(router):
    task = ClassifiedTask("quick", 100, False, False)
    # Empty all provider tier settings to guarantee no provider is chosen
    with patch("core.quota_router.TIER_PREFERENCE_ORDER", {"FAST": []}):
        res = await router.route("Hello", [], task, stream=True)
        chunks = []
        async for chunk in res:
            chunks.append(chunk)
        assert any("All providers are currently unavailable" in str(c) for c in chunks) or any("Streaming interrupted" in str(c) for c in chunks)

