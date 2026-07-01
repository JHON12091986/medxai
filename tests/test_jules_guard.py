import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

import core.jules_guard as jg

@pytest.fixture
def temp_state_file(tmp_path):
    state_file = tmp_path / "nina_state_test.json"
    state_file.write_text("{}")
    with patch("core.jules_guard.STATE_FILE", str(state_file)):
        yield state_file

@pytest.fixture
def mock_send_message():
    with patch("core.jules_guard.send_message") as mock:
        yield mock

def test_requires_human_action_blocked_keywords():
    assert jg.requires_human_action("This is a .env file") is True
    assert jg.requires_human_action("Normal text") is False

def test_requires_human_action_regex_patterns(mock_send_message):
    # Test each pattern
    # 1. 32+ hex chars
    assert jg.requires_human_action("My key is 1234567890abcdef1234567890abcdef") is True
    mock_send_message.assert_called()
    mock_send_message.reset_mock()
    
    # 2. Bearer token
    assert jg.requires_human_action("Authorization: Bearer mytoken123") is True
    mock_send_message.assert_called()
    mock_send_message.reset_mock()
    
    # 3. bot:id
    assert jg.requires_human_action("Telegram bot:123456:ABC") is True
    mock_send_message.assert_called()
    mock_send_message.reset_mock()
    
    # 4. sk-
    assert jg.requires_human_action("OpenAI sk-abcdefghijklmnopqrstuvwxyz") is True
    mock_send_message.assert_called()
    mock_send_message.reset_mock()
    
    # 5. AIza
    assert jg.requires_human_action("Google AIzaSyabcdefghijklmnopqrstuvwxyz") is True
    mock_send_message.assert_called()

def test_redact_secrets():
    text = "Key sk-1234567890, bot:12345:abc and AIza-123"
    redacted = jg.redact_secrets(text)
    assert "[REDACTED]" in redacted
    assert "sk-1234567890" not in redacted

def test_detect_loop(temp_state_file, mock_send_message):
    error_id = "ERR_404"
    
    # Set up initial state with open_prs matching error_id
    state_data = {
        "open_prs": [
            {"title": "Fix ERR_404", "body": "This fixes the issue"}
        ],
        "jules_attempts_tracker": {
            error_id: {
                "jules_attempts": 2,
                "last_attempt": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            }
        }
    }
    temp_state_file.write_text(json.dumps(state_data))
    
    # First check: jules_attempts >= 2, open PR, last_attempt within 24h -> detect_loop should return True, trigger alert and cooldown
    assert jg.detect_loop(error_id) is True
    mock_send_message.assert_called_with(
        "🚨 Loop Detected for error: ERR_404. Active PR exists with 2 attempts within 24h. Activating 48h cooldown."
    )
    
    # Read state file to verify cooldown is set
    updated_state = json.loads(temp_state_file.read_text())
    assert error_id in updated_state.get("cooldowns", {})
    
    # Next check: error_id is in cooldowns and cooldown hasn't expired -> should return True immediately
    mock_send_message.reset_mock()
    assert jg.detect_loop(error_id) is True
    mock_send_message.assert_not_called()

def test_daily_dispatch_counter(temp_state_file, mock_send_message):
    # Set up state with dispatched = 4
    state_data = {
        "jules_dispatched_today": 4,
        "last_dispatch_date": datetime.utcnow().date().isoformat()
    }
    temp_state_file.write_text(json.dumps(state_data))
    
    # 5th dispatch should be allowed (increment is True, so it will increment to 5 and return False)
    assert jg.daily_dispatch_counter(increment=True) is False
    
    updated_state = json.loads(temp_state_file.read_text())
    assert updated_state["jules_dispatched_today"] == 5
    
    # 6th dispatch should be blocked
    assert jg.daily_dispatch_counter(increment=True) is True
    mock_send_message.assert_called_with("⚠️ Jules daily dispatch limit of 5/day reached. Blocking further dispatches.")
    
    # Check UTC midnight date-change auto-reset
    mock_send_message.reset_mock()
    # Set date to yesterday
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    state_data = {
        "jules_dispatched_today": 5,
        "last_dispatch_date": yesterday
    }
    temp_state_file.write_text(json.dumps(state_data))
    
    # Calling it should reset the count because the date changed, and allow dispatch
    assert jg.daily_dispatch_counter(increment=True) is False
    mock_send_message.assert_not_called()
    updated_state = json.loads(temp_state_file.read_text())
    assert updated_state["jules_dispatched_today"] == 1
    assert updated_state["last_dispatch_date"] == datetime.utcnow().date().isoformat()

def test_validate_task_spec():
    # Valid spec
    valid_task = "Modify core/jules_guard.py to add validate_task_spec() function around line 120. Verify with pytest tests/test_jules_guard.py."
    res = jg.validate_task_spec(valid_task)
    assert res["valid"] is True
    assert len(res["failures"]) == 0

    # Invalid cases
    # 1. Multiple file paths
    with pytest.raises(ValueError):
        jg.validate_task_spec("Edit core/jules_guard.py and tools/jules.py around line 120. Verify with pytest.")

    # 2. No file path
    with pytest.raises(ValueError):
        jg.validate_task_spec("Fix the loop detection issue at line 120. Verify with pytest.")

    # 3. No line/function name
    with pytest.raises(ValueError):
        jg.validate_task_spec("Modify core/jules_guard.py. Verify with pytest.")

    # 4. Secret keywords
    with pytest.raises(ValueError):
        jg.validate_task_spec("In core/jules_guard.py around line 120, check the token password. Verify with pytest.")

    # 5. No verify command
    with pytest.raises(ValueError):
        jg.validate_task_spec("Modify core/jules_guard.py to add validate_task_spec() function around line 120.")

    # 6. Word count >= 200
    long_task = "Modify core/jules_guard.py at line 120. Verify with pytest. " + " ".join(["word"] * 250)
    with pytest.raises(ValueError):
        jg.validate_task_spec(long_task)
