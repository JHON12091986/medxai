import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock, MagicMock
from tools.nina_proxy import app

@pytest.fixture
def mock_router():
    with patch("tools.nina_proxy.router") as mock:
        mock.route = AsyncMock(return_value="Mocked response")
        
        # Mock the dispatcher -> plan -> execute flow
        mock_plan = MagicMock()
        mock_plan.execute = AsyncMock(return_value="Mocked response")
        mock.dispatcher.dispatch.return_value = mock_plan
        
        yield mock

@pytest_asyncio.fixture
async def proxy_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_chat_completions_success(proxy_client: AsyncClient, mock_router):
    response = await proxy_client.post(
        "/v1/chat/completions",
        json={
            "model": "nina-auto",
            "messages": [{"role": "user", "content": "Hello NINA"}],
            "temperature": 0.7
        },
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["model"] == "nina-auto"
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert data["choices"][0]["message"]["content"] == "Mocked response"
    assert data["choices"][0]["finish_reason"] == "stop"
    mock_router.dispatcher.dispatch.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completions_empty_messages(proxy_client: AsyncClient, mock_router):
    response = await proxy_client.post(
        "/v1/chat/completions",
        json={
            "model": "nina-auto",
            "messages": []
        }
    )
    assert response.status_code == 400
    assert "messages list is missing or empty" in response.json()["detail"]
    mock_router.route.assert_not_called()

@pytest.mark.asyncio
async def test_chat_completions_router_exception(proxy_client: AsyncClient, mock_router):
    mock_router.dispatcher.dispatch.side_effect = Exception("Router failed internally")
    response = await proxy_client.post(
        "/v1/chat/completions",
        json={
            "model": "nina-auto",
            "messages": [{"role": "user", "content": "Trigger error"}]
        }
    )
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["message"] == "Router failed internally"
    assert data["error"]["type"] == "router_error"
    assert data["error"]["code"] == 500

@pytest.mark.asyncio
async def test_health_endpoint(proxy_client: AsyncClient):
    response = await proxy_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "provider": "auto"}

@pytest.mark.asyncio
async def test_models_endpoint(proxy_client: AsyncClient):
    response = await proxy_client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == "nina-auto"
    assert data["data"][0]["object"] == "model"
    assert data["data"][0]["owned_by"] == "nina"

@pytest.mark.asyncio
async def test_missing_messages(proxy_client: AsyncClient, mock_router):
    response = await proxy_client.post(
        "/v1/chat/completions",
        json={
            "model": "nina-auto"
        }
    )
    assert response.status_code == 400
    assert "messages list is missing or empty" in response.json()["detail"]
    mock_router.route.assert_not_called()
