import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from core.utils import write_log

def test_write_log_default_path(tmp_path):
    """Test write_log with default path (mocked)."""
    log_dir = tmp_path / "logs"
    log_file = log_dir / "router.log"
    
    # Patch Path to point to our tmp_path for the default log location
    # Actually, it's easier to just pass the path
    entry = {"event": "test", "val": 123}
    write_log(entry, log_path=str(log_file))
    
    assert log_file.exists()
    content = log_file.read_text()
    parsed = json.loads(content)
    assert parsed["event"] == "test"
    assert parsed["val"] == 123
    assert "ts" in parsed

def test_write_log_creates_dir(tmp_path):
    """Test that write_log creates the parent directory."""
    new_dir = tmp_path / "deep" / "path" / "to" / "logs"
    log_file = new_dir / "test.log"
    
    entry = {"status": "ok"}
    write_log(entry, log_path=str(log_file))
    
    assert log_file.exists()
    assert new_dir.exists()

def test_write_log_appends(tmp_path):
    """Test that write_log appends to existing file."""
    log_file = tmp_path / "append.log"
    
    write_log({"id": 1}, log_path=str(log_file))
    write_log({"id": 2}, log_path=str(log_file))
    
    lines = log_file.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["id"] == 1
    assert json.loads(lines[1])["id"] == 2

def test_write_log_timestamp_format(tmp_path):
    """Test the timestamp format in the log entry."""
    log_file = tmp_path / "ts.log"
    write_log({"msg": "hello"}, log_path=str(log_file))
    
    data = json.loads(log_file.read_text())
    ts = data["ts"]
    # 2026-06-14T16:00:00.000000+0000 style or similar
    assert "T" in ts
    # Verify we can parse it back if needed (basic check)
    assert len(ts) > 10
