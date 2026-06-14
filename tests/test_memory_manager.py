import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch
from core.memory_manager import ScratchpadManager

@pytest.fixture
def temp_scratchpad(tmp_path):
    """Setup a temporary scratchpad file for testing."""
    file_path = tmp_path / "scratchpad.json"
    with patch("core.memory_manager.Path", return_value=file_path):
        # We need to be careful with how Path is patched
        pass
    
    # Simpler: Instantiate and then override the attribute
    mgr = ScratchpadManager()
    mgr.file_path = file_path
    mgr.file_path.parent.mkdir(parents=True, exist_ok=True)
    return mgr

def test_scratchpad_store_get(temp_scratchpad):
    temp_scratchpad.store("key1", {"data": 123}, ttl_seconds=100)
    
    val = temp_scratchpad.get("key1")
    assert val == {"data": 123}

def test_scratchpad_expiration(temp_scratchpad):
    # Store with 0 TTL (immediate expiration)
    temp_scratchpad.store("expired", "gone", ttl_seconds=-1)
    
    val = temp_scratchpad.get("expired")
    assert val is None
    
    # Verify it was removed from file
    data = temp_scratchpad._read()
    assert "expired" not in data

def test_scratchpad_clear_all(temp_scratchpad):
    temp_scratchpad.store("a", 1)
    temp_scratchpad.store("b", 2)
    assert temp_scratchpad.get("a") == 1
    
    temp_scratchpad.clear_all()
    assert temp_scratchpad.get("a") is None
    assert temp_scratchpad.get("b") is None

def test_scratchpad_clear_expired(temp_scratchpad):
    temp_scratchpad.store("valid", "keep", ttl_seconds=100)
    temp_scratchpad.store("old", "remove", ttl_seconds=-10)
    
    temp_scratchpad.clear_expired()
    
    assert temp_scratchpad.get("valid") == "keep"
    # get() also clears expired, but clear_expired should have done it
    data = temp_scratchpad._read()
    assert "old" not in data

def test_scratchpad_persistence(temp_scratchpad):
    temp_scratchpad.store("persistent", "value")
    
    # Create a new manager pointing to same file
    new_mgr = ScratchpadManager()
    new_mgr.file_path = temp_scratchpad.file_path
    
    assert new_mgr.get("persistent") == "value"

def test_scratchpad_corrupt_file_handling(temp_scratchpad):
    # Write invalid JSON
    temp_scratchpad.file_path.write_text("invalid json {")
    
    # Should not crash, return empty dict on _read
    val = temp_scratchpad.get("any")
    assert val is None
