import pytest
import os
from unittest.mock import patch
from core.config import NinaConfig, load_config

def test_validate_env_missing_required():
    with patch.dict(os.environ, {"AUTHORIZEDUSERID": "user123"}, clear=True):
        config = NinaConfig(telegram_bot_token="test", authorized_user_id="user123")
        errors, warnings = config.validate_env()
        assert "TELEGRAMBOTTOKEN" in errors
        assert "AUTHORIZEDUSERID" not in errors

def test_validate_env_missing_optional():
    with patch.dict(os.environ, {"TELEGRAMBOTTOKEN": "test", "AUTHORIZEDUSERID": "user123"}, clear=True):
        config = NinaConfig(telegram_bot_token="test", authorized_user_id="user123")
        errors, warnings = config.validate_env()
        assert not errors
        assert any("OPENAI_API_KEY" in w for w in warnings)

def test_load_config_missing_telegram_token():
    with patch.dict(os.environ, {"AUTHORIZEDUSERID": "user123"}, clear=True):
        with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN missing from .env — cannot start NINA."):
            load_config()

def test_load_config_missing_authorized_user():
    with patch.dict(os.environ, {"TELEGRAMBOTTOKEN": "test_token"}, clear=True):
        with pytest.raises(RuntimeError, match="AUTHORIZED_USER_ID missing from .env — cannot start NINA."):
            load_config()

def test_load_config_success():
    with patch.dict(os.environ, {"TELEGRAMBOTTOKEN": "test_token", "AUTHORIZEDUSERID": "user123"}, clear=True):
        config = load_config()
        assert config.telegram_bot_token == "test_token"
        assert config.authorized_user_id == "user123"
