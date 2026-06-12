import sys
from pathlib import Path
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.mark.asyncio
async def test_browser_smoke():
    from tools import browser

    assert browser._is_internal("http://127.0.0.1") == True

    with patch("tools.browser.async_playwright") as mock_pw:
        mock_pw_context = AsyncMock()
        mock_pw.return_value.__aenter__.return_value = mock_pw_context

        mock_browser = AsyncMock()
        mock_pw_context.chromium.launch.return_value = mock_browser

        mock_page = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_page.inner_text.return_value = "Mocked content"

        result = await browser.fetch("http://example.com")
        assert "Mocked content" in result

@pytest.mark.asyncio
async def test_officemail_smoke():
    from tools import office_mail

    mock_config = MagicMock()
    mock_config.ews_my_email = "test@example.com"
    mock_config.ews_shared_email = "shared@example.com"
    mock_config.ews_domain = "domain"
    mock_config.ews_username = "user"
    mock_config.ews_password = "password"
    mock_config.ews_server = "mail.example.com"
    mock_config.ews_max_emails = 5
    mock_config.ews_keywords = "urgent,important"

    with patch("exchangelib.Credentials"), \
         patch("exchangelib.Configuration"), \
         patch("exchangelib.Account") as mock_account_cls:

        mock_account = MagicMock()
        mock_account_cls.return_value = mock_account
        mock_account.inbox.filter.return_value.order_by.return_value.__getitem__.return_value = []

        result = await office_mail.fetch(mock_config)
        assert "**Personal**" in result
        assert "**BasicID**" in result

@pytest.mark.asyncio
async def test_search_smoke():
    from tools import search

    with patch("tools.search.httpx.AsyncClient") as mock_client:
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx

        mock_response = MagicMock()
        mock_response.json.return_value = {"answer": "Mocked Answer", "results": [{"title": "t", "url": "u", "content": "c"}]}
        mock_client_ctx.post.return_value = mock_response

        with patch("tools.search.TAVILY_KEY", "dummy_key"):
            result = await search.search("test query")
            assert "Mocked Answer" in result

@pytest.mark.asyncio
async def test_web_smoke():
    from tools import web

    with patch("tools.web.DDGS") as mock_ddgs:
        mock_ddgs_instance = MagicMock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.text.return_value = [{"title": "Web Title", "href": "http://web", "body": "Web Body"}]

        result = await web.search("test query")
        assert "Web Title" in result
        assert "http://web" in result

@pytest.mark.asyncio
async def test_files_smoke(tmp_path):
    from tools import files

    with patch("tools.files.WORKSPACE", tmp_path):
        with patch("tools.files.psutil.disk_usage") as mock_disk:
            mock_disk.return_value.percent = 50.0

            mock_config = MagicMock()
            mock_config.disk_guard_pct = 90.0

            write_res = await files.write("test.txt", "Hello World", mock_config)
            assert "Written" in write_res

            read_res = await files.read("test.txt")
            assert read_res == "Hello World"

@pytest.mark.asyncio
async def test_providerhunter_smoke(tmp_path):
    from tools import providerhunter

    with patch("tools.providerhunter.DISCOVERED", tmp_path / "discovered.json"):
        with patch("tools.providerhunter.httpx.AsyncClient") as mock_client:
            mock_client_ctx = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_ctx

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client_ctx.post.return_value = mock_response

            mock_router = MagicMock()
            mock_config = MagicMock()

            await providerhunter.hunt(mock_router, mock_config)

            import json
            data = json.loads((tmp_path / "discovered.json").read_text())
            assert len(data) > 0
            assert data[0]["healthy"] == True

@pytest.mark.asyncio
async def test_jules_smoke():
    from tools import jules
    with patch("tools.jules.make_request") as mock_req:
        with patch.dict("os.environ", {"JULES_API_KEY": "dummy"}):
            mock_req.return_value = {"sessions": [{"name": "sessions/mocked_sid", "title": "mocked_title", "state": "AWAITING_USER_FEEDBACK"}]}

            result = await jules.run("status")
            assert "Active Jules Sessions" in result

@pytest.mark.asyncio
async def test_gputuner_smoke(tmp_path):
    from tools import system
    gputuner = system

    with patch("tools.system.GPU_CONFIG", tmp_path / "gpu_config.json"):
        with patch("tools.system.asyncio.create_subprocess_exec") as mock_create_subprocess, \
             patch("tools.system.asyncio.wait_for") as mock_wait_for:

            mock_proc = MagicMock()
            mock_create_subprocess.return_value = mock_proc

            # stdout, stderr tuple return
            mock_wait_for.return_value = (b"8000\n", b"")

            result = await gputuner.tune() if __import__('inspect').iscoroutinefunction(gputuner.tune) else gputuner.tune()
            assert "GPU tuned" in result
            assert "LOCALFAST" in result
