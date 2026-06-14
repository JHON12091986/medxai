import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.capabilities import CapabilityRegistry

@pytest.fixture
def temp_cap_file(tmp_path):
    """Create a temporary capabilities file for testing."""
    cap_file = tmp_path / "capabilities.json"
    with patch("core.capabilities.CAP_FILE", cap_file):
        yield cap_file

@pytest.fixture
def registry(temp_cap_file):
    """Return a fresh CapabilityRegistry instance."""
    # Reset singleton-like lock for tests if needed, 
    # but here we just want a fresh instance
    return CapabilityRegistry()

def test_registry_init_creates_file(temp_cap_file):
    assert not temp_cap_file.exists()
    registry = CapabilityRegistry()
    assert temp_cap_file.exists()
    data = json.loads(temp_cap_file.read_text())
    assert "shell" in data

def test_register_capability(registry, temp_cap_file):
    registry.register("new_tool", "/path/to/tool", "A test tool", "helper")
    
    cap = registry.get_capability("new_tool")
    assert cap["path"] == "/path/to/tool"
    assert cap["description"] == "A test tool"
    assert cap["healthy"] is True
    
    # Verify persistence
    data = json.loads(temp_cap_file.read_text())
    assert "new_tool" in data

def test_list_capabilities(registry):
    caps = registry.list_capabilities()
    assert len(caps) >= 8 # Default caps
    names = [c["name"] for c in caps]
    assert "shell" in names
    assert "web" in names

def test_is_healthy(registry):
    assert registry.is_healthy("shell") is True
    assert registry.is_healthy("non_existent") is True # Default True

@pytest.mark.asyncio
async def test_mark_unhealthy_healthy(registry, temp_cap_file):
    await registry.mark_unhealthy("shell", "connection error")
    assert registry.is_healthy("shell") is False
    cap = registry.get_capability("shell")
    assert cap["error"] == "connection error"
    
    # Verify persistence
    data = json.loads(temp_cap_file.read_text())
    assert data["shell"]["healthy"] is False

    await registry.mark_healthy("shell")
    assert registry.is_healthy("shell") is True
    assert "error" not in registry.get_capability("shell")

def test_status_output(registry):
    status = registry.status()
    assert "Tool capabilities:" in status
    assert "✅ shell" in status
    
    # Mock an unhealthy tool
    registry._caps["web"]["healthy"] = False
    registry._caps["web"]["error"] = "timeout"
    status = registry.status()
    assert "❌ web — timeout" in status
