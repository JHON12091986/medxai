import pytest
from unittest.mock import patch, AsyncMock
from tools.browser import _is_internal, fetch

def test_is_internal_blocked():
    blocked_urls = [
        "http://127.0.0.1",
        "http://127.0.0.1:8080/path",
        "http://localhost",
        "https://10.0.0.1",
        "http://192.168.1.100",
        "http://172.16.0.1",
        "http://[::1]",
        "file:///etc/passwd",
        "invalid_url",
        "http://169.254.169.254" # AWS metadata service
    ]
    for url in blocked_urls:
        assert _is_internal(url) is True, f"Expected {url} to be blocked"

def test_is_internal_allowed():
    allowed_urls = [
        "http://example.com",
        "https://google.com",
        "http://8.8.8.8",
        "https://1.1.1.1"
    ]
    for url in allowed_urls:
        assert _is_internal(url) is False, f"Expected {url} to be allowed"

@pytest.mark.asyncio
async def test_fetch_blocked_url():
    result = await fetch("http://127.0.0.1")
    assert result == "Blocked: internal network target."

@pytest.mark.asyncio
@patch("tools.browser.async_playwright")
async def test_fetch_success(mock_async_playwright):
    # Setup mock
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()

    mock_async_playwright.return_value.__aenter__.return_value = mock_pw
    mock_pw.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page
    mock_page.inner_text.return_value = "Test page content"

    result = await fetch("http://example.com")

    assert result == "Test page content"
    mock_page.goto.assert_called_once_with("http://example.com", timeout=30000)
    mock_page.inner_text.assert_called_once_with("body")
    mock_browser.close.assert_called_once()

@pytest.mark.asyncio
@patch("tools.browser.async_playwright")
async def test_fetch_error(mock_async_playwright):
    # Setup mock to raise Exception
    mock_pw = AsyncMock()
    mock_async_playwright.return_value.__aenter__.return_value = mock_pw
    mock_pw.chromium.launch.side_effect = Exception("Launch failed")

    result = await fetch("http://example.com")

    assert result.startswith("Browser error:")
    assert "Launch failed" in result
