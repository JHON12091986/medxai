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
        # Higher is better
        # Normalize latency (lower is better, cap at 5000ms)
        lat_score = max(0.0, 1.0 - (self.avg_latency() / 5000.0))
        # Penalty for degraded states
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
        # Reset at 1PM BD (midnight PT approx). BD is UTC+6.
        # Midnight PT is 7AM or 8AM UTC. Let's use 1PM BD (07:00 UTC).
        now = time.time()
        now_dt = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
        reset_hour = 7 # 7AM UTC = 1PM BD
        
        # If last_reset was before the most recent 7AM UTC, reset.
        last_reset_dt = datetime.datetime.fromtimestamp(self.last_reset, datetime.timezone.utc)
        
        # Find the most recent 7AM UTC
        recent_reset = now_dt.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
        if now_dt < recent_reset:
            recent_reset -= datetime.timedelta(days=1)
            
        if last_reset_dt < recent_reset:
            logger.info("Quota reset triggered.")
            for k in self.quotas: self.quotas[k] = 0
            self.last_reset = now
            self.save()

    def increment(self, provider):
        self.check_reset()
        if provider in self.quotas:
            self.quotas[provider] += 1
            self.save()

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
        logger.info(f"Loaded {len(providers)} providers from {PROVIDERS_FILE}")
    except Exception as e:
        logger.error(f"Failed to load providers: {e}")

async def watch_providers():
    load_providers()
    async for changes in awatch(PROVIDERS_FILE):
        logger.info(f"Providers file changed, reloading... {changes}")
        load_providers()

async def fetch_models_background():
    """Periodically asks providers for their available models using httpx."""
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
                    data = resp.json()
                    for m in data.get("data", []):
                        if "id" in m:
                            # Prefix model ID with provider name to ensure uniqueness
                            models.append({"id": f"{p['name']}/{m['id']}", "object": "model", "owned_by": p["name"]})
            except Exception:
                pass
        
        available_models_cache = models
        await asyncio.sleep(600) # update every 10 mins

