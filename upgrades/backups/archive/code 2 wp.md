# core/router.py
import asyncio, hashlib, json, logging, time, uuid
from dataclasses import dataclass, field
from typing import Optional
import httpx, psutil
from core.config import NinaConfig, RATELIMITS

logger = logging.getLogger("nina.router")
PROVIDERS_TIER1 = {
    "POLLINATIONS": {"base_url": "https://text.pollinations.ai/openai", "model": "mistral", "key_field": None},
    "CHUTES": {"base_url": "https://llm.chutes.ai/v1", "model": "deepseek-r1", "key_field": None},
    "HFPUBLIC": {"base_url": "https://api-inference.huggingface.co", "model": "various", "key_field": None},
}
PROVIDERS_TIER2 = {
    "CEREBRAS": {"base_url": "https://api.cerebras.ai/v1", "model": "llama-3.3-70b", "key_field": "cerebras_api_key"},
    "GROQ": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile", "key_field": "groq_api_key"},
    "MISTRAL": {"base_url": "https://api.mistral.ai/v1", "model": "mistral-large-latest", "key_field": "mistral_api_key"},
    "DEEPSEEK": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat", "key_field": "deepseek_api_key"},
    "GEMINI": {"base_url": "https://generativelanguage.googleapis.com", "model": "gemini-1.5-pro", "key_field": "gemini_api_key"},
    "TOGETHER": {"base_url": "https://api.together.xyz/v1", "model": "llama-3.1-405b", "key_field": "together_api_key"},
    "COHERE": {"base_url": "https://api.cohere.ai/v2", "model": "command-r-plus", "key_field": "cohere_api_key"},
    "FIREWORKS": {"base_url": "https://api.fireworks.ai/inference/v1", "model": "llama-v3p1-405b", "key_field": "fireworks_api_key"},
    "XAI": {"base_url": "https://api.x.ai/v1", "model": "grok-beta", "key_field": "xai_api_key"},
    "PERPLEXITY": {"base_url": "https://api.perplexity.ai", "model": "sonar-pro", "key_field": "perplexity_api_key"},
    "SAMBANOVA": {"base_url": "https://api.sambanova.ai/v1", "model": "Meta-Llama-3.1-405B", "key_field": "sambanova_api_key"},
    "HYPERBOLIC": {"base_url": "https://api.hyperbolic.xyz/v1", "model": "llama-3.1-405b", "key_field": "hyperbolic_api_key"},
    "NOVITA": {"base_url": "https://api.novita.ai/v3/openai", "model": "llama-3.1-70b", "key_field": "novita_api_key"},
    "OPENAI": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini", "key_field": "openai_api_key"},
    "ONEBRAIN": {"base_url": None, "model": "default", "key_field": "onebrain_api_key"},
}
PROVIDERS_TIER3 = {
    "OPENROUTER": {"base_url": "https://openrouter.ai/api/v1", "model": "auto", "key_field": "openrouter_api_key"},
}
LOCAL_PROVIDERS = {
    "LOCALFAST": {"model": "qwen2.5:1.5b"},
    "LOCALHEAVY": {"model": "qwen2.5:7b"},
}
TASK_TYPES = ("sensitive", "coding", "research", "math", "multilingual", "document", "vision", "quick", "general")
STEP_BUDGETS = {"quick": 3, "general": 5, "multilingual": 5, "math": 6, "coding": 8, "document": 8, "research": 10, "sensitive": 5}
DEFAULT_MAX_STEPS = 5
CACHE_TTL = {"sensitive": 0, "quick": 3600, "research": 1800, "coding": 21600, "document": 14400, "general": 7200, "math": 21600, "multilingual": 7200}


@dataclass
class ClassifiedTask:
    task_type: str
    estimated_tokens: int
    is_parallel_candidate: bool
    is_sensitive: bool


