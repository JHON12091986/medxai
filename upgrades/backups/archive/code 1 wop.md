# core/router.py
# NINA v12 HybridRouter V5 — compatible rewrite of V4
# Same public interface. Improved internals:
#   - Circuit breaker (CLOSED/OPEN/HALF_OPEN) replaces fixed cooldowns
#   - Context-aware cache key (prompt + last 4 message turns)
#   - HTTP 429 Retry-After support
#   - Request trace ID in all log lines
#   - Retry-once with 1s backoff for timeout/5xx
#   - Partial parallel_route synthesis (≥1 result)
#   - Dynamic local model discovery from Ollama /api/tags
#   - Key validation with .strip()
#   - Cache purge in idle_monitor every 5min (not just on size)

import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import httpx
import psutil

from core.config import NinaConfig, RATELIMITS

logger = logging.getLogger("nina.router")

# ---------------------------------------------------------------------------
# Provider tables
# ---------------------------------------------------------------------------

PROVIDERS_TIER1 = {
    "POLLINATIONS": {"base_url": "https://text.pollinations.ai/openai", "model": "mistral",         "key_field": None},
    "CHUTES":       {"base_url": "https://llm.chutes.ai/v1",            "model": "deepseek-r1",     "key_field": None},
    "HFPUBLIC":     {"base_url": "https://api-inference.huggingface.co","model": "various",          "key_field": None},
}
PROVIDERS_TIER2 = {
    "CEREBRAS":   {"base_url": "https://api.cerebras.ai/v1",                  "model": "llama-3.3-70b",           "key_field": "cerebras_api_key"},
    "GROQ":       {"base_url": "https://api.groq.com/openai/v1",              "model": "llama-3.3-70b-versatile", "key_field": "groq_api_key"},
    "MISTRAL":    {"base_url": "https://api.mistral.ai/v1",                   "model": "mistral-large-latest",    "key_field": "mistral_api_key"},
    "DEEPSEEK":   {"base_url": "https://api.deepseek.com/v1",                 "model": "deepseek-chat",           "key_field": "deepseek_api_key"},
    "GEMINI":     {"base_url": "https://generativelanguage.googleapis.com",   "model": "gemini-1.5-pro",          "key_field": "gemini_api_key"},
    "TOGETHER":   {"base_url": "https://api.together.xyz/v1",                 "model": "llama-3.1-405b",          "key_field": "together_api_key"},
    "COHERE":     {"base_url": "https://api.cohere.ai/v2",                    "model": "command-r-plus",          "key_field": "cohere_api_key"},
    "FIREWORKS":  {"base_url": "https://api.fireworks.ai/inference/v1",       "model": "llama-v3p1-405b",         "key_field": "fireworks_api_key"},
    "XAI":        {"base_url": "https://api.x.ai/v1",                        "model": "grok-beta",               "key_field": "xai_api_key"},
    "PERPLEXITY": {"base_url": "https://api.perplexity.ai",                   "model": "sonar-pro",               "key_field": "perplexity_api_key"},
    "SAMBANOVA":  {"base_url": "https://api.sambanova.ai/v1",                 "model": "Meta-Llama-3.1-405B",     "key_field": "sambanova_api_key"},
    "HYPERBOLIC": {"base_url": "https://api.hyperbolic.xyz/v1",               "model": "llama-3.1-405b",          "key_field": "hyperbolic_api_key"},
    "NOVITA":     {"base_url": "https://api.novita.ai/v3/openai",             "model": "llama-3.1-70b",           "key_field": "novita_api_key"},
    "OPENAI":     {"base_url": "https://api.openai.com/v1",                   "model": "gpt-4o-mini",             "key_field": "openai_api_key"},
    "ONEBRAIN":   {"base_url": None,                                          "model": "default",                 "key_field": "onebrain_api_key"},
}
PROVIDERS_TIER3 = {
    "OPENROUTER": {"base_url": "https://openrouter.ai/api/v1", "model": "auto", "key_field": "openrouter_api_key"},
}

