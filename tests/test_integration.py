import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from core.router import HybridRouter, ClassifiedTask
from core.config import NinaConfig

@pytest.mark.asyncio
async def test_full_request_router_to_provider():
    # 1. Setup mock config
    mock_config = NinaConfig(
        telegram_bot_token="test_bot_token",
        authorized_user_id="test_user_id",
        groq_api_key="test_groq_key"
    )

    # 2. Instantiate router
    router = HybridRouter(config=mock_config)

    # Needs to run discovery
    with patch("core.router.ModelDiscoveryService.get_model", return_value="llama-3.3-70b-versatile"):
        await router.initialize()

    # 3. Setup Mock for network request
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a mock provider response."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20
        }
    }

    # 4. Patch httpx post to return the mock response
    # We must patch the router's internal call to _call_provider or the httpx client it uses.
    # Given the complexity of the router, patching _call_provider is cleanest for a "full route" test.
    with patch.object(router, "_call_provider", AsyncMock(return_value=("This is a mock provider response.", 10, 20, 100.0))) as mock_call:
        # Dummy inputs
        prompt = "Hello, world!"
        messages = [{"role": "user", "content": prompt}]
        task = ClassifiedTask(
            task_type="general",
            estimated_tokens=50,
            is_parallel_candidate=False,
            is_sensitive=False
        )

        # Force Tier 2 to only have GROQ
        with patch("core.router.PROVIDERS_TIER2", {"GROQ": {"model": "m", "base_url": "u", "key_field": "groq_api_key"}}):
            with patch("core.router.PROVIDERS_TIER1", {}):
                with patch("core.router.PROVIDERS_TIER3", {}):
                    response_text = await router.route(prompt, messages, task, force_local=False)

        # 5. Verify outcome
        assert response_text == "This is a mock provider response."
        mock_call.assert_called_once()
