import time
from unittest.mock import patch
from interfaces.middleware import RateLimiter, CommandRegistry

def test_rate_limiter_allows_under_limit():
    limiter = RateLimiter(max_calls=10, period_seconds=60)
    for _ in range(5):
        assert limiter.is_allowed(1) == True

def test_rate_limiter_blocks_over_limit():
    limiter = RateLimiter(max_calls=10, period_seconds=60)
    for _ in range(10):
        assert limiter.is_allowed(2) == True
    assert limiter.is_allowed(2) == False

def test_rate_limiter_resets_after_period():
    limiter = RateLimiter(max_calls=10, period_seconds=60)
    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0
        for _ in range(10):
            assert limiter.is_allowed(3) == True
        assert limiter.is_allowed(3) == False

        # Advance time by 61 seconds
        mock_time.return_value = 1061.0
        assert limiter.is_allowed(3) == True

def test_command_registry_register_and_get():
    registry = CommandRegistry()
    registry.register("test1", "handler1", "desc1")
    registry.register("test2", "handler2", "desc2")
    all_commands = registry.get_all()
    assert len(all_commands) == 2
    assert {"command": "test1", "handler_name": "handler1", "description": "desc1"} in all_commands
    assert {"command": "test2", "handler_name": "handler2", "description": "desc2"} in all_commands

def test_command_registry_is_registered():
    registry = CommandRegistry()
    registry.register("test_cmd", "handler", "desc")
    assert registry.is_registered("test_cmd") == True
    assert registry.is_registered("unknown_cmd") == False
