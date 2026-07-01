#!/usr/bin/env python3
"""
NinaGate — OpenAI-compatible API gateway for NINA.
Serves: /health  /v1/models  /v1/chat/completions

Routing priority:
  1. Ollama (local, free, always preferred if model available)
  2. Cloud providers in tier order (quota-aware, from ninagate/providers.json)
     — providers with 3 consecutive failures are skipped until a success resets them

Run:
  python3 -m tools.ninagate.main          # default port 8080
  NINAGATE_PORT=9090 python3 -m tools.ninagate.main

NINA_FEATURE: ninagate-server v1.3
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)

# ---------------------------------------------------------------------------
# Bootstrap path so imports work when run as script or module
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent   # ~/nina
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse, StreamingResponse
    import uvicorn
except ImportError:
    print("[ninagate] ERROR: fastapi / uvicorn not installed.\n"
          "  pip install fastapi uvicorn", file=sys.stderr)
    sys.exit(1)

from core.constants import ENV_OLLAMA_HOST, ENV_NINAGATE_PORT, ENV_NINAGATE_QUOTA_DAILY
from ninagate.circuit_breaker import CircuitBreaker

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PORT           = int(os.getenv(ENV_NINAGATE_PORT, "8080"))
OLLAMA_HOST    = os.getenv(ENV_OLLAMA_HOST, "http://localhost:11434")
PROVIDERS_FILE = ROOT / "ninagate" / "providers.json"
QUOTA_FILE     = ROOT / "data" / "quota_state.json"
QUOTA_DAILY    = int(os.getenv(ENV_NINAGATE_QUOTA_DAILY, "900"))
LOG_FILE       = ROOT / "data" / "logs" / "ninagate.log"

# Model name fragments that indicate non-chat models — skip for chat routing
_NON_CHAT_PATTERNS = (
    "embed", "embedding", "rerank", "reranker", "classify", "vision-only",
)

# ---------------------------------------------------------------------------
# Logging — stdout + rotating file
# ---------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_fmt = logging.Formatter(
    fmt="%(asctime)s [ninagate] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_fmt)

_file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,   # 5 MB per file
    backupCount=3,
    encoding="utf-8",
)
_file_handler.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_stream_handler, _file_handler])
log = logging.getLogger("ninagate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text()) if path.exists() else default
    except (json.JSONDecodeError, OSError, PermissionError):
        return default


def _save_json(path: Path, data: Any) -> None:
    """Atomic write via tempfile + os.replace — safe under concurrent requests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except (OSError, PermissionError):
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _http_get(url: str, timeout: int = 5) -> tuple[dict, int]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return {"error": e.reason}, e.code
    except urllib.error.URLError as e:
        return {"error": str(e.reason)}, 0
    except (json.JSONDecodeError, TimeoutError, OSError) as e:
        return {"error": str(e)}, 0


def _http_post(url: str, payload: dict, headers: dict | None = None,
               timeout: int = 60) -> tuple[dict, int]:
    data = json.dumps(payload).encode()
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        body: dict = {}
        try:
            body = json.loads(e.read())
        except (json.JSONDecodeError, OSError):
            pass
        return body, e.code
    except urllib.error.URLError as e:
        return {"error": str(e.reason)}, 0
    except (json.JSONDecodeError, TimeoutError, OSError) as e:
        return {"error": str(e)}, 0


def _is_chat_model(name: str) -> bool:
    """Return False for embed/rerank/non-chat Ollama models."""
    lower = name.lower()
    return not any(pat in lower for pat in _NON_CHAT_PATTERNS)


# ---------------------------------------------------------------------------
# Ollama health cache — avoids per-request HTTP probe (30s TTL)
# ---------------------------------------------------------------------------

