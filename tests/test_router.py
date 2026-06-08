import pytest
import time
from unittest.mock import AsyncMock

from core.router import CircuitBreaker, HybridRouter, ClassifiedTask, ProviderHealth, PROVIDERS_TIER1, PROVIDERS_TIER2, PROVIDERS_TIER3
from core.config import NinaConfig

@pytest.fixture
def dummy_config():
    # Provide minimal config for HybridRouter to function
    return NinaConfig(
        telegram_bot_token="dummy",
        authorized_user_id="123",
        groq_api_key="mock_key",
        gemini_api_key="mock_key"
    )

@pytest.fixture
def router(dummy_config):
    router = HybridRouter(dummy_config)
    # Don't call initialize() to avoid discovering real models.
    # Manually populate health dict for mock testing.
    for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, "LOCALFAST", "LOCALHEAVY"]:
        router.health[pid] = ProviderHealth(provider_id=pid)
    # mock _has_key to return True for our specific test providers
    def has_key_mock(pid):
        return pid in ["GROQ", "GEMINI", "LOCALFAST", "LOCALHEAVY"]
    router._has_key = has_key_mock

    # We also need to mock composite_score to avoid None errors on fallback
    for pid in router.health:
        router.health[pid].composite_score = lambda p: 50.0

    return router

def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker()
    # Initial state should be CLOSED
    assert cb.state == "CLOSED"
    assert cb.allow_request() is True

    # 3 Failures should open the circuit
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "CLOSED"
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.allow_request() is False

    # Simulate waiting past the recovery window
    # By default, RECOVERY_S = 60. Let's manipulate the open_until
    cb.open_until = time.time() - 1

    # Next allow_request should transition to HALF_OPEN
    assert cb.allow_request() is True
    assert cb.state == "HALF_OPEN"

    # Only one request allowed in HALF_OPEN
    assert cb.allow_request() is False

    # Record success -> CLOSED
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.allow_request() is True

def test_circuit_breaker_half_open_to_open():
    cb = CircuitBreaker()
    # Force state to HALF_OPEN
    cb.state = "HALF_OPEN"

    # Simulate a failure while HALF_OPEN
    cb.record_failure()

    # State should revert to OPEN immediately
    assert cb.state == "OPEN"
    assert cb.open_until > time.time()
    assert cb.allow_request() is False

@pytest.mark.asyncio
async def test_router_ordered_providers_sensitive_and_force_local(router):
    task = ClassifiedTask("general", 100, False, is_sensitive=True)
    # Sensitive task -> Local only
    providers = router._ordered_providers(task)
    assert providers == ["LOCALFAST", "LOCALHEAVY"]

    task2 = ClassifiedTask("general", 100, False, is_sensitive=False)
    # Force local -> Local only
    providers = router._ordered_providers(task2, force_local=True)
    assert providers == ["LOCALFAST", "LOCALHEAVY"]

@pytest.mark.asyncio
async def test_router_ordered_providers_ordering(router):
    task = ClassifiedTask("general", 100, False, False)
    # Mock composite scores
    router.health["GROQ"].composite_score = lambda p: 90.0
    router.health["GEMINI"].composite_score = lambda p: 80.0

    providers = router._ordered_providers(task)

    # Provider _ordered_providers returns a list of available providers, prioritizing Tier 1 and based on score
    # We mocked has_key for GROQ and GEMINI.
    assert "GROQ" in providers
    assert "GEMINI" in providers
    assert providers.index("GROQ") < providers.index("GEMINI")

    # Must end with local fallbacks
    assert providers[-2:] == ["LOCALFAST", "LOCALHEAVY"]

@pytest.mark.asyncio
async def test_router_fallback(router):
    # Mock call_provider to fail on first, succeed on second
    # providers list will be GROQ, GEMINI, LOCALFAST, LOCALHEAVY based on previous test mocking

    async def mock_call_provider(pid, messages, task):
        if pid == "GROQ":
            raise Exception("Provider down")
        if pid == "GEMINI":
            return "Gemini success", 10, 10, 100.0
        raise Exception("Should not reach here")

    router.call_provider = AsyncMock(side_effect=mock_call_provider)

    # Need to make sure GROQ and GEMINI are first in line for this test
    router.health["GROQ"].composite_score = lambda p: 90.0
    router.health["GEMINI"].composite_score = lambda p: 80.0

    task = ClassifiedTask("general", 100, False, False)

    # Test fallback route
    response = await router.route("Hello", [{"role": "user", "content": "Hello"}], task)

    assert response == "Gemini success"
    # Ensure health was recorded properly
    assert router.health["GROQ"].failure_count == 1
    assert router.health["GEMINI"].success_count == 1

@pytest.mark.asyncio
async def test_router_all_providers_fail(router):
    # Mock call_provider to always fail
    router.call_provider = AsyncMock(side_effect=Exception("All down"))

    task = ClassifiedTask("general", 100, False, False)

    # Test fallback route
    response = await router.route("Hello", [{"role": "user", "content": "Hello"}], task)

    assert "All providers are currently unavailable" in response

def test_router_ordered_providers_with_model_discovery(router):
    # Mock load_cache to return a specific cached model
    router._model_discovery.load_cache = lambda: {"GROQ": "discovered-groq-model"}
    task = ClassifiedTask("general", 100, False, False)
    
    # GROQ should resolve "discovered-groq-model", GEMINI should resolve fallback "gemini-2.5-flash"
    providers = router._ordered_providers(task)
    assert "GROQ" in providers
    assert "GEMINI" in providers

    # With model_overrides set, overrides should be preferred
    router.config.model_overrides["GROQ"] = "overridden-groq-model"
    providers = router._ordered_providers(task)
    assert "GROQ" in providers

def test_provider_health_limits():
    # Test token and request daily limits
    h = ProviderHealth(provider_id="GEMINI")
    
    # Under limits initially
    assert h.is_near_limit("GEMINI") is False
    assert h.is_exhausted("GEMINI") is False

    # Simulate token limit near (GEMINI tpd is 1500000, 80% is 1200000)
    h.tokens_today = 1200001
    assert h.is_near_limit("GEMINI") is True
    assert h.is_exhausted("GEMINI") is False

    # Simulate token limit reached
    h.tokens_today = 1500000
    assert h.is_exhausted("GEMINI") is True

    # Reset
    h.tokens_today = 0
    assert h.is_near_limit("GEMINI") is False
    assert h.is_exhausted("GEMINI") is False

    # Simulate request limit near (GEMINI rpd is 1500, 80% is 1200)
    h.requests_today = 1201
    assert h.is_near_limit("GEMINI") is True
    assert h.is_exhausted("GEMINI") is False

    # Simulate request limit reached
    h.requests_today = 1500
    assert h.is_exhausted("GEMINI") is True


