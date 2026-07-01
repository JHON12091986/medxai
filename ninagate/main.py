# =============================================================================
# SYNC NOTE — Delta Sync Protocol (see docs/space/DELTA_SYNC_PROTOCOL.md)
# This file is the NinaGate HTTP service process. It is intentionally
# isolated from core/ imports (except core.config and core.task_classifier)
# so it survives a nina core crash.  Changes to routing primitives
# (CircuitBreaker, ProviderHealth, cache key strategy) must be reflected
# here manually per the Delta Sync Protocol.
#
# Last delta sync: 2026-06-25  by Perplexity relay
#   + telemetry pass-4: span_id injected at proxy_chat_completions entry
#   + emit("ninagate", "request_in")  at entry
#   + emit("ninagate", "cache_hit")   on cache serve
#   + emit("ninagate", "response_out") in _make_provider_response
#   + emit("ninagate", "error")        on 503 exhausted
# Previous delta syncs:
#   2026-06-21 by Perplexity relay
#   + HALF_OPEN state logging added to CircuitBreaker
#   + consecutive_failures counter added to ProviderHealth
#   + 429 → 5-min cooldown with Telegram-ready log added
#   + MockRequest removed — /v1/responses now calls proxy_chat_completions directly
#   + QuotaManager simplified — single Gemini counter only, no multi-provider pretense
#   + flat CACHE_TTL dict removed (superseded by ResponseSessionStore.TTL_BY_TASK)
# =============================================================================
import re
import asyncio
import json
import logging
import os
import time
import datetime
import hashlib
import uuid
from pathlib import Path
from collections import deque
from contextlib import asynccontextmanager

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
import psutil
from watchfiles import awatch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import load_config
from core.task_classifier import classify_task

# telemetry pass-4: JSONL emitter — import with graceful fallback
try:
    from telemetry.emitter import emit as _telem_emit
except Exception:
    def _telem_emit(stage, event, payload, span_id=None):  # null-object fallback
        pass

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ninagate")

# Load environment variables from NINA's .env file (with .env.local override if exists)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
_local_env = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(_local_env):
    load_dotenv(dotenv_path=_local_env, override=True)

PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), "providers.json")
providers = []
available_models_cache = [{"id": "auto", "object": "model", "owned_by": "ninagate"}]

def write_log(entry, log_path=None):
    """Appends a log entry to the specified JSON log file."""
    if log_path is None:
        log_path = Path(__file__).parent.parent / "logs" / "ninagate.log"
    else:
        log_path = Path(log_path)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry["ts"] = datetime.datetime.now().isoformat()
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write log: {e}")


