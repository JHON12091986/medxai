# Using unittest.mock for all I/O as per NINA mission
import pytest
import os
from unittest.mock import patch
from core.config import NinaConfig, load_config

def test_validate_env_missing_required():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"AUTHORIZED_USER_ID": "user123", "API_SECRET_KEY": "secret", "TELEGRAM_CHAT_ID": "chat123"}, clear=True):
        config = NinaConfig(telegram_bot_token="test", authorized_user_id="user123", api_secret_key="secret", telegram_chat_id="chat123")
        errors, warnings = config.validate_env()
        assert "TELEGRAM_BOT_TOKEN" in errors
        assert "AUTHORIZED_USER_ID" not in errors

def test_validate_env_missing_optional():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test", "AUTHORIZED_USER_ID": "user123", "API_SECRET_KEY": "secret", "TELEGRAM_CHAT_ID": "chat123"}, clear=True):
        config = NinaConfig(telegram_bot_token="test", authorized_user_id="user123", api_secret_key="secret", telegram_chat_id="chat123")
        errors, warnings = config.validate_env()
        assert not errors
        assert any("OPENAI_API_KEY" in w for w in warnings)

def test_load_config_missing_telegram_token():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"AUTHORIZED_USER_ID": "user123", "API_SECRET_KEY": "secret"}, clear=True):
        with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN missing from .env — cannot start NINA."):
            load_config()

def test_load_config_missing_authorized_user():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "API_SECRET_KEY": "secret"}, clear=True):
        with pytest.raises(RuntimeError, match="AUTHORIZED_USER_ID missing from .env — cannot start NINA."):
            load_config()

def test_load_config_missing_telegram_chat_id():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "AUTHORIZED_USER_ID": "user123", "API_SECRET_KEY": "secret", "TEST_FORCE_MISSING_CHAT_ID": "true"}, clear=True):
        with pytest.raises(RuntimeError, match="TELEGRAM_CHAT_ID is required but not set. Add it to .env."):
            load_config()

def test_load_config_success():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "AUTHORIZED_USER_ID": "user123", "API_SECRET_KEY": "secret", "TELEGRAM_CHAT_ID": "chat123"}, clear=True):
        config = load_config()
        assert config.telegram_bot_token == "test_token"
        assert config.authorized_user_id == "user123"
        assert config.telegram_chat_id == "chat123"

def test_load_config_missing_api_secret():
    from core.vault import _SECRETS
    _SECRETS.clear()
    from core.vault import CredentialVault
    CredentialVault.get_instance()._secrets.clear()
    with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "test_token", "AUTHORIZED_USER_ID": "user123", "TELEGRAM_CHAT_ID": "chat123"}, clear=True):
        config = load_config()
        assert config.api_secret_key is not None
        assert len(config.api_secret_key) > 0
