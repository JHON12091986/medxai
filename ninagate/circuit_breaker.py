"""
NinaGate Circuit Breaker — provider health scoring + auto-disable.
NINA_FEATURE: ninagate-circuit-breaker v1.1

WIRING:
  This module is used in TWO places:
  1. ninagate/main.py: _circuit_breaker = CircuitBreaker() — the *global* file-backed
     CB that persists health scores across ninagate restarts.
  2. Each ProviderHealth instance has its own in-memory CB (ninagate.main.CircuitBreaker)
     for per-request allow/deny gating.

  The global _circuit_breaker records outcomes after every forward_to_provider() call
  and is checked by /v1/health/providers to expose EMA health scores to all agents.

Usage:
  from ninagate.circuit_breaker import CircuitBreaker
  cb = CircuitBreaker()
  if cb.is_open("gemini-flash"): skip_provider()
  cb.record("gemini-flash", success=True, latency_ms=210.0)
  report = cb.health_report()
"""
import json
import time
import threading
from pathlib import Path

HEALTH_FILE = Path.home() / "nina" / "data" / "router_health.json"


class CircuitBreaker:
    def __init__(self, health_file=HEALTH_FILE):
        self._file = Path(health_file)
        self._lock = threading.Lock()
        self._state: dict = self._load()

    def _load(self) -> dict:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text())
            except Exception:
                pass
        return {}

    def _save(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(json.dumps(self._state, indent=2))

    def _entry(self, provider: str) -> dict:
        if provider not in self._state:
            self._state[provider] = {
                "score": 1.0,
                "fail_streak": 0,
                "disabled_until": 0,
                "total_calls": 0,
                "total_failures": 0,
                "avg_latency_ms": 0.0,
            }
        return self._state[provider]

    def is_open(self, provider: str) -> bool:
        """Return True if provider is circuit-broken (should be skipped)."""
        with self._lock:
            e = self._entry(provider)
            if time.time() < e["disabled_until"]:
                return True
            return False

    def record(self, provider: str, success: bool, latency_ms: float = 0.0):
        """
        Record a call outcome.
        - EMA health score: 95% old weight, 5% new observation.
        - Latency EMA: 90% old weight, 10% new observation (only on success).
        - On failure streak: exponential backoff 60s * 2^streak, max 30min.
        """
        with self._lock:
            e = self._entry(provider)
            e["total_calls"] += 1
            e["score"] = e["score"] * 0.95 + (1.0 if success else 0.0) * 0.05
            if success and latency_ms > 0:
                old_lat = e.get("avg_latency_ms", 0.0)
                e["avg_latency_ms"] = old_lat * 0.9 + latency_ms * 0.1
            if not success:
                e["total_failures"] += 1
                e["fail_streak"] += 1
                if e["score"] < 0.2:
                    backoff = min(60 * (2 ** min(e["fail_streak"], 5)), 1800)
                    e["disabled_until"] = time.time() + backoff
                    print(
                        f"[CircuitBreaker] {provider} OPEN for {backoff}s "
                        f"(score={e['score']:.2f})"
                    )
            else:
                e["fail_streak"] = 0
                if e["score"] > 0.6 and e["disabled_until"] > 0:
                    e["disabled_until"] = 0
                    print(
                        f"[CircuitBreaker] {provider} CLOSED "
                        f"(score recovered to {e['score']:.2f})"
                    )
            self._save()

    def health_report(self) -> dict:
        """Returns per-provider EMA scores, open state, latency, and call stats."""
        with self._lock:
            now = time.time()
            return {
                p: {
                    "score": round(e["score"], 3),
                    "open": now < e["disabled_until"],
                    "disabled_until": e["disabled_until"],
                    "fail_streak": e["fail_streak"],
                    "total_calls": e["total_calls"],
                    "failure_rate": round(
                        e["total_failures"] / max(e["total_calls"], 1), 3
                    ),
                    "avg_latency_ms": round(e.get("avg_latency_ms", 0.0), 1),
                }
                for p, e in self._state.items()
            }