# ---------------------------------------------------------------------------
# Response Caching
# SYNC NOTE: uses SHA256 payload key + atomic tmp→rename (ported from core/router.py)
# ---------------------------------------------------------------------------
class ResponseCache:
    def __init__(self, cache_file):
        self.cache_file = Path(cache_file)
        self.cache = {}
        self.load()

    def _make_key(self, payload):
        key_payload = payload.copy()
        key_payload.pop("stream", None)
        key_payload.pop("stream_options", None)
        key_payload.pop("cache_control", None)
        serialized = json.dumps(key_payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, payload):
        key = self._make_key(payload)
        entry = self.cache.get(key)
        if entry:
            if time.time() < entry["expires_at"]:
                return entry
            else:
                self.cache.pop(key, None)
                self.save()
        return None

    def set(self, payload, response_data, ttl, provider):
        if ttl <= 0:
            return
        key = self._make_key(payload)
        self.cache[key] = {
            "response_data": response_data,
            "expires_at": time.time() + ttl,
            "provider": provider
        }
        if len(self.cache) > 1000:
            self.purge_expired()
        self.save()

    def purge_expired(self):
        now = time.time()
        expired = [k for k, v in self.cache.items() if now >= v["expires_at"]]
        for k in expired:
            self.cache.pop(k, None)
        self.save()

    def load(self):
        if not self.cache_file.exists():
            return
        try:
            self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            self.purge_expired()
        except Exception as e:
            logger.warning(f"Failed to load ninagate cache: {e}")

    def save(self):
        """Atomic write: tmp → rename to prevent cache corruption on crash."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.cache), encoding="utf-8")
            tmp.replace(self.cache_file)
        except Exception as e:
            logger.warning(f"Failed to save ninagate cache: {e}")


# Cache TTL is now driven entirely by ResponseSessionStore.TTL_BY_TASK.
# The flat CACHE_TTL dict is removed — it was a source of confusion.
# Lookup: CACHE_TTL[task_type] → ResponseSessionStore.TTL_BY_TASK[task_type]

NINAGATE_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ninagate_cache.json")
response_cache = ResponseCache(NINAGATE_CACHE_FILE)


# ---------------------------------------------------------------------------
# Responses API Session Store
# ---------------------------------------------------------------------------
class ResponseSessionStore:
    """
    Persists Responses API conversation threads across turns.
    Maps response_id -> { messages, ts, task_type, turn_count }

    TTL is tiered by task complexity:
      SIMPLE  -> 1800s  (30 min)
      MEDIUM  -> 7200s  (2 hours)
      COMPLEX -> 43200s (12 hours)
      MASSIVE -> 43200s (12 hours)
      default -> 7200s  (2 hours)

    Cache TTL reuse:
      ResponseCache.set() uses these same TTL values when storing
      completions responses, ensuring session and cache lifetimes align.
    """
    TTL_BY_TASK = {
        "SIMPLE": 1800,
        "MEDIUM": 7200,
        "COMPLEX": 43200,
        "MASSIVE": 43200,
    }
    DEFAULT_TTL = 7200
    MAX_SESSIONS = 500
    EVICT_COUNT = 100

    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        self._sessions: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        self._load()

    def _load(self):
        if not self.store_path.exists():
            logger.info("session_store: no store file yet — starting fresh")
            return
        try:
            raw = json.loads(self.store_path.read_text(encoding="utf-8"))
            now = time.time()
            self._sessions = {}
            for k, v in raw.items():
                ttl = self.TTL_BY_TASK.get(v.get("task_type", ""), self.DEFAULT_TTL)
                if now - v.get("ts", 0) < ttl:
                    self._sessions[k] = v
            logger.info(
                f"session_store: loaded {len(self._sessions)} active sessions"
                f" (discarded {len(raw) - len(self._sessions)} expired)"
            )
        except Exception as e:
            logger.warning(f"session_store load failed: {e}")

    def _save_sync(self):
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.store_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._sessions), encoding="utf-8")
            tmp.replace(self.store_path)
        except Exception as e:
            logger.warning(f"session_store save failed: {e}")

    async def _save(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_sync)

    def get_messages(self, response_id: str) -> list | None:
        entry = self._sessions.get(response_id)
        if not entry:
            return None
        ttl = self.TTL_BY_TASK.get(entry.get("task_type", ""), self.DEFAULT_TTL)
        if time.time() - entry["ts"] >= ttl:
            self._sessions.pop(response_id, None)
            return None
        return entry["messages"]

    def get_session_info(self, response_id: str) -> dict | None:
        entry = self._sessions.get(response_id)
        if not entry:
            return None
        ttl = self.TTL_BY_TASK.get(entry.get("task_type", ""), self.DEFAULT_TTL)
        age = time.time() - entry["ts"]
        if age >= ttl:
            self._sessions.pop(response_id, None)
            return None
        return {
            "response_id": response_id,
            "turn_count": entry.get("turn_count", 1),
            "task_type": entry.get("task_type", "unknown"),
            "message_count": len(entry["messages"]),
            "age_seconds": round(age),
            "ttl_seconds": ttl,
            "expires_in_seconds": round(ttl - age),
        }

    async def save_session(self, response_id: str, messages: list, task_type: str = "", turn_count: int = 1):
        async with self._lock:
            self._sessions[response_id] = {
                "messages": messages,
                "ts": time.time(),
                "task_type": task_type,
                "turn_count": turn_count,
            }
            if len(self._sessions) > self.MAX_SESSIONS:
                oldest = sorted(self._sessions, key=lambda k: self._sessions[k]["ts"])
                for k in oldest[:self.EVICT_COUNT]:
                    del self._sessions[k]
                logger.info(f"session_store: evicted {self.EVICT_COUNT} oldest sessions")
            await self._save()

    @staticmethod
    def new_response_id() -> str:
        return f"resp_{uuid.uuid4().hex[:24]}"


SESSION_STORE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "ninagate_sessions.json"
)
response_session_store = ResponseSessionStore(SESSION_STORE_FILE)


# ---------------------------------------------------------------------------
# Health, Circuit Breaking, and Scoring
# SYNC NOTE: CircuitBreaker now mirrors core/router.py HALF_OPEN semantics:
#   - HALF_OPEN → OPEN on test failure (logged explicitly)
#   - HALF_OPEN → CLOSED on success (logged explicitly)
#   - consecutive_failures added to ProviderHealth for degradation detection
#   - 429 forces 300s cooldown (same as core/router.py)
# ---------------------------------------------------------------------------
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_s=60):
        self.state = "CLOSED"
        self.failures = deque()
        self.open_until = 0.0
        self.failure_threshold = failure_threshold
        self.recovery_s = recovery_s
        self._provider_name = "unknown"  # set by ProviderHealth on init

    def allow_request(self):
        now = time.time()
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if now >= self.open_until:
                self.state = "HALF_OPEN"
                logger.info(f"{self._provider_name} CB: OPEN → HALF_OPEN (recovery window elapsed)")
                return True
            return False
        return True  # HALF_OPEN allows 1 probe request

    def record_success(self):
        if self.state == "HALF_OPEN":
            logger.info(f"{self._provider_name} CB: HALF_OPEN → CLOSED (probe succeeded)")
        self.failures.clear()
        self.state = "CLOSED"

    def record_failure(self, cooldown_s=None):
        now = time.time()
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.open_until = now + (cooldown_s or self.recovery_s)
            logger.warning(f"{self._provider_name} CB: HALF_OPEN → OPEN (probe failed)")
            return
        self.failures.append(now)
        while self.failures and now - self.failures[0] > 120:
            self.failures.popleft()
        if len(self.failures) >= self.failure_threshold:
            self.state = "OPEN"
            self.open_until = now + (cooldown_s or self.recovery_s)
            logger.warning(f"{self._provider_name} CB: CLOSED → OPEN ({len(self.failures)} failures in window)")


class ProviderHealth:
    def __init__(self, name):
        self.name = name
        self.success_count = 0
        self.failure_count = 0
        self.consecutive_failures = 0  # DELTA: degradation detector (from core/router.py)
        self.latencies = deque(maxlen=10)
        self.cb = CircuitBreaker()
        self.cb._provider_name = name  # bind name for CB log messages

    def avg_latency(self):
        return sum(self.latencies) / len(self.latencies) if self.latencies else 2000.0

    def success_rate(self):
        total = self.success_count + self.failure_count
        return self.success_count / total if total else 1.0

    def score(self):
        lat_score = max(0.0, 1.0 - (self.avg_latency() / 5000.0))
        penalty = 0.3 if self.cb.state == "HALF_OPEN" else 0.0
        return (self.success_rate() * 0.5) + (lat_score * 0.5) - penalty

    def record_success(self):
        self.success_count += 1
        self.consecutive_failures = 0
        self.latencies.append(time.time())  # timestamp placeholder; latency set in forward_to_provider
        self.cb.record_success()

    def record_failure(self, cooldown_s=None):
        self.failure_count += 1
        self.consecutive_failures += 1
        if self.consecutive_failures == 3:
            logger.warning(f"{self.name}: 3 consecutive failures — provider degraded, routing to fallback")
        self.cb.record_failure(cooldown_s)


# ---------------------------------------------------------------------------
# Quota Manager — simplified to Gemini-only counter
# SYNC NOTE: multi-provider quota tracking removed. core/quota/ handles that.
# This class is kept only to preserve the quota_soft_limit check for Gemini.
# ---------------------------------------------------------------------------
class QuotaManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.quotas = {"gemini": 0}
        self.last_reset = 0.0
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.quotas = data.get("quotas", {"gemini": 0})
                    self.last_reset = data.get("last_reset", 0.0)
                self.check_reset()
            except Exception:
                pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w") as f:
                json.dump({"quotas": self.quotas, "last_reset": self.last_reset}, f)
        except Exception:
            pass

    def check_reset(self):
        now = time.time()
        now_dt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
        reset_hour = 7  # 7AM UTC = 1PM BD
        last_reset_dt = datetime.datetime.fromtimestamp(self.last_reset, datetime.timezone.utc)
        recent_reset = now_dt.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        if now_dt < recent_reset:
            recent_reset -= datetime.timedelta(days=1)
        if last_reset_dt < recent_reset:
            for k in self.quotas:
                self.quotas[k] = 0
            self.last_reset = now
            self.save()

    def increment(self, provider):
        self.check_reset()
        provider_key = provider.lower()
        if provider_key not in self.quotas:
            self.quotas[provider_key] = 0
        self.quotas[provider_key] += 1
        asyncio.get_event_loop().run_in_executor(None, self.save)

    def is_available(self, provider, limit=900):
        self.check_reset()
        return self.quotas.get(provider.lower(), 0) < limit


QUOTA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "quota_state.json")
quota_manager = QuotaManager(QUOTA_FILE)
from ninagate.supply_ledger import SupplyLedger

health_tracker = {}

# --- Local Ollama Health Contract (INFRA-001) ---
_local_healthy: bool = False
_local_last_checked: float = 0.0
_LOCAL_HEALTH_TTL: int = 300
_LOCAL_HEALTH_URL: str = "http://localhost:11434/api/tags"


async def _check_local_health() -> bool:
    """Probe Ollama /api/tags with 3s timeout. Result cached for _LOCAL_HEALTH_TTL seconds."""
    global _local_healthy, _local_last_checked
    now = time.monotonic()
    if now - _local_last_checked < _LOCAL_HEALTH_TTL:
        return _local_healthy
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(_LOCAL_HEALTH_URL)
            _local_healthy = (r.status_code == 200)
    except Exception:
        _local_healthy = False
    _local_last_checked = now
    return _local_healthy


def load_providers():
    global providers
    try:
        with open(PROVIDERS_FILE, "r") as f:
            providers = json.load(f)
        for p in providers:
            if p["name"] not in health_tracker:
                health_tracker[p["name"]] = ProviderHealth(p["name"])
        logger.info(f"Loaded {len(providers)} providers")
    except Exception as e:
        logger.error(f"Failed to load providers: {e}")


async def watch_providers():
    load_providers()
    async for changes in awatch(PROVIDERS_FILE):
        load_providers()


async def fetch_models_background():
    global available_models_cache
    while True:
        models = [{"id": "auto", "object": "model", "owned_by": "ninagate"}]
        for p in providers:
            api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
            if p.get("api_key_env") is not None and not api_key:
                continue
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            url = f"{p['base_url']}/models"
            try:
                resp = await http_client.get(url, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    for m in resp.json().get("data", []):
                        if "id" in m:
                            models.append({"id": f"{p['name']}/{m['id']}", "object": "model", "owned_by": p["name"]})
            except Exception:
                pass
        available_models_cache = models
        await asyncio.sleep(600)


http_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client, _local_healthy
    http_client = httpx.AsyncClient(
        http2=True,
        timeout=httpx.Timeout(60.0, connect=3.0),
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=40,
            keepalive_expiry=30.0,
        ),
        headers={"User-Agent": "NinaGate/1.0"},
    )
    _local_healthy = await _check_local_health()
    logger.info(f"ninagate: startup local_health={_local_healthy}")
    watcher_task = asyncio.create_task(watch_providers())
    model_fetch_task = asyncio.create_task(fetch_models_background())

    ledger = SupplyLedger(health_tracker)
    ledger_task = asyncio.create_task(ledger.run_loop())

    async def hb_loop():
        from tools.heartbeat import write_heartbeat
        while True:
            await asyncio.sleep(60)
            write_heartbeat("ninagate.service")
    hb_task = asyncio.create_task(hb_loop())

    yield
    watcher_task.cancel()
    model_fetch_task.cancel()
    ledger_task.cancel()
    hb_task.cancel()
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
from ninagate.circuit_breaker import CircuitBreaker as _CB
_circuit_breaker = _CB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def stream_response(
    response: httpx.Response,
    h: ProviderHealth,
    start_time: float,
    cache_info: dict = None,
):
    chunks: list[bytes] = [] if cache_info else None
    first_chunk = True
    try:
        async for chunk in response.aiter_bytes():
            if first_chunk:
                ttft_ms = (time.time() - start_time) * 1000
                logger.debug(f"stream TTFT={ttft_ms:.0f}ms provider={cache_info['name'] if cache_info else 'unknown'}")
                first_chunk = False
            if chunks is not None:
                chunks.append(chunk)
            yield chunk
        h.record_success()
        h.latencies.append((time.time() - start_time) * 1000)
    finally:
        await response.aclose()

    if cache_info and chunks:
        try:
            body_str = b"".join(chunks).decode("utf-8", errors="replace")
            ttl = response_session_store.TTL_BY_TASK.get(cache_info.get("task_type", "MEDIUM"),
                                                          response_session_store.DEFAULT_TTL)
            response_cache.set(cache_info["payload"], body_str, ttl, cache_info["name"])
        except Exception as e:
            logger.warning(f"stream_cache_write failed: {e}")


@app.get("/v1/models")
@app.get("/genai/v1/models")
async def list_models():
    return JSONResponse(status_code=200, content={"object": "list", "data": available_models_cache})


@app.get("/health")
async def health():
    local_ok = await _check_local_health()
    return {"status": "ok", "local_ollama": local_ok, "timestamp": time.time()}


@app.get("/v1/status")
async def get_status():
    status_data = []
    for p in providers:
        name = p["name"]
        h = health_tracker.get(name)
        api_key_env = p.get("api_key_env")
        if api_key_env:
            has_key = bool(os.getenv(api_key_env))
            key_status = "Active" if has_key else "Missing key"
        else:
            has_key = True
            key_status = "Active"
        cb_state = h.cb.state if h else "CLOSED"
        avg_lat = h.avg_latency() if h else 0.0
        success_rate = h.success_rate() if h else 1.0
        req_today = quota_manager.quotas.get(name.lower(), 0)
        status_data.append({
            "name": name,
            "tier": p.get("tier", 2),
            "model": p.get("model", "unknown"),
            "active": has_key,
            "key_status": key_status,
            "cb_state": cb_state,
            "consecutive_failures": h.consecutive_failures if h else 0,
            "avg_latency_ms": round(avg_lat, 1),
            "success_rate": round(success_rate * 100, 1),
            "requests_today": req_today
        })
    return JSONResponse(status_code=200, content=status_data)


# ---------------------------------------------------------------------------
# Session Debug Endpoints
# ---------------------------------------------------------------------------

@app.get("/v1/sessions/{response_id}")
async def get_session(response_id: str):
    info = response_session_store.get_session_info(response_id)
    if info is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Session '{response_id}' not found or expired"}
        )
    return JSONResponse(status_code=200, content=info)


@app.get("/v1/sessions")
async def list_sessions():
    now = time.time()
    result = []
    for resp_id, entry in list(response_session_store._sessions.items()):
        ttl = response_session_store.TTL_BY_TASK.get(
            entry.get("task_type", ""), response_session_store.DEFAULT_TTL
        )
        age = now - entry.get("ts", now)
        if age < ttl:
            result.append({
                "response_id": resp_id,
                "turn_count": entry.get("turn_count", 1),
                "task_type": entry.get("task_type", "unknown"),
                "message_count": len(entry.get("messages", [])),
                "age_seconds": round(age),
                "expires_in_seconds": round(ttl - age),
            })
    result.sort(key=lambda x: x["age_seconds"])
    return JSONResponse(status_code=200, content={"sessions": result, "total": len(result)})


# ---------------------------------------------------------------------------
# Helpers for /v1/responses
# ---------------------------------------------------------------------------

def _parse_input_item(item: dict) -> dict | None:
    role = item.get("role", "user")
    content = item.get("content")
    if isinstance(content, list):
        parts = [
            p["text"] for p in content
            if isinstance(p, dict) and p.get("type") in ("input_text", "text") and "text" in p
        ]
        content = "\n".join(parts)
    if content is None:
        return None
    return {"role": role, "content": content}


def _build_responses_output(comp_data: dict) -> tuple[list, str]:
    output = []
    assistant_text = ""
    choices = comp_data.get("choices", [])
    if choices:
        choice = choices[0]
        message = choice.get("message", {})
        msg_content = message.get("content", "")
        assistant_text = msg_content or ""
        tool_calls = message.get("tool_calls", [])
        output_parts = []
        if msg_content:
            output_parts.append({"type": "output_text", "text": msg_content})
        output.append({
            "id": "out_0",
            "type": "message",
            "status": "completed",
            "content": output_parts
        })
        for idx, tc in enumerate(tool_calls):
            func = tc.get("function", {})
            output.append({
                "id": f"tc_{tc.get('id', idx)}",
                "type": "function_call",
                "status": "completed",
                "function_call": {
                    "id": tc.get("id"),
                    "name": func.get("name"),
                    "arguments": func.get("arguments")
                }
            })
    return output, assistant_text


_TASK_TYPE_ALIASES: dict[str, str] = {
    "quick":   "SIMPLE",
    "simple":  "SIMPLE",
    "medium":  "MEDIUM",
    "complex": "COMPLEX",
    "massive": "MASSIVE",
    "deep":    "COMPLEX",
    "large":   "COMPLEX",
    "fast":    "SIMPLE",
    "local":   "SIMPLE",
}


def _classify_safe(messages: list) -> str:
    try:
        last_content = messages[-1].get("content", "") if messages else ""
        classified = classify_task(text=last_content, messages=messages)
        raw = (classified.task_type or "").strip()
        normalised = _TASK_TYPE_ALIASES.get(raw.lower(), raw.upper())
        logger.debug(f"_classify_safe: raw={raw!r} -> normalised={normalised!r}")
        return normalised
    except Exception as exc:
        logger.warning(f"_classify_safe fallback to MEDIUM: {exc}")
        return "MEDIUM"


# ---------------------------------------------------------------------------
# /v1/responses — Stateful Responses API shim
# ---------------------------------------------------------------------------

@app.post("/v1/responses")
@app.post("/genai/v1/responses")
async def proxy_responses(request: Request):
    """
    OpenAI Responses API adapter with full multi-turn session support.
    MockRequest removed — delegates directly to proxy_chat_completions internals.
    """
    try:
        responses_payload = await request.json()
        logger.info(
            f"/v1/responses model={responses_payload.get('model')} "
            f"prev_id={responses_payload.get('previous_response_id')}"
        )
    except Exception as e:
        logger.error(f"/v1/responses JSON parse error: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    messages: list[dict] = []
    if "instructions" in responses_payload:
        messages.append({"role": "system", "content": responses_payload["instructions"]})

    prev_id = responses_payload.get("previous_response_id")
    prior_turn_count = 0
    if prev_id:
        prior_messages = response_session_store.get_messages(prev_id)
        if prior_messages:
            prior_carry = [m for m in prior_messages if m.get("role") != "system"] if messages else list(prior_messages)
            messages.extend(prior_carry)
            prior_info = response_session_store.get_session_info(prev_id)
            prior_turn_count = prior_info.get("turn_count", 1) if prior_info else 1
            logger.info(f"session resume: prev_id={prev_id} +{len(prior_carry)} msgs turn={prior_turn_count}")
        else:
            logger.warning(f"session resume: prev_id={prev_id} NOT FOUND — starting fresh")

    for item in responses_payload.get("input", []):
        item_type = item.get("type", "")
        if item_type == "function_call_output":
            messages.append({
                "role": "tool",
                "tool_call_id": item.get("call_id", ""),
                "content": str(item.get("output", "")),
            })
        else:
            msg = _parse_input_item(item)
            if msg:
                messages.append(msg)

    chat_payload = {
        k: responses_payload[k]
        for k in ["model", "stream", "temperature", "top_p", "max_tokens", "tools"]
        if k in responses_payload
    }
    chat_payload["messages"] = messages
    # _is_stream = chat_payload.get("stream", False)
    new_resp_id = response_session_store.new_response_id()

    # Direct internal call — no MockRequest needed
    # from starlette.testclient import _TestClientTransport  # noqa: F401 — existence check
    # Build a minimal Request with the chat_payload as body
    from starlette.requests import Request as StarletteRequest
    # from starlette.datastructures import Headers
    body_bytes = json.dumps(chat_payload).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/chat/completions",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
    }
    internal_request = StarletteRequest(scope, receive)
    comp_response = await proxy_chat_completions(internal_request)

    if isinstance(comp_response, JSONResponse):
        try:
            comp_data = json.loads(comp_response.body.decode("utf-8"))
        except Exception as e:
            logger.error(f"/v1/responses: failed to parse completions JSON: {e}")
            return comp_response

        output, assistant_text = _build_responses_output(comp_data)
        task_type = _classify_safe(messages)
        session_messages = messages + [{"role": "assistant", "content": assistant_text}]
        await response_session_store.save_session(
            new_resp_id, session_messages, task_type=task_type, turn_count=prior_turn_count + 1,
        )
        logger.info(f"session saved: id={new_resp_id} turns={prior_turn_count + 1} task={task_type}")
        return JSONResponse(
            status_code=comp_response.status_code,
            content={
                "id": new_resp_id,
                "object": "response",
                "created": comp_data.get("created", int(time.time())),
                "model": comp_data.get("model", chat_payload.get("model", "unknown")),
                "output": output,
                "usage": comp_data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
            }
        )

    if isinstance(comp_response, StreamingResponse):
        accumulated_text: list[str] = []

        async def translate_and_persist_stream():
            try:
                iterator = getattr(comp_response, "body_iterator", None) or \
                           getattr(comp_response, "aiter_bytes", lambda: None)()
                if iterator is None:
                    return
                async for chunk in iterator:
                    chunk_str = chunk.decode("utf-8", errors="replace")
                    for line in chunk_str.split("\n"):
                        if not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            assistant_text = "".join(accumulated_text)
                            task_type = _classify_safe(messages)
                            session_messages = messages + [{"role": "assistant", "content": assistant_text}]
                            asyncio.create_task(
                                response_session_store.save_session(
                                    new_resp_id, session_messages,
                                    task_type=task_type, turn_count=prior_turn_count + 1,
                                )
                            )
                            yield b"data: [DONE]\n\n"
                        else:
                            try:
                                data_json = json.loads(data_str)
                                delta_content = (
                                    data_json.get("choices", [{}])[0]
                                    .get("delta", {}).get("content", "")
                                )
                                if delta_content:
                                    accumulated_text.append(delta_content)
                                    event_data = json.dumps({
                                        "response_id": new_resp_id,
                                        "delta": {"text": delta_content},
                                    })
                                    yield (
                                        f"event: response.content_part.delta\n"
                                        f"data: {event_data}\n\n"
                                    ).encode("utf-8")
                            except Exception:
                                pass
            except Exception as stream_err:
                logger.error(f"/v1/responses stream error: {stream_err}")

        return StreamingResponse(
            translate_and_persist_stream(),
            status_code=comp_response.status_code,
            media_type="text/event-stream",
        )

    return comp_response


# ---------------------------------------------------------------------------
# DULAL Post-Processor and Security Pre-Filter helpers
# ---------------------------------------------------------------------------

def strip_dulal_preamble(text: str) -> str:
    """Remove any text before the first code fence."""
    match = re.search(r"```", text)
    if match:
        return text[match.start():]
    return text  # no fence found — return as-is

async def stream_response_dulal_stripped(original_generator):
    buffered_text = ""
    seen_fence = False
    async for chunk in original_generator:
        if seen_fence:
            yield chunk
            continue
        try:
            chunk_str = chunk.decode("utf-8", errors="replace")
        except Exception:
            yield chunk
            continue
        for line in chunk_str.splitlines():
            if line.startswith("data: "):
                data_content = line[6:]
                if data_content.strip() == "[DONE]":
                    continue
                try:
                    data_json = json.loads(data_content)
                    delta_content = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    buffered_text += delta_content
                except Exception:
                    pass
        if "```" in buffered_text:
            seen_fence = True
            start_idx = buffered_text.find("```")
            stripped_text = buffered_text[start_idx:]
            fake_data = {
                "id": "chatcmpl-dulal",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "dulal",
                "choices": [{
                    "index": 0,
                    "delta": {"content": stripped_text},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(fake_data)}\n\n".encode("utf-8")
        else:
            pass
    if not seen_fence:
        fake_data = {
            "id": "chatcmpl-dulal",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "dulal",
            "choices": [{
                "index": 0,
                "delta": {"content": buffered_text},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(fake_data)}\n\n".encode("utf-8")
        yield b"data: [DONE]\n\n"

SECURITY_KEYWORDS = {".env", "api_key", "secret", "password", "token", "credential"}

def is_security_probe(prompt: str) -> bool:
    lower = prompt.lower()
    return any(kw in lower for kw in SECURITY_KEYWORDS)

def make_security_block_response(is_stream: bool):
    if is_stream:
        async def stream_block():
            fake_data = {
                "id": "chatcmpl-security-block",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "dulal",
                "choices": [{
                    "index": 0,
                    "delta": {"content": "SECURITY_BLOCK"},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(fake_data)}\n\n".encode("utf-8")
            yield b"data: [DONE]\n\n"
        return StreamingResponse(stream_block(), media_type="text/event-stream")
    else:
        return JSONResponse(status_code=200, content={
            "id": "chatcmpl-security-block",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "dulal",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "SECURITY_BLOCK"},
                "finish_reason": "stop"
            }]
        })

# ---------------------------------------------------------------------------
# /v1/chat/completions — Main proxy
# SYNC NOTE: 429 handling now forces 300s cooldown (mirrors core/router.py)
# telemetry pass-4: span_id generated at entry; emit request_in/cache_hit/
#                   response_out/error events into telemetry.jsonl
# ---------------------------------------------------------------------------

@app.post("/v1/chat/completions")
@app.post("/genai/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    config = load_config()
    # telemetry pass-4: generate span_id at entry — propagated to all emit() calls
    _t0 = time.time()
    _span_id = str(uuid.uuid4())[:8]

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    is_stream = payload.get("stream", False)
    target_provider_name = None
    target_model = None
    messages = payload.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if last_msg.get("role") == "user" and isinstance(last_msg.get("content"), str):
            match = re.search(r'^/model\s+([^\s]+)', last_msg["content"])
            if match:
                model_str = match.group(1)
                if "," in model_str:
                    target_provider_name, target_model = model_str.split(",", 1)
                else:
                    target_provider_name = model_str
                last_msg["content"] = last_msg["content"].replace(match.group(0), "", 1).lstrip()
                if target_model:
                    payload["model"] = target_model

    classified = classify_task(
        text=messages[-1].get("content", "") if messages else "",
        messages=messages
    )
    task_type = classified.task_type
    recommended_tier = classified.recommended_tier

    if "max_tokens" not in payload and classified.max_tokens_cap:
        payload["max_tokens"] = classified.max_tokens_cap

    # telemetry pass-4: emit request_in
    _telem_emit("ninagate", "request_in", {
        "task_type": task_type,
        "stream": is_stream,
        "model": payload.get("model", "auto"),
        "target_provider": target_provider_name,
        "msg_count": len(messages),
    }, span_id=_span_id)

    elapsed_wait = 0
    wait_interval = 2
    max_wait = 15  # Limit wait time to prevent blocking uvicorn

    while True:
        if await request.is_disconnected():
            logger.warning("Client disconnected while waiting for inference route.")
            return JSONResponse(status_code=499, content={"error": "Client disconnected"})

        cloud_providers = []
        local_providers = []
        for p in providers:
            if target_provider_name and p.get("name").upper() != target_provider_name.upper():
                continue
            if not target_provider_name and p.get("name").lower() in quota_manager.quotas:
                if not quota_manager.is_available(p["name"]):
                    continue
            api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
            if p.get("api_key_env") is not None and not api_key:
                continue
            h = health_tracker[p["name"]]
            if target_provider_name or h.cb.allow_request():
                entry = (h.score(), p, api_key, h)
                if p.get("name").lower() in ("ollama", "dulal"):
                    local_providers.append(entry)
                else:
                    cloud_providers.append(entry)

        def get_tier_boost(provider_name):
            name_upper = provider_name.upper()
            if recommended_tier == "LOCAL" and name_upper in ("OLLAMA", "DULAL"): return 2.0
            if recommended_tier == "FAST" and name_upper in ("CEREBRAS", "GROQ"): return 2.0
            if recommended_tier == "DEEP" and name_upper in ("DEEPSEEK", "MISTRAL"): return 2.0
            if recommended_tier == "LARGE" and name_upper == "GEMINI": return 2.0
            return 0.0

        cloud_providers.sort(key=lambda x: x[0] + get_tier_boost(x[1]["name"]), reverse=True)

        if not cloud_providers and not local_providers:
            logger.error("No active/configured providers available to route request.")
            break

        quota_ok = quota_manager.is_available("gemini", limit=config.quota_soft_limit)
        force_local = not quota_ok and not target_provider_name
        if force_local:
            logger.warning(f"Quota soft-limit reached ({config.quota_soft_limit}). Forcing local routing.")

        def _make_provider_response(response, h, start, name, task_type, escalated=False):
            total_ms = (time.time() - start) * 1000
            ttl = response_session_store.TTL_BY_TASK.get(task_type, response_session_store.DEFAULT_TTL)
            if is_stream:
                write_log({"provider": name, "total_ms": total_ms, "cached": False,
                           "task_type": task_type, "escalated": escalated})
                # telemetry pass-4: stream response_out
                _telem_emit("ninagate", "response_out", {
                    "provider": name,
                    "task_type": task_type,
                    "latency_ms": round(total_ms, 1),
                    "stream": True,
                    "escalated": escalated,
                    "cached": False,
                }, span_id=_span_id)
                cache_info = None
                if not target_provider_name and ttl > 0:
                    cache_info = {"payload": payload, "ttl": ttl, "name": name, "task_type": task_type}
                gen = stream_response(response, h, start, cache_info)
                if name.lower() == "dulal":
                    gen = stream_response_dulal_stripped(gen)
                return StreamingResponse(
                    gen,
                    status_code=response.status_code,
                    media_type="text/event-stream"
                )
            data = response.json()
            h.record_success()
            if name.lower() == "dulal" and "choices" in data:
                for choice in data["choices"]:
                    if "message" in choice and "content" in choice["message"]:
                        choice["message"]["content"] = strip_dulal_preamble(choice["message"]["content"])
            usage = data.get("usage", {})
            write_log({
                "provider": name,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_ms": total_ms,
                "cached": False,
                "task_type": task_type,
                "escalated": escalated,
            })
            # telemetry pass-4: non-stream response_out
            _telem_emit("ninagate", "response_out", {
                "provider": name,
                "task_type": task_type,
                "latency_ms": round(total_ms, 1),
                "stream": False,
                "escalated": escalated,
                "cached": False,
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
            }, span_id=_span_id)
            if not target_provider_name:
                response_cache.set(payload, data, ttl, name)
            return JSONResponse(status_code=response.status_code, content=data)

        # Cache lookup
        if not target_provider_name:
            cached_entry = response_cache.get(payload)
            if cached_entry:
                resp_data = cached_entry["response_data"]
                prov_name = cached_entry["provider"]
                logger.info(f"Cache HIT: serving from {prov_name}")
                # telemetry pass-4: cache_hit event
                _telem_emit("ninagate", "cache_hit", {
                    "provider": prov_name,
                    "task_type": task_type,
                    "stream": is_stream,
                }, span_id=_span_id)
                if is_stream:
                    async def stream_cached():
                        chunk_size = 1024
                        data_bytes = resp_data.encode("utf-8", errors="replace")
                        for i in range(0, len(data_bytes), chunk_size):
                            yield data_bytes[i:i+chunk_size]
                            await asyncio.sleep(0.005)
                    write_log({"provider": prov_name, "total_ms": 0, "cached": True, "task_type": task_type})
                    return StreamingResponse(stream_cached(), status_code=200, media_type="text/event-stream")
                else:
                    usage = resp_data.get("usage", {}) if isinstance(resp_data, dict) else {}
                    write_log({"provider": prov_name, "input_tokens": usage.get("prompt_tokens", 0),
                               "output_tokens": usage.get("completion_tokens", 0),
                               "total_ms": 0, "cached": True, "task_type": task_type})
                    return JSONResponse(status_code=200, content=resp_data)

        # Security pre-filter before any prompt reaches DULAL
        is_dulal_dest = False
        if target_provider_name and target_provider_name.upper() == "DULAL":
            is_dulal_dest = True
        elif not target_provider_name:
            is_simple = (task_type == "SIMPLE" or force_local)
            is_medium = (task_type == "MEDIUM")
            has_local = bool(local_providers)
            if (is_simple or is_medium) and has_local:
                is_dulal_dest = True
            elif has_local:
                is_dulal_dest = True

        if is_dulal_dest:
            prompt_text = messages[-1].get("content", "") if messages else ""
            if is_security_probe(prompt_text):
                logger.warning("Security probe targeting DULAL provider detected. Blocking request.")
                return make_security_block_response(is_stream)

        # Real-time thermal safeguard
        local_allowed = True
        if local_providers and not target_provider_name:
            try:
                from tools.system import is_thermal_safe
                local_allowed, thermal_msg = await is_thermal_safe(cpu_limit=90, gpu_limit=88)
                if not local_allowed:
                    logger.warning(f"Local inference bypassed: {thermal_msg}")
            except Exception as e:
                logger.warning(f"Failed to run thermal safeguard: {e}")

        # Flag to track if any provider was successfully forwarded to
        # found_usable_route = False

        if (task_type == "SIMPLE" or force_local) and local_providers and not target_provider_name and local_allowed:
            if not await _check_local_health():
                logger.warning("local Ollama unhealthy — routing SIMPLE to cloud fallback")
            else:
                local_response, lh, l_start, l_name = await forward_to_provider(payload, local_providers, is_stream)
                if local_response:
                    return _make_provider_response(local_response, lh, l_start, l_name, task_type)
                logger.warning("SIMPLE: local unavailable, falling back to cloud")

        elif task_type == "MEDIUM" and local_providers and not target_provider_name and local_allowed:
            if not await _check_local_health():
                logger.warning("local Ollama unhealthy — routing MEDIUM directly to cloud")
            else:
                local_response, lh, l_start, l_name = await forward_to_provider(payload, local_providers, is_stream)
                if local_response:
                    return _make_provider_response(local_response, lh, l_start, l_name, task_type)
            cloud_response, ch, c_start, c_name = await forward_to_provider(payload, cloud_providers, is_stream)
            if cloud_response:
                return _make_provider_response(cloud_response, ch, c_start, c_name, task_type, escalated=True)
            logger.warning("MEDIUM: local and cloud providers exhausted")

        else:
            cloud_response, ch, c_start, c_name = await forward_to_provider(payload, cloud_providers, is_stream)
            if cloud_response:
                return _make_provider_response(cloud_response, ch, c_start, c_name, task_type)
            if local_providers and local_allowed:
                local_response, lh, l_start, l_name = await forward_to_provider(payload, local_providers, is_stream)
                if local_response:
                    logger.warning("COMPLEX: cloud failed, using local fallback")
                    return _make_provider_response(local_response, lh, l_start, l_name, task_type, escalated=True)
                logger.warning("COMPLEX: cloud and local fallback exhausted")

        # If we got here, all tried options for this loop iteration failed/exhausted.
        if elapsed_wait < max_wait:
            logger.warning(
                f"No healthy/usable provider routes found or thermal safeguards active for {task_type} task. "
                f"Retrying in {wait_interval}s... (elapsed wait: {elapsed_wait}s/{max_wait}s)"
            )
            await asyncio.sleep(wait_interval)
            elapsed_wait += wait_interval
            wait_interval = min(wait_interval * 2, 8)
        else:
            break

    # telemetry pass-4: full exhaustion error
    _telem_emit("ninagate", "error", {
        "reason": "all providers exhausted",
        "task_type": task_type,
        "latency_ms": round((time.time() - _t0) * 1000, 1),
    }, span_id=_span_id)
    return JSONResponse(status_code=503, content={"error": "All providers exhausted"})


async def forward_to_provider(payload, providers_to_try, is_stream):
    for score, provider, api_key, h in providers_to_try:
        provider_name = provider["name"]
        provider_name_lower = provider_name.lower()
        base_url = provider.get("base_url")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        provider_payload = payload.copy()
        if provider.get("model"):
            provider_payload["model"] = provider["model"]
        elif provider_name_lower in ("ollama", "dulal") and "model" not in provider_payload:
            provider_payload["model"] = "dulal"

        if provider_name_lower == "gemini":
            provider_payload.pop("stream_options", None)
            provider_payload.pop("cache_control", None)
        elif provider_name_lower == "groq":
            provider_payload.pop("stream_options", None)

        url = f"{base_url}/chat/completions"
        for attempt in range(2):
            try:
                start_time = time.time()
                req = http_client.build_request("POST", url, json=provider_payload, headers=headers)
                response = await http_client.send(req, stream=is_stream)

                if response.status_code >= 400:
                    if response.status_code == 429:
                        # DELTA: 429 → 5-min hard cooldown (mirrors core/router.py)
                        retry_after = float(response.headers.get("retry-after", 300))
                        cooldown = max(retry_after, 300.0)
                        h.record_failure(cooldown_s=cooldown)
                        logger.warning(
                            f"429 from {provider_name}: forcing {cooldown:.0f}s cooldown"
                        )
                        await response.aclose()
                        break
                    elif 500 <= response.status_code < 600 and attempt == 0:
                        await response.aclose()
                        await asyncio.sleep(1.0)
                        continue
                    await response.aclose()
                    h.record_failure()
                    break

                quota_manager.increment(provider_name)
                return response, h, start_time, provider_name
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(1.0)
                    continue
                h.record_failure()
                break
    return None, None, None, None


@app.websocket("/v1/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'router.log')
    last_pos = 0
    try:
        while True:
            if not hasattr(websocket_telemetry, '_cached_cpu'):
                websocket_telemetry._cached_cpu = psutil.cpu_percent(interval=None)
                websocket_telemetry._cached_time = time.time()
            else:
                now = time.time()
                if now - websocket_telemetry._cached_time > 2.0:
                    websocket_telemetry._cached_cpu = psutil.cpu_percent(interval=None)
                    websocket_telemetry._cached_time = now
            metrics = {
                "cpu_percent": websocket_telemetry._cached_cpu,
                "gpu_memory_used_mb": 0,
                "router_events": []
            }
            try:
                proc = await asyncio.create_subprocess_exec(
                    "nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits",
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=2.0)
                if proc.returncode == 0:
                    metrics["gpu_memory_used_mb"] = int(stdout.decode().strip())
            except Exception:
                pass
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        f.seek(0, 2)
                        current_size = f.tell()
                        if current_size < last_pos:
                            last_pos = 0
                        if current_size > last_pos:
                            f.seek(last_pos)
                            new_lines = f.readlines()
                            last_pos = current_size
                            for line in new_lines:
                                try:
                                    metrics["router_events"].append(json.loads(line))
                                except json.JSONDecodeError:
                                    metrics["router_events"].append({"raw": line.strip()})
                except Exception as e:
                    logger.error(f"Error reading router.log: {e}")
            await websocket.send_json(metrics)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info("Telemetry WebSocket disconnected")
    except Exception as e:
        logger.error(f"Telemetry WebSocket error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
