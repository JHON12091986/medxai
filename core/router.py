# core/router.py
import asyncio, hashlib, json, logging, re, time, uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, cast
import httpx, psutil
from core.config import NinaConfig, RATELIMITS
from tools import jules_api
from tools.model_discovery import ModelDiscoveryService
_ = jules_api

logger = logging.getLogger("nina.router")

# F-03f: Bangla Unicode block U+0980–U+09FF
_BANGLA_RE = re.compile(r'[\u0980-\u09FF]')
# Instruction-compliant providers in preference order for Bangla requests.
# GEMINI is first (best multilingual instruction-following).
# The normal scored chain is appended as fallback so nothing is ever lost.
_BANGLA_PREFERRED = ["GEMINI", "OPENAI", "MISTRAL", "CEREBRAS", "GROQ", "PERPLEXITY"]
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
    "GEMINI": {"base_url": "https://generativelanguage.googleapis.com", "model": "gemini-2.5-flash", "key_field": "gemini_api_key"},
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

class CircuitBreaker:
    FAILURE_THRESHOLD = 3
    WINDOW_S = 120
    RECOVERY_S = 60

    def __init__(self):
        self.state = "CLOSED"
        self.failures = deque()
        self.open_until = 0.0
        self.half_open_in_flight = False

    def _prune(self):
        now = time.time()
        while self.failures and now - self.failures[0] > self.WINDOW_S:
            self.failures.popleft()

    def allow_request(self) -> bool:
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
        self.failures.clear()
        self.state = "CLOSED"
        self.open_until = 0.0
        self.half_open_in_flight = False

    def record_failure(self, cooldown_s: Optional[float] = None):
        now = time.time()
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.open_until = now + (cooldown_s if cooldown_s is not None else self.RECOVERY_S)
            self.half_open_in_flight = False
            return
        self.failures.append(now)
        self._prune()
        if self.state == "CLOSED" and len(self.failures) >= self.FAILURE_THRESHOLD:
            self.state = "OPEN"
            self.open_until = now + (cooldown_s if cooldown_s is not None else self.RECOVERY_S)
            self.half_open_in_flight = False

    def set_cooldown(self, seconds: float):
        self.state = "OPEN"
        self.open_until = time.time() + max(1.0, float(seconds))
        self.half_open_in_flight = False

@dataclass
class ProviderHealth:
    provider_id: str
    success_count: int = 0
    failure_count: int = 0
    latencies: deque = field(default_factory=lambda: deque(maxlen=20))
    requests_today: int = 0
    tokens_today: int = 0
    last_request_ts: float = 0.0
    reserved_requests: int = 0
    reserved_tokens: int = 0
    cb: CircuitBreaker = field(default_factory=CircuitBreaker)

    @property
    def cooldown_until(self) -> float:
        return self.cb.open_until

    @property
    def degraded_until(self) -> float:
        return self.cb.open_until

    def avg_latency_ms(self) -> float:
        return sum(self.latencies) / len(self.latencies) if self.latencies else 999.0

    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total else 1.0

    def is_available(self, has_key: bool) -> bool:
        return has_key and self.cb.allow_request()

    def is_degraded(self) -> bool:
        return self.cb.state in ("OPEN", "HALF_OPEN")

    def is_near_limit(self, pid: str) -> bool:
        tpd = cast(dict, RATELIMITS).get(pid, {}).get("tpd")
        return bool(tpd and (self.tokens_today + self.reserved_tokens) > 0.8 * tpd)

    def is_exhausted(self, pid: str) -> bool:
        tpd = cast(dict, RATELIMITS).get(pid, {}).get("tpd")
        return bool(tpd and (self.tokens_today + self.reserved_tokens) >= tpd)

    def composite_score(self, pid: str) -> float:
        lat = min(self.avg_latency_ms() / 5000.0, 1.0)
        limit_penalty = 0.2 if self.is_near_limit(pid) else 0.0
        degraded_penalty = 0.25 if self.cb.state == "HALF_OPEN" else (0.5 if self.cb.state == "OPEN" else 0.0)
        return (self.success_rate() * 0.4) + ((1.0 - lat) * 0.4) + (0.2 - limit_penalty) - degraded_penalty

    def record_success(self, latency_ms: float, total_tokens: int):
        self.success_count += 1
        self.requests_today += 1
        self.tokens_today += max(0, int(total_tokens))
        self.last_request_ts = time.time()
        self.latencies.append(float(latency_ms))
        self.cb.record_success()

    def record_failure(self, cooldown_s: Optional[float] = None):
        self.failure_count += 1
        self.last_request_ts = time.time()
        self.cb.record_failure(cooldown_s=cooldown_s)

    def reset_daily(self):
        self.requests_today = 0
        self.tokens_today = 0
        self.reserved_requests = 0
        self.reserved_tokens = 0