class _OllamaHealth:
    """Cache Ollama reachability so we probe at most once per 30 s."""
    _ttl: int = 30
    _last_check: float = 0.0
    _healthy: bool = False
    _models: list[str] = []

    def refresh(self) -> None:
        now = time.time()
        if now - self._last_check < self._ttl:
            return
        data, st = _http_get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        self._last_check = now
        if st == 200 and "models" in data:
            self._healthy = True
            self._models = [m["name"] for m in data["models"]]
        else:
            self._healthy = False
            self._models = []
            log.warning("Ollama health check failed (HTTP %s): %s", st, data.get("error", ""))

    @property
    def healthy(self) -> bool:
        self.refresh()
        return self._healthy

    @property
    def models(self) -> list[str]:
        self.refresh()
        return self._models


_ollama = _OllamaHealth()


# ---------------------------------------------------------------------------
# Circuit Breaker — provider health scoring + auto-disable
# ---------------------------------------------------------------------------

cb = CircuitBreaker()


# ---------------------------------------------------------------------------
# Quota state
# ---------------------------------------------------------------------------

class QuotaManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._reload()

    def _reload(self) -> None:
        raw = _load_json(QUOTA_FILE, {})
        self.quotas: dict[str, int] = raw.get("quotas", {})
        self.last_reset: float = raw.get("last_reset", 0.0)
        self.exhausted: bool = raw.get("quota_exhausted", False)

    def _save(self) -> None:
        _save_json(QUOTA_FILE, {
            "quotas": self.quotas,
            "last_reset": self.last_reset,
            "quota_exhausted": self.exhausted,
        })

    def _maybe_reset(self) -> None:
        now = time.time()
        if now - self.last_reset >= 86400:
            log.info("Quota daily reset triggered.")
            self.quotas = {}
            self.last_reset = now
            self.exhausted = False
            self._save()

    def check(self, provider: str) -> bool:
        """Return True if provider has quota remaining."""
        with self._lock:
            self._maybe_reset()
            return self.quotas.get(provider, 0) < QUOTA_DAILY

    def consume(self, provider: str) -> None:
        with self._lock:
            self._maybe_reset()
            self.quotas[provider] = self.quotas.get(provider, 0) + 1
            if self.quotas[provider] >= QUOTA_DAILY:
                self.exhausted = True
            self._save()

    def usage(self) -> dict[str, int]:
        with self._lock:
            self._maybe_reset()
            return dict(self.quotas)


quota = QuotaManager()

# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

def load_providers() -> list[dict]:
    providers = _load_json(PROVIDERS_FILE, [])
    if not providers:
        log.warning("ninagate/providers.json not found or empty — cloud fallback disabled.")
    return sorted(providers, key=lambda p: p.get("tier", 99))


def ollama_chat_models() -> list[str]:
    """Return only chat-capable Ollama models (exclude embed/rerank). Uses health cache."""
    return [m for m in _ollama.models if _is_chat_model(m)]


def ollama_chat(model: str, messages: list[dict], max_tokens: int = 512,
                temperature: float = 0.7,
                timeout: int = 120) -> tuple[str | None, str | None, dict]:
    """Returns (content, error, usage)."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    r, st = _http_post(f"{OLLAMA_HOST}/api/chat", payload, timeout=timeout)
    if st == 200 and "message" in r:
        usage = {
            "prompt_tokens": r.get("prompt_eval_count", 0),
            "completion_tokens": r.get("eval_count", 0),
            "total_tokens": r.get("prompt_eval_count", 0) + r.get("eval_count", 0),
        }
        return r["message"].get("content", ""), None, usage
    return None, r.get("error", f"Ollama HTTP {st}"), {}


def ollama_chat_stream(model: str, messages: list[dict], max_tokens: int = 512,
                       temperature: float = 0.7,
                       timeout: int = 120) -> Generator[str, None, None]:
    """Yield SSE chunks from Ollama streaming API."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    chunk_id = f"chatcmpl-ninagate-{int(time.time())}"
    created = int(time.time())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            for raw_line in r:
                try:
                    chunk = json.loads(raw_line)
                except (json.JSONDecodeError, ValueError):
                    continue
                delta_content = chunk.get("message", {}).get("content", "")
                done = chunk.get("done", False)
                sse_payload = {
                    "id": chunk_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": delta_content} if not done else {},
                        "finish_reason": "stop" if done else None,
                    }],
                }
                yield f"data: {json.dumps(sse_payload)}\n\n"
                if done:
                    break
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        err_payload = {"error": {"message": str(e), "type": "stream_error"}}
        yield f"data: {json.dumps(err_payload)}\n\n"
    yield "data: [DONE]\n\n"


