# core/router.py
from typing import List, Dict, Optional, Tuple, cast
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
    "LOCALFAST": {"model": "qwen2.5:1.5b", "context_window": 8192},
    "LOCALHEAVY": {"model": "qwen2.5:7b", "context_window": 32768},
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
    "lpu_deterministic": 86400, # High cache persistence for mechanical tasks
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
    "lpu_deterministic": 1, # LPUs don't loop
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
        self.discovery = ModelDiscoveryService(config=self.config)
        self.http: httpx.AsyncClient | None = None
        self._idle_task: asyncio.Task | None = None

    async def initialize(self) -> None:
        self.http = httpx.AsyncClient(timeout=60.0)
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
        start = time.time()
        req_id = str(uuid.uuid4())

        if pid in LOCAL_PROVIDERS:
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
            return content, 0, 0, lat

        meta = cast(dict, ALL_PROVIDERS[pid]).copy()
        api_key = self.config.get_secret(meta["key_field"]) if meta["key_field"] else None

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
        return content, it, ot, lat

    async def _validate_response(self, content: str, task: ClassifiedTask) -> Tuple[bool, str]:
        """
        OODA Loop (Observe/Orient): Validate the AI response for quality.
        Returns (is_valid, error_reason).
        """
        # 1. Heuristic: Empty or too short for a complex task
        if task.task_type == "research" and len(content) < 100:
            return False, "Response too short for a research task."
        
        # 2. Heuristic: Hallucination markers
        hallucination_markers = ["I am a large language model", "As an AI", "I cannot fulfill this request"]
        if any(m.lower() in content.lower() for m in hallucination_markers):
            return False, "AI refusal or boilerplate detected."

        # 3. Model-based validation (for Coding/Complex tasks)
        if task.task_type in ["coding", "research"]:
            try:
                # Use LOCALFAST (low latency) as a "Logic Gate" validator
                messages = [
                    {"role": "system", "content": "You are a logic gate. Review the following AI response for a coding/research task. Is it technically sound, idiomatic, and complete? Respond only with 'VALID' or a one-sentence error reason."},
                    {"role": "user", "content": f"TASK: {task.task_type}\nRESPONSE: {content[:2000]}"}
                ]
                # Avoid infinite recursion by using _call_provider directly for the validator
                val_content, _, _, _ = await self._call_provider("LOCALFAST", messages, ClassifiedTask("quick", 100, False, False))
                if "valid" in val_content.lower():
                    return True, ""
                else:
                    return False, f"Logic Gate Refusal: {val_content}"
            except Exception:
                # If validator fails, default to trusting the response to avoid deadlock
                pass

        return True, ""

    async def route(
        self, goal: str, messages: list, task: ClassifiedTask, force_local: bool = False
    ) -> str:
        # NINA-GROQ: Deterministic LPU Fast-Track
        if task.task_type == "lpu_deterministic":
            try:
                # Bypass all routing overhead, go straight to localized execution
                content, i, o, lat = await self._call_provider("LOCALFAST", messages, task)
                return content
            except Exception as e:
                logger.warning(f"LPU Fast-track failed: {e}. Falling back to standard route.")

        # CRITICAL Task Override: Force Gemini 3.5 Flash
        if task.task_type == "critical":
            logger.info("CRITICAL Task detected: Forcing GEMINI_FLASH_PROD routing.")
            # Ensure GEMINI_FLASH_PROD is defined in ninagate/providers.json as Tier 2 or 3
            # Forcing a specific provider and bypassing normal tier selection
            pid = "GEMINI_FLASH_PROD" # This provider must exist and be configured for Gemini 3.5 Flash
            if pid in ALL_PROVIDERS and self.health[pid].cb.can_attempt():
                try:
                    content, i, o, lat = await self._call_provider(pid, messages, task)
                    is_valid, error = await self._validate_response(content, task)
                    if is_valid:
                        self.health[pid].record_success(lat, i + o)
                        return content
                    else:
                        logger.bind(provider=pid, error=error).warning("critical_task_validation_failed")
                        self.health[pid].record_failure()
                        # Fallback to standard routing logic if critical task fails validation
                except Exception as e:
                    logger.bind(provider=pid, error=str(e)).warning("critical_task_provider_failed")
                    self.health[pid].record_failure()
            else:
                logger.warning("GEMINI_FLASH_PROD not available or circuit open for CRITICAL task, falling back.")

        # Cache check
        cached = self.cache.get(goal, messages)
        if cached:
            return cached

        tiers = [PROVIDERS_TIER1, PROVIDERS_TIER2, PROVIDERS_TIER3]
        if force_local:
            tiers = [LOCAL_PROVIDERS]

        for attempt in range(2): # OODA: Act -> Observe loop
            for tier in tiers:
                available = []
                for pid in tier:
                    if pid in LOCAL_PROVIDERS:
                        meta = LOCAL_PROVIDERS[pid]
                    else:
                        meta = ALL_PROVIDERS.get(pid, tier.get(pid, {}))
                    
                    if (
                        self.health[pid].cb.can_attempt()
                        and self.health[pid].requests_today < 1000
                        and meta.get("context_window", 8192) >= task.estimated_tokens
                    ):
                        available.append(pid)

                if not available:
                    continue

                available.sort(key=lambda pid: self.health[pid].health_score, reverse=True)

                for pid in available:
                    try:
                        content, i, o, lat = await self._call_provider(pid, messages, task)
                        
                        # OODA: Observe & Decide (Validate)
                        is_valid, error = await self._validate_response(content, task)
                        if is_valid:
                            self.health[pid].record_success(lat, i + o)
                            ttl = CACHE_TTL.get(task.task_type, 3600)
                            if ttl > 0:
                                self.cache.set(goal, content, ttl, messages)
                            return content
                        else:
                            # OODA: Adapt (Penalize and retry)
                            logger.bind(provider=pid, error=error).warning("response_validation_failed")
                            self.health[pid].record_failure()
                            # Prepend the validation error to help the next model refine the response
                            messages.append({"role": "assistant", "content": content})
                            messages.append({"role": "user", "content": f"The previous response failed validation: {error}. Please refine and provide a correct, high-quality answer."})
                            continue

                    except Exception as e:
                        self.health[pid].record_failure()
                        asyncio.create_task(self._check_health_and_notify(pid))
                        logger.bind(provider=pid, error=str(e)).warning("provider_retry")
                        continue

        return "⚠️ All providers are currently unavailable or failing validation. Try again in a moment."

    async def parallel_route(
        self, prompts: List[str], task: ClassifiedTask
    ) -> List[Optional[str]]:
        results = []
        for p in prompts:
            results.append(await self.route(p, [{"role": "user", "content": p}], task))
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
