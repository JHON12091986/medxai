"""
NINA v12 — HybridRouter V4  (Stage 2)
"""

import asyncio, hashlib, json, logging, time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx, psutil

from core.config import NinaConfig, RATELIMITS

logger = logging.getLogger("nina.router")

PROVIDERS_TIER1 = {
    "POLLINATIONS": {"base_url": "https://text.pollinations.ai/openai", "model": "mistral",    "key_field": None},
    "CHUTES":       {"base_url": "https://llm.chutes.ai/v1",            "model": "deepseek-r1","key_field": None},
    "HFPUBLIC":     {"base_url": "https://api-inference.huggingface.co","model": "various",    "key_field": None},
}
PROVIDERS_TIER2 = {
    "CEREBRAS":   {"base_url": "https://api.cerebras.ai/v1",                "model": "llama-3.3-70b",           "key_field": "cerebras_api_key"},
    "GROQ":       {"base_url": "https://api.groq.com/openai/v1",            "model": "llama-3.3-70b-versatile", "key_field": "groq_api_key"},
    "MISTRAL":    {"base_url": "https://api.mistral.ai/v1",                 "model": "mistral-large-latest",    "key_field": "mistral_api_key"},
    "DEEPSEEK":   {"base_url": "https://api.deepseek.com/v1",               "model": "deepseek-chat",           "key_field": "deepseek_api_key"},
    "GEMINI":     {"base_url": "https://generativelanguage.googleapis.com", "model": "gemini-1.5-pro",          "key_field": "gemini_api_key"},
    "TOGETHER":   {"base_url": "https://api.together.xyz/v1",               "model": "llama-3.1-405b",          "key_field": "together_api_key"},
    "COHERE":     {"base_url": "https://api.cohere.ai/v2",                  "model": "command-r-plus",          "key_field": "cohere_api_key"},
    "FIREWORKS":  {"base_url": "https://api.fireworks.ai/inference/v1",     "model": "llama-v3p1-405b",         "key_field": "fireworks_api_key"},
    "XAI":        {"base_url": "https://api.x.ai/v1",                      "model": "grok-beta",               "key_field": "xai_api_key"},
    "PERPLEXITY": {"base_url": "https://api.perplexity.ai",                 "model": "sonar-pro",               "key_field": "perplexity_api_key"},
    "SAMBANOVA":  {"base_url": "https://api.sambanova.ai/v1",               "model": "Meta-Llama-3.1-405B",     "key_field": "sambanova_api_key"},
    "HYPERBOLIC": {"base_url": "https://api.hyperbolic.xyz/v1",             "model": "llama-3.1-405b",          "key_field": "hyperbolic_api_key"},
    "NOVITA":     {"base_url": "https://api.novita.ai/v3/openai",           "model": "llama-3.1-70b",           "key_field": "novita_api_key"},
    "OPENAI":     {"base_url": "https://api.openai.com/v1",                 "model": "gpt-4o-mini",             "key_field": "openai_api_key"},
    "ONEBRAIN":   {"base_url": None,                                        "model": "default",                 "key_field": "one_brain_api_key"},
}
PROVIDERS_TIER3 = {
    "OPENROUTER": {"base_url": "https://openrouter.ai/api/v1", "model": "auto", "key_field": "openrouter_api_key"},
}
LOCAL_PROVIDERS = {
    "LOCALFAST":  {"model": "qwen2.5:1.5b"},
    "LOCALHEAVY": {"model": "qwen2.5:7b"},
}
TASK_TYPES   = ["sensitive","coding","research","math","multilingual","document","vision","quick","general"]
STEP_BUDGETS = {"quick":3,"general":5,"multilingual":5,"math":6,"coding":8,"document":8,"research":10,"sensitive":5}
DEFAULT_MAX_STEPS = 5
CACHE_TTL = {"sensitive":0,"quick":3600,"research":1800,"coding":21600,"document":14400,"general":7200,"math":21600,"multilingual":7200}


