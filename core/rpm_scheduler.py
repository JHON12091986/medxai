import asyncio
import time
from collections import deque
from typing import Dict
from core.config import RATELIMITS

class RPMScheduler:
    def __init__(self) -> None:
        # Maps provider name -> deque of request timestamps in the last 60s
        self.history: Dict[str, deque] = {}

    def _get_history(self, provider: str) -> deque:
        if provider not in self.history:
            self.history[provider] = deque()
        return self.history[provider]

    def _clean_history(self, history: deque, now: float) -> None:
        # Remove timestamps older than 60 seconds
        while history and now - history[0] >= 60.0:
            history.popleft()

    async def acquire(self, provider: str) -> None:
        """Acquires a slot for a request to the provider. Sleeps if RPM limit is reached."""
        limits = RATELIMITS.get(provider, {})
        rpm = limits.get("rpm")
        if not rpm:
            # If no RPM limit is defined (like OLLAMA or local models), proceed immediately
            return

        history = self._get_history(provider)
        
        while True:
            now = time.time()
            self._clean_history(history, now)

            if len(history) < rpm:
                # Slot available! Record the request timestamp and proceed
                history.append(now)
                return

            # RPM limit reached. Calculate wait time until the oldest request falls out of the 60s window
            oldest = history[0]
            wait_time = 60.0 - (now - oldest)
            
            if wait_time > 0:
                # Sleep asynchronously until a slot opens up
                await asyncio.sleep(wait_time)