@dataclass
class CircuitBreaker:
    state: str = "CLOSED"
    failure_count: int = 0
    failure_window_start: float = 0.0
    open_until: float = 0.0
    half_open_in_flight: bool = False
    failure_threshold: int = 5
    failure_window_s: int = 120
    recovery_timeout_s: int = 60

    def allow(self) -> bool:
        now = time.time()
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if now >= self.open_until:
                self.state = "HALF_OPEN"
                self.half_open_in_flight = False
            else:
                return False
        if self.state == "HALF_OPEN":
            if self.half_open_in_flight:
                return False
            self.half_open_in_flight = True
            return True
        return True

    def record_success(self):
        self.state = "CLOSED"
        self.failure_count = 0
        self.failure_window_start = 0.0
        self.open_until = 0.0
        self.half_open_in_flight = False

    def record_failure(self, cooldown_s: Optional[float] = None):
        now = time.time()
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.open_until = now + (cooldown_s if cooldown_s is not None else self.recovery_timeout_s)
            self.half_open_in_flight = False
            return
        if self.failure_window_start == 0.0 or now - self.failure_window_start > self.failure_window_s:
            self.failure_window_start = now
            self.failure_count = 1
        else:
            self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.open_until = now + (cooldown_s if cooldown_s is not None else self.recovery_timeout_s)
            self.half_open_in_flight = False

    def force_open(self, cooldown_s: float):
        self.state = "OPEN"
        self.open_until = time.time() + max(1.0, float(cooldown_s))
        self.half_open_in_flight = False


@dataclass
class ProviderHealth:
    provider_id: str
    success_count: int = 0
    failure_count: int = 0
    last_latency_ms: float = 0.0
    avg_latency_ms_value: float = 0.0
    requests_today: int = 0
    tokens_today: int = 0
    last_request_ts: float = 0.0
    reserved_requests: int = 0
    reserved_tokens: int = 0
    cooldown_until: float = 0.0
    degraded_until: float = 0.0
    breaker: CircuitBreaker = field(default_factory=CircuitBreaker)

    def avg_latency_ms(self) -> float:
        return self.avg_latency_ms_value or 999.0

    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return (self.success_count / total) if total else 1.0

    def is_available(self, has_key: bool) -> bool:
        if not has_key:
            return False
        return self.breaker.allow()

    def is_degraded(self) -> bool:
        return self.breaker.state in ("OPEN", "HALF_OPEN") or time.time() < self.degraded_until

    def is_near_limit(self, pid: str) -> bool:
        lim = RATELIMITS.get(pid, {})
        tpd = lim.get("tpd")
        if not tpd:
            return False
        return (self.tokens_today + self.reserved_tokens) >= int(tpd * 0.8)

    def is_exhausted(self, pid: str) -> bool:
        lim = RATELIMITS.get(pid, {})
        tpd = lim.get("tpd")
        if not tpd:
            return False
        return (self.tokens_today + self.reserved_tokens) >= tpd

    def composite_score(self, pid: str) -> float:
        sr = self.success_rate()
        lat = self.avg_latency_ms()
        latency_score = max(0.0, 1.0 - min(lat, 5000.0) / 5000.0)
        limit_penalty = 0.2 if self.is_near_limit(pid) else 0.0
        degraded_penalty = 0.25 if self.breaker.state == "HALF_OPEN" else (0.5 if self.breaker.state == "OPEN" else 0.0)
        return (sr * 0.45) + (latency_score * 0.4) + (0.15 - limit_penalty) - degraded_penalty

    def record_success(self, latency_ms: float, total_tokens: int):
        self.success_count += 1
        self.requests_today += 1
        self.tokens_today += max(0, int(total_tokens))
        self.last_request_ts = time.time()
        self.last_latency_ms = float(latency_ms)
        if self.avg_latency_ms_value <= 0:
            self.avg_latency_ms_value = float(latency_ms)
        else:
            self.avg_latency_ms_value = (self.avg_latency_ms_value * 0.7) + (float(latency_ms) * 0.3)
        self.breaker.record_success()
        self.cooldown_until = 0.0
        self.degraded_until = 0.0

    def record_failure(self, cooldown_s: Optional[float] = None):
        self.failure_count += 1
        self.last_request_ts = time.time()
        self.breaker.record_failure(cooldown_s=cooldown_s)
        self.cooldown_until = self.breaker.open_until
        self.degraded_until = self.breaker.open_until

    def reset_daily(self):
        self.requests_today = 0
        self.tokens_today = 0
        self.reserved_requests = 0
        self.reserved_tokens = 0


