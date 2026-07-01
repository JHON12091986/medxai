"""
tests/test_key_resolver.py — KeyResolver unit tests
"""
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_resolver():
    """Reset singleton between tests."""
    from core import key_resolver as kr
    kr.resolver._initialized = False
    kr.resolver._loaded = False
    kr.resolver._cache.clear()
    kr.resolver._json_secrets.clear()
    kr.resolver._env_values.clear()
    kr.resolver._env_local_values.clear()
    kr.KeyResolver._instance = None
    yield
    kr.KeyResolver._instance = None


def test_resolves_from_os_environ():
    os.environ["TELEGRAM_BOT_TOKEN"] = "test_token_123"
    os.environ["TELEGRAM_CHAT_ID"] = "99999999"
    os.environ["API_SECRET_KEY"] = "test_secret_456"
    from core.key_resolver import resolver
    resolver._loaded = False
    assert resolver.get("TELEGRAM_BOT_TOKEN") == "test_token_123"


def test_resolves_alias():
    """TELEGRAMCHATID alias resolves to TELEGRAM_CHAT_ID."""
    if "TELEGRAM_CHAT_ID" in os.environ:
        del os.environ["TELEGRAM_CHAT_ID"]
    os.environ["TELEGRAMCHATID"] = "88888888"
    from core.key_resolver import resolver
    resolver._loaded = False
    val = resolver.get("TELEGRAM_CHAT_ID", required=False)
    assert val == "88888888"


def test_optional_key_returns_none_when_missing(tmp_path):
    """Optional key returns None without raising."""
    env = {k: v for k, v in os.environ.items() if "GROQ" not in k}
    with patch.dict(os.environ, env, clear=True):
        from core.key_resolver import resolver
        resolver._loaded = False
        result = resolver.get("GROQ_API_KEY", required=False)
        assert result is None


def test_required_key_raises_on_missing():
    """Missing required key raises KeyResolutionError with remediation."""
    from core.key_resolver import KeyResolutionError
    env = {k: v for k, v in os.environ.items() if "TELEGRAM_BOT_TOKEN" not in k}
    with patch.dict(os.environ, env, clear=True):
        from core.key_resolver import resolver
        resolver._loaded = False
        resolver._env_values = {}
        resolver._env_local_values = {}
        resolver._json_secrets = {}
        resolver._loaded = True
        with pytest.raises(KeyResolutionError) as exc_info:
            resolver.get("TELEGRAM_BOT_TOKEN", required=True)
        assert "remediation" in str(exc_info.value).lower() or "Fix" in str(exc_info.value)


def test_api_secret_key_auto_generates(tmp_path):
    """API_SECRET_KEY auto-generates and persists when missing."""
    from core import key_resolver as kr
    kr._SECRETS_JSON = tmp_path / "secrets.json"
    env = {k: v for k, v in os.environ.items() if "API_SECRET_KEY" not in k
           and "NINA_API_KEY" not in k and "SECRET_KEY" not in k}
    with patch.dict(os.environ, env, clear=True):
        from core.key_resolver import resolver
        resolver._loaded = False
        resolver._env_values = {}
        resolver._env_local_values = {}
        resolver._json_secrets = {}
        resolver._loaded = True
        val = resolver.get("API_SECRET_KEY")
        assert val is not None
        assert len(val) > 20
        assert (tmp_path / "secrets.json").exists()


def test_set_persists_to_json(tmp_path):
    """resolver.set() persists to secrets.json."""
    from core import key_resolver as kr
    kr._SECRETS_JSON = tmp_path / "secrets.json"
    from core.key_resolver import resolver
    resolver.set("GROQ_API_KEY", "gsk_testvalue")
    data = json.loads((tmp_path / "secrets.json").read_text())
    assert data["GROQ_API_KEY"] == "gsk_testvalue"


def test_invalid_placeholder_rejected():
    """Dummy/placeholder values are treated as missing."""
    from core.key_resolver import _is_valid_value
    assert not _is_valid_value("your_token_here")
    assert not _is_valid_value("dummy")
    assert not _is_valid_value("placeholder")
    assert not _is_valid_value("")
    assert not _is_valid_value(None)
    assert _is_valid_value("gsk_realvalue123")


def test_audit_runs_without_error():
    """audit() returns a non-empty string."""
    from core.key_resolver import audit_keys
    report = audit_keys()
    assert "AUDIT REPORT" in report
    assert "TELEGRAM_BOT_TOKEN" in report