http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global http_client
    http_client = httpx.AsyncClient(timeout=60.0)
    watcher_task = asyncio.create_task(watch_providers())
    model_fetch_task = asyncio.create_task(fetch_models_background())
    yield
    # Shutdown
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
    """Returns dynamically fetched models + 'auto'."""
    return JSONResponse(status_code=200, content={
        "object": "list",
        "data": available_models_cache
    })

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    is_stream = payload.get("stream", False)

    target_provider_name = None
    target_model = None

    # Check for /model directive in the last message
    messages = payload.get("messages", [])
    if messages and len(messages) > 0:
        last_msg = messages[-1]
        if last_msg.get("role") == "user" and isinstance(last_msg.get("content"), str):
            content_str = last_msg["content"]
            match = re.search(r'^/model\s+([^\s]+)', content_str)
            if match:
                model_str = match.group(1)
                if "," in model_str:
                    target_provider_name, target_model = model_str.split(",", 1)
                else:
                    target_provider_name = model_str

                # Strip the directive
                last_msg["content"] = content_str.replace(match.group(0), "", 1).lstrip()
                payload["messages"] = messages

    # Dynamic Load Balancing: Sort providers by real-time health score
    available_providers = []
    for p in providers:
        # If a target provider is specified, skip others
        if target_provider_name and p.get("name") != target_provider_name:
            continue
            
        # 0. Quota Check (unless explicitly targeted)
        if not target_provider_name and p.get("name") in quota_manager.quotas:
            if not quota_manager.is_available(p["name"]):
                logger.warning(f"Quota exceeded for {p['name']}, skipping.")
                continue

        api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
        if not api_key and p.get("name") != "ollama":
            continue
            
        h = health_tracker[p["name"]]
        
        # 1. Circuit Breaker validation (unless explicitly targeted)
        if target_provider_name or h.cb.allow_request():
            available_providers.append((h.score(), p, api_key, h))
            
    if not target_provider_name:
        available_providers.sort(key=lambda x: x[0], reverse=True)
    elif not available_providers:
        logger.warning(f"Target provider {target_provider_name} not found or missing API key, using fallback cascade.")
        # Fallback to normal behavior if target not found
        for p in providers:
            api_key = os.getenv(p.get("api_key_env", "")) if p.get("api_key_env") else None
            if not api_key and p.get("name") != "ollama": continue
            h = health_tracker[p["name"]]
            if h.cb.allow_request():
                available_providers.append((h.score(), p, api_key, h))
        available_providers.sort(key=lambda x: x[0], reverse=True)

    for score, provider, api_key, h in available_providers:
        provider_name = provider["name"]
        base_url = provider.get("base_url")
        
        headers = {"Content-Type": "application/json"}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"

        provider_payload = payload.copy()
        
        # Priority: target_model (from directive) > provider["model"] (from config) > default
        if target_model:
            provider_payload["model"] = target_model
        elif provider.get("model"):
            provider_payload["model"] = provider["model"]
        elif provider_name == "ollama" and "model" not in provider_payload:
            provider_payload["model"] = "qwen2.5:7b"

        # Basic Transformers / Payload Sanitization
        if provider_name == "gemini":
            provider_payload.pop("stream_options", None)
            provider_payload.pop("cache_control", None)
        elif provider_name == "groq":
            provider_payload.pop("stream_options", None)

        url = f"{base_url}/chat/completions"

        # 2. Automatic Retries with backoff (up to 2 attempts)
        for attempt in range(2):
            try:
                start_time = time.time()
                if attempt == 0:
                    logger.info(f"Trying provider: {provider_name} (health_score: {score:.2f}) at {url}")
                else:
                    logger.info(f"Retrying provider: {provider_name} (attempt 2)")
                
                req = http_client.build_request("POST", url, json=provider_payload, headers=headers)
                response = await http_client.send(req, stream=is_stream)

                if response.status_code >= 400:
                    error_body = ""
                    try:
                        error_body = await response.aread()
                        error_body = error_body.decode("utf-8")
                    except Exception:
                        pass
                    
                    if response.status_code == 429:
                        retry_after = float(response.headers.get("retry-after", 60))
                        logger.warning(f"Rate limited by {provider_name}. Breaker open for {retry_after}s.")
                        h.record_failure(cooldown_s=retry_after)
                        await response.aclose()
                        break # Break retry loop, immediately failover to next provider
                        
                    elif 500 <= response.status_code < 600 and attempt == 0:
                        logger.warning(f"5xx Server Error from {provider_name}, retrying... {error_body[:100]}")
                        await response.aclose()
                        await asyncio.sleep(1.0) # 1 second backoff
                        continue # Retry same provider
                    
                    logger.warning(f"Provider {provider_name} failed with status {response.status_code}: {error_body[:100]}")
                    h.record_failure()
                    write_log({
                        "provider": provider_name, "task_type": "proxy",
                        "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
                        "ttf_ms": 0, "total_ms": 0, "status": "failure",
                        "error": f"http_{response.status_code}", "source": "ninagate"
                    }, log_path="logs/ninagate.log")
                    await response.aclose()
                    break # Try next provider in cascade

                logger.info(f"Provider {provider_name} succeeded in {(time.time() - start_time)*1000:.0f}ms.")
                quota_manager.increment(provider_name)
                if is_stream:
                    return StreamingResponse(
                        stream_response(response, h, start_time),
                        status_code=response.status_code,
                        background=None
                    )
                else:
                    data = response.json()
                    h.record_success()
                    h.latencies.append((time.time() - start_time) * 1000)
                    return JSONResponse(status_code=response.status_code, content=data)

            except httpx.TimeoutException:
                logger.warning(f"Provider {provider_name} timed out.")
                if attempt == 0: 
                    await asyncio.sleep(1.0) # wait and retry
                    continue
                h.record_failure()
                break
            except Exception as e:
                logger.warning(f"Provider {provider_name} exception: {e}")
                h.record_failure()
                break

    logger.error("All providers exhausted.")
    return JSONResponse(
        status_code=503,
        content={"error": {"message": "All proxy providers exhausted.", "type": "server_error"}}
    )


@app.get("/v1/config/providers")
async def get_providers_config():
    return JSONResponse(status_code=200, content=providers)

@app.post("/v1/config/providers")
async def update_providers_config(request: Request):
    try:
        new_providers = await request.json()
        if not isinstance(new_providers, list):
            return JSONResponse(status_code=400, content={"error": "Expected a JSON array of providers"})

        # Write to file
        with open(PROVIDERS_FILE, "w") as f:
            json.dump(new_providers, f, indent=2)

        # The watchfiles awatch will pick this up and reload globally,
        # but we can also update it immediately.
        global providers
        providers = new_providers
        return JSONResponse(status_code=200, content={"status": "success", "message": "Providers updated successfully"})
    except Exception as e:
        logger.error(f"Failed to update providers: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
="0.0.0.0", port=8080)
