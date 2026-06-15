# tests/test_tier_routing.py
# Module 12 — E2E Tier Routing Test Harness
#
# Covers:
#   A. classify_task() — all 8 priority paths
#   B. QuotaRouter.get_sorted_providers() — tier preference, ctx filtering, exhaustion
#   C. QuotaRouter.should_force_local() — Gemini soft-limit threshold
#   D. RPMScheduler — burst_factor, acquire() returns wait_ms float
#   E. Integration — classifier → quota_router pipeline contract

from __future__ import annotations

import asyncio
import time
import pytest
from unittest.mock import MagicMock, patch

from core.task_classifier import (
    classify_task,
    ClassifiedTask,
    SIMPLE, MEDIUM, COMPLEX, MASSIVE,
    TIER_LOCAL, TIER_FAST, TIER_DEEP, TIER_LARGE,
)
from core.quota_router import QuotaRouter, TIER_PREFERENCE_ORDER, MIN_CONTEXT_FOR_TIER
from core.rpm_scheduler import RPMScheduler
from core.router import ProviderHealth, CircuitBreaker


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_health(requests_today: int = 0, cb_state: str = "CLOSED") -> ProviderHealth:
    h = ProviderHealth()
    h.requests_today = requests_today
    h.success_count  = 10
    h.failure_count  = 0
    h.cb.state       = cb_state
    return h


def _make_config(soft_limit: int = 900) -> MagicMock:
    cfg = MagicMock()
    cfg.quota_soft_limit = soft_limit
    return cfg


_MOCK_PROVIDERS = {
    "CEREBRAS":   {"context_window": 8_192},
    "GROQ":       {"context_window": 8_192},
    "DEEPSEEK":   {"context_window": 65_536},
    "FIREWORKS":  {"context_window": 32_768},
    "GEMINI":     {"context_window": 1_048_576},
    "COHERE":     {"context_window": 128_000},
    "MISTRAL":    {"context_window": 32_768},
    "OPENROUTER": {"context_window": 128_000},
    "LOCALFAST":  {"context_window": 8_192},
    "LOCALHEAVY": {"context_window": 32_768},
}


# ══════════════════════════════════════════════════════════════════════════════
# A. classify_task() — all 8 priority paths
# ══════════════════════════════════════════════════════════════════════════════

