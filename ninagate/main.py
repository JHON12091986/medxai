import re
import asyncio
import json
import logging
import os
import time
import datetime
from collections import deque
from contextlib import asynccontextmanager

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from watchfiles import awatch

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ninagate")

# Load environment variables from NINA's .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

PROVIDERS_FILE = os.path.join(os.path.dirname(__file__), "providers.json")
providers = []
available_models_cache = [{"id": "auto", "object": "model", "owned_by": "ninagate"}]

def write_log(entry, log_path="logs/ninagate.log"):
    """Appends a log entry to the specified JSON log file."""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry["ts"] = datetime.datetime.now().isoformat()
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write log: {e}")

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
            with open(self.file_path, "w") as f:
                json.dump({"quotas": self.quotas, "last_reset": self.last_reset}, f)
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
        if provider in self.quotas:
            self.quotas[provider] += 1
            asyncio.get_event_loop().run_in_executor(None, self.save)

    def is_available(self, provider, limit=900):
        self.check_reset()
        return self.quotas.get(provider, 0) < limit

QUOTA_FILE = os.path.join(os.path.dirname(__file__), "quotas.json")
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
            if not api_key and p.get("name") != "ollama": continue
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
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=3.0))
    watcher_task = asyncio.create_task(watch_providers())
    model_fetch_task = asyncio.create_task(fetch_models_background())
    yield
    watcher_task.cancel()
    model_fetch_task.cancel()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

async def stream_response(response: httpx.Response, h: ProviderHealth, start_time: float):
    try:
        async for chunk in response.aiter_bytes():
            yield chunk
        h.record_success()
        h.latencies.append((time.time() - start_time) * 1000)
    finally:
        await response.aclose()

@app.get("/v1/models")
async def list_models():
    return JSONResponse(status_code=200, content={"object": "list", "data": available_models_cache})

async def classify_request(payload):
    messages = payload.get("messages", [])
    if not messages: return "SIMPLE"
    last_content = messages[-1].get("content", "")
    text = last_content.lower()
    
    SIMPLE_KEYWORDS = [
        "fix", "rename", "format", "docstring", "type hint", "boilerplate",
        "grep", "sort", "read", "show", "list", "print", "check", "verify",
        "compile", "status", "outline", "symbol", "signature", "log", "tail",
        "sync", "commit", "diff", "import", "lint", "echo"
    ]
    if any(x in text for x in SIMPLE_KEYWORDS):
        return "SIMPLE"
    if len(last_content) < 200:
        return "SIMPLE"
    return "COMPLEX"

async def forward_to_provider(payload, providers_to_try, is_stream):
    for score, provider, api_key, h in providers_to_try:
        provider_name = provider["name"]
        base_url = provider.get("base_url")
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"

        provider_payload = payload.copy()
        if provider.get("model"):
            provider_payload["model"] = provider["model"]
        elif provider_name == "ollama" and "model" not in provider_payload:
            provider_payload["model"] = "qwen2.5-coder:7b"

        # Payload Sanitization
        if provider_name == "gemini":
            provider_payload.pop("stream_options", None)
            provider_payload.pop("cache_control", None)
        elif provider_name == "groq":
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
async def proxy_chat_completions(request: Request):
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
        if not target_provider_name and p.get("name") in quota_manager.quotas:
            if not quota_manager.is_available(p["name"]): continue

        api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
        if not api_key and p.get("name") != "ollama": continue
        h = health_tracker[p["name"]]
        if target_provider_name or h.cb.allow_request():
            entry = (h.score(), p, api_key, h)
            if p.get("name") == "ollama": local_providers.append(entry)
            else: cloud_providers.append(entry)
                
    cloud_providers.sort(key=lambda x: x[0], reverse=True)
    
    # Async Pipeline
    classification_task = asyncio.create_task(classify_request(payload))
    cloud_task = asyncio.create_task(forward_to_provider(payload, cloud_providers, is_stream))
    
    task_type = await classification_task
    
    if task_type == "SIMPLE" and local_providers and not target_provider_name:
        cloud_task.cancel()
        local_response, lh, l_start, l_name = await forward_to_provider(payload, local_providers, is_stream)
        if local_response:
            logger.info(f"SIMPLE task -> local ({l_name})")
            if is_stream: return StreamingResponse(stream_response(local_response, lh, l_start), status_code=local_response.status_code)
            else:
                data = local_response.json()
                lh.record_success()
                return JSONResponse(status_code=local_response.status_code, content=data)

    response, h, start_time, provider_name = await cloud_task
    if response:
        logger.info(f"Forwarded to {provider_name}")
        if is_stream: return StreamingResponse(stream_response(response, h, start_time), status_code=response.status_code)
        else:
            data = response.json()
            h.record_success()
            return JSONResponse(status_code=response.status_code, content=data)

    if local_providers:
        response, h, start_time, provider_name = await forward_to_provider(payload, local_providers, is_stream)
        if response:
            if is_stream: return StreamingResponse(stream_response(response, h, start_time), status_code=response.status_code)
            else:
                data = response.json()
                h.record_success()
                return JSONResponse(status_code=response.status_code, content=data)

    return JSONResponse(status_code=503, content={"error": "All providers exhausted"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
