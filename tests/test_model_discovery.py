import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
from core.config import NinaConfig
from tools.model_discovery import ModelDiscoveryService, PROVIDER_MODEL_ENDPOINTS

@pytest.fixture
def dummy_config():
    return NinaConfig(
        telegram_bot_token="dummy",
        authorized_user_id="123",
        groq_api_key="mock_groq_key",
        gemini_api_key="mock_gemini_key"
    )

def test_init_success(dummy_config):
    service = ModelDiscoveryService(dummy_config, cache_path="dummy/path.json")
    assert service.config == dummy_config
    assert service.cache_path == "dummy/path.json"
    assert service.ttl == 24 * 3600

def test_init_missing_env_vars():
    config = NinaConfig(telegram_bot_token="dummy", authorized_user_id="123")
    service = ModelDiscoveryService(config)
    assert service.config == config

def test_load_cache_missing_file(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    with patch("os.path.exists", return_value=False):
        cache = service.load_cache()
        assert cache == {}

def test_save_cache_success(dummy_config):
    service = ModelDiscoveryService(dummy_config, cache_path="test_cache.json")
    mocked_open = mock_open()
    with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mocked_open):
        service.save_cache({"GROQ": "llama-3"})

        mock_makedirs.assert_called_once_with("", exist_ok=True)
        mocked_open.assert_called_once_with("test_cache.json", "w")
        assert mocked_open().write.called

@pytest.mark.asyncio
async def test_get_model_fresh_cache(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    service.load_cache = MagicMock(return_value={"GROQ": "llama-3-test"})

    with patch("os.path.exists", return_value=True), \
         patch("os.path.getmtime", return_value=time.time() - 100), \
         patch("asyncio.create_task") as mock_create_task:

        model = await service.get_model("GROQ")
        assert model == "llama-3-test"
        mock_create_task.assert_not_called()

@pytest.mark.asyncio
async def test_get_model_stale_cache(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    service.load_cache = MagicMock(return_value={"GROQ": "llama-old"})

    with patch("os.path.exists", return_value=True), \
         patch("os.path.getmtime", return_value=time.time() - 25 * 3600), \
         patch("asyncio.create_task") as mock_create_task, \
         patch.object(service, "discover_all", new_callable=AsyncMock):

        model = await service.get_model("GROQ")
        assert model == "llama-old"
        mock_create_task.assert_called_once()

@pytest.mark.asyncio
async def test_discover_all_success(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    service.save_cache = MagicMock()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"models": [{"id": "llama-3.3-70b-versatile"}, {"name": "models/gemini-2.5-flash"}]}

    async def mock_get(*args, **kwargs):
        return mock_response

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        results = await service.discover_all()

        assert "GROQ" in results
        assert results["GROQ"] == "llama-3.3-70b-versatile"
        assert "GEMINI" in results
        assert results["GEMINI"] == "gemini-2.5-flash"

        service.save_cache.assert_called_once()

@pytest.mark.asyncio
async def test_discover_all_error_fallback(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    service.save_cache = MagicMock()

    async def mock_get_error(*args, **kwargs):
        raise Exception("API down")

    with patch("httpx.AsyncClient.get", side_effect=mock_get_error):
        results = await service.discover_all()

        assert "GROQ" in results
        assert results["GROQ"] == PROVIDER_MODEL_ENDPOINTS["GROQ"]["fallback_model"]

        service.save_cache.assert_called_once()

@pytest.mark.asyncio
async def test_discover_all_no_models_url(dummy_config):
    service = ModelDiscoveryService(dummy_config)
    service.save_cache = MagicMock()

    with patch("httpx.AsyncClient.get"):
        results = await service.discover_all()

        assert "COHERE" in results
        assert results["COHERE"] == PROVIDER_MODEL_ENDPOINTS["COHERE"]["fallback_model"]
