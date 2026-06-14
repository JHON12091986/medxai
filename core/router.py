# core/router.py
from typing import Any, List, Dict, Optional, Tuple, cast
import asyncio
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field

import os
import re
import time
import uuid
import httpx
from pydantic import ValidationError

from core.config import NinaConfig
from core.logger import get_logger
from core.task_classifier import ClassifiedTask
import tools.jules as jules
from tools.model_discovery import ModelDiscoveryService

_ = jules

logger = get_logger("nina.router")

# F-03f: Bangla Unicode block U+0980–U+09FF
_BANGLA_RE = re.compile(r"[\u0980-\u09FF]")

def load_providers_from_json() -> tuple[dict, dict, dict]:
    path = Path(__file__).parent.parent / "ninagate" / "providers.json"
    t1, t2, t3 = {}, {}, {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
            for p in data:
                entry = {
                    "base_url": p.get("base_url"),
                    "model": p.get("model"),
                    "key_field": p.get("api_key_env").lower() if p.get("api_key_env") else None
                }
                tier = p.get("tier", 2)
                name = p["name"].upper()
                if tier == 1: t1[name] = entry
                elif tier == 2: t2[name] = entry
                elif tier == 3: t3[name] = entry
        except Exception as e:
            logger.error(f"Failed to load providers from json: {e}")
    return t1, t2, t3

PROVIDERS_TIER1, PROVIDERS_TIER2, PROVIDERS_TIER3 = load_providers_from_json()

# Precomputed to avoid O(N) dict merging overhead in hot paths like routing lookups
ALL_PROVIDERS = PROVIDERS_TIER1 | PROVIDERS_TIER2 | PROVIDERS_TIER3

LOCAL_PROVIDERS = {
    "LOCALFAST": {"model": "qwen2.5:1.5b"},
    "LOCALHEAVY": {"model": "qwen2.5:7b"},
}

CACHE_TTL = {
    "sensitive": 0,
    "quick": 3600,
    "research": 1800,
    "coding": 21600,
    "document": 14400,
    "general": 7200,
    "math": 21600,
    "multilingual": 7200,
}

STEP_BUDGETS = {
    "quick": 3,
    "general": 5,
    "multilingual": 5,
    "math": 6,
    "coding": 8,
    "document": 8,
    "research": 10,
    "sensitive": 5,
}
DEFAULT_MAX_STEPS = 5


class CircuitBreaker:
    FAILURE_THRESHOLD = 3
    WINDOW_S = 120
    RECOVERY_S = 60

    def __init__(self) -> None:
        self.failures: List[float] = []
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.open_until = 0.0
        self.half_open_index = 0

    def record_success(self) -> None:
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failures.clear()
        elif self.state == "CLOSED":
            self.failures.clear()

    def record_failure(self, cooldown_s: Optional[float] = None) -> None:
        now = time.time()
        self.failures.append(now)
        # Purge old failures
        self.failures = [f for f in self.failures if now - f < self.WINDOW_S]

        if len(self.failures) >= self.FAILURE_THRESHOLD:
            self.state = "OPEN"
            wait = cooldown_s or self.RECOVERY_S
            self.open_until = now + wait

    def can_attempt(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            if now > self.open_until:
                self.state = "HALF_OPEN"
                return True
            return False
        return True


@dataclass
class ProviderHealth:
    success_count: int = 0
    failure_count: int = 0
    latencies: deque = field(default_factory=lambda: deque(maxlen=20))
    _latency_sum: float = 0.0
    requests_today: int = 0
    tokens_today: int = 0
    last_request_ts: float = 0.0
    reserved_requests: int = 0
    reserved_tokens: int = 0
    consecutive_failures: int = 0
    cb: CircuitBreaker = field(default_factory=CircuitBreaker)

    @property
    def cooldown_until(self) -> float:
        return self.cb.open_until

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return self._latency_sum / len(self.latencies)

    @property
    def health_score(self) -> float:
        # Simple score based on success rate and latency
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        success_rate = self.success_count / total
        # Penalty for high latency (above 2s)
        lat_penalty = min(0.5, self.avg_latency_ms / 5000.0)
        # Penalty for recent failures (circuit breaker state)
        degraded_penalty = 0.5 if self.cb.state != "CLOSED" else 0.0
        return max(0.0, success_rate - lat_penalty - degraded_penalty)

    def record_success(self, latency_ms: float, total_tokens: int) -> None:
        self.success_count += 1
        self.consecutive_failures = 0
        self.requests_today += 1
        self.tokens_today += max(0, int(total_tokens))
        self.last_request_ts = time.time()
        # O(1) latency sum tracking
        if len(self.latencies) == self.latencies.maxlen:
            self._latency_sum -= self.latencies[0]
        self._latency_sum += float(latency_ms)
        self.latencies.append(float(latency_ms))
        self.cb.record_success()

    def record_failure(self, cooldown_s: Optional[float] = None) -> None:
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_request_ts = time.time()
        self.cb.record_failure(cooldown_s=cooldown_s)

    def reset_daily(self) -> None:
        self.requests_today = 0
        self.tokens_today = 0
        self.reserved_requests = 0
        self.reserved_tokens = 0


class ResponseCache:
    def __init__(self) -> None:
        self.s: dict = {}

    def _k(self, prompt: str, messages: list | None = None) -> str:
        s = prompt
        if messages:
            s += json.dumps(messages, sort_keys=True)
        return hashlib.md5(s.encode()).hexdigest()

    def get(self, prompt: str, messages: list | None = None) -> str | None:
        k = self._k(prompt, messages)
        if k in self.s:
            v = self.s[k]
            if time.time() < v.get("expires_at", 0):
                return cast(str, v["text"])
        return None

    def set(self, prompt: str, text: str, ttl: int, messages: list | None = None) -> None:
        k = self._k(prompt, messages)
        self.s[k] = {"text": text, "expires_at": time.time() + ttl}

    def purge_expired(self) -> None:
        now = time.time()
        self.s = {k: v for k, v in self.s.items() if now < v.get("expires_at", 0)}

    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.s, f)
        except Exception as e:
            logger.warning(f"cache_save_failed: {e}")

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                self.s = json.load(f)
            self.purge_expired()
        except Exception as e:
            logger.warning(f"cache_load_failed: {e}")


class CostTracker:
    def __init__(self) -> None:
        self.daily_cost_usd = 0.0

    def record(
        self,
        provider: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        error: str | None = None,
        req_id: str | None = None,
    ) -> None:
        # Mock cost calculation
        cost = (input_tokens + output_tokens) * 0.0000002
        self.daily_cost_usd += cost
        write_log(
            {
                "id": req_id or str(uuid.uuid4()),
                "provider": provider,
                "task": task_type,
                "in": input_tokens,
                "out": output_tokens,
                "cost": round(cost, 8),
                "error": error,
            }
        )

    def reset_daily(self) -> None:
        self.daily_cost_usd = 0.0


def write_log(entry: dict, log_path: str = "logs/router.log") -> None:
    """Writes a structured JSON log entry to the specified path."""
    entry["ts"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


class HybridRouter:
    def __init__(self, config: NinaConfig) -> None:
        self.config = config
        self.health: Dict[str, ProviderHealth] = {
            pid: ProviderHealth() for pid in ALL_PROVIDERS
        }
        for pid in LOCAL_PROVIDERS:
            self.health[pid] = ProviderHealth()
        self.cache = ResponseCache()
        self.cost = CostTracker()
        self.discovery = ModelDiscoveryService()
        self.http: httpx.AsyncClient | None = None
        self._idle_task: asyncio.Task | None = None

    async def initialize(self) -> None:
        self.http = httpx.AsyncClient(timeout=60.0)
        # Re-load from index logic if necessary, for now use providers.json result
        self.cache.load("data/router_cache.json")
        self._load_circuit_state()
        self._idle_task = asyncio.create_task(self._idle_monitor())

    def _save_circuit_state(self) -> None:
        state = {
            pid: {
                "state": h.cb.state,
                "open_until": h.cb.open_until,
                "requests_today": h.requests_today,
                "tokens_today": h.tokens_today,
            }
            for pid, h in self.health.items()
        }
        try:
            with open("data/circuit_state.json", "w") as f:
                json.dump(state, f)
        except Exception as e:
            logger.warning(f"circuit_save_failed: {e}")

    def _load_circuit_state(self) -> None:
        if not os.path.exists("data/circuit_state.json"):
            return
        try:
            with open("data/circuit_state.json", "r") as f:
                state = json.load(f)
            for pid, s in state.items():
                if pid in self.health:
                    h = self.health[pid]
                    h.cb.state = s.get("state", "CLOSED")
                    h.cb.open_until = s.get("open_until", 0.0)
                    h.requests_today = s.get("requests_today", 0)
                    h.tokens_today = s.get("tokens_today", 0)
        except Exception as e:
            logger.warning(f"circuit_load_failed: {e}")

    async def close(self) -> None:
        if self._idle_task:
            self._idle_task.cancel()
            try:
                await self._idle_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        self._save_circuit_state()
        if self.http:
            await self.http.aclose()

    async def _check_health_and_notify(self, pid: str) -> None:
        h = self.health.get(pid)
        if h and h.consecutive_failures == 3:
            msg = f"⚠️ Provider *{pid}* degraded after 3 consecutive failures. Routing to fallback tier."
            try:
                await jules.send_telegram(msg)
            except Exception as e:
                logger.warning(f"Failed to send health alert to Telegram: {e}")

    async def _call_provider(
        self, pid: str, messages: list, task: ClassifiedTask
    ) -> Tuple[str, int, int, float]:
        start = time.time()
        h = self.health[pid]
        req_id = str(uuid.uuid4())

        if pid in LOCAL_PROVIDERS:
            # NinaFlash / Ollama
            try:
                r = await self.http.post(
                    f"{self.config.ollama_host}/api/chat",
                    json={
                        "model": LOCAL_PROVIDERS[pid]["model"],
                        "messages": messages,
                        "stream": False,
                    },
                    timeout=60,
                )
                r.raise_for_status()
                d = cast(dict, r.json())
                content = d["message"]["content"]
                lat = (time.time() - start) * 1000
                h.record_success(lat, 0)
                return content, 0, 0, lat
            except Exception as e:
                h.record_failure()
                asyncio.create_task(self._check_health_and_notify(pid))
                raise e

        meta = cast(dict, ALL_PROVIDERS[pid]).copy()
        api_key = self.config.get_secret(meta["key_field"]) if meta["key_field"] else None

        try:
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            r = await self.http.post(
                f"{meta['base_url']}/chat/completions",
                headers=headers,
                json={"model": meta["model"], "messages": messages, "stream": False},
            )
            r.raise_for_status()
            res = r.json()
            content = res["choices"][0]["message"]["content"]
            it = res["usage"]["prompt_tokens"]
            ot = res["usage"]["completion_tokens"]
            lat = (time.time() - start) * 1000
            h.record_success(lat, it + ot)
            self.cost.record(pid, task.task_type, it, ot, req_id=req_id)
            return content, it, ot, lat

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (429, 500, 502, 503, 504):
                cooldown_s = 60.0
                if e.response.status_code == 429:
                    try:
                        cooldown_s = float(e.response.headers.get("retry-after", 60))
                    except Exception:
                        cooldown_s = 60.0
                h.record_failure(cooldown_s=cooldown_s)
                asyncio.create_task(self._check_health_and_notify(pid))
                self.cost.record(
                    pid,
                    task.task_type,
                    0,
                    0,
                    error=f"http_{e.response.status_code}",
                    req_id=req_id,
                )
            raise e
        except Exception as e:
            h.record_failure()
            asyncio.create_task(self._check_health_and_notify(pid))
            self.cost.record(pid, task.task_type, 0, 0, error="exception", req_id=req_id)
            raise e

    async def route(
        self, goal: str, messages: list, task: ClassifiedTask, force_local: bool = False
    ) -> str:
        # Cache check
        cached = self.cache.get(goal, messages)
        if cached:
            return cached

        # Logic for Bangla requests
        has_bangla = _BANGLA_RE.search(goal) or any(
            _BANGLA_RE.search(m.get("content", "")) for m in messages
        )

        # Provider selection
        tiers = [PROVIDERS_TIER1, PROVIDERS_TIER2, PROVIDERS_TIER3]
        if force_local:
            tiers = [LOCAL_PROVIDERS]

        for tier in tiers:
            # Sort by health score
            available = [
                pid
                for pid in tier
                if self.health[pid].cb.can_attempt()
                and self.health[pid].requests_today < 1000
            ]
            if not available:
                continue

            available.sort(key=lambda pid: self.health[pid].health_score, reverse=True)

            for pid in available:
                try:
                    content, i, o, lat = await self._call_provider(pid, messages, task)
                    # Cache successful result
                    ttl = CACHE_TTL.get(task.task_type, 3600)
                    if ttl > 0:
                        self.cache.set(goal, content, ttl, messages)
                    return content
                except Exception as e:
                    logger.bind(provider=pid, error=str(e)).warning("provider_retry")
                    continue

        return "⚠️ All providers are currently unavailable. Try again in a moment."

    async def parallel_route(
        self, prompts: List[str], task: ClassifiedTask
    ) -> List[Optional[str]]:
        """Run multiple prompts in parallel across available providers."""
        # Highly simplified for implementation
        results = []
        for p in prompts:
            results.append(await self.route(p, [{"role": "user", "content": p}], task))
        return results

    async def _idle_monitor(self) -> None:
        """Background loop to probe provider health and purge cache."""
        while True:
            try:
                await asyncio.sleep(60)
                self.cache.purge_expired()
                self._save_circuit_state()

                # Quality probe: pick a degraded provider and try a small task
                degraded = [
                    pid
                    for pid, h in self.health.items()
                    if h.cb.state != "CLOSED" and pid not in LOCAL_PROVIDERS
                ]
                if degraded:
                    pid = degraded[0]
                    try:
                        # Probe task
                        messages = [
                            {"role": "user", "content": "Explain async/await in 5 words."}
                        ]
                        _, _, _, lat = await self._call_provider(
                            pid, messages, ClassifiedTask("quick", 10, False, False)
                        )
                        logger.info("quality_probe_success provider=%s", pid)
                    except Exception:
                        logger.warning("quality_probe_fail provider=%s", pid)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("idle_monitor_error: %s", e)

    def get_models_status(self) -> str:
        """Returns a terminal-formatted table of provider health."""
        lines = [
            f"{'Provider':<15} | {'Status':<10} | {'Score':<6} | {'Lat':<6} | {'Reqs':<6}"
        ]
        lines.append("-" * 55)
        for pid in sorted(self.health.keys()):
            h = self.health[pid]
            status = h.cb.state
            if h.requests_today >= 1000:
                status = "QUOTA"
            lines.append(
                f"{pid:<15} | {status:<10} | {h.health_score:>6.2f} | {h.avg_latency_ms:>5.0f} | {h.requests_today:>6}"
            )
        return "\n".join(lines)