@dataclass
class ClassifiedTask:
    task_type: str
    estimated_tokens: int
    is_parallel_candidate: bool
    is_sensitive: bool

async def classify_task(text: str, local_fast_fn) -> ClassifiedTask:
    try:
        raw = await local_fast_fn(
            f"Classify into one of {','.join(TASK_TYPES)}. Reply JSON only "
            f'{{"task_type":"general","estimated_tokens":500}} User Input: <text>{text[:500]}</text>'
        )
        data = json.loads(raw.strip())
        tt = data.get("task_type", "general")
        if tt not in TASK_TYPES:
            tt = "general"
        est = int(data.get("estimated_tokens", 500))
        est = max(50, min(est, 200000))
        return ClassifiedTask(tt, est, tt in ("research", "coding", "math") and est > 800, tt == "sensitive")
    except Exception:
        t = (text or "").lower()
        if any(k in t for k in ("password", "secret", "token", "private", "confidential", "bank", "account")):
            return ClassifiedTask("sensitive", 300, False, True)
        if any(k in t for k in ("code", "python", "bug", "traceback", "function", "class", "patch")):
            return ClassifiedTask("coding", 800, True, False)
        if any(k in t for k in ("research", "compare", "search", "latest", "find", "news")):
            return ClassifiedTask("research", 1200, True, False)
        if any(k in t for k in ("calculate", "equation", "math", "solve")):
            return ClassifiedTask("math", 700, False, False)
        logger.warning(f"nlp_classification_failed input={text[:80]!r} falling through to general task", extra={"log": "nina.log"})
        return ClassifiedTask("general", 500, False, False)

class ResponseCache:
    def __init__(self):
        self.s: dict = {}

    def _k(self, prompt: str, messages: list | None = None) -> str:
        ctx = prompt.strip().lower()
        if messages:
            ctx += "".join(f"{m.get('role','')}:{m.get('content','')}" for m in messages[-4:])
        return hashlib.sha256(ctx.encode("utf-8", errors="replace")).hexdigest()

    def get(self, prompt: str, tt: str, messages: list | None = None) -> Optional[str]:
        if CACHE_TTL.get(tt, 0) == 0:
            return None
        e = self.s.get(self._k(prompt, messages))
        return e["response"] if e and time.time() < e["expires_at"] else None

    def set(self, prompt: str, tt: str, response: str, provider: str, messages: list | None = None):
        if len(self.s) > 500:
            self.purge_expired()
        ttl = CACHE_TTL.get(tt, 0)
        if ttl:
            self.s[self._k(prompt, messages)] = {
                "response": response,
                "expires_at": time.time() + ttl,
                "provider": provider,
            }

    def clear(self):
        self.s.clear()

    def purge_expired(self):
        now = time.time()
        dead = []
        for k, v in list(self.s.items()):
            if now >= v["expires_at"]:
                dead.append(k)
        for k in dead:
            self.s.pop(k, None)

