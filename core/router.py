# core/router.py
from typing import List, Dict, Optional, Tuple, cast, Union, AsyncGenerator
import asyncio
import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque

import os
import re
import time
import uuid
from datetime import datetime, timezone
import httpx
import psutil

from core.config import NinaConfig
from core.logger import get_logger
from core.task_classifier import ClassifiedTask
from tools.provider_health import tracker as _health_tracker
import tools.jules as jules
from tools.model_discovery import ModelDiscoveryService
from core.quota_router import QuotaRouter
from core.rpm_scheduler import RPMScheduler
from core.smart_router import SmartRouter

# telemetry pass-2: structured pipeline emitter (null-safe fallback)
try:
    from telemetry.emitter import emit as _telem_emit
except ImportError:
    def _telem_emit(stage, event, payload, span_id=None): pass  # noqa: E731

_ = jules

logger = get_logger("nina.router")

# F-03f: Bangla Unicode block U+0980–U+09FF
_BANGLA_RE = re.compile(r"[\u0980-\u09FF]")
_HALLUCINATION_RE = re.compile(r"i am a large language model|as an ai|i cannot fulfill this request", re.IGNORECASE)
_REFUSAL_RE = re.compile(r"i cannot|as an ai|i'm unable", re.IGNORECASE)
_STRUCTURE_RE = re.compile(r"1\\.|2\\.|-|\\*\\*|##")

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
                    "key_field": p.get("api_key_env").lower() if p.get("api_key_env") else None,
                    "context_window": p.get("context_window", 8192)
                }
                tier = p.get("tier", 2)
                name = p["name"].upper()
                if tier == 1:
                    t1[name] = entry
                elif tier == 2:
                    t2[name] = entry
                elif tier == 3:
                    t3[name] = entry
        except Exception as e:
            logger.error(f"Failed to load providers from json: {e}")
    return t1, t2, t3

PROVIDERS_TIER1, PROVIDERS_TIER2, PROVIDERS_TIER3 = load_providers_from_json()

# Precomputed to avoid O(N) dict merging overhead in hot paths like routing lookups
ALL_PROVIDERS = PROVIDERS_TIER1 | PROVIDERS_TIER2 | PROVIDERS_TIER3

LOCAL_PROVIDERS = {
    "LOCALFAST": {"model": "dulal", "context_window": 8192},
    "LOCALHEAVY": {"model": "dulal", "context_window": 32768},
}

CACHE_TTL = {
    "sensitive": 0,
    "diagnostic": 0,
    "quick": 3600,
    "research": 1800,
    "coding": 21600,
    "document": 14400,
    "general": 7200,
    "math": 21600,
    "multilingual": 7200,
    "lpu_deterministic": 86400,
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
    "lpu_deterministic": 1,
    "diagnostic": 3,
}
DEFAULT_MAX_STEPS = 5

# MoA: providers used as parallel proposers (cheap + fast)
_MOA_PROPOSERS = ["POLLINATIONS", "GROQ", "CHUTES"]
# MoA: task types that trigger multi-model aggregation
_MOA_TASK_TYPES = {"research", "analysis", "coding"}