@dataclass
class ProviderHealth:
    provider_id: str
    success_count: int = 0
    failure_count: int = 0
    latencies: deque = field(default_factory=lambda: deque(maxlen=20))
    requests_today: int = 0
    tokens_today: int = 0
    cooldown_until: float = 0.0
    degraded_until: float = 0.0
    last_request_ts: float = 0.0
    reserved_requests: int = 0
    reserved_tokens: int = 0

    def avg_latency_ms(self):
        return sum(self.latencies)/len(self.latencies) if self.latencies else 999.0
    def success_rate(self):
        t = self.success_count + self.failure_count
        return self.success_count/t if t else 1.0
    def is_available(self, has_key):
        return has_key and time.time() > self.cooldown_until
    def is_degraded(self):
        return time.time() < self.degraded_until
    def is_near_limit(self, pid):
        tpd = RATELIMITS.get(pid,{}).get("tpd")
        return bool(tpd and self.tokens_today >= 0.8*tpd)
    def is_exhausted(self, pid):
        tpd = RATELIMITS.get(pid,{}).get("tpd")
        return bool(tpd and self.tokens_today >= tpd)
    def is_spacing_blocked(self, pid):
        s = RATELIMITS.get(pid,{}).get("min_spacing_s",0)
        return bool(s and (time.time()-self.last_request_ts) < s)
    def composite_score(self, pid):
        lat = min(self.avg_latency_ms()/5000.0,1.0)
        return self.success_rate()*0.4 + (1.0-lat)*0.4 + (0.0 if self.is_near_limit(pid) else 1.0)*0.2
    def record_success(self, latency_ms, tokens):
        self.success_count+=1; self.latencies.append(latency_ms)
        self.requests_today+=1; self.tokens_today+=tokens; self.last_request_ts=time.time()
    def record_failure(self):
        self.failure_count+=1
        self.cooldown_until = time.time()+(1800 if self.failure_count>=3 else 300)
    def reset_daily(self):
        self.requests_today=0; self.tokens_today=0


@dataclass
class ClassifiedTask:
    task_type: str
    estimated_tokens: int
    is_parallel_candidate: bool
    is_sensitive: bool


async def classify_task(text: str, local_fast_fn) -> ClassifiedTask:
    try:
        raw = await local_fast_fn(
            f"Classify into one of: {','.join(TASK_TYPES)}. "
            f"Reply JSON only: {{\"task_type\":\"...\",\"estimated_tokens\":N}}\nRequest: {text[:500]}")
        d = json.loads(raw.strip())
        tt = d.get("task_type","general")
        if tt not in TASK_TYPES: tt = "general"
        est = int(d.get("estimated_tokens",500))
        return ClassifiedTask(tt, est, tt in ("research","coding","math") and est>800, tt=="sensitive")
    except Exception:
        logger.warning(f"nlp_classification_failed input={text[:80]!r} falling_through_to_generaltask", extra={"log":"nina.log"})
        return ClassifiedTask("general",500,False,False)


class ResponseCache:
    def __init__(self): self._s: dict = {}
    def _k(self, p): return hashlib.sha256(p.strip().lower().encode()).hexdigest()
    def get(self, prompt, tt):
        if CACHE_TTL.get(tt,0)==0: return None
        e=self._s.get(self._k(prompt))
        return e["response"] if e and time.time()<e["expires_at"] else None
    def set(self, prompt, tt, response, provider):
        if len(self.s) > 500:
            self.purge_expired()
        ttl=CACHE_TTL.get(tt,0)
        if ttl: self._s[self._k(prompt)]={"response":response,"expires_at":time.time()+ttl,"provider":provider}
    def clear(self): self._s.clear()
    def purge_expired(self):
        now = time.time()
        dead = [k for k,v in self._s.items() if now >= v["expires_at"]]
        for k in dead: self._s.pop(k, None)


class CostTracker:
    def __init__(self): self.daily_cost_usd=0.0; self._rlog=logging.getLogger("nina.router_log")
    def record(self, provider, tt, in_t, out_t, cost, ttf, total, parallel=False, cached=False, error=None):
        self._rlog.info(json.dumps({"ts":time.strftime("%Y-%m-%dT%H:%M:%S.000+0600"),
            "provider":provider,"task_type":tt,"input_tokens":in_t,"output_tokens":out_t,
            "cost_usd":cost,"ttf_ms":ttf,"total_ms":total,"parallel":parallel,"cached":cached,
            "status":"success" if not error else "failure","error":error}))
        if not error: self.daily_cost_usd+=cost
    def reset_daily(self): self.daily_cost_usd=0.0


