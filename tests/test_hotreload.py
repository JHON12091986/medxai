# Using unittest.mock for all I/O as per NINA mission
import pytest
from unittest.mock import patch
from core.hotreload import ConfigHotReload
from core.config import NinaConfig

@pytest.fixture
def mock_config():
    return NinaConfig(telegram_bot_token="test", authorized_user_id="user123")

def test_hotreload_initialization(mock_config):
    with patch("core.hotreload.Path.stat") as mock_stat:
        mock_stat.return_value.st_mtime = 12345.0
        hotreload = ConfigHotReload(mock_config)
        assert hotreload.config == mock_config
        assert hotreload._last_mtime == 12345.0

def test_hotreload_mtime_exception(mock_config):
    with patch("core.hotreload.Path.stat") as mock_stat:
        mock_stat.side_effect = Exception("File not found")
        hotreload = ConfigHotReload(mock_config)
        assert hotreload._last_mtime == 0.0

@pytest.mark.asyncio
async def test_hotreload_reload_changes(mock_config):
    with patch("core.hotreload.Path.stat") as mock_stat:
        mock_stat.return_value.st_mtime = 12345.0
        hotreload = ConfigHotReload(mock_config)

        with patch("core.hotreload.dotenv_values") as mock_dotenv:
            mock_dotenv.return_value = {
                "IDLE_THRESHOLD_MIN": "20",
                "IDLE_AUTO_APPROVE": "True"
            }
            await hotreload._reload()

            assert mock_config.idle_threshold_min == 20
            assert mock_config.idle_auto_approve is True

@pytest.mark.asyncio
async def test_hotreload_reload_revert_to_default(mock_config):
    with patch("core.hotreload.Path.stat") as mock_stat:
        mock_stat.return_value.st_mtime = 12345.0
        mock_config.idle_threshold_min = 25 # Non-default value
        hotreload = ConfigHotReload(mock_config)

        with patch("core.hotreload.dotenv_values") as mock_dotenv:
            mock_dotenv.return_value = {
                "IDLE_THRESHOLD_MIN": "", # Empty should revert to default
            }
            await hotreload._reload()

            assert mock_config.idle_threshold_min == 15 # Default value in NinaConfig
