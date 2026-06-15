# core/quota_router.py
# QuotaRouter v2 — Tier-aware, classifier-driven provider sorting
#
# New in v2:
#   - get_sorted_providers(tier_label, task) → returns providers pre-sorted
#     by health score, filtered by context window AND complexity tier
#   - TIER_MAP: maps classifier's recommended_tier → actual provider name lists
#   - is_context_fit(pid, estimated_tokens) → guards context window overflow
#   - demote/promote logic unchanged but now also respects tier preference

from __future__ import annotations
from core.config import RATELIMITS, NinaConfig
from core.task_classifier import (
    TIER_LOCAL, TIER_FAST, TIER_DEEP, TIER_LARGE,
    SIMPLE, MEDIUM, COMPLEX, MASSIVE,
)

# Maps classifier recommended_tier → ordered list of provider name sets to try
# Each entry is tried in order; if all in the first set are exhausted, fall to next
TIER_PREFERENCE_ORDER: dict[str, list[list[str]]] = {
    TIER_LOCAL: [
        ["LOCALFAST", "LOCALHEAVY"],
        ["POLLINATIONS", "CHUTES", "HFPUBLIC"],  # free keyless fallback
    ],
    TIER_FAST: [
        ["CEREBRAS", "GROQ"],           # sub-second inference
        ["DEEPSEEK", "FIREWORKS"],      # fast cloud
        ["GEMINI"],                     # large ctx fallback
        ["LOCALFAST", "LOCALHEAVY"],    # local last resort
    ],
    TIER_DEEP: [
        ["DEEPSEEK", "MISTRAL"],        # reasoning quality
        ["GEMINI", "COHERE"],           # large ctx
        ["GROQ", "CEREBRAS"],           # speed fallback
        ["LOCALHEAVY"],                 # local last resort
    ],
    TIER_LARGE: [
        ["GEMINI"],                     # 1M ctx — only option for MASSIVE
        ["OPENROUTER", "COHERE"],       # 128K fallback
        ["DEEPSEEK"],                   # 64K fallback
        ["LOCALHEAVY"],                 # local last resort
    ],
}

# Minimum context window required per complexity tier
# Prevents routing a COMPLEX task to an 8K provider
MIN_CONTEXT_FOR_TIER: dict[str, int] = {
    SIMPLE:  1_000,
    MEDIUM:  4_000,
    COMPLEX: 16_000,
    MASSIVE: 100_000,
}


class QuotaRouter:
    def __init__(self, config: NinaConfig, health_tracker: dict) -> None:
        self.config  = config
        self.health  = health_tracker

    # ── Quota & usage ─────────────────────────────────────────────────────────

    def get_provider_usage(self, pid: str) -> float:
        """Returns usage fraction (0.0–1.0+) — max of RPD and TPD usage."""
        limits = RATELIMITS.get(pid, {})
        h = self.health.get(pid)
        if not h:
            return 0.0
        pcts = [0.0]
        if rpd := limits.get("rpd"):
            pcts.append(h.requests_today / rpd)
        if tpd := limits.get("tpd"):
            pcts.append(h.tokens_today / tpd)
        return max(pcts)

    def is_exhausted(self, pid: str) -> bool:
        """True if provider has hit its daily quota or hard safety cap."""
        if pid == "GEMINI":
            h = self.health.get(pid)
            if h and h.requests_today >= self.config.quota_soft_limit:
                return True
        h = self.health.get(pid)
        if not h:
            return False
        if h.requests_today >= 1000:
            return True
        return self.get_provider_usage(pid) >= 1.0

    def is_context_fit(self, pid: str, estimated_tokens: int, all_providers: dict) -> bool:
        """True if provider's context window can hold the estimated input."""
        from core.router import LOCAL_PROVIDERS
        meta = all_providers.get(pid) or LOCAL_PROVIDERS.get(pid, {})
        ctx = meta.get("context_window", 8192)
        return ctx >= max(estimated_tokens, 1)

    # ── Score adjustment ──────────────────────────────────────────────────────

    def adjust_health_score(self, pid: str, base_score: float) -> float:
        """Demote providers approaching 80% daily quota."""
        usage = self.get_provider_usage(pid)
        if usage >= 0.8:
            penalty = (usage - 0.8) * 5.0   # max penalty 1.0 at 100% usage
            return max(0.0, base_score - penalty)
        return base_score

    # ── Tier-aware sorted provider list ──────────────────────────────────────

    def get_sorted_providers(
        self,
        recommended_tier: str,
        complexity: str,
        estimated_tokens: int,
        all_providers: dict,
    ) -> list[list[str]]:
        """
        Returns a list-of-lists matching TIER_PREFERENCE_ORDER for the given
        recommended_tier, but filters each group to only include providers that:
          1. Are not exhausted
          2. Have sufficient context window for estimated_tokens
          3. Meet minimum context floor for the complexity tier
          4. Have their circuit breaker closed (or half-open)
          5. Are sorted by adjusted health score (descending)

        The outer list preserves tier group ordering — caller tries group[0]
        first, falls back to group[1], etc.
        """
        min_ctx = MIN_CONTEXT_FOR_TIER.get(complexity, 1_000)
        effective_min = max(min_ctx, estimated_tokens)
        groups = TIER_PREFERENCE_ORDER.get(recommended_tier, TIER_PREFERENCE_ORDER[TIER_FAST])

        result = []
        for group in groups:
            filtered = []
            for pid in group:
                h = self.health.get(pid)
                if not h:
                    continue
                if not h.cb.can_attempt():
                    continue
                if self.is_exhausted(pid):
                    continue
                from core.router import LOCAL_PROVIDERS
                meta = all_providers.get(pid) or LOCAL_PROVIDERS.get(pid, {})
                if meta.get("context_window", 8192) < effective_min:
                    continue
                filtered.append(pid)

            # Sort by adjusted health score
            filtered.sort(
                key=lambda p: self.adjust_health_score(p, self.health[p].health_score),
                reverse=True,
            )
            result.append(filtered)

        return result

    # ── Local promotion ───────────────────────────────────────────────────────

    def should_force_local(self) -> bool:
        """True when Gemini is within 100 requests of the soft quota limit."""
        h = self.health.get("GEMINI")
        if h and h.requests_today >= (self.config.quota_soft_limit - 100):
            return True
        return False
