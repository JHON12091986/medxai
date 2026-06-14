import sys
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.mark.smoke
def test_config_imports():
    from core.config import NinaConfig
    assert NinaConfig

@pytest.mark.smoke
def test_router_imports():
    from core.router import HybridRouter
    assert HybridRouter

@pytest.mark.smoke
def test_agent_imports():
    from core.agent import AgentLoop
    assert AgentLoop

@pytest.mark.smoke
def test_memory_imports():
    from core.memory import MemorySystem
    assert MemorySystem

@pytest.mark.smoke
def test_capabilities_imports():
    from core.capabilities import CapabilityRegistry
    assert CapabilityRegistry

@pytest.mark.smoke
def test_hotreload_imports():
    from core.hotreload import ConfigHotReload
    assert ConfigHotReload

@pytest.mark.smoke
def test_shell_tool_imports():
    from tools.shell import run
    assert run

@pytest.mark.smoke
def test_system_tool_imports():
    from tools.system import get_ram_used_gb, get_temps
    assert get_ram_used_gb
    assert get_temps

@pytest.mark.smoke
def test_upgrade_pipeline_imports():
    from tools.upgradepipeline import UpgradePipeline
    assert UpgradePipeline

@pytest.mark.smoke
def test_crons_manager_imports():
    from crons.manager import TaskScheduler
    assert TaskScheduler

@pytest.mark.smoke
def test_nina_class_name():
    """Guard: core/nina.py class must be named 'Nina'. Catches agent renames."""
    from core.nina import Nina
    assert Nina.__name__ == "Nina", f"Expected 'Nina', got '{Nina.__name__}' — update main.py import"

@pytest.mark.smoke
def test_hybridrouter_has_reset_daily():
    """Guard: HybridRouter.reset_daily must exist — called by crons/manager.py at startup."""
    from core.router import HybridRouter
    assert callable(getattr(HybridRouter, 'reset_daily', None)), \
        "HybridRouter.reset_daily missing — crons/manager.py will AttributeError at startup"

@pytest.mark.smoke
def test_main_imports_nina():
    """Guard: main.py must be able to import Nina from core.nina."""
    import importlib.util, ast, pathlib
    src = pathlib.Path("main.py").read_text()
    tree = ast.parse(src)
    imports = [
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "core.nina"
        for alias in node.names
    ]
    assert "Nina" in imports, f"main.py imports {imports} from core.nina — expected 'Nina'"
