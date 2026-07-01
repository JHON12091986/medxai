import os
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def _patch_os_environ():
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "test_token_123",
        "AUTHORIZED_USER_ID": "test_user_123",
        "API_SECRET_KEY": "test_secret_123",
        "TELEGRAM_CHAT_ID": "test_chat_id",
        "OPENAI_API_KEY": "test",
        "ANTHROPIC_API_KEY": "test",
        "TELEGRAM_TOKEN": "test",
        "PERPLEXITY_API_KEY": "test"
    }, clear=False):
        yield
import pytest

@pytest.fixture
def nina_tmp_dir(tmp_path):
    d = tmp_path / "nina_test"
    d.mkdir()
    yield d

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setenv("TELEGRAM_TOKEN", "test")
    monkeypatch.setenv("PERPLEXITY_API_KEY", "test")
    yield
