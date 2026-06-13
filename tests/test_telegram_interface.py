import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from interfaces.telegram_interface import TelegramInterface

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.message = MagicMock()
    update.message.delete = AsyncMock()
    return update

@pytest.fixture
def mock_nina():
    nina = MagicMock()
    nina.router = MagicMock()
    nina.router.get_status = MagicMock(return_value="Router Status")
    nina.get_status = AsyncMock(return_value="NINA Status")
    return nina

@pytest.mark.asyncio
async def test_handle_command_backlog_found(mock_update, mock_nina):
    interface = TelegramInterface(MagicMock(), mock_nina)
    interface._reply = AsyncMock()

    mock_backlog_content = """
| ID | Title | Status | Files Touched |
|----|-------|--------|---------------|
| B-001 | Test task 1 | `DONE` | test.py |
| B-002 | Ready task 1 | `READY` | test.py |
| B-003 | Ready task 2 | `READY` | test2.py |
| B-004 | In progress | `IN_PROGRESS` | test3.py |
| B-005 | Ready task 3 | `READY` | test4.py |
| B-006 | Ready task 4 | `READY` | test5.py |
| B-007 | Ready task 5 | `READY` | test6.py |
| B-008 | Ready task 6 | `READY` | test7.py |
"""

    with patch("interfaces.telegram_interface.Path.exists", return_value=True):
        with patch("interfaces.telegram_interface.Path.read_text", return_value=mock_backlog_content):
            await interface._handle_command(mock_update, "backlog", "")

    expected_reply = "*Top 5 READY Backlog Items:*\n" + \
                     "• B-002: Ready task 1\n" + \
                     "• B-003: Ready task 2\n" + \
                     "• B-005: Ready task 3\n" + \
                     "• B-006: Ready task 4\n" + \
                     "• B-007: Ready task 5"

    interface._reply.assert_called_once_with(mock_update, expected_reply, parse_mode=interface.PARSE_MODE_DEFAULT)

@pytest.mark.asyncio
async def test_handle_command_backlog_not_found(mock_update, mock_nina):
    interface = TelegramInterface(MagicMock(), mock_nina)
    interface._reply = AsyncMock()

    with patch("interfaces.telegram_interface.Path.exists", return_value=False):
        await interface._handle_command(mock_update, "backlog", "")

    interface._reply.assert_called_once_with(mock_update, "Backlog not found.")

@pytest.mark.asyncio
async def test_handle_command_backlog_empty_ready(mock_update, mock_nina):
    interface = TelegramInterface(MagicMock(), mock_nina)
    interface._reply = AsyncMock()

    mock_backlog_content = """
| ID | Title | Status | Files Touched |
|----|-------|--------|---------------|
| B-001 | Test task 1 | `DONE` | test.py |
"""

    with patch("interfaces.telegram_interface.Path.exists", return_value=True):
        with patch("interfaces.telegram_interface.Path.read_text", return_value=mock_backlog_content):
            await interface._handle_command(mock_update, "backlog", "")

    interface._reply.assert_called_once_with(mock_update, "No READY items found.", parse_mode=interface.PARSE_MODE_DEFAULT)