class HybridRouter:
    def __init__(self, config: NinaConfig):
        self.config=config; self.health: dict[str,ProviderHealth]={}
        self.cache=ResponseCache(); self.cost=CostTracker()
        self._http: Optional[httpx.AsyncClient]=None; self._idle_task=None

    async def initialize(self):
        self._http=httpx.AsyncClient(timeout=60.0)
        for pid in list(PROVIDERS_TIER1)+list(PROVIDERS_TIER2)+list(PROVIDERS_TIER3)+["LOCALFAST","LOCALHEAVY"]:
            self.health[pid]=ProviderHealth(provider_id=pid)
        self._idle_task=asyncio.create_task(self._idle_monitor())
        logger.info("HybridRouter V4 initialized")

    async def close(self):
        if self._idle_task: self._idle_task.cancel()
        if self._http: await self._http.aclose()

    def _has_key(self, pid):
        if pid in LOCAL_PROVIDERS or pid in PROVIDERS_TIER1: return True
        meta=(PROVIDERS_TIER2|PROVIDERS_TIER3).get(pid,{})
        kf=meta.get("key_field")
        return bool(kf and getattr(self.config,kf,None))

    def _ordered_providers(self, task: ClassifiedTask, force_local=False):
        if task.is_sensitive or force_local: return ["LOCALFAST"]
        avail,deg=[],[]
        for pid,h in self.health.items():
            if pid in LOCAL_PROVIDERS: continue
            if not self._has_key(pid) or h.is_exhausted(pid) or not h.is_available(True): continue
            (deg if h.is_degraded() else avail).append(pid)
        sk=lambda p: self.health[p].composite_score(p)
        ordered=sorted(avail,key=sk,reverse=True)+sorted(deg,key=sk,reverse=True)
        if "ONEBRAIN" in ordered: ordered.remove("ONEBRAIN"); ordered.append("ONEBRAIN")
        return ordered+["LOCALFAST"]

    async def _call_provider(self, pid, messages, task):
        start=time.time()
        if pid in LOCAL_PROVIDERS:
            r=await self._http.post(f"{self.config.ollama_host}/api/chat",
                json={"model":LOCAL_PROVIDERS[pid]["model"],"messages":messages,"stream":False},timeout=60)
            r.raise_for_status()
            return r.json()["message"]["content"],0,0,(time.time()-start)*1000
        meta=(PROVIDERS_TIER1|PROVIDERS_TIER2|PROVIDERS_TIER3)[pid]
        base=meta["base_url"] or getattr(self.config,"one_brain_api_base","")
        kf=meta.get("key_field"); key=getattr(self.config,kf,None) if kf else "no-key"
        r=await self._http.post(f"{base}/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":meta["model"],"messages":messages,"stream":False},timeout=60)
        r.raise_for_status()
        d=r.json(); u=d.get("usage",{})
        return d["choices"][0]["message"]["content"],u.get("prompt_tokens",0),u.get("completion_tokens",0),(time.time()-start)*1000

    async def route(self, prompt, messages, task: ClassifiedTask, force_local=False):
        cached=self.cache.get(prompt,task.task_type)
        if cached: self.cost.record("CACHE",task.task_type,0,0,0,0,0,cached=True); return cached
        for pid in self._ordered_providers(task,force_local):
            h=self.health[pid]; rl=RATELIMITS.get(pid,{})
            sp=rl.get("min_spacing_s",0)
            if sp:
                w=sp-(time.time()-h.last_request_ts)
                if w>0: await asyncio.sleep(w)
            try:
                text,in_t,out_t,lat=await self._call_provider(pid,messages,task)
                h.record_success(lat,in_t+out_t)
                self.cost.record(pid,task.task_type,in_t,out_t,0.0,lat,lat)
                self.cache.set(prompt,task.task_type,text,pid)
                return text
            except asyncio.TimeoutError:
                h.record_failure(); self.cost.record(pid,task.task_type,0,0,0,0,0,error="timeout")
            except Exception as e:
                h.record_failure(); self.cost.record(pid,task.task_type,0,0,0,0,0,error=str(e)[:80])
        failed = list(self.ordered_providers(task, forcelocal))
        logger.error(f"allprovidersfailed task={task.tasktype} tried={failed}")
        return (
            "\u26a0\ufe0f All providers are currently unavailable. "
            "Try again in a moment, or send /status to check provider health."
        )

    async def parallel_route(self, prompt, messages, task: ClassifiedTask, local_fast_fn):
        if psutil.virtual_memory().used/1e9 >= self.config.ram_guard_gb:
            return await self.route(prompt,messages,task)
        cloud=[p for p in self._ordered_providers(task) if p not in LOCAL_PROVIDERS]
        if len(cloud)<2: return await self.route(prompt,messages,task)
        try:
            raw=await local_fast_fn(f"Split into {min(3,len(cloud))} independent sub-questions. JSON array only.\nTask: {prompt}")
            subs=json.loads(raw)
        except Exception: return await self.route(prompt,messages,task)
        chosen=cloud[:len(subs)]
        for p in chosen: self.health[p].reserved_requests+=1; self.health[p].reserved_tokens+=task.estimated_tokens//len(chosen)
        async def fetch(pid,q):
            try:
                t,i,o,l=await asyncio.wait_for(self._call_provider(pid,messages[:-1]+[{"role":"user","content":q}],task),45.0)
                self.health[pid].record_success(l,i+o); return t
            except Exception: self.health[pid].record_failure(); return None
        results=await asyncio.gather(*[fetch(p,q) for p,q in zip(chosen,subs)])
        for p in chosen: self.health[p].reserved_requests=0; self.health[p].reserved_tokens=0
        parts=[r for r in results if r]
        if not parts: return await self.route(prompt,messages,task)
        return await local_fast_fn("Synthesize these answers:\n\n"+"---\n".join(parts))

    async def single_turn(self, prompt, session_history):
        msgs=session_history+[{"role":"user","content":prompt}]
        return await self.route(prompt,msgs,ClassifiedTask("quick",300,False,False))

    async def _idle_monitor(self):
        while True:
            await asyncio.sleep(300)
            if psutil.virtual_memory().used/1e9 >= self.config.ram_guard_gb: continue
            cloud=[p for p in self.health if p not in LOCAL_PROVIDERS and self._has_key(p)]
            if not cloud: continue
            pid=min(cloud,key=lambda p: self.health[p].composite_score(p))
            try:
                _,_,_,lat=await asyncio.wait_for(self._call_provider(pid,[{"role":"user","content":"Reply: OK"}],ClassifiedTask("quick",10,False,False)),15.0)
                self.health[pid].record_success(lat,10)
            except Exception:
                self.health[pid].degraded_until=time.time()+1800
                logger.warning(f"quality_probe_fail provider={pid} marked DEGRADED")


    async def activate_key(self, provider: str, key: str) -> str:
        meta = (PROVIDERS_TIER2 | PROVIDERS_TIER3).get(provider)
        if not meta:
            return f"Unknown provider: {provider}"
        kf = meta.get("key_field")
        if not kf:
            return f"{provider} does not use an API key."
        setattr(self.config, kf, key)
        self.health[provider] = ProviderHealth(provider_id=provider)
        return f"✅ Key set for {provider}."
    def reset_daily_counters(self):
        [h.reset_daily() for h in self.health.values()]; self.cost.reset_daily()

    def get_status(self):
        lines=["**Router V4 — Provider Status**\n"]
        for pid,h in sorted(self.health.items()):
            state="✅" if h.is_available(self._has_key(pid)) and not h.is_exhausted(pid) else ("⛔ exhausted" if h.is_exhausted(pid) else "❌ no key")
            lines.append(f"{pid:<14} {state:<18} score={h.composite_score(pid):.2f} lat={h.avg_latency_ms():.0f}ms sr={h.success_rate()*100:.0f}% tok={h.tokens_today}")
        lines.append(f"\nCost today: ${self.cost.daily_cost_usd:.4f}")
        return "\n".join(lines)