class ResponseCache:
    def __init__(self):
        self.s = {}

    def _k(self, prompt: str, messages: Optional[list] = None) -> str:
        parts = [prompt or ""]
        if messages:
            recent = messages[-4:]
            for m in recent:
                role = m.get("role", "")
                content = m.get("content", "")
                parts.append(f"{role}:{content}")
        ctx = "\n".join(parts)
        return hashlib.sha256(ctx.encode("utf-8", errors="replace")).hexdigest()

    def get(self, prompt: str, tt: str, messages: Optional[list] = None) -> Optional[str]:
        if CACHE_TTL.get(tt, 0) == 0:
            return None
        k = self._k(prompt, messages)
        item = self.s.get(k)
        if not item:
            return None
        if time.time() >= item["expires_at"]:
            self.s.pop(k, None)
            return None
        return item["response"]

    def set(self, prompt: str, tt: str, response: str, provider: str, messages: Optional[list] = None):
        ttl = CACHE_TTL.get(tt, 0)
        if ttl <= 0:
            return
        if len(self.s) >= 500:
            self.purge_expired()
        self.s[self._k(prompt, messages)] = {
            "response": response,
            "provider": provider,
            "expires_at": time.time() + ttl,
        }

    def clear(self):
        self.s.clear()

    def purge_expired(self):
        now = time.time()
        dead = [k for k, v in self.s.items() if v.get("expires_at", 0) <= now]
        for k in dead:
            self.s.pop(k, None)


class CostTracker:
    def __init__(self):
        self.daily_cost_usd = 0.0
        self._rlog = logging.getLogger("nina.routerlog")

    def record(self, provider, task_type, in_tokens, out_tokens, cost, ttf_ms, total_ms, parallel=False, cached=False, error=None, req_id=None):
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "req_id": req_id or "",
            "provider": provider,
            "task_type": task_type,
            "input_tokens": int(in_tokens or 0),
            "output_tokens": int(out_tokens or 0),
            "cost_usd": float(cost or 0.0),
            "ttf_ms": int(ttf_ms or 0),
            "total_ms": int(total_ms or 0),
            "parallel": bool(parallel),
            "cached": bool(cached),
            "error": error or "",
        }
        try:
            self._rlog.info(json.dumps(row, ensure_ascii=False), extra={"log": "router.log"})
        except Exception:
            logger.info("routerlog_fallback %s", row)
        if not error:
            self.daily_cost_usd += float(cost or 0.0)

    def reset_daily(self):
        self.daily_cost_usd = 0.0


async def classify_task(text: str, local_fast_fn) -> ClassifiedTask:
    try:
        prompt = (
            "Classify this user request into exactly one of: "
            f"{', '.join(TASK_TYPES)}.\n"
            "Return strict JSON only like "
            '{"task_type":"general","estimated_tokens":500}\n'
            f"Text:\n{text[:1500]}"
        )
        raw = await local_fast_fn(prompt)
        data = json.loads(raw)
        tt = data.get("task_type", "general")
        if tt not in TASK_TYPES:
            tt = "general"
        est = int(data.get("estimated_tokens", 500))
        est = max(50, min(est, 200000))
        return ClassifiedTask(
            task_type=tt,
            estimated_tokens=est,
            is_parallel_candidate=tt in ("research", "coding") and est > 800,
            is_sensitive=(tt == "sensitive"),
        )
    except Exception:
        t = (text or "").lower()
        if any(k in t for k in ("password", "secret", "token", "private", "confidential", "bank", "account number")):
            return ClassifiedTask("sensitive", 300, False, True)
        if any(k in t for k in ("code", "python", "bug", "traceback", "function", "class", "patch")):
            return ClassifiedTask("coding", 800, True, False)
        if any(k in t for k in ("research", "compare", "search", "latest", "find", "news")):
            return ClassifiedTask("research", 1200, True, False)
        if any(k in t for k in ("calculate", "equation", "math", "solve")):
            return ClassifiedTask("math", 700, False, False)
        return ClassifiedTask("general", 500, False, False)


