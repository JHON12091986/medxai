import asyncio
import psutil
from unittest.mock import MagicMock
from core.router import HybridRouter, ClassifiedTask
from core.config import NinaConfig

async def test_parallel_route_ram_guard():
    config = NinaConfig(telegram_bot_token="dummy", authorized_user_id="123")
    router = HybridRouter(config)
    await router.initialize()
    
    task = ClassifiedTask("research", 1000, True, False)
    
    # Mock local_fast_fn
    local_fast_fn = MagicMock(side_effect=lambda x: asyncio.Future())
    # Actually it needs to be an async function
    async def mock_local_fast(prompt):
        return '["sub1", "sub2"]'
    
    # Force RAM guard to trigger
    router.config.ram_guard_gb = 0.01 # Very low
    
    print(f"RAM used: {psutil.virtual_memory().used / 1e9} GB")
    print(f"RAM guard: {router.config.ram_guard_gb} GB")
    
    try:
        res = await router.parallel_route("test prompt", [], task, mock_local_fast)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parallel_route_ram_guard())
