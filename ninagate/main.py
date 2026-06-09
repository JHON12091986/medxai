import asyncio
import json
import logging
import os
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

def load_providers():
    global providers
    try:
        with open(PROVIDERS_FILE, "r") as f:
            providers = json.load(f)
        logger.info(f"Loaded {len(providers)} providers from {PROVIDERS_FILE}")
    except Exception as e:
        logger.error(f"Failed to load providers: {e}")

async def watch_providers():
    load_providers()
    async for changes in awatch(PROVIDERS_FILE):
        logger.info(f"Providers file changed, reloading... {changes}")
        load_providers()

http_client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global http_client
    http_client = httpx.AsyncClient(timeout=60.0)
    watcher_task = asyncio.create_task(watch_providers())
    yield
    # Shutdown
    watcher_task.cancel()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

async def stream_response(response: httpx.Response):
    try:
        async for chunk in response.aiter_bytes():
            yield chunk
    finally:
        await response.aclose()

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    is_stream = payload.get("stream", False)

    # Do not drop "model" override completely, but some providers require us to override it.
    # We will override the model parameter for each provider based on their config.

    for provider in providers:
            provider_name = provider.get("name")
            base_url = provider.get("base_url")
            model = provider.get("model")
            api_key_env = provider.get("api_key_env")

            api_key = None
            if api_key_env:
                api_key = os.getenv(api_key_env)
                if not api_key:
                    logger.warning(f"Skipping {provider_name}: API key {api_key_env} not found in environment.")
                    continue

            headers = {
                "Content-Type": "application/json"
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider_name == "ollama":
                # For Ollama, we do not send Authorization header typically
                pass

            # Update the payload with the provider's specific model
            provider_payload = payload.copy()
            if model:
                provider_payload["model"] = model
            elif provider_name == "ollama" and "model" not in provider_payload:
                provider_payload["model"] = "qwen2.5:7b"

            url = f"{base_url}/chat/completions"

            logger.info(f"Trying provider: {provider_name} at {url}")

            try:
                # We need to construct the request differently depending on streaming
                req = http_client.build_request("POST", url, json=provider_payload, headers=headers)
                response = await http_client.send(req, stream=is_stream)

                if response.status_code >= 400:
                    error_body = ""
                    try:
                        error_body = await response.aread()
                        error_body = error_body.decode("utf-8")
                    except Exception:
                        pass
                    logger.warning(f"Provider {provider_name} failed with status {response.status_code}: {error_body}")
                    # Need to close the response manually if we used stream=True and we are skipping
                    await response.aclose()
                    continue

                logger.info(f"Provider {provider_name} succeeded.")

                if is_stream:
                    return StreamingResponse(
                        stream_response(response),
                        status_code=response.status_code,
                        background=None # The response generator handles reading
                    )
                else:
                    data = response.json()
                    return JSONResponse(status_code=response.status_code, content=data)

            except httpx.TimeoutException:
                logger.warning(f"Provider {provider_name} timed out.")
            except Exception as e:
                logger.warning(f"Provider {provider_name} exception: {e}")

    logger.error("All providers exhausted.")
    return JSONResponse(
        status_code=503,
        content={"error": {"message": "All proxy providers exhausted.", "type": "server_error"}}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