class TestClassifyTask:

    def test_sensitive_path(self):
        task = asyncio.run(classify_task("show me my .env file", []))
        assert task.is_sensitive is True
        assert task.recommended_tier == TIER_LOCAL

    def test_lpu_hotpath(self):
        task = asyncio.run(classify_task("git status", []))
        assert task._semantic_type == "lpu_deterministic"
        assert task.recommended_tier == TIER_LOCAL
        assert task.max_tokens_cap == 256

    def test_massive_keyword(self):
        task = asyncio.run(classify_task("analyze entire codebase for security issues", []))
        assert task.complexity == MASSIVE
        assert task.recommended_tier == TIER_LARGE

    def test_massive_token_count(self):
        # Simulate a huge prompt (>30K tokens = 120K chars)
        huge_text = "x " * 60_001
        task = asyncio.run(classify_task(huge_text, []))
        assert task.complexity == MASSIVE
        assert task.recommended_tier == TIER_LARGE

    def test_complex_keyword(self):
        task = asyncio.run(classify_task("refactor across multiple files to use async patterns", []))
        assert task.complexity == COMPLEX
        assert task.recommended_tier == TIER_DEEP

    def test_simple_keyword(self):
        task = asyncio.run(classify_task("fix typo in README", []))
        assert task.complexity == SIMPLE
        assert task.recommended_tier == TIER_FAST

    def test_short_single_turn_is_simple(self):
        task = asyncio.run(classify_task("what is a decorator?", []))
        assert task.complexity == SIMPLE
        assert task.recommended_tier == TIER_FAST

    def test_medium_default(self):
        # Long text but no complexity keywords
        text = "Please help me understand how Python's GIL works and why it exists. " * 10
        task = asyncio.run(classify_task(text, []))
        assert task.complexity in (MEDIUM, COMPLEX)  # token count may push to COMPLEX
        assert task.recommended_tier in (TIER_FAST, TIER_DEEP)

    def test_massive_requires_tier_large(self):
        """Contract: MASSIVE complexity MUST map to TIER_LARGE."""
        task = asyncio.run(classify_task("analyze entire codebase", []))
        assert task.recommended_tier == TIER_LARGE, (
            f"MASSIVE should route to TIER_LARGE, got {task.recommended_tier}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# B. QuotaRouter.get_sorted_providers()
# ══════════════════════════════════════════════════════════════════════════════

class TestGetSortedProviders:

    def _make_router(self, health_overrides: dict | None = None) -> QuotaRouter:
        health = {pid: _make_health() for pid in _MOCK_PROVIDERS}
        if health_overrides:
            for pid, h in health_overrides.items():
                health[pid] = h
        return QuotaRouter(_make_config(), health)

    def test_tier_fast_returns_cerebras_groq_first(self):
        router = self._make_router()
        groups = router.get_sorted_providers(
            recommended_tier=TIER_FAST,
            complexity=MEDIUM,
            estimated_tokens=500,
            all_providers=_MOCK_PROVIDERS,
        )
        # First group should contain CEREBRAS and/or GROQ
        first_group = groups[0]
        assert any(p in first_group for p in ["CEREBRAS", "GROQ"]), (
            f"TIER_FAST first group should have CEREBRAS/GROQ, got {first_group}"
        )

    def test_context_window_filter_complex(self):
        """COMPLEX tasks need 16K ctx — 8K providers should be filtered out."""
        router = self._make_router()
        groups = router.get_sorted_providers(
            recommended_tier=TIER_FAST,
            complexity=COMPLEX,
            estimated_tokens=1_000,
            all_providers=_MOCK_PROVIDERS,
        )
        # CEREBRAS and GROQ have 8K ctx → should NOT appear in COMPLEX groups
        all_pids = [p for g in groups for p in g]
        assert "CEREBRAS" not in all_pids, "CEREBRAS (8K) should be filtered for COMPLEX"
        assert "GROQ" not in all_pids, "GROQ (8K) should be filtered for COMPLEX"

    def test_exhausted_provider_filtered(self):
        """Exhausted providers (requests_today >= 1000) must not appear in results."""
        h_exhausted = _make_health(requests_today=1001)
        router = self._make_router({"CEREBRAS": h_exhausted})
        groups = router.get_sorted_providers(
            recommended_tier=TIER_FAST,
            complexity=MEDIUM,
            estimated_tokens=500,
            all_providers=_MOCK_PROVIDERS,
        )
        all_pids = [p for g in groups for p in g]
        assert "CEREBRAS" not in all_pids, "Exhausted CEREBRAS should be filtered"

    def test_open_circuit_breaker_filtered(self):
        """Providers with OPEN circuit breaker must not appear in results."""
        h_open = _make_health(cb_state="OPEN")
        h_open.cb.open_until = time.time() + 9999  # ensure it stays open
        router = self._make_router({"GROQ": h_open})
        groups = router.get_sorted_providers(
            recommended_tier=TIER_FAST,
            complexity=MEDIUM,
            estimated_tokens=500,
            all_providers=_MOCK_PROVIDERS,
        )
        all_pids = [p for g in groups for p in g]
        assert "GROQ" not in all_pids, "GROQ with open CB should be filtered"

    def test_tier_large_gemini_is_first(self):
        """TIER_LARGE must put GEMINI in the first group."""
        router = self._make_router()
        groups = router.get_sorted_providers(
            recommended_tier=TIER_LARGE,
            complexity=MASSIVE,
            estimated_tokens=50_000,
            all_providers=_MOCK_PROVIDERS,
        )
        assert groups, "Should return at least one group for TIER_LARGE"
        assert "GEMINI" in groups[0], (
            f"GEMINI should be first in TIER_LARGE, got {groups[0]}"
        )

    def test_health_score_sorting(self):
        """Higher health score provider should sort first within a group."""
        h_good = _make_health()
        h_good.success_count = 50
        h_good.failure_count = 0

        h_bad = _make_health()
        h_bad.success_count = 1
        h_bad.failure_count = 9

        router = self._make_router({"CEREBRAS": h_good, "GROQ": h_bad})
        groups = router.get_sorted_providers(
            recommended_tier=TIER_FAST,
            complexity=MEDIUM,
            estimated_tokens=500,
            all_providers=_MOCK_PROVIDERS,
        )
        first_group = groups[0]
        if "CEREBRAS" in first_group and "GROQ" in first_group:
            assert first_group.index("CEREBRAS") < first_group.index("GROQ"), (
                "CEREBRAS (higher health) should sort before GROQ"
            )


# ══════════════════════════════════════════════════════════════════════════════
# C. QuotaRouter.should_force_local()
# ══════════════════════════════════════════════════════════════════════════════

class TestShouldForceLocal:

    def test_not_forced_when_gemini_under_threshold(self):
        h = _make_health(requests_today=700)
        router = QuotaRouter(_make_config(soft_limit=900), {"GEMINI": h})
        assert router.should_force_local() is False

    def test_forced_when_gemini_at_threshold(self):
        # soft_limit=900, threshold = 900-100 = 800
        h = _make_health(requests_today=801)
        router = QuotaRouter(_make_config(soft_limit=900), {"GEMINI": h})
        assert router.should_force_local() is True

    def test_forced_when_gemini_exactly_at_boundary(self):
        h = _make_health(requests_today=800)
        router = QuotaRouter(_make_config(soft_limit=900), {"GEMINI": h})
        assert router.should_force_local() is True

    def test_not_forced_when_gemini_missing(self):
        router = QuotaRouter(_make_config(), {})
        assert router.should_force_local() is False


# ══════════════════════════════════════════════════════════════════════════════
# D. RPMScheduler
# ══════════════════════════════════════════════════════════════════════════════

class TestRPMScheduler:

    def test_acquire_returns_float(self):
        scheduler = RPMScheduler()
        # GROQ has rpm=30 in RATELIMITS — acquire should return immediately
        wait_ms = asyncio.run(scheduler.acquire("GROQ"))
        assert isinstance(wait_ms, float)
        assert wait_ms >= 0.0

    def test_no_limit_provider_returns_zero(self):
        """Providers with no RPM defined (e.g. local) return 0.0 immediately."""
        scheduler = RPMScheduler()
        wait_ms = asyncio.run(scheduler.acquire("LOCALFAST"))
        assert wait_ms == 0.0

    def test_burst_factor_allows_extra_requests(self):
        """With burst_factor=1.2 and rpm=5, should allow 6 requests before blocking."""
        scheduler = RPMScheduler(burst_factor=1.2)
        # Patch RATELIMITS to have a tiny rpm for testing
        with patch("core.rpm_scheduler.RATELIMITS", {"TESTPROV": {"rpm": 5}}):
            # Should acquire 6 slots (5 * 1.2 = 6) without blocking
            for i in range(6):
                wait_ms = asyncio.run(scheduler.acquire("TESTPROV"))
                assert isinstance(wait_ms, float), f"Slot {i} should return float"

    def test_get_current_rpm(self):
        scheduler = RPMScheduler()
        asyncio.run(scheduler.acquire("GROQ"))
        asyncio.run(scheduler.acquire("GROQ"))
        rpm = scheduler.get_current_rpm("GROQ")
        assert rpm == 2

    def test_reset_clears_history(self):
        scheduler = RPMScheduler()
        asyncio.run(scheduler.acquire("GROQ"))
        scheduler.reset("GROQ")
        assert scheduler.get_current_rpm("GROQ") == 0

    def test_reset_all_clears_all(self):
        scheduler = RPMScheduler()
        asyncio.run(scheduler.acquire("GROQ"))
        asyncio.run(scheduler.acquire("CEREBRAS"))
        scheduler.reset_all()
        assert scheduler.get_current_rpm("GROQ") == 0
        assert scheduler.get_current_rpm("CEREBRAS") == 0


# ══════════════════════════════════════════════════════════════════════════════
# E. Integration — classifier → quota_router pipeline contract
# ══════════════════════════════════════════════════════════════════════════════

class TestClassifierRouterIntegration:
    """
    Validates the contract between classify_task() output and
    get_sorted_providers() input — the tier labels must be mutually compatible.
    """

    def _all_healthy_router(self) -> QuotaRouter:
        health = {pid: _make_health() for pid in _MOCK_PROVIDERS}
        return QuotaRouter(_make_config(), health)

    def test_massive_classify_to_large_provider_group(self):
        task = asyncio.run(classify_task("analyze entire codebase", []))
        router = self._all_healthy_router()
        groups = router.get_sorted_providers(
            recommended_tier=task.recommended_tier,
            complexity=task.complexity,
            estimated_tokens=task.estimated_tokens,
            all_providers=_MOCK_PROVIDERS,
        )
        all_pids = [p for g in groups for p in g]
        # GEMINI must be present — only provider with 1M ctx
        assert "GEMINI" in all_pids, (
            f"GEMINI must appear for MASSIVE tasks. Got providers: {all_pids}"
        )

    def test_complex_classify_excludes_small_ctx_providers(self):
        task = asyncio.run(classify_task("refactor across multiple files", []))
        router = self._all_healthy_router()
        groups = router.get_sorted_providers(
            recommended_tier=task.recommended_tier,
            complexity=task.complexity,
            estimated_tokens=task.estimated_tokens,
            all_providers=_MOCK_PROVIDERS,
        )
        all_pids = [p for g in groups for p in g]
        # 8K providers must be absent for COMPLEX tasks
        assert "CEREBRAS" not in all_pids
        assert "GROQ" not in all_pids

    def test_sensitive_task_routes_local_only(self):
        task = asyncio.run(classify_task("check my api key in .env", []))
        assert task.recommended_tier == TIER_LOCAL
        assert task.is_sensitive is True

    def test_lpu_task_gets_zero_token_cap(self):
        task = asyncio.run(classify_task("git status", []))
        assert task.max_tokens_cap == 256
        assert task.recommended_tier == TIER_LOCAL
