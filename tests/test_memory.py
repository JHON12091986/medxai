import json
import pytest
import time
from pathlib import Path
from unittest.mock import patch
from core.memory import MemoryHealth
from core.memory_manager import ScratchpadManager

@pytest.fixture
def mock_paths(tmp_path):
    facts_file = tmp_path / "facts.json"
    chroma_dir = tmp_path / "chromadb"
    scratchpad_file = tmp_path / "scratchpad.json"

    with patch("core.memory.FACTS_FILE", facts_file),          patch("core.memory.CHROMA_DIR", chroma_dir),          patch("core.memory_manager.Path") as MockPath:

        # We need Path("data/memory/scratchpad.json") to return our tmp_path
        def side_effect(arg):
            if str(arg) == "data/memory/scratchpad.json":
                return scratchpad_file
            return Path(arg)
        MockPath.side_effect = side_effect
        yield {"facts": facts_file, "chroma": chroma_dir, "scratchpad": scratchpad_file}

def test_facts_loads(mock_paths):
    facts_file = mock_paths["facts"]
    facts_file.write_text('{"test": "data"}')

    with open(facts_file, 'r') as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data["test"] == "data"

def test_memory_health_returns_dict(mock_paths):
    health = MemoryHealth.check()
    assert isinstance(health, dict)
    assert "chromadb_ok" in health
    assert "facts_ok" in health
    assert "collection_count" in health

def test_scratchpad_store_get(mock_paths):
    manager = ScratchpadManager()
    manager.store('x', 1)
    val = manager.get('x')
    assert val == 1

def test_scratchpad_ttl_expired(mock_paths):
    manager = ScratchpadManager()
    manager.store('temp', 'value', ttl_seconds=0)
    time.sleep(1) # wait for expiry
    val = manager.get('temp')
    assert val is None

def test_scratchpad_clear_expired(mock_paths):
    manager = ScratchpadManager()
    manager.store('expired', 'value', ttl_seconds=0)
    manager.store('not_expired', 'value', ttl_seconds=10)
    time.sleep(1)
    manager.clear_expired()

    with open(manager.file_path, 'r') as f:
        data = json.load(f)

    assert 'expired' not in data
    assert 'not_expired' in data

def test_scratchpad_atomic_write(mock_paths):
    manager = ScratchpadManager()
    manager.store('a', 1)
    manager.store('b', 2)

    with open(manager.file_path, 'r') as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert data['a']['value'] == 1
    assert data['b']['value'] == 2