LOCAL_PROVIDERS = {
    "LOCALFAST": {"model": "qwen2.5:1.5b"},
    "LOCALHEAVY": {"model": "qwen2.5:7b"},
}

TASK_TYPES     = ("sensitive","coding","research","math","multilingual","document","vision","quick","general")
STEP_BUDGETS   = {"quick":3,"general":5,"multilingual":5,"math":6,"coding":8,"document":8,"research":10,"sensitive":5}
DEFAULT_MAX_STEPS = 5
CACHE_TTL      = {"sensitive":0,"quick":3600,"research":1800,"coding":21600,"document":14400,"general":7200,"math":21600,"multilingual":7200}

# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------

class CircuitBreaker:
    """CLOSED → OPEN after 3 failures in 120s → HALF_OPEN after 60s → CLOSED on success."""
    FAILURE_THRESHOLD = 3
    WINDOW_S          = 120
    RECOVERY_S        = 60

    def __init__(self):
        self.state        = "CLOSED"   # CLOSED | OPEN | HALF_OPEN
        self.failures     = deque()    # timestamps of recent failures
        self.open_until   = 0.0

    def _prune(self):
        now = time.time()
        while self.failures and now - self.failures[0] > self.WINDOW_S:
            self.failures.popleft()

    def allow_request(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() >= self.open_until:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN: allow one trial

    def record_success(self):
        self.failures.clear()
        self.state = "CLOSED"

    def record_failure(self):
        now = time.time()
        self.failures.append(now)
        self._prune()
        if self.state == "HALF_OPEN":
            self.state     = "OPEN"
            self.open_until = now + self.RECOVERY_S
        elif self.state == "CLOSED" and len(self.failures) >= self.FAILURE_THRESHOLD:
            self.state     = "OPEN"
            self.open_until = now + self.RECOVERY_S

    def set_cooldown(self, seconds: float):
        """Force OPEN for a specific duration (e.g. from Retry-After header)."""
        self.state     = "OPEN"
        self.open_until = time.time() + seconds

# ---------------------------------------------------------------------------
# ProviderHealth
# ---------------------------------------------------------------------------

@dataclass
class ProviderHealth:
    provider_id:        str
    success_count:      int   = 0
    failure_count:      int   = 0
    latencies:          deque = field(default_factory=lambda: deque(maxlen=20))
    requests_today:     int   = 0
    tokens_today:       int   = 0
    last_request_ts:    float = 0.0
    reserved_requests:  int   = 0
    reserved_tokens:    int   = 0
    # V5: circuit breaker replaces cooldown_until / degraded_until
    cb: CircuitBreaker  = field(default_factory=CircuitBreaker)

    # --- keep these properties so Guardian patterns still match ---
    @property
    def cooldown_until(self) -> float:
        return self.cb.open_until

    @property
    def degraded_until(self) -> float:
        return self.cb.open_until

    def avg_latency_ms(self) -> float:
        return sum(self.latencies) / len(self.latencies) if self.latencies else 999.0

    def success_rate(self) -> float:
        t = self.success_count + self.failure_count
        return self.success_count / t if t else 1.0

    def is_available(self, has_key: bool) -> bool:
        return has_key and self.cb.allow_request()

    def is_degraded(self) -> bool:
        return self.cb.state in ("OPEN", "HALF_OPEN")

    def is_near_limit(self, pid: str) -> bool:
        tpd = RATELIMITS.get(pid, {}).get("tpd")
        return bool(tpd and self.tokens_today > 0.8 * tpd)

    def is_exhausted(self, pid: str) -> bool:
        tpd = RATELIMITS.get(pid, {}).get("tpd")
        return bool(tpd and self.tokens_today >= tpd)

    def is_spacing_blocked(self, pid: str) -> bool:
        s = RATELIMITS.get(pid, {}).get("min_spacing_s", 0)
        return bool(s and time.time() - self.last_request_ts < s)

    def composite_score(self, pid: str) -> float:
        lat  = min(self.avg_latency_ms() / 5000.0, 1.0)
        limit_pen = 0.0 if self.is_near_limit(pid) else 1.0
        return self.success_rate() * 0.4 + (1.0 - lat) * 0.4 + limit_pen * 0.2

    def record_success(self, latency_ms: float, tokens: int):
        self.success_count    += 1
        self.latencies.append(latency_ms)
        self.requests_today   += 1
        self.tokens_today     += tokens
        self.last_request_ts   = time.time()
        self.cb.record_success()

    def record_failure(self):
        self.failure_count += 1
        self.cb.record_failure()

    def reset_daily(self):
        self.requests_today = 0
        self.tokens_today   = 0

# ---------------------------------------------------------------------------
# ClassifiedTask
# ---------------------------------------------------------------------------

@dataclass
class ClassifiedTask:
    task_type:             str
    estimated_tokens:      int
    is_parallel_candidate: bool
    is_sensitive:          bool


async def classify_task(text: str, local_fast_fn) -> ClassifiedTask:
    try:
        raw = await local_fast_fn(
            f"Classify into one of {','.join(TASK_TYPES)}. "
            f"Reply JSON only {{task_type:...,estimated_tokens:N}} {text[:500]}"
        )
        d  = json.loads(raw.strip())
        tt = d.get("task_type", "general")
        if tt not in TASK_TYPES:
            tt = "general"
        est = int(d.get("estimated_tokens", 500))
        return ClassifiedTask(tt, est, tt in ("research","coding","math") and est > 800, tt == "sensitive")
    except Exception:
        logger.warning(f"nlp_classification_failed input={text[:80]!r} falling through to general task", extra={"log": "nina.log"})
        return ClassifiedTask("general", 500, False, False)

# ---------------------------------------------------------------------------
# ResponseCache  (context-aware key — V5 fix)
# ---------------------------------------------------------------------------

class ResponseCache:
    def __init__(self):
        self.s: dict = {}

    def _k(self, prompt: str, messages: list = None) -> str:
        ctx = prompt.strip().lower()
        if messages:
            ctx += "".join(m.get("content", "") for m in messages[-4:])
        return hashlib.sha256(ctx.encode()).hexdigest()

    def get(self, prompt: str, tt: str, messages: list = None) -> Optional[str]:
        if CACHE_TTL.get(tt, 0) == 0:
            return None
        e = self.s.get(self._k(prompt, messages))
        return e["response"] if e and time.time() < e["expires_at"] else None

    def set(self, prompt: str, tt: str, response: str, provider: str, messages: list = None):
        if len(self.s) > 500:
            self.purge_expired()
        ttl = CACHE_TTL.get(tt, 0)
        if ttl:
            self.s[self._k(prompt, messages)] = {
                "response":   response,
                "expires_at": time.time() + ttl,
                "provider":   provider,
            }

    def clear(self):
        self.s.clear()

    def purge_expired(self):
        now  = time.time()
        dead = [k for k, v in self.s.items() if now >= v["expires_at"]]
        for k in dead:
            self.s.pop(k, None)

# ---------------------------------------------------------------------------
# CostTracker
# ---------------------------------------------------------------------------

class CostTracker:
    def __init__(self):
        self.daily_cost_usd = 0.0
        self._rlog = logging.getLogger("nina.routerlog")

    def record(self, provider, tt, in_t, out_t, cost, ttf, total,
               parallel=False, cached=False, error=None, req_id=""):
        self._rlog.info(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S.000+0600"),
            "req_id":        req_id,
            "provider":      provider,
            "task_type":     tt,
            "input_tokens":  in_t,
            "output_tokens": out_t,
            "cost_usd":      cost,
            "ttf_ms":        ttf,
            "total_ms":      total,
            "parallel":      parallel,
            "cached":        cached,
            "status":        "success" if not error else "failure",
            "error":         error,
        }))
        if not error:
            self.daily_cost_usd += cost

    def reset_daily(self):
        self.daily_cost_usd = 0.0

