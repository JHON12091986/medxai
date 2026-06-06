import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config_imports():
    from core.config import NinaConfig
    assert NinaConfig

def test_router_imports():
    from core.router import HybridRouter
    assert HybridRouter

def test_agent_imports():
    from core.agent import AgentLoop
    assert AgentLoop

def test_memory_imports():
    from core.memory import MemorySystem
    assert MemorySystem

def test_capabilities_imports():
    from core.capabilities import CapabilityRegistry
    assert CapabilityRegistry

def test_hotreload_imports():
    from core.hotreload import ConfigHotReload
    assert ConfigHotReload

def test_shell_tool_imports():
    from tools.shell import run
    assert run

def test_system_tool_imports():
    from tools.system import get_ram_used_gb, get_temps
    assert get_ram_used_gb
    assert get_temps

def test_upgrade_pipeline_imports():
    from tools.upgradepipeline import UpgradePipeline
    assert UpgradePipeline

def test_crons_manager_imports():
    from crons.manager import TaskScheduler
    assert TaskScheduler