def cloud_chat(provider: dict, messages: list[dict], model: str | None,
               max_tokens: int = 512, temperature: float = 0.7,
               timeout: int = 60) -> tuple[str | None, str | None, dict]:
    """Route to any OpenAI-compatible cloud provider. Returns (content, error, usage)."""
    name     = provider["name"]
    base_url = provider.get("base_url", "")
    api_key  = ""
    key_env  = provider.get("api_key_env")
    if key_env:
        api_key = os.getenv(key_env, "")

    # Keyless providers (POLLINATIONS, CHUTES) have api_key_env=null — allow them
    if key_env and not api_key:
        return None, f"{name}: API key not configured", {}
    if not quota.check(name):
        return None, f"{name}: daily quota exhausted", {}
    if cb.is_open(name):
        return None, f"{name}: circuit-broken — skipping", {}

    chosen_model = model or provider.get("model", "")
    payload = {
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    url = f"{base_url.rstrip('/')}/chat/completions"
    r, st = _http_post(url, payload, headers=headers, timeout=timeout)
    if st == 200 and "choices" in r:
        quota.consume(name)
        cb.record(name, success=True)
        content = r["choices"][0]["message"]["content"]
        raw_usage = r.get("usage", {})
        usage = {
            "prompt_tokens": raw_usage.get("prompt_tokens", 0),
            "completion_tokens": raw_usage.get("completion_tokens", 0),
            "total_tokens": raw_usage.get("total_tokens", 0),
        }
        return content, None, usage

    # Count as failure; still consume quota to avoid hammering
    quota.consume(name)
    cb.record(name, success=False)
    err_msg = r.get("error", {})
    if isinstance(err_msg, dict):
        err_msg = err_msg.get("message", f"{name} HTTP {st}")
    return None, str(err_msg) or f"{name} HTTP {st}", {}


def cloud_chat_stream(provider: dict, messages: list[dict], model: str | None,
                      max_tokens: int = 512, temperature: float = 0.7,
                      timeout: int = 60) -> Generator[str, None, None]:
    """Yield SSE chunks from an OpenAI-compatible cloud provider."""
    name     = provider["name"]
    base_url = provider.get("base_url", "")
    api_key  = ""
    key_env  = provider.get("api_key_env")
    if key_env:
        api_key = os.getenv(key_env, "")

    if key_env and not api_key:
        yield f"data: {json.dumps({'error': {'message': f'{name}: API key not configured'}})}\n\ndata: [DONE]\n\n"
        return
    if not quota.check(name):
        yield f"data: {json.dumps({'error': {'message': f'{name}: daily quota exhausted'}})}\n\ndata: [DONE]\n\n"
        return
    if cb.is_open(name):
        yield f"data: {json.dumps({'error': {'message': f'{name}: circuit-broken'}})}\n\ndata: [DONE]\n\n"

        return

    chosen_model = model or provider.get("model", "")
    payload = {
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = f"{base_url.rstrip('/')}/chat/completions"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
        quota.consume(name)
        cb.record(name, success=True)
            for raw_line in r:
                line = raw_line.decode("utf-8").strip()
                if line.startswith("data:"):
                    yield line + "\n\n"
                    if line == "data: [DONE]":
                        return
    except urllib.error.HTTPError as e:
        quota.consume(name)
        cb.record(name, success=False)
        err_payload = {"error": {"message": f"{name} HTTP {e.code}: {e.reason}"}}
        yield f"data: {json.dumps(err_payload)}\n\n"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        cb.record(name, success=False)
        err_payload = {"error": {"message": str(e)}}
        yield f"data: {json.dumps(err_payload)}\n\n"
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NinaGate",
    description="NINA OpenAI-compatible gateway",
    version="1.2.0",
)


@app.get("/health")
async def health() -> JSONResponse:
    all_models = _ollama.models
    chat_models = [m for m in all_models if _is_chat_model(m)]
    providers = load_providers()
    cb_report = cb.health_report()
    degraded = [n for n in [p["name"] for p in providers] if cb_report.get(n, {}).get("open", False)]
    return JSONResponse({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ollama": {
            "reachable": _ollama.healthy,
            "models": all_models[:10],
            "chat_models": chat_models,
            "health_cache_age_s": round(time.time() - _ollama._last_check, 1),
        },
        "providers": [p["name"] for p in providers],
        "degraded_providers": degraded,
        "circuit_breaker": cb_report,
        "quota": quota.usage(),
    })