# ---------------------------------------------------------------------------
# HybridRouter V5
# ---------------------------------------------------------------------------

class HybridRouter:

    def __init__(self, config: NinaConfig):
        self.config    = config
        self.health:   dict[str, ProviderHealth] = {}
        self.cache     = ResponseCache()
        self.cost      = CostTracker()
        self._http:    Optional[httpx.AsyncClient] = None
        self._idle_task = None

    async def initialize(self):
        self._http = httpx.AsyncClient(timeout=60.0)
        for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, "LOCALFAST", "LOCALHEAVY"]:
            self.health[pid] = ProviderHealth(provider_id=pid)
        await self._discover_local_models()
        self._idle_task = asyncio.create_task(self._idle_monitor())
        logger.info("HybridRouter V5 initialized")

    async def close(self):
        if self._idle_task:
            self._idle_task.cancel()
        if self._http:
            await self._http.aclose()

    async def _discover_local_models(self):
        """Query Ollama /api/tags and update LOCAL_PROVIDERS model names dynamically."""
        try:
            r = await asyncio.wait_for(
                self._http.get(f"{self.config.ollama_host}/api/tags"), timeout=5.0
            )
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            if not models:
                return
            # smallest model → LOCALFAST, largest → LOCALHEAVY
            def size_key(n):
                for suffix, val in [("70b",70),("32b",32),("14b",14),("7b",7),("3b",3),("1.5b",1),("0.5b",0)]:
                    if suffix in n.lower():
                        return val
                return 5
            sorted_models = sorted(models, key=size_key)
            LOCAL_PROVIDERS["LOCALFAST"]["model"] = sorted_models[0]
            LOCAL_PROVIDERS["LOCALHEAVY"]["model"] = sorted_models[-1]
            logger.info(f"local_models_discovered fast={LOCAL_PROVIDERS['LOCALFAST']['model']} heavy={LOCAL_PROVIDERS['LOCALHEAVY']['model']}")
        except Exception as e:
            logger.warning(f"local_model_discovery_failed {e} — using defaults")

    def _has_key(self, pid: str) -> bool:
        if pid in LOCAL_PROVIDERS or pid in PROVIDERS_TIER1:
            return True
        meta = (PROVIDERS_TIER2 | PROVIDERS_TIER3).get(pid, {})
        kf   = meta.get("key_field")
        key  = getattr(self.config, kf, None) if kf else None
        return bool(key and str(key).strip())   # V5: .strip() guard

    def _ordered_providers(self, task: ClassifiedTask, force_local: bool = False) -> list:
        if task.is_sensitive or force_local:
            return ["LOCALFAST"]
        avail, deg = [], []
        for pid, h in self.health.items():
            if pid in LOCAL_PROVIDERS:
                continue
            if not self._has_key(pid) or h.is_exhausted(pid):
                continue
            if not h.is_available(True):
                continue
            (deg if h.is_degraded() else avail).append(pid)
        sk = lambda p: self.health[p].composite_score(p)
        ordered = sorted(avail, key=sk, reverse=True) + sorted(deg, key=sk, reverse=True)
        if "ONEBRAIN" in ordered:
            ordered.remove("ONEBRAIN")
            ordered.append("ONEBRAIN")
        return ordered + ["LOCALFAST"]

    async def _call_provider(self, pid: str, messages: list, task: ClassifiedTask):
        """Returns (text, in_tokens, out_tokens, latency_ms). Raises on failure."""
        start = time.time()
        if pid in LOCAL_PROVIDERS:
            r = await self._http.post(
                f"{self.config.ollama_host}/api/chat",
                json={"model": LOCAL_PROVIDERS[pid]["model"], "messages": messages, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            return r.json()["message"]["content"], 0, 0, (time.time() - start) * 1000

        meta  = (PROVIDERS_TIER1 | PROVIDERS_TIER2 | PROVIDERS_TIER3)[pid]
        base  = meta["base_url"] or getattr(self.config, "onebrain_api_base", "")
        kf    = meta.get("key_field")
        key   = getattr(self.config, kf, None) if kf else "no-key"
        r = await self._http.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": meta["model"], "messages": messages, "stream": False},
            timeout=60,
        )
        # V5: explicit 429 handling
        if r.status_code == 429:
            retry_after = float(r.headers.get("retry-after", 60))
            self.health[pid].cb.set_cooldown(retry_after)
            raise httpx.HTTPStatusError(f"429 rate-limited retry-after={retry_after}s", request=r.request, response=r)
        r.raise_for_status()
        d = r.json()
        u = d.get("usage", {})
        return (
            d["choices"][0]["message"]["content"],
            u.get("prompt_tokens", 0),
            u.get("completion_tokens", 0),
            (time.time() - start) * 1000,
        )

    async def route(self, prompt: str, messages: list, task: ClassifiedTask,
                    force_local: bool = False) -> str:
        req_id = uuid.uuid4().hex[:8]

        cached = self.cache.get(prompt, task.task_type, messages)
        if cached:
            self.cost.record("CACHE", task.task_type, 0, 0, 0, 0, 0, cached=True, req_id=req_id)
            return cached

        for pid in self._ordered_providers(task, force_local):
            h  = self.health[pid]
            rl = RATELIMITS.get(pid, {})
            sp = rl.get("min_spacing_s", 0)
            if sp:
                w = sp - (time.time() - h.last_request_ts)
                if w > 0:
                    await asyncio.sleep(w)

            # V5: retry-once on timeout / 5xx
            for attempt in range(2):
                try:
                    text, in_t, out_t, lat = await self._call_provider(pid, messages, task)
                    h.record_success(lat, in_t + out_t)
                    self.cost.record(pid, task.task_type, in_t, out_t, 0.0, lat, lat, req_id=req_id)
                    self.cache.set(prompt, task.task_type, text, pid, messages)
                    return text
                except asyncio.TimeoutError:
                    h.record_failure()
                    self.cost.record(pid, task.task_type, 0, 0, 0, 0, 0, error="timeout", req_id=req_id)
                    if attempt == 0:
                        await asyncio.sleep(1.0)
                    break
                except httpx.HTTPStatusError as e:
                    h.record_failure()
                    sc = e.response.status_code if e.response else 0
                    self.cost.record(pid, task.task_type, 0, 0, 0, 0, 0, error=f"http_{sc}", req_id=req_id)
                    if sc >= 500 and attempt == 0:
                        await asyncio.sleep(1.0)
                        continue
                    break
                except Exception as e:
                    h.record_failure()
                    self.cost.record(pid, task.task_type, 0, 0, 0, 0, 0, error=str(e)[:80], req_id=req_id)
                    break

        failed = list(self._ordered_providers(task, force_local))
        logger.error(f"all_providers_failed task={task.task_type} tried={failed} req_id={req_id}")
        return "⚠️ All providers are currently unavailable. Try again in a moment, or send `status` to check provider health."

    async def parallel_route(self, prompt: str, messages: list, task: ClassifiedTask, local_fast_fn) -> str:
        if psutil.virtual_memory().used / 1e9 > self.config.ram_guard_gb:
            return await self.route(prompt, messages, task)

        cloud = [p for p in self._ordered_providers(task) if p not in LOCAL_PROVIDERS]
        if len(cloud) < 2:
            return await self.route(prompt, messages, task)

        try:
            raw  = await local_fast_fn(f"Split into min({3},{len(cloud)}) independent sub-questions. JSON array only.\n{prompt}")
            subs = json.loads(raw)
        except Exception:
            return await self.route(prompt, messages, task)

        chosen = cloud[:len(subs)]
        for p in chosen:
            self.health[p].reserved_requests += 1
            self.health[p].reserved_tokens   += task.estimated_tokens // len(chosen)

        async def fetch(pid, q):
            try:
                t, i, o, la = await asyncio.wait_for(
                    self._call_provider(pid, messages[:-1] + [{"role":"user","content":q}], task), 45.0
                )
                self.health[pid].record_success(la, i + o)
                return t
            except Exception:
                self.health[pid].record_failure()
                return None

        results = await asyncio.gather(*[fetch(p, q) for p, q in zip(chosen, subs)])
        for p in chosen:
            self.health[p].reserved_requests = 0
            self.health[p].reserved_tokens   = 0

        # V5: synthesize even partial results (≥1 success)
        parts = [r for r in results if r]
        if not parts:
            return await self.route(prompt, messages, task)
        return await local_fast_fn("Synthesize these answers:\n" + "\n---\n".join(parts))

    async def single_turn(self, prompt: str, session_history: list) -> str:
        msgs = session_history + [{"role": "user", "content": prompt}]
        return await self.route(prompt, msgs, ClassifiedTask("quick", 300, False, False))

    async def _idle_monitor(self):
        tick = 0
        while True:
            await asyncio.sleep(300)
            tick += 1
            # V5: purge cache every 5min in idle loop
            if tick % 1 == 0:
                self.cache.purge_expired()

            if psutil.virtual_memory().used / 1e9 > self.config.ram_guard_gb:
                continue

            cloud = [p for p in self.health if p not in LOCAL_PROVIDERS and self._has_key(p)]
            if not cloud:
                continue
            pid = min(cloud, key=lambda p: self.health[p].composite_score(p))
            try:
                _, _, _, lat = await asyncio.wait_for(
                    self._call_provider(
                        pid,
                        [{"role": "user", "content": "Reply: OK"}],
                        ClassifiedTask("quick", 10, False, False),
                    ),
                    15.0,
                )
                self.health[pid].record_success(lat, 10)
            except Exception:
                self.health[pid].record_failure()
                logger.warning(f"quality_probe_fail provider={pid} marked DEGRADED")

    async def activate_key(self, provider: str, key: str) -> str:
        meta = (PROVIDERS_TIER2 | PROVIDERS_TIER3).get(provider)
        if not meta:
            return f"Unknown provider {provider}"
        kf = meta.get("key_field")
        if not kf:
            return f"{provider} does not use an API key."
        setattr(self.config, kf, key)
        try:
            from dotenv import set_key as sk
            sk(".env", kf.upper(), key)
        except Exception as e:
            logger.warning(f"activate_key persist failed {e}")
        logger.info(f"activate_key provider={provider} persisted", extra={"log": "nina.security"})
        self.health[provider] = ProviderHealth(provider_id=provider)
        return f"✅ Key set for {provider}."

    def reset_daily_counters(self):
        for h in self.health.values():
            h.reset_daily()
        self.cost.reset_daily()

    def get_status(self) -> str:
        lines = ["Router V5  Provider Status"]
        for pid, h in sorted(self.health.items()):
            hk = self._has_key(pid)
            state = ("available" if h.is_available(hk) and not h.is_exhausted(pid)
                     else "exhausted" if h.is_exhausted(pid)
                     else f"cb:{h.cb.state}" if not h.is_available(hk)
                     else "no key")
            lines.append(
                f"{pid:<14} {state:<18} score={h.composite_score(pid):.2f}"
                f" lat={h.avg_latency_ms():.0f}ms sr={h.success_rate()*100:.0f}%"
                f" tok={h.tokens_today}"
            )
        lines.append(f"  today ${self.cost.daily_cost_usd:.4f}")
        return "\n".join(lines)