class HybridRouter:
    def __init__(self, config: NinaConfig):
        self.config = config
        self.health = {pid: ProviderHealth(pid) for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, *LOCAL_PROVIDERS]}
        self.cache = ResponseCache()
        self.cost = CostTracker()
        self._http: Optional[httpx.AsyncClient] = None
        self._idle_task = None

    async def initialize(self):
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=60.0)
        await self._discover_local_models()
        if self._idle_task is None or self._idle_task.done():
            self._idle_task = asyncio.create_task(self._idle_monitor())
        logger.info("HybridRouter initialized")

    async def close(self):
        if self._idle_task:
            self._idle_task.cancel()
            try:
                await self._idle_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            self._idle_task = None
        if self._http:
            await self._http.aclose()
            self._http = None

    async def _discover_local_models(self):
        try:
            if not self._http:
                return
            r = await self._http.get(f"{self.config.ollama_host}/api/tags", timeout=5.0)
            r.raise_for_status()
            models = r.json().get("models", [])
            names = [m.get("name", "") for m in models if m.get("name")]
            if not names:
                return

            def size_rank(name: str):
                s = name.lower()
                for token, rank in (
                    ("0.5b", 0.5), ("1b", 1), ("1.5b", 1.5), ("2b", 2), ("3b", 3), ("4b", 4),
                    ("7b", 7), ("8b", 8), ("9b", 9), ("13b", 13), ("14b", 14), ("27b", 27),
                    ("32b", 32), ("34b", 34), ("70b", 70), ("72b", 72),
                ):
                    if token in s:
                        return rank
                return 10

            sorted_names = sorted(names, key=size_rank)
            LOCAL_PROVIDERS["LOCALFAST"]["model"] = sorted_names[0]
            LOCAL_PROVIDERS["LOCALHEAVY"]["model"] = sorted_names[-1]
            logger.info("ollama_models_discovered fast=%s heavy=%s", LOCAL_PROVIDERS["LOCALFAST"]["model"], LOCAL_PROVIDERS["LOCALHEAVY"]["model"])
        except Exception as e:
            logger.warning("ollama_model_discovery_failed %s", e)

    def _provider_meta(self, pid: str) -> dict:
        if pid in LOCAL_PROVIDERS:
            return LOCAL_PROVIDERS[pid]
        if pid in PROVIDERS_TIER1:
            return PROVIDERS_TIER1[pid]
        if pid in PROVIDERS_TIER2:
            return PROVIDERS_TIER2[pid]
        return PROVIDERS_TIER3.get(pid, {})

    def _has_key(self, pid: str) -> bool:
        if pid in LOCAL_PROVIDERS or pid in PROVIDERS_TIER1:
            return True
        meta = self._provider_meta(pid)
        key_field = meta.get("key_field")
        if not key_field:
            return True
        key = getattr(self.config, key_field, None)
        return bool(isinstance(key, str) and key.strip())

    def _ordered_providers(self, task: ClassifiedTask, force_local: bool = False):
        if force_local or task.is_sensitive:
            return ["LOCALFAST", "LOCALHEAVY"]
        local_first = []
        cloud = []
        for pid, h in self.health.items():
            if pid in LOCAL_PROVIDERS:
                local_first.append(pid)
                continue
            if not self._has_key(pid):
                continue
            if h.is_exhausted(pid):
                continue
            if not h.breaker.allow():
                continue
            cloud.append(pid)
        cloud.sort(key=lambda pid: self.health[pid].composite_score(pid), reverse=True)
        if task.task_type in ("quick", "general"):
            return cloud + ["LOCALFAST", "LOCALHEAVY"]
        if task.task_type in ("coding", "research", "document", "math", "multilingual"):
            return cloud + ["LOCALHEAVY", "LOCALFAST"]
        return cloud + ["LOCALFAST", "LOCALHEAVY"]

    def _messages_to_text(self, messages: list) -> str:
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    async def _call_local(self, pid: str, messages: list):
        model = LOCAL_PROVIDERS[pid]["model"]
        started = time.time()
        r = await self._http.post(
            f"{self.config.ollama_host}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60.0,
        )
        r.raise_for_status()
        d = r.json()
        text = d.get("message", {}).get("content", "")
        usage = d.get("usage", {}) if isinstance(d, dict) else {}
        in_t = int(usage.get("prompt_eval_count", 0) or 0)
        out_t = int(usage.get("eval_count", 0) or 0)
        total_ms = int((time.time() - started) * 1000)
        return text, in_t, out_t, total_ms

    async def _call_openai_compatible(self, pid: str, meta: dict, messages: list):
        started = time.time()
        key = None
        key_field = meta.get("key_field")
        if key_field:
            key = getattr(self.config, key_field, None)
        headers = {"Content-Type": "application/json"}
        if key and str(key).strip():
            headers["Authorization"] = f"Bearer {key}"
        body = {"model": meta["model"], "messages": messages}
        r = await self._http.post(f"{meta['base_url']}/chat/completions", headers=headers, json=body, timeout=60.0)
        if r.status_code == 429:
            raise httpx.HTTPStatusError("429 rate limit", request=r.request, response=r)
        r.raise_for_status()
        d = r.json()
        text = d["choices"][0]["message"]["content"]
        usage = d.get("usage", {})
        in_t = int(usage.get("prompt_tokens", 0) or 0)
        out_t = int(usage.get("completion_tokens", 0) or 0)
        total_ms = int((time.time() - started) * 1000)
        return text, in_t, out_t, total_ms

    async def _call_gemini(self, pid: str, meta: dict, messages: list):
        started = time.time()
        key = getattr(self.config, meta["key_field"], None)
        msg = self._messages_to_text(messages)
        url = f"{meta['base_url']}/v1beta/models/{meta['model']}:generateContent?key={key}"
        body = {"contents": [{"parts": [{"text": msg}]}]}
        r = await self._http.post(url, json=body, timeout=60.0)
        if r.status_code == 429:
            raise httpx.HTTPStatusError("429 rate limit", request=r.request, response=r)
        r.raise_for_status()
        d = r.json()
        candidates = d.get("candidates", [])
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
        usage = d.get("usageMetadata", {})
        in_t = int(usage.get("promptTokenCount", 0) or 0)
        out_t = int(usage.get("candidatesTokenCount", 0) or 0)
        total_ms = int((time.time() - started) * 1000)
        return text, in_t, out_t, total_ms

    async def _call_provider(self, pid: str, messages: list, task: ClassifiedTask, req_id: Optional[str] = None):
        if not self._http:
            raise RuntimeError("Router not initialized")
        h = self.health[pid]
        meta = self._provider_meta(pid)
        lim = RATELIMITS.get(pid, {})
        min_spacing = float(lim.get("min_spacing_s", 0) or 0)
        wait = (h.last_request_ts + min_spacing) - time.time()
        if wait > 0:
            await asyncio.sleep(wait)

        try:
            if pid in LOCAL_PROVIDERS:
                text, in_t, out_t, total_ms = await self._call_local(pid, messages)
            elif pid == "GEMINI":
                text, in_t, out_t, total_ms = await self._call_gemini(pid, meta, messages)
            else:
                text, in_t, out_t, total_ms = await self._call_openai_compatible(pid, meta, messages)
            h.record_success(total_ms, in_t + out_t)
            return text, in_t, out_t, total_ms
        except httpx.HTTPStatusError as e:
            cooldown_s = None
            if e.response is not None and e.response.status_code == 429:
                ra = e.response.headers.get("retry-after", "").strip()
                try:
                    cooldown_s = float(ra) if ra else 60.0
                except Exception:
                    cooldown_s = 60.0
                h.breaker.force_open(cooldown_s)
                h.cooldown_until = h.breaker.open_until
                h.degraded_until = h.breaker.open_until
            else:
                h.record_failure()
            raise
        except Exception:
            h.record_failure()
            raise

    async def call_provider(self, pid: str, messages: list, task: ClassifiedTask, req_id: Optional[str] = None):
        backoffs = [0.0, 1.0]
        last_exc = None
        for idx, delay in enumerate(backoffs):
            if delay > 0:
                await asyncio.sleep(delay)
            try:
                return await self._call_provider(pid, messages, task, req_id=req_id)
            except asyncio.TimeoutError as e:
                last_exc = e
                if idx == len(backoffs) - 1:
                    raise
            except httpx.HTTPStatusError as e:
                last_exc = e
                status = e.response.status_code if e.response is not None else None
                if status == 429:
                    raise
                if status is not None and 500 <= status < 600 and idx < len(backoffs) - 1:
                    continue
                raise
            except Exception as e:
                last_exc = e
                raise
        raise last_exc if last_exc else RuntimeError("provider call failed")

    async def route(self, prompt, messages, task, force_local=False) -> str:
        req_id = uuid.uuid4().hex[:8]
        cached = self.cache.get(prompt, task.task_type, messages)
        if cached:
            self.cost.record("CACHE", task.task_type, 0, 0, 0.0, 0, 0, cached=True, req_id=req_id)
            return cached

        providers = self._ordered_providers(task, force_local=force_local)
        last_errors = []
        for pid in providers:
            try:
                text, in_t, out_t, total_ms = await self.call_provider(pid, messages, task, req_id=req_id)
                self.cost.record(pid, task.task_type, in_t, out_t, 0.0, total_ms, total_ms, req_id=req_id)
                self.cache.set(prompt, task.task_type, text, pid, messages)
                logger.info("router_success req_id=%s provider=%s task=%s ms=%s", req_id, pid, task.task_type, total_ms, extra={"log": "router.log"})
                return text
            except Exception as e:
                err = f"{pid}:{type(e).__name__}:{str(e)[:120]}"
                last_errors.append(err)
                self.cost.record(pid, task.task_type, 0, 0, 0.0, 0, 0, error=err, req_id=req_id)
                logger.warning("router_fail req_id=%s provider=%s err=%s", req_id, pid, err, extra={"log": "router.log"})
                continue

        logger.error("all_providers_failed req_id=%s task=%s errs=%s", req_id, task.task_type, " | ".join(last_errors[-5:]), extra={"log": "router.log"})
        return "⚠️ All providers are currently unavailable. Please try again in a moment."

    async def parallel_route(self, prompt, messages, task, local_fast_fn) -> str:
        ram = psutil.virtual_memory().used / 1e9
        if ram > self.config.ram_guard_gb:
            return await self.route(prompt, messages, task)

        try:
            raw = await local_fast_fn(
                "Split this request into 2 or 3 independent sub-questions as JSON array of strings only.\n"
                f"Request:\n{prompt[:3000]}"
            )
            subs = json.loads(raw)
            if not isinstance(subs, list):
                return await self.route(prompt, messages, task)
            subs = [str(x).strip() for x in subs if str(x).strip()][:3]
            if not subs:
                return await self.route(prompt, messages, task)
        except Exception:
            return await self.route(prompt, messages, task)

        cloud = [p for p in self._ordered_providers(task) if p not in LOCAL_PROVIDERS]
        if not cloud:
            return await self.route(prompt, messages, task)

        chosen = cloud[:max(1, min(len(cloud), len(subs)))]
        reserved = max(1, task.estimated_tokens // max(1, len(chosen)))
        for p in chosen:
            self.health[p].reserved_requests += 1
            self.health[p].reserved_tokens += reserved

        async def fetch_one(pid, q):
            try:
                part_msgs = list(messages[:-1]) + [{"role": "user", "content": q}]
                text, in_t, out_t, total_ms = await self.call_provider(pid, part_msgs, task)
                self.cost.record(pid, task.task_type, in_t, out_t, 0.0, total_ms, total_ms, parallel=True)
                return text
            except Exception:
                return None

        try:
            results = await asyncio.gather(*[fetch_one(p, q) for p, q in zip(chosen, subs)])
        finally:
            for p in chosen:
                self.health[p].reserved_requests = max(0, self.health[p].reserved_requests - 1)
                self.health[p].reserved_tokens = max(0, self.health[p].reserved_tokens - reserved)

        parts = [r for r in results if r]
        if len(parts) >= 1:
            try:
                merged = await local_fast_fn("Synthesize these partial answers into one coherent answer:\n\n" + "\n---\n".join(parts))
                return merged if isinstance(merged, str) and merged.strip() else parts[0]
            except Exception:
                return parts[0]
        return await self.route(prompt, messages, task)

    async def single_turn(self, prompt, session_history) -> str:
        task = ClassifiedTask("quick", 300, False, False)
        msgs = list(session_history) + [{"role": "user", "content": prompt}]
        return await self.route(prompt, msgs, task)

    async def _idle_monitor(self):
        last_cache_purge = 0.0
        while True:
            try:
                await asyncio.sleep(300)
                now = time.time()
                if now - last_cache_purge >= 300:
                    self.cache.purge_expired()
                    last_cache_purge = now

                ram = psutil.virtual_memory().used / 1e9
                if ram > self.config.ram_guard_gb:
                    continue

                available = [pid for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3] if self._has_key(pid)]
                if not available:
                    continue

                probe_candidates = []
                for pid in available:
                    h = self.health[pid]
                    if h.breaker.state == "HALF_OPEN":
                        probe_candidates.append(pid)
                if not probe_candidates:
                    continue

                pid = probe_candidates[0]
                task = ClassifiedTask("quick", 20, False, False)
                msgs = [{"role": "user", "content": "Explain async/await in one short sentence."}]
                try:
                    text, in_t, out_t, total_ms = await self.call_provider(pid, msgs, task)
                    if isinstance(text, str) and text.strip():
                        self.health[pid].record_success(total_ms, in_t + out_t)
                    else:
                        self.health[pid].record_failure()
                except Exception:
                    self.health[pid].record_failure()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("idle_monitor_error %s", e)

    async def activate_key(self, provider, key) -> str:
        pid = (provider or "").upper().strip()
        if pid not in PROVIDERS_TIER2 and pid not in PROVIDERS_TIER3:
            return f"Unknown provider {provider}"
        meta = self._provider_meta(pid)
        key_field = meta.get("key_field")
        if not key_field:
            return f"{pid} does not require an API key."
        setattr(self.config, key_field, key)
        self.health[pid] = ProviderHealth(pid)
        logger.info("activate_key provider=%s", pid, extra={"log": "nina.security"})
        return f"✅ Key set for {pid}."

    def get_status(self) -> str:
        lines = ["Provider status:"]
        for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, *LOCAL_PROVIDERS]:
            h = self.health[pid]
            has_key = self._has_key(pid)
            state = "OK"
            if pid not in LOCAL_PROVIDERS and not has_key:
                state = "NO_KEY"
            elif h.breaker.state == "OPEN":
                state = f"OPEN {max(0, int(h.breaker.open_until - time.time()))}s"
            elif h.breaker.state == "HALF_OPEN":
                state = "HALF_OPEN"
            elif h.is_exhausted(pid):
                state = "EXHAUSTED"
            lines.append(
                f"{pid:<12} {state:<12} sr={h.success_rate():.0%} lat={int(h.avg_latency_ms())}ms "
                f"req={h.requests_today} tok={h.tokens_today}"
            )
        lines.append(f"Daily cost: ${self.cost.daily_cost_usd:.4f}")
        return "\n".join(lines)

    def reset_daily_counters(self):
        for h in self.health.values():
            h.reset_daily()
        self.cost.reset_daily()
