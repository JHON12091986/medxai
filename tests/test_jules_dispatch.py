import json
import pytest
from unittest.mock import patch
from tools.jules import run_dispatch

@pytest.mark.asyncio
async def test_run_dispatch_basic():
    # Test dispatch without template injection
    with patch("tools.jules.Path.exists", return_value=False):
        with patch("tools.jules.make_request", return_value={"id": "session-123"}) as mock_make:
            sid = await run_dispatch("Hello, Task", title="Task Title")
            assert sid == "session-123"
            mock_make.assert_called_once()
            called_json = mock_make.call_args[1]["json_data"]
            assert called_json["prompt"] == "Hello, Task"

@pytest.mark.asyncio
async def test_run_dispatch_template_injection():
    # Test dispatch with template injection under 8000 characters
    mock_template = {
        "system": "Use strict conventional commit rules."
    }
    mock_template_str = json.dumps(mock_template)
    
    with patch("tools.jules.Path.exists", return_value=True):
        with patch("tools.jules.Path.read_text", return_value=mock_template_str):
            with patch("tools.jules.make_request", return_value={"id": "session-123"}) as mock_make:
                sid = await run_dispatch("Code logic changes", title="Task Title")
                assert sid == "session-123"
                called_json = mock_make.call_args[1]["json_data"]
                assert "[NINA CONTEXT]" in called_json["prompt"]
                assert "Use strict conventional commit rules." in called_json["prompt"]
                assert "[TASK]" in called_json["prompt"]
                assert "Code logic changes" in called_json["prompt"]

@pytest.mark.asyncio
async def test_run_dispatch_template_truncation():
    # Test dispatch with template injection exceeding 8000 characters
    mock_template = {
        "system": "Use strict conventional commit rules."
    }
    mock_template_str = json.dumps(mock_template)
    huge_prompt = "A" * 9000
    
    with patch("tools.jules.Path.exists", return_value=True):
        with patch("tools.jules.Path.read_text", return_value=mock_template_str):
            with patch("tools.jules.make_request", return_value={"id": "session-123"}) as mock_make:
                sid = await run_dispatch(huge_prompt, title="Task Title")
                assert sid == "session-123"
                called_json = mock_make.call_args[1]["json_data"]
                final_prompt = called_json["prompt"]
                assert len(final_prompt) <= 8000
                assert "[TRUNCATED]" in final_prompt
                assert "Use strict conventional commit rules." in final_prompt
