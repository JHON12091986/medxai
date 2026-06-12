import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from interfaces.telegram_interface import TelegramInterface

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.message = MagicMock()
    return update

@pytest.fixture
def mock_nina():
    nina = MagicMock()
    nina.router = MagicMock()
    return nina

@pytest.fixture
def mock_config():
    config = MagicMock()
    return config

@pytest.mark.asyncio
async def test_errors_command_no_file(mock_update, mock_config, mock_nina):
    with patch("interfaces.telegram_interface.Path") as mock_path:
        # Simulate file not found
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        interface = TelegramInterface(mock_config, mock_nina)
        interface._reply = AsyncMock()

        await interface._handle_command(mock_update, "errors", "")

        mock_path.assert_called_with("docs/space/nina_error_register.md")
        interface._reply.assert_called_once_with(mock_update, "Error register not found.")

@pytest.mark.asyncio
async def test_errors_command_no_open_errors(mock_update, mock_config, mock_nina):
    content = """| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |
|----|----------|-----------|---------------|--------|----------|----------|---------|
| ERR-1 | 🔴 BLOCKER | core | Fixed err | ✅ FIXED | unassigned | v1 | main.py |
"""
    with patch("interfaces.telegram_interface.Path") as mock_path:
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = content
        mock_path.return_value = mock_path_instance

        interface = TelegramInterface(mock_config, mock_nina)
        interface._reply = AsyncMock()

        await interface._handle_command(mock_update, "errors", "")
        interface._reply.assert_called_once_with(mock_update, "No open errors found.")

@pytest.mark.asyncio
async def test_errors_command_with_open_errors(mock_update, mock_config, mock_nina):
    content = """| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |
|----|----------|-----------|---------------|--------|----------|----------|---------|
| ERR-1 | 🔴 BLOCKER | core | Some issue | 🔵 OPEN/PENDING | unassigned | v1 | main.py |
| ERR-2 | 🟡 DEBT | core | Another | ✅ FIXED | unassigned | v1 | main.py |
| ERR-3 | 🔵 OPEN | core | Pending err | 🔵 PENDING | unassigned | v1 | main.py |
"""
    with patch("interfaces.telegram_interface.Path") as mock_path:
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.read_text.return_value = content
        mock_path.return_value = mock_path_instance

        interface = TelegramInterface(mock_config, mock_nina)
        interface._reply = AsyncMock()

        await interface._handle_command(mock_update, "errors", "")

        expected_reply = "Open Error Register Items:\n• [ERR-1] Some issue\n• [ERR-3] Pending err"
        interface._reply.assert_called_once_with(mock_update, expected_reply[:4000])
