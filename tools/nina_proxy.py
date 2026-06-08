import time
import uuid
import logging

from fastapi import FastAPI, Request, HTTPException
import uvicorn
from fastapi.responses import JSONResponse

from core.router import HybridRouter, ClassifiedTask
from core.config import load_config

logger = logging.getLogger("nina.proxy")

app = FastAPI()

router = None
last_used_provider = "auto"

@app.on_event("startup")
async def startup_event():
    global router
    config = load_config()
    router = HybridRouter(config)
    await router.initialize()
    logger.info({"event": "nina_proxy_start", "port": 8765, "router": "ready"})

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    messages = body.get("messages")
    if not messages or not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages list is missing or empty")

    prompt = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            prompt = msg.get("content", "")
            break

    if not prompt:
        raise HTTPException(status_code=400, detail="No user message found in messages")

    task = ClassifiedTask(task_type="general", estimated_tokens=500, is_parallel_candidate=False, is_sensitive=False)

    try:
        response_text = await router.route(prompt, messages, task)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": str(e),
                    "type": "router_error",
                    "code": 500
                }
            }
        )

    response_id = "nina-" + uuid.uuid4().hex
    created_at = int(time.time())

    return {
        "id": response_id,
        "object": "chat.completion",
        "created": created_at,
        "model": "nina-auto",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok", "provider": last_used_provider}

@app.get("/v1/models")
async def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "nina-auto",
                "object": "model",
                "owned_by": "nina"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
