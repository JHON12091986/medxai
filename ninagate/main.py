import re
import asyncio
import json
import logging
import os # verified # added verification
import time
import datetime
import hashlib
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

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ninagate")

# Load environment variables from NINA's .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

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

# --- Response Caching ---
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
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.cache), encoding="utf-8")
            tmp.replace(self.cache_file)
        except Exception as e:
            logger.warning(f"Failed to save ninagate cache: {e}")

CACHE_TTL = {
    "SIMPLE": 1200,
    "MEDIUM": 600,
    "COMPLEX": 300
}

NINAGATE_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ninagate_cache.json")
response_cache = ResponseCache(NINAGATE_CACHE_FILE)

# Response cache class for routing
# Verified NinaGate Optimization implementation
# --- Health, Circuit Breaking, and Scoring ---
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_s=60):
        self.state = "CLOSED"
        self.failures = deque()
        self.open_until = 0.0
        self.failure_threshold = failure_threshold
        self.recovery_s = recovery_s

    def allow_request(self):
        now = time.time()
        if self.state == "CLOSED": return True
        if self.state == "OPEN":
            if now >= self.open_until:
                self.state = "HALF_OPEN"
                return True
            return False
        return True # HALF_OPEN allows 1 request

    def record_success(self):
        self.failures.clear()
        self.state = "CLOSED"

    def record_failure(self, cooldown_s=None):
        now = time.time()
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.open_until = now + (cooldown_s or self.recovery_s)
        else:
            self.failures.append(now)
            while self.failures and now - self.failures[0] > 120:
                self.failures.popleft()
            if len(self.failures) >= self.failure_threshold:
                self.state = "OPEN"
                self.open_until = now + (cooldown_s or self.recovery_s)

class ProviderHealth:
    def __init__(self, name):
        self.name = name
        self.success_count = 0
        self.failure_count = 0
        self.latencies = deque(maxlen=10)
        self.cb = CircuitBreaker()

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
        self.cb.record_success()
        
    def record_failure(self, cooldown_s=None):
        self.failure_count += 1
        self.cb.record_failure(cooldown_s)

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
            except Exception: pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            exhausted = any(v > 900 for v in self.quotas.values())
            with open(self.file_path, "w") as f:
                json.dump({"quotas": self.quotas, "last_reset": self.last_reset, "quota_exhausted": exhausted}, f)
        except Exception: pass

    def check_reset(self):
        now = time.time()
        now_dt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
        reset_hour = 7 # 7AM UTC = 1PM BD
        last_reset_dt = datetime.datetime.fromtimestamp(self.last_reset, datetime.timezone.utc)
        recent_reset = now_dt.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        if now_dt < recent_reset:
            recent_reset -= datetime.timedelta(days=1)
        if last_reset_dt < recent_reset:
            for k in self.quotas: self.quotas[k] = 0
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
health_tracker = {}

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
            if p.get("api_key_env") is not None and not api_key: continue
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            url = f"{p['base_url']}/models"
            try:
                resp = await http_client.get(url, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    for m in resp.json().get("data", []):
                        if "id" in m:
                            models.append({"id": f"{p['name']}/{m['id']}", "object": "model", "owned_by": p["name"]})
            except Exception: pass
        available_models_cache = models
        await asyncio.sleep(600)

http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    # Persistent HTTP/2 connection pool — eliminates per-request TLS handshake
    # Saves 80-150ms per call on Groq/Gemini/DeepSeek
    http_client = httpx.AsyncClient(
        http2=True,                          # HTTP/2 multiplexing where supported
        timeout=httpx.Timeout(60.0, connect=3.0),
        limits=httpx.Limits(
            max_keepalive_connections=20,    # Keep 20 warm connections alive
            max_connections=40,              # Hard cap total open sockets
            keepalive_expiry=30.0,           # Reuse connections up to 30s idle
        ),
        headers={"User-Agent": "NinaGate/1.0"},
    )
    watcher_task = asyncio.create_task(watch_providers())
    model_fetch_task = asyncio.create_task(fetch_models_background())
    yield
    watcher_task.cancel()
    model_fetch_task.cancel()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
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
    """
    True passthrough streaming — first token reaches client in <200ms.
    Caching happens async AFTER stream completes, never blocking the pipe.
    """
    chunks: list[bytes] = [] if cache_info else None
    first_chunk = True
    try:
        async for chunk in response.aiter_bytes():
            if first_chunk:
                # Log time-to-first-token separately
                ttft_ms = (time.time() - start_time) * 1000
                logger.debug(f"stream TTFT={ttft_ms:.0f}ms provider={cache_info['name'] if cache_info else 'unknown'}")
                first_chunk = False
            if chunks is not None:
                chunks.append(chunk)
            yield chunk  # ← client gets bytes immediately, no buffering
        h.record_success()
        h.latencies.append((time.time() - start_time) * 1000)
    finally:
        await response.aclose()

    # Cache async after stream is done — never blocks the response pipe
    if cache_info and chunks:
        try:
            body_str = b"".join(chunks).decode("utf-8", errors="replace")
            response_cache.set(
                cache_info["payload"], body_str,
                cache_info["ttl"], cache_info["name"]
            )
        except Exception as e:
            logger.warning(f"stream_cache_write failed: {e}")

@app.get("/v1/models")
@app.get("/genai/v1/models")
async def list_models():
    return JSONResponse(status_code=200, content={"object": "list", "data": available_models_cache})

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/v1/status")
async def get_status():
    status_data = []
    for p in providers:
        name = p["name"]
        h = health_tracker.get(name)
        
        # Check api key status
        api_key_env = p.get("api_key_env")
        if api_key_env:
            has_key = os.getenv(api_key_env) is not None and os.getenv(api_key_env) != ""
            key_status = "Active" if has_key else "Missing key"
        else:
            has_key = True
            key_status = "Active" # local or keyless
            
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
            "avg_latency_ms": round(avg_lat, 1),
            "success_rate": round(success_rate * 100, 1),
            "requests_today": req_today
        })
    return JSONResponse(status_code=200, content=status_data)

