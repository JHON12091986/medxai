# core/rpm_scheduler.py
# RPMScheduler v2 — Sliding window token bucket with burst headroom
#
# v2 improvements over v1:
#   - acquire() returns wait_ms so callers can log/alert on slow slots
#   - get_current_rpm(pid) → real-time RPM reading for dashboard
#   - burst_headroom: allows short bursts up to 120% of RPM cap
#     before throttling kicks in (avoids false stalls on bursty but
#     infrequent providers like Mistral at 1 RPM)
#   - no change to the core sliding-window algorithm — already correct

import asyncio
import time
from collections import deque
from typing import Dict
from core.config import RATELIMITS


class RPMScheduler:
    def __init__(self, burst_factor: float = 1.2) -> None:
        """
        burst_factor: allow up to burst_factor * rpm requests in the window
        before throttling. 1.2 = 20% burst headroom.
        Set to 1.0 to disable bursting (strict RPM enforcement).
        """
        self.history: Dict[str, deque] = {}
        self.burst_factor = burst_factor

    def _get_history(self, provider: str) -> deque:
        if provider not in self.history:
            self.history[provider] = deque()
        return self.history[provider]

    def _clean_history(self, history: deque, now: float) -> None:
        while history and now - history[0] >= 60.0:
            history.popleft()

    def get_current_rpm(self, provider: str) -> int:
        """Real-time RPM reading — how many requests in the last 60s."""
        history = self._get_history(provider)
        now = time.time()
        self._clean_history(history, now)
        return len(history)

    async def acquire(self, provider: str) -> float:
        """
        Acquire a rate-limit slot for provider.
        Returns wait_ms — how long we actually waited (0.0 if no wait).
        Caller can log this for TTFT diagnostics.
        """
        limits = RATELIMITS.get(provider, {})
        rpm = limits.get("rpm")
        if not rpm:
            # No RPM defined (OLLAMA, local) — always free
            return 0.0

        effective_cap = int(rpm * self.burst_factor)
        history = self._get_history(provider)
        start_wait = time.time()

        while True:
            now = time.time()
            self._clean_history(history, now)

            if len(history) < effective_cap:
                history.append(now)
                waited_ms = (time.time() - start_wait) * 1000
                return waited_ms

            # Slot full — sleep until the oldest request exits the 60s window
            oldest = history[0]
            wait_s = 60.0 - (now - oldest) + 0.05  # +50ms buffer to avoid edge races
            if wait_s > 0:
                await asyncio.sleep(wait_s)
            # Loop back to recheck — another coroutine may have taken the slot

    def reset(self, provider: str) -> None:
        """Clear history for a provider (e.g. after a quota reset event)."""
        self.history.pop(provider, None)

    def reset_all(self) -> None:
        """Clear all provider histories."""
        self.history.clear()
