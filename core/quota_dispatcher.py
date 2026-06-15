"""
core/quota_dispatcher.py
========================
Quota-Aware Task Dispatcher

Sits between the NINA agentic loop and HybridRouter.
Before any task runs, it:
  1. Reads data/agy_quota.json  (written by agy_quota_monitor.sh)
  2. Runs TokenGuard evaluation → classifies prompt, estimates tokens
  3. Returns a DispatchPlan: which tool/provider to use + compressed prompt

This is the SINGLE entry point for all LLM calls from NINA.
All agents should call dispatcher.dispatch() instead of router.route() directly.

USAGE
-----
    from core.quota_dispatcher import QuotaDispatcher
    dispatcher = QuotaDispatcher(router)
    plan = dispatcher.dispatch(prompt, context=code_context)
    result = await plan.execute()
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from core.logger import get_logger
from core.task_classifier import ClassifiedTask
from tools.nina_token_guard import TokenGuard, GuardDecision

logger = get_logger("nina.dispatcher")
QUOTA_PATH = Path("data/agy_quota.json")


@dataclass
class DispatchPlan:
    provider: str
    prompt: str           # compressed
    tier: str
    tokens: int
    cached_result: Optional[str]
    _execute_fn: Optional[Callable] = None

    async def execute(self) -> str:
        if self.cached_result:
            logger.info(f"dispatch_cache_hit tier={self.tier}")
            return self.cached_result
        if self._execute_fn:
            return await self._execute_fn(self.provider, self.prompt)
        return f"[DispatchPlan] No executor set for provider={self.provider}"


class QuotaDispatcher:
    def __init__(self, router) -> None:
        self.router = router
        self.guard = TokenGuard()
        self._quota: dict = {}
        self._load_quota()

    def _load_quota(self) -> None:
        if QUOTA_PATH.exists():
            try:
                self._quota = json.loads(QUOTA_PATH.read_text())
            except Exception:
                self._quota = {}

    def refresh_quota(self) -> None:
        """Reload quota state from disk (call after agy_quota_monitor.sh runs)."""
        self._load_quota()
        self.guard._load_quota()

    def dispatch(
        self,
        prompt: str,
        context: str = "",
        force_tier: Optional[str] = None,
    ) -> DispatchPlan:
        """
        Classify → compress → route.
        Returns a DispatchPlan with provider + compressed prompt.
        Call plan.execute() to actually run the LLM call.
        """
        self.refresh_quota()
        decision: GuardDecision = self.guard.evaluate(
            prompt, context=context, force_tier=force_tier
        )

        logger.info(
            f"dispatch provider={decision.provider} tier={decision.tier} "
            f"tokens={decision.estimated_tokens} reason={decision.reason}"
        )

        async def _execute(provider: str, compressed_prompt: str) -> str:
            task = ClassifiedTask(
                task_type="quick" if decision.tier == "TRIVIAL" else
                          "coding" if decision.tier in ("COMPLEX","CRITICAL") else "general",
                estimated_tokens=decision.estimated_tokens,
                requires_tool_use=False,
                is_multilingual=False,
            )
            messages = [{"role": "user", "content": compressed_prompt}]
            result = await self.router.route(
                goal=compressed_prompt,
                messages=messages,
                task=task,
                force_local=(provider in ("LOCALFAST", "LOCALHEAVY")),
            )
            # Cache the result for future identical calls
            self.guard.cache_result(compressed_prompt, result, ttl=3600)
            return result

        return DispatchPlan(
            provider=decision.provider,
            prompt=decision.prompt,
            tier=decision.tier,
            tokens=decision.estimated_tokens,
            cached_result=decision.cached,
            _execute_fn=_execute,
        )

    def summary(self) -> dict:
        """Return current quota + routing recommendation."""
        return {
            "quota": self._quota,
            "recommended": self._quota.get("recommended_model", "UNKNOWN"),
            "exhausted": self._quota.get("exhausted", False),
        }