@app.get("/v1/models")
async def list_models() -> JSONResponse:
    all_models = _ollama.models
    providers = load_providers()

    model_list: list[dict] = []

    for m in all_models:
        model_list.append({
            "id": m,
            "object": "model",
            "owned_by": "ollama",
            "created": 0,
            "chat_capable": _is_chat_model(m),
        })

    for p in providers:
        model_list.append({
            "id": p.get("model", p["name"]),
            "object": "model",
            "owned_by": p["name"],
            "created": 0,
            "chat_capable": True,
        })

    return JSONResponse({"object": "list", "data": model_list})


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    messages    = body.get("messages", [])
    model_req   = body.get("model", "auto")
    max_tokens  = int(body.get("max_tokens", 512))
    temperature = float(body.get("temperature", 0.7))
    stream      = bool(body.get("stream", False))
    timeout     = int(body.get("timeout", 0)) or None  # 0 → use per-backend defaults

    if not messages:
        raise HTTPException(status_code=400, detail="messages field required")

    errors: list[str] = []

    # ── Route 1: Ollama (local, always preferred) ──────────────────────────
    chat_models = ollama_chat_models()
    if chat_models:
        chosen = None
        if model_req and model_req != "auto":
            for m in chat_models:
                if m == model_req or m.startswith(model_req.split(":")[0]):
                    chosen = m
                    break
        if not chosen:
            chosen = chat_models[0]

        ollama_timeout = timeout or 120

        if stream:
            log.info("Streaming via Ollama → %s", chosen)
            return StreamingResponse(
                ollama_chat_stream(chosen, messages, max_tokens, temperature, ollama_timeout),
                media_type="text/event-stream",
            )

        content, err, usage = ollama_chat(chosen, messages, max_tokens, temperature,
                                          timeout=ollama_timeout)
        if content is not None:
            log.info("Routed via Ollama → %s", chosen)
            return _openai_response(content, chosen, "ollama", usage)
        errors.append(f"ollama/{chosen}: {err}")

    # ── Route 2: Cloud providers in tier order ─────────────────────────────
    for provider in load_providers():
        cloud_timeout = timeout or 60

        if stream:
            log.info("Streaming via cloud → %s", provider["name"])
            return StreamingResponse(
                cloud_chat_stream(provider, messages,
                                  model_req if model_req != "auto" else None,
                                  max_tokens, temperature, cloud_timeout),
                media_type="text/event-stream",
            )

        content, err, usage = cloud_chat(provider, messages,
                                         model_req if model_req != "auto" else None,
                                         max_tokens, temperature, cloud_timeout)
        if content is not None:
            log.info("Routed via cloud → %s", provider["name"])
            return _openai_response(content, provider.get("model", provider["name"]),
                                    provider["name"], usage)
        errors.append(err or provider["name"])

    log.error("All routes failed: %s", errors)
    raise HTTPException(status_code=503, detail={
        "message": "All providers failed or quota exhausted",
        "errors": errors,
    })


def _openai_response(content: str, model: str, provider: str,
                     usage: dict | None = None) -> JSONResponse:
    return JSONResponse({
        "id": f"chatcmpl-ninagate-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "provider": provider,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    })


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("NinaGate v1.3 starting on port %d", PORT)
    log.info("Ollama: %s", OLLAMA_HOST)
    log.info("Log file: %s", LOG_FILE)
    uvicorn.run(
        "tools.ninagate.main:app",
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        reload=False,
    )