class CircuitBreaker:
    FAILURE_THRESHOLD = 3
    WINDOW_S = 120
    RECOVERY_S = 60
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, *, recovery_window: float = 60.0) -> None:
        self.failures: List[float] = []
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.open_until = 0.0
        self.half_open_index = 0
        self._recovery_window = recovery_window
        self._half_open_time = 0.0

    def record_success(self) -> None:
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failures.clear()
            provider = getattr(self, "provider", "provider")
            logger.info(f"{provider} circuit breaker: HALF_OPEN → CLOSED (recovered)")
        elif self.state == "CLOSED":
            self.failures.clear()

    def record_failure(self, cooldown_s: Optional[float] = None) -> None:
        now = time.time()
        self.failures.append(now)
        self.failures = [f for f in self.failures if now - f < self.WINDOW_S]

        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self._half_open_time = time.monotonic() + self._recovery_window
            provider = getattr(self, "provider", "provider")
            logger.warning(f"{provider} circuit breaker: HALF_OPEN → OPEN (test request failed)")
            return

        if len(self.failures) >= self.FAILURE_THRESHOLD:
            self.state = "OPEN"
            self._half_open_time = time.monotonic() + self._recovery_window
            wait = cooldown_s or self.RECOVERY_S
            self.open_until = now + wait

    def can_attempt(self) -> bool:
        now = time.time()
        if self.state == "OPEN":
            if self._half_open_time > 0.0 and time.monotonic() >= self._half_open_time:
                self.state = "HALF_OPEN"
                return True
            if now > self.open_until:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
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
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        success_rate = self.success_count / total
        lat_penalty = min(0.5, self.avg_latency_ms / 5000.0)
        degraded_penalty = 0.5 if self.cb.state != "CLOSED" else 0.0
        return max(0.0, success_rate - lat_penalty - degraded_penalty)

    def record_success(self, latency_ms: float, total_tokens: int) -> None:
        self.success_count += 1
        self.consecutive_failures = 0
        self.requests_today += 1
        self.tokens_today += max(0, int(total_tokens))
        self.last_request_ts = time.time()
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
    entry["ts"] = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    try:
        path = Path(log_path)
        if path.exists() and path.stat().st_size > 100000:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as rf:
                lines = rf.readlines()
            if len(lines) > 200:
                with open(log_path, "w", encoding="utf-8") as wf:
                    wf.writelines(lines[-100:])
    except Exception:
        pass


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
        self.discovery = ModelDiscoveryService(config=self.config)
        self.quota_router = QuotaRouter(self.config, self.health)
        self.rpm_scheduler = RPMScheduler()
        self.smart_router = SmartRouter()
        self.provider_metrics = self.smart_router
        self.dispatcher = None
        self.http: httpx.AsyncClient | None = None
        self._idle_task: asyncio.Task | None = None

    async def initialize(self) -> None:
        self.http = httpx.AsyncClient(timeout=60.0)
        _health_tracker.set_notify(jules.send_telegram)
        self.cache.load("data/router_cache.json")
        self._load_circuit_state()
        self._idle_task = asyncio.create_task(self._idle_monitor())

    @property
    def supply_pressure(self) -> float:
        try:
            snap = Path("data/supply_snapshot.json")
            if snap.exists():
                d = json.loads(snap.read_text())
                if time.time() - d.get("ts", 0) < 60:   # fresh within 60s
                    return float(d.get("pressure", 0.0))
        except Exception:
            pass
        # fallback: compute locally from self.health
        total = len(self.health)
        degraded = sum(1 for h in self.health.values() if h.cb.state != "CLOSED")
        return degraded / total if total else 1.0

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

    def reset_daily(self) -> None:
        """Reset daily cost and request counters across all providers."""
        self.cost.reset_daily()
        for h in self.health.values():
            h.requests_today = 0
            h.tokens_today = 0

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

        if not self.http:
            await self.initialize()
        wait_ms = await self.rpm_scheduler.acquire(pid)
        if wait_ms > 500:
            logger.warning(f"rpm_throttle provider={pid} waited={wait_ms:.0f}ms")
        start = time.time()
        req_id = str(uuid.uuid4())

        try:
            if pid in LOCAL_PROVIDERS:
                from tools.system import is_thermal_safe
                safe, thermal_msg = await is_thermal_safe(cpu_limit=90, gpu_limit=88)
                if not safe:
                    raise RuntimeError(f"Local inference blocked by thermal safeguard: {thermal_msg}")
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
                except Exception as http_err:
                    # If local provider returns HTTP 400 (Bad Request), abort retries and trigger immediate fallback
                    status_code = getattr(getattr(http_err, "response", None), "status_code", None)
                    if status_code == 400:
                        logger.error(f"Local provider {pid} failed with HTTP 400 Bad Request (likely context limit overrun). Aborting local provider.")
                        raise ValueError("Local provider HTTP 400: context limit overrun or bad payload. Aborting local provider.") from http_err
                    raise http_err
                d = cast(dict, r.json())
                content = d["message"]["content"]
                lat = (time.time() - start) * 1000
                self.smart_router.record_invocation(pid, task.task_type, lat, True)
                # telemetry pass-1: local provider success
                write_log({
                    "event": "provider_call_ok",
                    "provider": pid,
                    "task_type": task.task_type,
                    "latency_ms": round(lat, 1),
                    "local": True,
                })
                # telemetry pass-2: dual-emit to structured pipeline
                _telem_emit("ouroboros", "provider_call_ok", {
                    "provider": pid,
                    "task_type": task.task_type,
                    "latency_ms": round(lat, 1),
                    "local": True,
                    "circuit_state": self.health[pid].cb.state,
                })
                return content, 0, 0, lat

            meta = cast(dict, ALL_PROVIDERS[pid]).copy()
            api_key = getattr(self.config, meta["key_field"], None) if meta["key_field"] else None

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
            self.cost.record(pid, task.task_type, it, ot, req_id=req_id)
            self.smart_router.record_invocation(pid, task.task_type, lat, True)
            # telemetry pass-1: cloud provider success
            write_log({
                "event": "provider_call_ok",
                "provider": pid,
                "task_type": task.task_type,
                "latency_ms": round(lat, 1),
                "local": False,
                "tokens_in": it,
                "tokens_out": ot,
            })
            # telemetry pass-2: dual-emit to structured pipeline
            _telem_emit("ouroboros", "provider_call_ok", {
                "provider": pid,
                "task_type": task.task_type,
                "latency_ms": round(lat, 1),
                "local": False,
                "tokens_in": it,
                "tokens_out": ot,
                "circuit_state": self.health[pid].cb.state,
            })
            return content, it, ot, lat
        except Exception as e:
            self.smart_router.record_invocation(pid, task.task_type, 0.0, False)
            # telemetry pass-2: provider_error (no pass-1 equivalent existed)
            _telem_emit("ouroboros", "provider_error", {
                "provider": pid,
                "task_type": task.task_type,
                "exc_type": type(e).__name__,
                "msg": str(e)[:200],
                "circuit_state": self.health[pid].cb.state,
            })
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                logger.warning(f"Rate limit (429) hit for provider {pid}. Force-triggering 5-minute cooldown.")
                self.health[pid].record_failure(cooldown_s=300)
                self.health[pid].cb.state = "OPEN"
                self.health[pid].cb.open_until = time.time() + 300
                msg = f"🚨 *Quota Exhausted (429)* for provider *{pid}*. Immediately routing to fallback tiers. Cooldown of 5 minutes activated."
                asyncio.create_task(jules.send_telegram(msg))
            raise e

    async def moa_route(
        self, goal: str, messages: list, task: ClassifiedTask
    ) -> str:
        """
        Mixture-of-Agents (MoA) aggregation for hard reasoning tasks.

        Fires the prompt to _MOA_PROPOSERS in parallel, then feeds all
        responses to the best available quality provider as an aggregator.
        Falls back to standard route() on any error.

        Only called when task.task_type is in _MOA_TASK_TYPES.
        Does NOT touch circuit breaker logic or existing route() internals.
        """
        # Collect available proposer providers (skip if circuit open)
        available_proposers = [
            p for p in _MOA_PROPOSERS
            if p in self.health and self.health[p].cb.can_attempt()
        ]
        if len(available_proposers) < 2:
            # Not enough proposers — fall back to standard routing
            logger.info("moa_route: fewer than 2 proposers available, falling back to route()")
            result = await self.route(goal, messages, task)
            return result if isinstance(result, str) else goal

        quick_task = ClassifiedTask("quick", task.estimated_tokens, False, False)

        async def _safe_propose(pid: str) -> Optional[str]:
            try:
                content, _, _, _ = await self._call_provider(pid, messages, quick_task)
                self.health[pid].record_success(0.0, 0)
                return content
            except Exception as e:
                logger.warning(f"moa_route: proposer {pid} failed: {e}")
                self.health[pid].record_failure()
                return None

        # Fire all proposers in parallel
        raw_results = await asyncio.gather(
            *[_safe_propose(pid) for pid in available_proposers],
            return_exceptions=False
        )
        proposals = [r for r in raw_results if r]

        if not proposals:
            logger.warning("moa_route: all proposers failed, falling back to route()")
            result = await self.route(goal, messages, task)
            return result if isinstance(result, str) else goal

        if len(proposals) == 1:
            # Only one proposal — skip aggregation overhead
            return proposals[0]

        # Build aggregation prompt
        proposals_text = ""
        for i, p in enumerate(proposals, 1):
            proposals_text += f"\n\n--- Response {i} ---\n{p[:3000]}"

        aggregator_messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert synthesis engine. You will receive multiple AI responses "
                    "to the same question. Synthesize the best, most accurate, and most complete "
                    "answer by combining their strongest elements. Correct any errors you spot. "
                    "Do not mention that you are synthesizing multiple responses."
                )
            },
            {
                "role": "user",
                "content": f"Original question: {goal}\n\nResponses to synthesize:{proposals_text}\n\nProvide the best synthesized answer:"
            }
        ]

        # Pick best available aggregator: prefer GEMINI tier, then GROQ, then LOCALFAST
        aggregator_candidates = ["GEMINI", "GEMINI_FLASH", "GEMINI_FLASH_PROD", "GROQ", "LOCALFAST"]
        aggregator_pid = next(
            (p for p in aggregator_candidates
             if p in self.health and self.health[p].cb.can_attempt()),
            None
        )

        if not aggregator_pid:
            # No aggregator available — return best proposal by length heuristic
            def _score_proposal(p: str) -> float:
                length_score = min(1.0, len(p) / 2000.0)
                has_structure = 0.2 if any(c in p for c in ["1.", "2.", "-", "**", "##"]) else 0.0
                p_lower = p.lower()
                no_refusal = 0.0 if "i cannot" in p_lower or "as an ai" in p_lower or "i'm unable" in p_lower else 0.15
                return length_score + has_structure + no_refusal
            return max(proposals, key=_score_proposal)

        try:
            agg_content, ai, ao, alat = await self._call_provider(
                aggregator_pid, aggregator_messages, task
            )
            self.health[aggregator_pid].record_success(alat, ai + ao)
            logger.info(f"moa_route: aggregated {len(proposals)} proposals via {aggregator_pid}")
            return agg_content
        except Exception as e:
            logger.warning(f"moa_route: aggregator {aggregator_pid} failed: {e}. Returning best proposal.")
            self.health[aggregator_pid].record_failure()
            def _score_proposal(p: str) -> float:
                length_score = min(1.0, len(p) / 2000.0)
                has_structure = 0.2 if any(c in p for c in ["1.", "2.", "-", "**", "##"]) else 0.0
                p_lower = p.lower()
                no_refusal = 0.0 if "i cannot" in p_lower or "as an ai" in p_lower or "i'm unable" in p_lower else 0.15
                return length_score + has_structure + no_refusal
            return max(proposals, key=_score_proposal)

    async def _call_provider_stream(
        self, pid: str, messages: list, task: ClassifiedTask
    ) -> AsyncGenerator[str, None]:

        if not self.http:
            await self.initialize()
        wait_ms = await self.rpm_scheduler.acquire(pid)
        if wait_ms > 500:
            logger.warning(f"rpm_throttle provider={pid} waited={wait_ms:.0f}ms")
        start = time.time()
        try:
            if pid in LOCAL_PROVIDERS:
                from tools.system import is_thermal_safe
                safe, thermal_msg = await is_thermal_safe(cpu_limit=90, gpu_limit=88)
                if not safe:
                    raise RuntimeError(f"Local inference stream blocked by thermal safeguard: {thermal_msg}")
                async with self.http.stream(
                    "POST",
                    f"{self.config.ollama_host}/api/chat",
                    json={
                        "model": LOCAL_PROVIDERS[pid]["model"],
                        "messages": messages,
                        "stream": True,
                    },
                    timeout=60,
                ) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except Exception:
                            pass
                lat = (time.time() - start) * 1000
                self.smart_router.record_invocation(pid, task.task_type, lat, True)
                # telemetry pass-2: local stream success
                _telem_emit("ouroboros", "provider_call_ok", {
                    "provider": pid,
                    "task_type": task.task_type,
                    "latency_ms": round(lat, 1),
                    "local": True,
                    "stream": True,
                    "circuit_state": self.health[pid].cb.state,
                })
                return

            meta = cast(dict, ALL_PROVIDERS[pid]).copy()
            api_key = getattr(self.config, meta["key_field"], None) if meta["key_field"] else None

            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            async with self.http.stream(
                "POST",
                f"{meta['base_url']}/chat/completions",
                headers=headers,
                json={"model": meta["model"], "messages": messages, "stream": True},
                timeout=60,
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.startswith("data: "):
                        line_data = line[6:].strip()
                        if line_data == "[DONE]":
                            break
                        try:
                            data = json.loads(line_data)
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                        except Exception:
                            pass
                lat = (time.time() - start) * 1000
                self.smart_router.record_invocation(pid, task.task_type, lat, True)
                # telemetry pass-2: cloud stream success
                _telem_emit("ouroboros", "provider_call_ok", {
                    "provider": pid,
                    "task_type": task.task_type,
                    "latency_ms": round(lat, 1),
                    "local": False,
                    "stream": True,
                    "circuit_state": self.health[pid].cb.state,
                })
        except Exception as e:
            self.smart_router.record_invocation(pid, task.task_type, 0.0, False)
            # telemetry pass-2: stream provider error
            _telem_emit("ouroboros", "provider_stream_error", {
                "provider": pid,
                "task_type": task.task_type,
                "exc_type": type(e).__name__,
                "msg": str(e)[:200],
                "circuit_state": self.health[pid].cb.state,
            })
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                logger.warning(f"Rate limit (429) hit for provider {pid} during stream. Force-triggering 5-minute cooldown.")
                self.health[pid].record_failure(cooldown_s=300)
                self.health[pid].cb.state = "OPEN"
                self.health[pid].cb.open_until = time.time() + 300
                msg = f"🚨 *Quota Exhausted (429)* for provider *{pid}* during stream. Immediately routing to fallback tiers. Cooldown of 5 minutes activated."
                asyncio.create_task(jules.send_telegram(msg))
            raise e

    async def _validate_response(self, content: str, task: ClassifiedTask) -> Tuple[bool, str]:
        """
        OODA Loop (Observe/Orient): Validate the AI response for quality.
        Returns (is_valid, error_reason).
        """
        if task.task_type == "research" and len(content) < 100:
            return False, "Response too short for a research task."
        
        if _HALLUCINATION_RE.search(content):
            return False, "AI refusal or boilerplate detected."

        if task.task_type in ["coding", "research", "diagnostic"]:
            try:
                messages = [
                    {"role": "system", "content": "You are a logic gate. Review this AI response. Check: (1) Is it technically sound and complete? (2) Does it cite a specific file, git command, or tool result as evidence — or does it theorize without reading source? Respond only with 'VALID' or a one-sentence error reason starting with the failed check number."},
                    {"role": "user", "content": f"TASK: {task.task_type}\nRESPONSE: {content[:2000]}"}
                ]
                _val_pid = "GROQ" if ("GROQ" in self.health and self.health["GROQ"].cb.can_attempt()) else "LOCALFAST"
                val_content, _, _, _ = await self._call_provider(_val_pid, messages, ClassifiedTask("quick", 100, False, False))
                if "valid" in val_content.lower():
                    return True, ""
                else:
                    return False, f"Logic Gate Refusal: {val_content}"
            except Exception:
                pass

        return True, ""

    async def route(
        self, goal: str, messages: list, task: Optional[ClassifiedTask] = None, force_local: bool = False, stream: bool = False, **kwargs
    ) -> Union[str, AsyncGenerator[str, None]]:
        if task is None:
            task_type_arg = kwargs.get("task_type", "general")
            task = ClassifiedTask(task_type=task_type_arg)

        # telemetry pass-1: generate span_id for this routing attempt
        _span_id = str(uuid.uuid4())[:8]
        write_log({
            "event": "route_start",
            "span_id": _span_id,
            "task_type": task.task_type,
            "estimated_tokens": task.estimated_tokens,
            "stream": stream,
            "force_local": force_local,
        })
        # telemetry pass-2: dual-emit route_start
        _telem_emit("ouroboros", "route_start", {
            "task_type": task.task_type,
            "estimated_tokens": task.estimated_tokens,
            "stream": stream,
            "force_local": force_local,
        }, span_id=_span_id)

        from core.hyperdrive_policy import policy
        from core.memo_cache import cache

        if policy.is_enabled():
            hd_tier = policy.estimate_required_tier(task)
            if hd_tier == "LOCALFAST":
                force_local = True
            elif hd_tier in ("FAST", "DEEP", "LARGE"):
                task.recommended_tier = hd_tier

            if policy.is_cacheable(goal, task):
                cached_hd = cache.get_exact(goal, messages)
                if not cached_hd:
                    cached_hd = cache.get_semantic(goal)
                if cached_hd:
                    logger.info(f"hyperdrive: cache hit for goal: {goal}")
                    if stream:
                        async def stream_cached():
                            yield cached_hd
                        return stream_cached()
                    return cached_hd

        # NINA-GROQ: Deterministic LPU Fast-Track
        if task.task_type == "lpu_deterministic":
            try:
                content, i, o, lat = await self._call_provider("LOCALFAST", messages, task)
                return content
            except Exception as e:
                logger.warning(f"LPU Fast-track failed: {e}. Falling back to standard route.")

        # CRITICAL Task Override: Force Gemini 3.5 Flash
        if task.task_type == "critical":
            logger.info("CRITICAL Task detected: Forcing GEMINI_FLASH_PROD routing.")
            pid = "GEMINI_FLASH_PROD"
            if pid in ALL_PROVIDERS and self.health[pid].cb.can_attempt():
                try:
                    content, i, o, lat = await self._call_provider(pid, messages, task)
                    is_valid, error = await self._validate_response(content, task)
                    if is_valid:
                        self.health[pid].record_success(lat, i + o)
                        write_log({
                            "event": "route_ok",
                            "span_id": _span_id,
                            "provider": pid,
                            "task_type": task.task_type,
                            "fallback_attempt": 0,
                            "circuit_state": self.health[pid].cb.state,
                        })
                        # telemetry pass-2: dual-emit route_ok (critical path)
                        _telem_emit("ouroboros", "route_ok", {
                            "provider": pid,
                            "task_type": task.task_type,
                            "fallback_attempt": 0,
                            "circuit_state": self.health[pid].cb.state,
                            "critical": True,
                        }, span_id=_span_id)
                        return content
                    else:
                        logger.bind(provider=pid, error=error).warning("critical_task_validation_failed")
                        self.health[pid].record_failure()
                except Exception as e:
                    logger.bind(provider=pid, error=str(e)).warning("critical_task_provider_failed")
                    self.health[pid].record_failure()
            else:
                logger.warning("GEMINI_FLASH_PROD not available or circuit open for CRITICAL task, falling back.")

        # Cache check
        cached = self.cache.get(goal, messages)
        if cached:
            if stream:
                async def stream_cached():
                    yield cached
                return stream_cached()
            return cached

        # MoA fast-path for hard reasoning tasks (non-streaming only)
        if not stream and not force_local and task.task_type in _MOA_TASK_TYPES:
            try:
                return await self.moa_route(goal, messages, task)
            except Exception as e:
                logger.warning(f"moa_route top-level failed: {e}, falling through to standard routing")

        # Real-time thermal safeguard check
        local_allowed = True
        try:
            from tools.system import is_thermal_safe
            local_allowed, thermal_msg = await is_thermal_safe(cpu_limit=90, gpu_limit=88)
            if not local_allowed:
                logger.warning(f"Local inference bypassed: {thermal_msg}")
        except Exception as e:
            logger.warning(f"Failed to run thermal safeguard: {e}")

        # ── Tier-aware routing ────────────────────────────────────────────────
        if force_local and local_allowed:
            sorted_groups = [[p for p in LOCAL_PROVIDERS if self.health[p].cb.can_attempt()]]
        elif force_local:
            sorted_groups = []
        elif self.quota_router.should_force_local():
            local_group = [p for p in LOCAL_PROVIDERS if self.health[p].cb.can_attempt()] if local_allowed else []
            cloud_groups = self.quota_router.get_sorted_providers(
                recommended_tier=task.recommended_tier,
                complexity=task.complexity,
                estimated_tokens=task.estimated_tokens,
                all_providers=ALL_PROVIDERS,
            )
            sorted_groups = ([local_group] if local_group else []) + cloud_groups
        else:
            sorted_groups = self.quota_router.get_sorted_providers(
                recommended_tier=getattr(task, "recommended_tier", "FAST"),
                complexity=getattr(task, "complexity", "MEDIUM"),
                estimated_tokens=task.estimated_tokens,
                all_providers=ALL_PROVIDERS,
            )
            local_group = [p for p in LOCAL_PROVIDERS if self.health[p].cb.can_attempt()] if local_allowed else []
            if local_group:
                sorted_groups.append(local_group)

        best_provider = self.smart_router.get_best_provider(task.task_type)
        if best_provider:
            logger.info(f"Learned Smart Router prioritizing {best_provider} for task type '{task.task_type}'")

        if stream:
            selected_pid = None
            for group in sorted_groups:
                if not group:
                    continue
                current_group = list(group)
                if best_provider:
                    current_group.sort(key=lambda x: 0 if x.lower() == best_provider.lower() else 1)
                for pid in current_group:
                    selected_pid = pid
                    break
                if selected_pid:
                    break
            
            if not selected_pid:
                async def fallback_generator():
                    yield "⚠️ All providers are currently unavailable or failing validation. Try again in a moment."
                return fallback_generator()
                
            async def generator_wrapper():
                accumulated = []
                start_time = time.time()
                try:
                    async for chunk in self._call_provider_stream(selected_pid, messages, task):
                        accumulated.append(chunk)
                        yield chunk
                    lat = (time.time() - start_time) * 1000
                    full_text = "".join(accumulated)
                    self.health[selected_pid].record_success(lat, len(full_text) // 4)
                    asyncio.create_task(_health_tracker.record(selected_pid, True, lat))
                    # telemetry pass-1: stream path success
                    write_log({
                        "event": "route_ok_stream",
                        "span_id": _span_id,
                        "provider": selected_pid,
                        "task_type": task.task_type,
                        "latency_ms": round(lat, 1),
                        "circuit_state": self.health[selected_pid].cb.state,
                    })
                    # telemetry pass-2: dual-emit route_ok_stream
                    _telem_emit("ouroboros", "route_ok_stream", {
                        "provider": selected_pid,
                        "task_type": task.task_type,
                        "latency_ms": round(lat, 1),
                        "tokens_est": len(full_text) // 4,
                        "circuit_state": self.health[selected_pid].cb.state,
                    }, span_id=_span_id)
                    ttl = CACHE_TTL.get(task.task_type, 3600)
                    if ttl > 0:
                        self.cache.set(goal, full_text, ttl, messages)
                        from core.hyperdrive_policy import policy
                        from core.memo_cache import cache
                        if policy.is_enabled() and policy.is_cacheable(goal, task):
                            cache.set(goal, full_text, ttl=ttl, messages=messages)
                except Exception as e:
                    self.health[selected_pid].record_failure()
                    asyncio.create_task(_health_tracker.record(selected_pid, False, 0.0, str(e)))
                    asyncio.create_task(self._check_health_and_notify(selected_pid))
                    # telemetry pass-2: stream route error
                    _telem_emit("ouroboros", "route_stream_error", {
                        "provider": selected_pid,
                        "task_type": task.task_type,
                        "exc_type": type(e).__name__,
                        "msg": str(e)[:200],
                    }, span_id=_span_id)
                    yield f"\n⚠️ Streaming interrupted: {e}"
            return generator_wrapper()

        for attempt in range(2):
            for group in sorted_groups:
                if not group:
                    continue
                current_group = list(group)
                if best_provider:
                    current_group.sort(key=lambda x: 0 if x.lower() == best_provider.lower() else 1)
                for pid in current_group:
                    try:
                        content, i, o, lat = await self._call_provider(pid, messages, task)
                        is_valid, error = await self._validate_response(content, task)
                        if is_valid:
                            self.health[pid].record_success(lat, i + o)
                            asyncio.create_task(_health_tracker.record(pid, True, lat))
                            # telemetry pass-1: non-stream success
                            write_log({
                                "event": "route_ok",
                                "span_id": _span_id,
                                "provider": pid,
                                "task_type": task.task_type,
                                "fallback_attempt": attempt,
                                "circuit_state": self.health[pid].cb.state,
                            })
                            # telemetry pass-2: dual-emit route_ok
                            _telem_emit("ouroboros", "route_ok", {
                                "provider": pid,
                                "task_type": task.task_type,
                                "fallback_attempt": attempt,
                                "latency_ms": round(lat, 1),
                                "tokens_in": i,
                                "tokens_out": o,
                                "circuit_state": self.health[pid].cb.state,
                            }, span_id=_span_id)
                            ttl = CACHE_TTL.get(task.task_type, 3600)
                            if ttl > 0:
                                self.cache.set(goal, content, ttl, messages)
                                from core.hyperdrive_policy import policy
                                from core.memo_cache import cache
                                if policy.is_enabled() and policy.is_cacheable(goal, task):
                                    cache.set(goal, content, ttl=ttl, messages=messages)
                            return content
                        else:
                            logger.bind(provider=pid, error=error).warning("response_validation_failed")
                            self.health[pid].record_failure()
                            asyncio.create_task(_health_tracker.record(pid, False, lat, f"Validation failed: {error}"))
                            messages.append({"role": "assistant", "content": content})
                            messages.append({"role": "user", "content": f"The previous response failed validation: {error}. Please refine and provide a correct answer."})
                            continue
                    except Exception as e:
                        self.health[pid].record_failure()
                        asyncio.create_task(_health_tracker.record(pid, False, 0.0, str(e)))
                        asyncio.create_task(self._check_health_and_notify(pid))
                        logger.bind(provider=pid, error=str(e)).warning("provider_retry")
                        continue

        # telemetry pass-1: all providers exhausted
        write_log({
            "event": "route_exhausted",
            "span_id": _span_id,
            "task_type": task.task_type,
        })
        # telemetry pass-2: dual-emit route_exhausted
        _telem_emit("ouroboros", "route_exhausted", {
            "task_type": task.task_type,
        }, span_id=_span_id)
        return "⚠️ All providers are currently unavailable or failing validation. Try again in a moment."

    async def parallel_route(
        self, prompts: List[str], task: ClassifiedTask
    ) -> List[Optional[str]]:
        use_parallel = True
        try:
            ram_pct = psutil.virtual_memory().percent
            if ram_pct > 85:
                logger.warning(f"parallel_route_skipped ram={ram_pct}%")
                use_parallel = False
            else:
                available_gb = psutil.virtual_memory().available / (1024 ** 3)
                threshold_val = getattr(self.config, "ram_guard_gb", 10.5) if self.config else 10.5
                try:
                    threshold = float(threshold_val)
                except (ValueError, TypeError):
                    threshold = 10.5
                if available_gb < threshold:
                    logger.warning(
                        "parallel_route: insufficient RAM (%.2f GB available, threshold %.2f GB). Falling back to sequential routing.",
                        available_gb,
                        threshold
                    )
                    use_parallel = False
        except (MemoryError, OSError, AttributeError, Exception) as e:
            logger.warning(
                "parallel_route: RAM check failed (%s), falling back to sequential routing",
                str(e)
            )
            use_parallel = False

        if not use_parallel:
            results = []
            for p in prompts:
                try:
                    res = await self.route(p, [{"role": "user", "content": p}], task)
                    results.append(res)
                except Exception as e:
                    logger.warning("parallel_route sequential fallback item failed: %s", str(e))
                    results.append(None)
            return results

        try:
            tasks = [self.route(p, [{"role": "user", "content": p}], task) for p in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [res if not isinstance(res, Exception) else None for res in results]
        except Exception as e:
            logger.warning("parallel_route: parallel gather failed (%s), falling back to sequential", str(e))
            results = []
            for p in prompts:
                try:
                    res = await self.route(p, [{"role": "user", "content": p}], task)
                    results.append(res)
                except Exception:
                    results.append(None)
            return results

    async def _idle_monitor(self) -> None:
        while True:
            try:
                await asyncio.sleep(60)
                self.cache.purge_expired()
                self._save_circuit_state()

                degraded = [
                    pid
                    for pid, h in self.health.items()
                    if h.cb.state != "CLOSED" and pid not in LOCAL_PROVIDERS
                ]
                if degraded:
                    pid = degraded[0]
                    try:
                        messages = [
                            {"role": "user", "content": "Explain async/await in 5 words."}
                        ]
                        _, _, _, lat = await self._call_provider(
                            pid, messages, ClassifiedTask("quick", 10, False, False)
                        )
                        self.health[pid].record_success(lat, 10)
                        logger.info("quality_probe_success provider=%s", pid)
                    except Exception:
                        self.health[pid].record_failure()
                        asyncio.create_task(self._check_health_and_notify(pid))
                        logger.warning("quality_probe_fail provider=%s", pid)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("idle_monitor_error: %s", e)

    def get_models_status(self) -> str:
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

    def get_status(self) -> str:
        """Alias for get_models_status to maintain backward compatibility."""
        return self.get_models_status()

    def get_available_providers(self) -> List[str]:
        """Returns the list of providers currently available (circuit breaker CLOSED or HALF_OPEN)."""
        return [pid for pid, h in self.health.items() if h.cb.can_attempt()]

    async def graceful_fallback_chain(self, prompt: str, context: dict) -> str:
        """Try providers in fallback order: local models first, then any non-open cloud provider.
        Returns the first successful response. Raises RuntimeError if all providers exhausted."""
        from core.task_classifier import ClassifiedTask
        messages = [{"role": "user", "content": prompt}]
        task = ClassifiedTask("general")
        
        # Try local models first
        local_pids = list(LOCAL_PROVIDERS.keys())
        for pid in local_pids:
            if pid in self.health and self.health[pid].cb.can_attempt():
                try:
                    content, i, o, lat = await self._call_provider(pid, messages, task)
                    self.health[pid].record_success(lat, i + o)
                    return content
                except Exception as e:
                    logger.warning(f"graceful_fallback_chain local provider {pid} failed: {e}")
                    self.health[pid].record_failure()
                    
        # Try remaining providers checking circuit breaker state
        all_pids = list(ALL_PROVIDERS.keys())
        for pid in all_pids:
            if pid in self.health and self.health[pid].cb.can_attempt():
                try:
                    content, i, o, lat = await self._call_provider(pid, messages, task)
                    self.health[pid].record_success(lat, i + o)
                    return content
                except Exception as e:
                    logger.warning(f"graceful_fallback_chain cloud provider {pid} failed: {e}")
                    self.health[pid].record_failure()
                    
        raise RuntimeError('All providers exhausted in graceful fallback chain')



# compatibility shim added by nina-super fix
def classify_task(prompt: str, **kwargs):
    """Shim: classify_task was removed. Extend with real logic."""
    return {'type': 'unknown', 'prompt': prompt}