class CostTracker:
    def __init__(self):
        self.daily_cost_usd = 0.0
        self._rlog = logging.getLogger("nina.routerlog")

    def record(self, provider, tt, in_t, out_t, cost, ttf, total, parallel=False, cached=False, error=None, req_id=""):
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S.000+0600"),
            "req_id": req_id or "",
            "provider": provider,
            "task_type": tt,
            "input_tokens": int(in_t or 0),
            "output_tokens": int(out_t or 0),
            "cost_usd": float(cost or 0.0),
            "ttf_ms": int(ttf or 0),
            "total_ms": int(total or 0),
            "parallel": bool(parallel),
            "cached": bool(cached),
            "status": "success" if not error else "failure",
            "error": error or "",
        }
        try:
            self._rlog.info(json.dumps(row, ensure_ascii=False))
        except Exception:
            logger.info("routerlog_fallback %s", row)
        if not error:
            self.daily_cost_usd += float(cost or 0.0)

    def reset_daily(self):
        self.daily_cost_usd = 0.0

class HybridRouter:
    def __init__(self, config: NinaConfig):
        self.config = config
        self._model_discovery = ModelDiscoveryService(config)
        self.health: dict[str, ProviderHealth] = {}
        self.cache = ResponseCache()
        self.cost = CostTracker()
        self.http: Optional[httpx.AsyncClient] = None
        self._idle_task = None

    async def initialize(self):
        self.http = httpx.AsyncClient(timeout=60.0)
        for pid in [*PROVIDERS_TIER1, *PROVIDERS_TIER2, *PROVIDERS_TIER3, "LOCALFAST", "LOCALHEAVY"]:
            self.health[pid] = ProviderHealth(provider_id=pid)
        await self._discover_local_models()
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
        if self.http:
            await self.http.aclose()

    async def _discover_local_models(self):
        try:
            r = await asyncio.wait_for(self.http.get(f"{self.config.ollama_host}/api/tags"), timeout=5.0)
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            if not models:
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
            sorted_models = sorted(models, key=size_rank)
            LOCAL_PROVIDERS["LOCALFAST"]["model"] = sorted_models[0]
            LOCAL_PROVIDERS["LOCALHEAVY"]["model"] = sorted_models[-1]
            logger.info("local_models_discovered fast=%s heavy=%s", LOCAL_PROVIDERS["LOCALFAST"]["model"], LOCAL_PROVIDERS["LOCALHEAVY"]["model"])
        except Exception as e:
            logger.warning("local_model_discovery_failed %s", e)

    def _has_key(self, pid: str) -> bool:
        if pid in LOCAL_PROVIDERS or pid in PROVIDERS_TIER1:
            return True
        meta = cast(dict, (PROVIDERS_TIER2 | PROVIDERS_TIER3).get(pid, {}))
        kf = meta.get("key_field")
        key = getattr(self.config, kf, None) if kf else None
        return bool(key and str(key).strip())

    def _ordered_providers(self, task: ClassifiedTask, force_local: bool = False) -> list:
        if task.is_sensitive or force_local:
            return ["LOCALFAST", "LOCALHEAVY"]
        avail: list[str] = []
        degraded: list[str] = []
        for pid, h in self.health.items():
            if pid in LOCAL_PROVIDERS:
                continue
            if not self._has_key(pid) or h.is_exhausted(pid):
                continue
            if not h.is_available(True):
                continue
            (degraded if h.is_degraded() else avail).append(pid)
        sk = lambda p: self.health[p].composite_score(p)
        ordered = sorted(avail, key=sk, reverse=True) + sorted(degraded, key=sk, reverse=True)
        if "ONEBRAIN" in ordered:
            ordered.remove("ONEBRAIN")
            ordered.append("ONEBRAIN")
        if task.task_type in ("coding", "research", "document", "math", "multilingual"):
            return ordered + ["LOCALHEAVY", "LOCALFAST"]
        return ordered + ["LOCALFAST", "LOCALHEAVY"]

    async def _call_provider(self, pid: str, messages: list, task: ClassifiedTask):
        if self.http is None:
            raise RuntimeError('router_not_initialized')
        start = time.time()
        if pid in LOCAL_PROVIDERS:
            r = await self.http.post(
                f"{self.config.ollama_host}/api/chat",
                json={"model": LOCAL_PROVIDERS[pid]["model"], "messages": messages, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            d = cast(dict, r.json())
            return d["message"]["content"], 0, 0, (time.time() - start) * 1000

        meta = cast(dict, (PROVIDERS_TIER1 | PROVIDERS_TIER2 | PROVIDERS_TIER3)[pid]).copy()

        discovered_model = await self._model_discovery.get_model(pid)
        fallback = meta.get("model", "default")

        final_model = self.config.model_overrides.get(pid) or discovered_model or fallback
        meta["model"] = final_model
        base = meta["base_url"] or getattr(self.config, "onebrain_api_base", "")
        kf = meta.get("key_field")
        key = getattr(self.config, kf, None) if kf else "no-key"

        if pid == "GEMINI":
            gemini_contents = []
            for m in messages:
                c = m.get("content", "")
                if not c: continue
                role = "user" if m.get("role") in ("user", "system") else "model"
                gemini_contents.append({"role": role, "parts": [{"text": c}]})
            payload = {"contents": gemini_contents}
            r = await self.http.post(
                f"{base}/v1beta/models/{meta['model']}:generateContent?key={key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            if r.status_code == 429:
                retry_after = float(r.headers.get("retry-after", 60))
                self.health[pid].cb.set_cooldown(retry_after)
                raise httpx.HTTPStatusError(f"429 rate-limited retry-after={retry_after}s", request=r.request, response=r)
            r.raise_for_status()
            d = cast(dict, r.json())
            text = "".join(p.get("text", "") for p in d.get("candidates", [{}])[0].get("content", {}).get("parts", []))
            usage = d.get("usageMetadata", {})
            return text, int(usage.get("promptTokenCount", 0) or 0), int(usage.get("candidatesTokenCount", 0) or 0), (time.time() - start) * 1000

        r = await self.http.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": meta["model"], "messages": messages, "stream": False},
            timeout=60,
        )
        if r.status_code == 429:
            retry_after = float(r.headers.get("retry-after", 60))
            self.health[pid].cb.set_cooldown(retry_after)
            raise httpx.HTTPStatusError(f"429 rate-limited retry-after={retry_after}s", request=r.request, response=r)
        r.raise_for_status()
        d = cast(dict, r.json())
        u = d.get("usage", {})
        return d["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0), (time.time() - start) * 1000

    async def call_provider(self, pid: str, messages: list, task: ClassifiedTask):
        backoffs = [0.0, 1.0]
        last_exc: Exception | None = None
        for attempt, delay in enumerate(backoffs):
            if delay > 0:
                await asyncio.sleep(delay)
            try:
                return await self._call_provider(pid, messages, task)
            except asyncio.TimeoutError as e:
                last_exc = e
                if attempt == len(backoffs) - 1:
                    raise
            except httpx.HTTPStatusError as e:
                last_exc = e
                status = e.response.status_code if e.response else 0
                if status == 429:
                    raise
                if 500 <= status < 600 and attempt < len(backoffs) - 1:
                    continue
                raise
            except Exception as e:
                last_exc = e
                raise
        raise last_exc if last_exc else RuntimeError("provider call failed")

    async def route(self, prompt: str, messages: list, task: ClassifiedTask, force_local: bool = False) -> str:
        req_id = uuid.uuid4().hex[:8]
        cached = self.cache.get(prompt, task.task_type, messages)
        if cached:
            self.cost.record("CACHE", task.task_type, 0, 0, 0.0, 0, 0, cached=True, req_id=req_id)
            return cached

        # F-03f: Bangla detection — force instruction-compliant provider order.
        # Sensitive tasks always stay local regardless of language.
        if not force_local and not task.is_sensitive and _BANGLA_RE.search(prompt):
            normal_order = self._ordered_providers(task, force_local=False)
            # Build preferred list: available Bangla-preferred providers first,
            # then the normal scored order (deduplicated) as the full fallback chain.
            seen: set = set()
            bangla_order: list = []
            for pid in _BANGLA_PREFERRED:
                if pid in self.health and self._has_key(pid) and self.health[pid].cb.allow_request():
                    if pid not in seen:
                        bangla_order.append(pid)
                        seen.add(pid)
            for pid in normal_order:
                if pid not in seen:
                    bangla_order.append(pid)
                    seen.add(pid)
            logger.info(
                "bangla_route req_id=%s preferred=%s full_chain=%d",
                req_id, bangla_order[:3], len(bangla_order),
                extra={"log": "router.log"},
            )
            provider_order = bangla_order
        else:
            provider_order = self._ordered_providers(task, force_local)

        for pid in provider_order:
            h = self.health[pid]
            rl = cast(dict, RATELIMITS).get(pid, {})
            sp = rl.get("min_spacing_s", 0)
            if sp:
                w = sp - (time.time() - h.last_request_ts)
                if w > 0:
                    await asyncio.sleep(w)
            try:
                text, in_t, out_t, lat = await self.call_provider(pid, messages, task)
                h.record_success(lat, in_t + out_t)
                self.cost.record(pid, task.task_type, in_t, out_t, 0.0, lat, lat, req_id=req_id)
                self.cache.set(prompt, task.task_type, text, pid, messages)
                logger.info("router_success req_id=%s provider=%s task=%s ms=%s", req_id, pid, task.task_type, int(lat), extra={"log": "router.log"})
                return text
            except httpx.HTTPStatusError as e:
                cooldown_s = None
                if e.response is not None and e.response.status_code == 429:
                    try:
                        cooldown_s = float(e.response.headers.get("retry-after", 60))
                    except Exception:
                        cooldown_s = 60.0
                h.record_failure(cooldown_s=cooldown_s)
                self.cost.record(pid, task.task_type, 0, 0, 0.0, 0, 0, error=f"http_{e.response.status_code if e.response else 0}", req_id=req_id)
                logger.warning("router_fail req_id=%s provider=%s err=%s", req_id, pid, f"http_{e.response.status_code if e.response else 0}", extra={"log": "router.log"})
            except Exception as e:
                h.record_failure()
                self.cost.record(pid, task.task_type, 0, 0, 0.0, 0, 0, error=str(e)[:120], req_id=req_id)
                logger.warning("router_fail req_id=%s provider=%s err=%s", req_id, pid, str(e)[:120], extra={"log": "router.log"})

        logger.error("all_providers_failed req_id=%s task=%s", req_id, task.task_type, extra={"log": "router.log"})
        return "⚠️ All providers are currently unavailable. Try again in a moment, or send `status` to check provider health."

    async def parallel_route(self, prompt: str, messages: list, task: ClassifiedTask, local_fast_fn) -> str:
        if psutil.virtual_memory().used / 1e9 > self.config.ram_guard_gb:
            return await self.route(prompt, messages, task)

        cloud = [p for p in self._ordered_providers(task) if p not in LOCAL_PROVIDERS]
        if len(cloud) < 2:
            return await self.route(prompt, messages, task)

        try:
            raw = await local_fast_fn(f"Split into min({3},{len(cloud)}) independent sub-questions. JSON array only.\n{prompt}")
            subs = json.loads(raw.strip().removeprefix('```json').removesuffix('```').strip())
        except Exception:
            return await self.route(prompt, messages, task)

        if not isinstance(subs, list):
            return await self.route(prompt, messages, task)
        subs = [str(s).strip() for s in subs if str(s).strip()][:3]
        if not subs:
            return await self.route(prompt, messages, task)

        chosen = cloud[:len(subs)]
        reserved = max(1, task.estimated_tokens // max(1, len(chosen)))
        for p in chosen:
            self.health[p].reserved_requests += 1
            self.health[p].reserved_tokens += reserved

        async def fetch(pid, q):
            try:
                t, i, o, la = await asyncio.wait_for(
                    self.call_provider(pid, messages[:-1] + [{"role": "user", "content": q}], task), 45.0
                )
                self.health[pid].record_success(la, i + o)
                return t
            except Exception:
                self.health[pid].record_failure()
                return None

        try:
            results = await asyncio.gather(*[fetch(p, q) for p, q in zip(chosen, subs)])
        finally:
            for p in chosen:
                self.health[p].reserved_requests = max(0, self.health[p].reserved_requests - 1)
                self.health[p].reserved_tokens = max(0, self.health[p].reserved_tokens - reserved)

        parts = [r for r in results if r]
        if len(parts) >= 1:
            try:
                merged = await local_fast_fn("Synthesize these answers:\n" + "\n---\n".join(parts))
                return merged if isinstance(merged, str) and merged.strip() else parts[0]
            except Exception:
                return parts[0]
        return await self.route(prompt, messages, task)

    async def single_turn(self, prompt: str, session_history: list) -> str:
        msgs = session_history + [{"role": "user", "content": prompt}]
        return await self.route(prompt, msgs, ClassifiedTask("quick", 300, False, False))

    async def _idle_monitor(self):
        last_cache_purge = 0.0
        while True:
            try:
                await asyncio.sleep(300)
                now = time.time()
                if now - last_cache_purge >= 300:
                    self.cache.purge_expired()
                    last_cache_purge = now

                if psutil.virtual_memory().used / 1e9 > self.config.ram_guard_gb:
                    continue

                half_open = [p for p in self.health if p not in LOCAL_PROVIDERS and self._has_key(p) and self.health[p].cb.state == "HALF_OPEN"]
                if not half_open:
                    continue

                pid = half_open[0]
                try:
                    _, _, _, lat = await asyncio.wait_for(
                        self.call_provider(pid, [{"role": "user", "content": "Explain async/await in one short sentence."}], ClassifiedTask("quick", 20, False, False)),
                        15.0,
                    )
                    self.health[pid].record_success(lat, 10)
                except Exception:
                    self.health[pid].record_failure()
                    logger.warning("quality_probe_fail provider=%s marked degraded", pid)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("idle_monitor_error %s", e)

    async def activate_key(self, provider: str, key: str) -> str:
        meta = cast(dict, (PROVIDERS_TIER2 | PROVIDERS_TIER3).get(provider) or {})
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
            logger.warning("activate_key persist failed %s", e)
        logger.info("activate_key provider=%s persisted", provider, extra={"log": "nina.security"})
        self.health[provider] = ProviderHealth(provider_id=provider)
        return f"✅ Key set for {provider}."

    def reset_daily_counters(self):
        for h in self.health.values():
            h.reset_daily()
        self.cost.reset_daily()

    def get_status(self) -> str:
        lines = ["Router  Provider Status"]
        for pid, h in sorted(self.health.items()):
            hk = self._has_key(pid)
            state = (
                "available" if h.is_available(hk) and not h.is_exhausted(pid)
                else "exhausted" if h.is_exhausted(pid)
                else f"cb:{h.cb.state}" if hk
                else "no key"
            )
            lines.append(
                f"{pid:<14} {state:<18} score={h.composite_score(pid):.2f}"
                f" lat={h.avg_latency_ms():.0f}ms sr={h.success_rate()*100:.0f}%"
                f" tok={h.tokens_today}"
            )
        lines.append(f"  today ${self.cost.daily_cost_usd:.4f}")
        return "\n".join(lines)
