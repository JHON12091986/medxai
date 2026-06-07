import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch, MagicMock
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

    # The router might default to an ordered list where a different provider without a key has a higher score.
    # We should just ensure GROQ is returned or mock out `_ordered_providers`

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
    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
        # Dummy inputs
        prompt = "Hello, world!"
        messages = [{"role": "user", "content": prompt}]
        task = ClassifiedTask(
            task_type="general",
            estimated_tokens=50,
            is_parallel_candidate=False,
            is_sensitive=False
        )

        # Execute
        # We need to make sure the key is correctly set in the config and the router will pick it up
        with patch.object(router, "_ordered_providers", return_value=["GROQ"]):
            response_text = await router.route(prompt, messages, task, force_local=False)

        # 5. Verify outcome
        assert response_text == "This is a mock provider response."

        # Verify network mock was called
        mock_post.assert_called()

        # Verify network call parameters
        args, kwargs = mock_post.call_args
        assert "Authorization" in kwargs.get("headers", {})
        assert kwargs["headers"]["Authorization"] == "Bearer test_groq_key"