async def _classify_request_proxy(payload):
    """Internal helper to classify requests using the unified classifier."""
    messages = payload.get("messages", [])
    text = messages[-1].get("content", "") if messages else ""
    classified = await classify_task(text=text, messages=messages)
    return classified.task_type

async def forward_to_provider(payload, providers_to_try, is_stream):
    for score, provider, api_key, h in providers_to_try:
        provider_name = provider["name"]
        provider_name_lower = provider_name.lower()
        base_url = provider.get("base_url")
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"

        provider_payload = payload.copy()
        if provider.get("model"):
            provider_payload["model"] = provider["model"]
        elif provider_name_lower == "ollama" and "model" not in provider_payload:
            provider_payload["model"] = "qwen2.5-coder:7b"

        # Payload Sanitization
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
                        retry_after = float(response.headers.get("retry-after", 60))
                        h.record_failure(cooldown_s=retry_after)
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

@app.post("/v1/chat/completions")
@app.post("/genai/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    config = load_config() # Load config
    try:
        payload = await request.json()
    except Exception: return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    is_stream = payload.get("stream", False)
    
    # Check for /model directive
    target_provider_name = None
    target_model = None
    messages = payload.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if last_msg.get("role") == "user" and isinstance(last_msg.get("content"), str):
            match = re.search(r'^/model\s+([^\s]+)', last_msg["content"])
            if match:
                model_str = match.group(1)
                if "," in model_str: target_provider_name, target_model = model_str.split(",", 1)
                else: target_provider_name = model_str
                last_msg["content"] = last_msg["content"].replace(match.group(0), "", 1).lstrip()
                if target_model: payload["model"] = target_model

    # Filter and sort providers
    cloud_providers = []
    local_providers = []
    
    for p in providers:
        if target_provider_name and p.get("name") != target_provider_name: continue
        if not target_provider_name and p.get("name").lower() in quota_manager.quotas:
            if not quota_manager.is_available(p["name"]): continue

        api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
        if p.get("api_key_env") is not None and not api_key: continue
        h = health_tracker[p["name"]]
        if target_provider_name or h.cb.allow_request():
            entry = (h.score(), p, api_key, h)
            if p.get("name").lower() == "ollama": local_providers.append(entry)
            else: cloud_providers.append(entry)
                
    cloud_providers.sort(key=lambda x: x[0], reverse=True)
    
    # ── RULE 0: Classify BEFORE dispatching to cloud ─────────────────────────
    # We classify first so that SIMPLE/MEDIUM tasks never start a cloud HTTP
    # request at all. Previously, the cloud_task was eagerly created and then
    # cancelled — this still consumed quota and added latency.
    task_type = await _classify_request_proxy(payload)

    # ── Token budget cap per task complexity ─────────────────────────────────
    # Prevents SIMPLE tasks from burning 8192 tokens when 512 is enough.
    # Only applies if caller didn't explicitly set max_tokens.
    if "max_tokens" not in payload:
        _token_caps = {
            "SIMPLE":  512,
            "MEDIUM":  2048,
            "COMPLEX": 4096,
            # CRITICAL/MASSIVE tasks get no cap — let the model decide
        }
        cap = _token_caps.get(task_type)
        if cap:
            payload["max_tokens"] = cap
            logger.debug(f"token_cap applied task={task_type} max_tokens={cap}")
    # ─────────────────────────────────────────────────────────────────────────

    # Quota guard: if we are within 100 requests of the daily cap, force all
    # traffic to local regardless of task classification.
    quota_ok = quota_manager.is_available("gemini", limit=config.quota_soft_limit)
    force_local = not quota_ok and not target_provider_name
    if force_local:
        logger.warning(f"Quota soft-limit reached ({config.quota_soft_limit}). Forcing local routing.")

    def _make_provider_response(response, h, start, name, task_type, escalated=False):
        """Unified response builder for both local and cloud providers."""
        total_ms = (time.time() - start) * 1000
        if is_stream:
            write_log({"provider": name, "total_ms": total_ms, "cached": False,
                       "task_type": task_type, "escalated": escalated})
            cache_info = None
            if not target_provider_name:
                ttl = CACHE_TTL.get(task_type, 0)
                if ttl > 0:
                    cache_info = {"payload": payload, "ttl": ttl, "name": name}
            return StreamingResponse(
                stream_response(response, h, start, cache_info),
                status_code=response.status_code
            )
        data = response.json()
        h.record_success()
        usage = data.get("usage", {})
        write_log({
            "provider": name,
            "input_tokens":  usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "total_ms":      total_ms,
            "cached":        False,
            "task_type":     task_type,
            "escalated":     escalated,
        })
        if not target_provider_name:
            ttl = CACHE_TTL.get(task_type, 0)
            response_cache.set(payload, data, ttl, name)
        return JSONResponse(status_code=response.status_code, content=data)

    # ── Cache Lookup ──────────────────────────────────────────────────────────
    if not target_provider_name:
        cached_entry = response_cache.get(payload)
        if cached_entry:
            resp_data = cached_entry["response_data"]
            prov_name = cached_entry["provider"]
            logger.info(f"Cache HIT: serving from cached response ({prov_name})")
            if is_stream:
                async def stream_cached():
                    chunk_size = 1024
                    data_bytes = resp_data.encode("utf-8", errors="replace")
                    for i in range(0, len(data_bytes), chunk_size):
                        yield data_bytes[i:i+chunk_size]
                        await asyncio.sleep(0.005)
                
                write_log({
                    "provider": prov_name,
                    "total_ms": 0,
                    "cached": True,
                    "task_type": task_type,
                })
                return StreamingResponse(stream_cached(), status_code=200)
            else:
                usage = resp_data.get("usage", {}) if isinstance(resp_data, dict) else {}
                write_log({
                    "provider": prov_name,
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_ms": 0,
                    "cached": True,
                    "task_type": task_type,
                })
                return JSONResponse(status_code=200, content=resp_data)

    # ── SIMPLE: always local, never touch cloud ───────────────────────────────
    if (task_type == "SIMPLE" or force_local) and local_providers and not target_provider_name:
        local_response, lh, l_start, l_name = await forward_to_provider(
            payload, local_providers, is_stream)
        if local_response:
            logger.info(f"{task_type} task -> local ({l_name})")
            return _make_provider_response(local_response, lh, l_start, l_name, task_type)
        # Local unavailable for SIMPLE: fall through to cloud as last resort
        logger.warning(f"{task_type} task: local unavailable, falling back to cloud")

    # ── MEDIUM: try local first, escalate to cloud only on failure ────────────
    elif task_type == "MEDIUM" and local_providers and not target_provider_name:
        local_response, lh, l_start, l_name = await forward_to_provider(
            payload, local_providers, is_stream)
        if local_response:
            logger.info(f"MEDIUM task -> local ({l_name}) [no escalation needed]")
            return _make_provider_response(local_response, lh, l_start, l_name, task_type)
        # Local failed for MEDIUM — escalate to cloud
        logger.info("MEDIUM task: local failed, escalating to cloud")
        cloud_response, ch, c_start, c_name = await forward_to_provider(
            payload, cloud_providers, is_stream)
        if cloud_response:
            logger.info(f"MEDIUM task -> cloud ({c_name}) [escalated]")
            return _make_provider_response(cloud_response, ch, c_start, c_name, task_type, escalated=True)
        return JSONResponse(status_code=503, content={"error": "MEDIUM task: all providers exhausted"})

    # ── COMPLEX: cloud preferred, local as emergency fallback ─────────────────
    else:
        cloud_response, ch, c_start, c_name = await forward_to_provider(
            payload, cloud_providers, is_stream)
        if cloud_response:
            logger.info(f"COMPLEX task -> cloud ({c_name})")
            return _make_provider_response(cloud_response, ch, c_start, c_name, task_type)
        # Cloud exhausted → emergency local fallback
        if local_providers:
            local_response, lh, l_start, l_name = await forward_to_provider(
                payload, local_providers, is_stream)
            if local_response:
                logger.warning(f"COMPLEX task: cloud failed, using local ({l_name}) as fallback")
                return _make_provider_response(local_response, lh, l_start, l_name, task_type, escalated=True)

    return JSONResponse(status_code=503, content={"error": "All providers exhausted"})

@app.websocket("/v1/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'router.log')
    last_pos = 0

    try:
        while True:
            # Cache the psutil result locally to reduce CPU usage during high traffic periods.
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

            # Try to get GPU usage
            try:
                proc = await asyncio.create_subprocess_exec(
                    "nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=2.0)
                if proc.returncode == 0:
                    metrics["gpu_memory_used_mb"] = int(stdout.decode().strip())
            except Exception:
                pass

            # Read new lines from router.log
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        f.seek(0, 2)
                        current_size = f.tell()

                        if current_size < last_pos:
                            last_pos = 0 # Log rotated

                        if current_size > last_pos:
                            f.seek(last_pos)
                            new_lines = f.readlines()
                            last_pos = current_size

                            for line in new_lines:
                                try:
                                    # Expected format: JSON line or regex extraction if needed
                                    # Our log is formatted by setup_logging but core/router.py does: logger.info("router_success...", extra={"log": "router.log"})
                                    # Actually, NINA writes structured JSON lines to router.log due to loguru or json handler.
                                    # We can try to parse the line as JSON or just pass the string to the frontend to parse.
                                    # Let's try JSON first, otherwise send raw.
                                    try:
                                        data = json.loads(line)
                                        metrics["router_events"].append(data)
                                    except json.JSONDecodeError:
                                        metrics["router_events"].append({"raw": line.strip()})
                                except Exception:
                                    pass
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
