from core.config import RATELIMITS, NinaConfig

class QuotaRouter:
    def __init__(self, config: NinaConfig, health_tracker: dict) -> None:
        self.config = config
        self.health = health_tracker

    def get_provider_usage(self, pid: str) -> float:
        """Returns the usage percentage (0.0 to 1.0+) of the provider's daily quota."""
        limits = RATELIMITS.get(pid, {})
        h = self.health.get(pid)
        if not h:
            return 0.0

        rpd_limit = limits.get("rpd")
        tpd_limit = limits.get("tpd")

        usage_pcts = [0.0]

        if rpd_limit:
            usage_pcts.append(h.requests_today / rpd_limit)
        if tpd_limit:
            usage_pcts.append(h.tokens_today / tpd_limit)

        return max(usage_pcts)

    def is_exhausted(self, pid: str) -> bool:
        """Checks if a provider has exhausted its daily quota or hard limit."""
        # Gemini specific soft limit cap
        if pid == "GEMINI" and self.health[pid].requests_today >= self.config.quota_soft_limit:
            return True
        
        h = self.health.get(pid)
        if not h:
            return False

        if h.requests_today >= 1000:  # Hard safety cap
            return True

        return self.get_provider_usage(pid) >= 1.0

    def adjust_health_score(self, pid: str, base_score: float) -> float:
        """Adjusts the routing score based on quota usage (demotion at 80%)."""
        usage = self.get_provider_usage(pid)
        if usage >= 0.8:
            # Scale down score sharply as usage approaches 1.0
            penalty = (usage - 0.8) * 5.0  # At 1.0 usage, penalty is 1.0
            return max(0.0, base_score - penalty)
        return base_score

    def should_force_local(self) -> bool:
        """Checks if cloud quotas are tight enough to promote local fallback."""
        # Check if Gemini request limit is close to soft limit
        gemini_health = self.health.get("GEMINI")
        if gemini_health and gemini_health.requests_today >= (self.config.quota_soft_limit - 100):
            return True
        return False
