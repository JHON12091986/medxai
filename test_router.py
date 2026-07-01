#!/usr/bin/env python3
import asyncio
from core.router import HybridRouter
from pydantic import BaseModel
from typing import Optional

# Mock NinaConfig for testing
class MockNinaConfig(BaseModel):
    telegram_bot_token: str = "placeholder"
    telegram_chat_id: str = "placeholder"
    ollama_host: str = "http://localhost:11434"
    api_secret_key: Optional[str] = None

async def test_router():
    r = HybridRouter(MockNinaConfig())
    await r.initialize()
    print("Router initialized. Testing for 100 minutes...")
    
    # Simulate requests every 10 seconds
    for i in range(600):  # 600 requests * 10 seconds = 6000 seconds (100 minutes)
        try:
            task = {"task_type": "quick", "estimated_tokens": 100, "is_read_only": False, "is_sensitive": False}
            result = await r.route(f"Test request {i}", [{"role": "user", "content": f"Test request {i}"}], task)
            print(f"Request {i}: Success")
        except Exception as e:
            print(f"Request {i}: Failed - {e}")
        await asyncio.sleep(10)
    
    await r.close()

if __name__ == "__main__":
    asyncio.run(test_router())