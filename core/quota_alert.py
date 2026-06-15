# core/quota_alert.py
# Module 11 — Proactive Quota Reset Alerter
#
# Fires a Telegram summary 30 minutes before each provider's daily quota resets.
# Summary includes:
#   - Providers >70% used (warn: approaching limit)
#   - Providers at 0% (fully available for the next window)
#   - Recommended routing tier for the next window
#
# Integration:
#   1. Instantiate QuotaAlerter(router, config) in nina.py after router.initialize()
#   2. Call await alerter.start() — runs APScheduler in background
#   3. Call alerter.stop() in shutdown hook
#
# Reset times are read from config.quota_reset_times (dict[str, str], provider → "HH:MM" UTC)
# Falls back to a default 24h rolling window if not configured.

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    _HAS_APSCHEDULER = True
except ImportError:
    _HAS_APSCHEDULER = False

if TYPE_CHECKING:
    from core.router import HybridRouter
    from core.config import NinaConfig

import tools.jules as jules

logger = logging.getLogger("nina.quota_alert")

# Default reset schedule — UTC hour:minute for each provider's daily window reset.
# Override per-provider in NinaConfig.quota_reset_times if known.
_DEFAULT_RESET_HOUR_UTC = 13   # 1 PM UTC = 7 PM BD
_ALERT_LEAD_MINUTES     = 30   # fire alert this many minutes before reset
_WARN_THRESHOLD         = 0.70 # providers above this fraction get a warning badge

# Providers to include in pre-reset summary (skip LOCAL/keyless — they don't have daily limits)
_TRACKED_PROVIDERS = [
    "GEMINI", "GROQ", "CEREBRAS", "DEEPSEEK", "MISTRAL",
    "TOGETHER", "COHERE", "FIREWORKS", "XAI", "PERPLEXITY",
    "SAMBANOVA", "HYPERBOLIC", "NOVITA", "OPENROUTER", "ONEBRAIN",
]


class QuotaAlerter:
    """
    APScheduler-backed background service that sends a Telegram pre-reset
    summary 30 minutes before the daily quota window rolls over.
    """

    def __init__(self, router: "HybridRouter", config: "NinaConfig") -> None:
        self.router  = router
        self.config  = config
        self._scheduler: "AsyncIOScheduler | None" = None

    async def start(self) -> None:
        """Start the background scheduler. Call once after router.initialize()."""
        if not _HAS_APSCHEDULER:
            logger.warning(
                "apscheduler not installed — quota pre-reset alerts disabled. "
                "Install with: pip install apscheduler"
            )
            return

        self._scheduler = AsyncIOScheduler(timezone="UTC")

        # Fire 30 min before the daily reset hour
        alert_minute = 60 - _ALERT_LEAD_MINUTES  # → minute=30
        alert_hour   = _DEFAULT_RESET_HOUR_UTC - 1 if alert_minute == 30 else _DEFAULT_RESET_HOUR_UTC

        self._scheduler.add_job(
            self._send_pre_reset_summary,
            CronTrigger(hour=alert_hour, minute=alert_minute, timezone="UTC"),
            id="quota_pre_reset_alert",
            replace_existing=True,
            misfire_grace_time=300,   # tolerate up to 5-minute scheduler drift
        )
        self._scheduler.start()
        logger.info(
            "quota_alert scheduler started — fires daily at %02d:%02d UTC",
            alert_hour, alert_minute,
        )

    def stop(self) -> None:
        """Gracefully shut down the scheduler."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("quota_alert scheduler stopped")

    # ── Alert builder ─────────────────────────────────────────────────────────

    async def _send_pre_reset_summary(self) -> None:
        """Build and dispatch the pre-reset Telegram summary."""
        try:
            msg = self._build_summary()
            await jules.send_telegram(msg)
            logger.info("quota_pre_reset_alert sent")
        except Exception as e:
            logger.error("quota_alert_send_failed: %s", e)

    def _build_summary(self) -> str:
        now_utc   = datetime.now(tz=timezone.utc)
        reset_utc = now_utc.replace(
            hour=_DEFAULT_RESET_HOUR_UTC, minute=0, second=0, microsecond=0
        )
        if reset_utc <= now_utc:
            reset_utc += timedelta(days=1)
        mins_to_reset = int((reset_utc - now_utc).total_seconds() // 60)

        warn_lines:      list[str] = []
        available_lines: list[str] = []
        recommended_tier: str      = "FAST"  # default for next window

        for pid in _TRACKED_PROVIDERS:
            h = self.router.health.get(pid)
            if not h:
                continue

            usage = self.router.quota_router.get_provider_usage(pid)
            reqs  = h.requests_today
            score = h.health_score

            if usage >= _WARN_THRESHOLD:
                bar   = self._usage_bar(usage)
                badge = "🔴" if usage >= 1.0 else "🟡"
                warn_lines.append(f"{badge} *{pid}*: {bar} {usage*100:.0f}% ({reqs} reqs)")
            elif usage < 0.05 and score >= 0.8:
                available_lines.append(f"✅ *{pid}* — {score:.2f} health score")

        # Suggest routing tier for next window
        gemini_h = self.router.health.get("GEMINI")
        if gemini_h and gemini_h.requests_today >= (self.config.quota_soft_limit - 100):
            recommended_tier = "LOCAL → FAST"
        elif warn_lines:
            recommended_tier = "FAST (CEREBRAS/GROQ)"
        else:
            recommended_tier = "NORMAL — all tiers healthy"

        lines = [
            f"⏰ *NINA Quota Pre-Reset Alert* — resets in *{mins_to_reset} min*\n",
        ]

        if warn_lines:
            lines.append("*⚠️ Approaching limit:*")
            lines.extend(warn_lines)
            lines.append("")

        if available_lines:
            lines.append("*💚 Fully available next window:*")
            lines.extend(available_lines[:5])   # cap at 5 to keep message compact
            lines.append("")

        lines.append(f"*📡 Recommended tier for next window:* `{recommended_tier}`")
        lines.append(f"_Reset at {reset_utc.strftime('%H:%M UTC')} · {now_utc.strftime('%Y-%m-%d')}_")

        return "\n".join(lines)

    @staticmethod
    def _usage_bar(fraction: float, width: int = 10) -> str:
        filled = min(width, int(fraction * width))
        return "▓" * filled + "░" * (width - filled)


# ── Manual trigger helper (for nf gemini status or tests) ────────────────────

async def send_now(router: "HybridRouter", config: "NinaConfig") -> str:
    """Build and return the alert message without scheduling — for manual triggers."""
    alerter = QuotaAlerter(router, config)
    return alerter._build_summary()
