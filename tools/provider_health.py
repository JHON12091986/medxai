"""
tools/provider_health.py
P1: Provider Health Monitoring — rolling window tracker + persistent state + recovery alerts.
Observability only. Does NOT modify routing logic in core/router.py.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("nina.provider_health")

_STATE_PATH = Path("data/provider_health.json")
_WINDOW_S = 600          # 10-minute rolling window
_RECENT_CALLS = 20       # max calls to keep per provider
_FAILURE_STREAK_ALERT = 3
_RECOVERY_ALERT_AFTER = 1  # successes after a failure streak


@dataclass
class ProviderWindow:
    """Rolling 10-minute call window for a single provider."""
    name: str
    # Each entry: {"ts": float, "ok": bool, "latency_ms": float}
    calls: deque = field(default_factory=lambda: deque(maxlen=_RECENT_CALLS))
    last_error: str = ""
    alerted_degraded: bool = False  # True after degraded alert sent — prevents spam
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    def record(self, ok: bool, latency_ms: float, error: str = "") -> None:
        now = time.time()
        self.calls.append({"ts": now, "ok": ok, "latency_ms": latency_ms})
        if ok:
            self.consecutive_failures = 0
            self.consecutive_successes += 1
            if error:
                self.last_error = ""
        else:
            self.consecutive_successes = 0
            self.consecutive_failures += 1
            if error:
                self.last_error = error

    def _window_calls(self) -> list[dict]:
        cutoff = time.time() - _WINDOW_S
        return [c for c in self.calls if c["ts"] >= cutoff]

    @property
    def ok_rate(self) -> float:
        wc = self._window_calls()
        if not wc:
            return 1.0
        return sum(1 for c in wc if c["ok"]) / len(wc)

    @property
    def avg_latency_ms(self) -> float:
        wc = self._window_calls()
        if not wc:
            return 0.0
        return sum(c["latency_ms"] for c in wc) / len(wc)

    @property
    def call_count_window(self) -> int:
        return len(self._window_calls())

    def summary(self) -> dict:
        return {
            "name": self.name,
            "ok_rate": round(self.ok_rate, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "call_count_10m": self.call_count_window,
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "alerted_degraded": self.alerted_degraded,
        }


class ProviderHealthTracker:
    """
    Standalone observability tracker. Import into HybridRouter and call
    tracker.record(pid, ok, latency_ms) after every provider call.
    """

    def __init__(self) -> None:
        self._windows: dict[str, ProviderWindow] = {}
        self._notify_fn = None  # injected at runtime
        self._load()

    def set_notify(self, fn) -> None:
        """Inject a coroutine function: async (msg: str) -> None."""
        self._notify_fn = fn

    def _get(self, pid: str) -> ProviderWindow:
        if pid not in self._windows:
            self._windows[pid] = ProviderWindow(name=pid)
        return self._windows[pid]

    def record_sync(self, pid: str, ok: bool, latency_ms: float, error: str = "") -> None:
        """Thread-safe synchronous record. Use this from non-async call sites."""
        w = self._get(pid)
        w.record(ok, latency_ms, error)

    async def record(self, pid: str, ok: bool, latency_ms: float, error: str = "") -> None:
        """Async record — also fires Telegram alerts when needed."""
        w = self._get(pid)
        was_degraded = w.alerted_degraded
        w.record(ok, latency_ms, error)

        # — Degraded alert: 3 consecutive failures, alert once per streak —
        if (
            not ok
            and w.consecutive_failures >= _FAILURE_STREAK_ALERT
            and not w.alerted_degraded
        ):
            w.alerted_degraded = True
            await self._alert(
                f"⚠️ Provider *{pid}* degraded after {w.consecutive_failures} consecutive failures. "
                f"Last error: `{error or 'unknown'}`. Routing to fallback tier."
            )

        # — Recovery alert: first success after a degraded streak —
        elif ok and was_degraded and w.consecutive_successes >= _RECOVERY_ALERT_AFTER:
            w.alerted_degraded = False
            await self._alert(
                f"✅ Provider *{pid}* recovered. "
                f"Success after degraded streak. Ok rate (10m): {w.ok_rate:.0%}."
            )

        self._persist()

    async def _alert(self, msg: str) -> None:
        logger.warning("provider_health_alert: %s", msg)
        if self._notify_fn:
            try:
                await self._notify_fn(msg)
            except Exception as e:
                logger.warning("provider_health_notify_failed: %s", e)

    def health_summary(self) -> dict[str, dict]:
        """Returns {provider: {ok_rate, avg_latency, last_error}} — used by /v1/status."""
        return {pid: w.summary() for pid, w in self._windows.items()}

    def _persist(self) -> None:
        try:
            _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                pid: {
                    "ok_rate": w.ok_rate,
                    "avg_latency_ms": w.avg_latency_ms,
                    "call_count_10m": w.call_count_window,
                    "consecutive_failures": w.consecutive_failures,
                    "last_error": w.last_error,
                    "alerted_degraded": w.alerted_degraded,
                    "updated_at": time.time(),
                }
                for pid, w in self._windows.items()
            }
            _STATE_PATH.write_text(json.dumps(payload, indent=2))
        except Exception as e:
            logger.warning("provider_health_persist_failed: %s", e)

    def _persist(self) -> None:
        try:
            _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                pid: {
                    "ok_rate": w.ok_rate,
                    "avg_latency_ms": w.avg_latency_ms,
                    "call_count_10m": w.call_count_window,
                    "consecutive_failures": w.consecutive_failures,
                    "last_error": w.last_error,
                    "alerted_degraded": w.alerted_degraded,
                    "updated_at": time.time(),
                }
                for pid, w in self._windows.items()
            }
            _STATE_PATH.write_text(json.dumps(payload, indent=2))
        except Exception as e:
            logger.warning("provider_health_persist_failed: %s", e)

    def _load(self) -> None:
        if not _STATE_PATH.exists():
            return
        try:
            data = json.loads(_STATE_PATH.read_text())
            for pid, s in data.items():
                w = ProviderWindow(name=pid)
                w.consecutive_failures = s.get("consecutive_failures", 0)
                w.last_error = s.get("last_error", "")
                w.alerted_degraded = s.get("alerted_degraded", False)
                self._windows[pid] = w
            logger.info("provider_health_loaded: %d providers", len(self._windows))
        except Exception as e:
            logger.warning("provider_health_load_failed: %s", e)


# Module-level singleton — import this everywhere
tracker = ProviderHealthTracker()
