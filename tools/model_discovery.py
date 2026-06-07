import json
import logging
import time
import asyncio
import os
import httpx


logger = logging.getLogger("nina.model_discovery")

PROVIDER_MODEL_ENDPOINTS = {
    "GROQ": {
        "models_url": "https://api.groq.com/openai/v1/models",
        "auth_header": "Bearer",
        "model_filter_fn": lambda models: next((m["id"] for m in models if m["id"] == "llama-3.3-70b-versatile"),
                                              sorted([m["id"] for m in models if "llama-3" in m["id"].lower()], reverse=True)[0] if any("llama-3" in m["id"].lower() for m in models) else "llama-3.3-70b-versatile"),
        "fallback_model": "llama-3.3-70b-versatile"
    },
    "GEMINI": {
        "models_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "auth_header": "?key=",
        "model_filter_fn": lambda models: next((m["name"].split("/")[-1] for m in models if "gemini-2.5-flash" in m["name"] and "preview" not in m["name"] and "experimental" not in m["name"]), "gemini-2.5-flash"),
        "fallback_model": "gemini-2.5-flash"
    },
    "CEREBRAS": {
        "models_url": "https://api.cerebras.ai/v1/models",
        "auth_header": "Bearer",
        "model_filter_fn": lambda models: next((m["id"] for m in models if m["id"] == "llama-3.3-70b"),
                                              sorted([m["id"] for m in models if "llama" in m["id"].lower()], reverse=True)[0] if any("llama" in m["id"].lower() for m in models) else "llama-3.3-70b"),
        "fallback_model": "llama-3.3-70b"
    },
    "MISTRAL": {
        "models_url": "https://api.mistral.ai/v1/models",
        "auth_header": "Bearer",
        "model_filter_fn": lambda models: next((m["id"] for m in models if "mistral-small" in m["id"] and "latest" in m["id"]), "mistral-small-latest"),
        "fallback_model": "mistral-small-latest"
    },
    "DEEPSEEK": {
        "models_url": "https://api.deepseek.com/models",
        "auth_header": "Bearer",
        "model_filter_fn": lambda models: next((m["id"] for m in models if m["id"] == "deepseek-chat"), "deepseek-chat"),
        "fallback_model": "deepseek-chat"
    },
    "TOGETHER": {
        "models_url": "https://api.together.xyz/v1/models",
        "auth_header": "Bearer",
        "model_filter_fn": lambda models: next((m["id"] for m in models if m["id"] == "meta-llama/Llama-3.3-70B-Instruct-Turbo"), "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
        "fallback_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    },
    "COHERE": {"fallback_model": "command-r-plus"},
    "XAI": {"fallback_model": "grok-3-mini"},
    "SAMBANOVA": {"fallback_model": "Meta-Llama-3.3-70B-Instruct"},
    "OPENAI": {"fallback_model": "gpt-4o-mini"},
    "PERPLEXITY": {"fallback_model": "llama-3.1-sonar-small-128k-online"},
    "FIREWORKS": {"fallback_model": "accounts/fireworks/models/llama-v3p3-70b-instruct"},
    "HYPERBOLIC": {"fallback_model": "meta-llama/Llama-3.3-70B-Instruct"},
    "NOVITA": {"fallback_model": "meta-llama/llama-3.3-70b-instruct"},
    "ONEBRAIN": {"fallback_model": "llama-3.3-70b-versatile"},
    "OPENROUTER": {"fallback_model": "meta-llama/llama-3.3-70b-instruct"}
}

class ModelDiscoveryService:
    def __init__(self, config, cache_path="data/model_cache.json"):
        self.config = config
        self.cache_path = cache_path
        self.ttl = 24 * 3600  # 24 hours

    def load_cache(self) -> dict:
        if not os.path.exists(self.cache_path):
            return {}
        try:
            with open(self.cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from {self.cache_path}: {e}")
            return {}

    def save_cache(self, models: dict):
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w") as f:
                json.dump(models, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache to {self.cache_path}: {e}")

    async def get_model(self, provider_id: str) -> str:
        fallback = PROVIDER_MODEL_ENDPOINTS.get(provider_id, {}).get("fallback_model", "default")

        # Check cache freshness
        if os.path.exists(self.cache_path):
            mtime = os.path.getmtime(self.cache_path)
            if time.time() - mtime < self.ttl:
                cache = self.load_cache()
                if provider_id in cache:
                    return cache[provider_id]

        # Trigger discovery asynchronously without waiting for it, return fallback or old cache immediately
        # Since the task requires returning a string and triggering discover_all,
        # let's trigger it in the background if not fresh
        asyncio.create_task(self.discover_all())

        cache = self.load_cache()
        return cache.get(provider_id, fallback)

    async def discover_all(self) -> dict[str, str]:
        results = {}
        async with httpx.AsyncClient(timeout=5.0) as client:
            for pid, meta in PROVIDER_MODEL_ENDPOINTS.items():
                fallback = meta.get("fallback_model")
                if "models_url" not in meta:
                    results[pid] = fallback
                    continue

                url = meta["models_url"]
                filter_fn = meta["model_filter_fn"]

                # Fetch key from config
                key_field = f"{pid.lower()}_api_key"
                if pid == "GEMINI":
                    key = getattr(self.config, key_field, None)
                    if key:
                        url = f"{url}?key={key}"
                    headers = {}
                else:
                    key = getattr(self.config, key_field, None)
                    headers = {"Authorization": f"Bearer {key}"} if key else {}

                try:
                    r = await client.get(url, headers=headers)
                    r.raise_for_status()
                    data = r.json()
                    models = data.get("models", data.get("data", []))
                    if not isinstance(models, list):
                        # Some APIs like Gemini might have a different structure
                        if "models" in data:
                            models = data["models"]
                        else:
                            models = []

                    if models:
                        best_model = filter_fn(models)
                        results[pid] = best_model
                    else:
                        results[pid] = fallback
                except Exception as e:
                    logger.warning(f"Discovery failed for {pid}: {e}. Using fallback.")
                    results[pid] = fallback

        self.save_cache(results)

        # Log discovered models at INFO level
        log_msg = " ".join([f"{k}={v}" for k, v in results.items()])
        logger.info(f"Model discovery: {log_msg}")
        return results
