import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from interfaces.telegram_interface import TelegramInterface
from core.config import NinaConfig

@pytest.mark.asyncio
async def test_telegram_interface_status():
    config = NinaConfig(telegram_bot_token="test", telegram_chat_id="1", authorized_user_id="1")
    nina_os = MagicMock()
    nina_os.config = config
    nina_os.router = MagicMock()
    nina_os.router.get_health_summary.return_value = "Providers: 3 available | 1 exhausted | 2 inactive"
    nina_os.get_status = AsyncMock(return_value="NINA Status")

    interface = TelegramInterface(config, nina_os)

    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await interface._handle_command(update, "status", "")

    nina_os.get_status.assert_called_once()
    nina_os.router.get_health_summary.assert_called_once()
    update.message.reply_text.assert_called_once()

    called_with = update.message.reply_text.call_args[0][0]
    assert "Providers: 3 available" in called_with
    assert "NINA Status" in called_with
