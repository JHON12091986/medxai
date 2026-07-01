import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from core.circuit_breaker import BehavioralCircuitBreaker, CircuitState
from core.smart_router import ProviderMetrics
from core.memory import MemorySystem
from core.reflexion import ReflexionEngine

# Setup test database paths
TEST_METRICS_DB = "data/router/test_provider_metrics.db"
TEST_MEMORY_DB = "data/memory/test_knowledge_base.db"

@pytest.fixture(autouse=True)
def cleanup_dbs():
    # Remove files before test
    for db in [TEST_METRICS_DB, TEST_MEMORY_DB]:
        if os.path.exists(db):
            try:
                os.remove(db)
            except OSError:
                pass
    yield
    # Remove files after test
    for db in [TEST_METRICS_DB, TEST_MEMORY_DB]:
        if os.path.exists(db):
            try:
                os.remove(db)
            except OSError:
                pass

def test_circuit_breaker_basic():
    cb = BehavioralCircuitBreaker(cost_limit=0.1, max_tool_calls_per_run=3)
    assert cb.state == CircuitState.CLOSED
    
    # Tool call recording
    cb.record_tool_call("web", "http://google.com")
    assert cb.tool_call_count == 1
    
    # Exceeding tool calls
    cb.record_tool_call("web", "http://google.com")
    with pytest.raises(RuntimeError, match="Maximum tool calls exceeded"):
        cb.record_tool_call("web", "http://google.com")
    
    assert cb.state == CircuitState.OPEN

def test_circuit_breaker_dangerous_pattern():
    cb = BehavioralCircuitBreaker()
    with pytest.raises(RuntimeError, match="Dangerous command pattern detected"):
        cb.record_tool_call("shell", "rm -rf *")

def test_circuit_breaker_cost_limit():
    cb = BehavioralCircuitBreaker(cost_limit=0.01)
    cb.record_cost(0.005)
    assert cb.state == CircuitState.CLOSED
    with pytest.raises(RuntimeError, match="Cost limit exceeded"):
        cb.record_cost(0.006)
    assert cb.state == CircuitState.OPEN

def test_provider_metrics_smart_router():
    metrics = ProviderMetrics(db_path=TEST_METRICS_DB)
    metrics.record_execution("groq", 120.0, True, "coding")
    metrics.record_execution("groq", 80.0, True, "coding")
    metrics.record_execution("pollinations", 400.0, True, "coding")
    
    # groq has lower average latency
    best = metrics.select_best_provider("coding")
    assert best == "groq"
    
    # For unrecorded task types
    assert metrics.select_best_provider("sensitive") is None

@pytest.mark.asyncio
async def test_three_tier_cognitive_memory():
    # Use real test SQLite database
    mem = MemorySystem(db_path=TEST_MEMORY_DB)
    
    # Episodic memory test
    epi_id = await mem.episodic_add("session_123", "Write a python script", "Optimize loop next time")
    assert epi_id.startswith("epi_")
    
    epi_results = await mem.episodic_search("Write")
    assert len(epi_results) == 1
    assert epi_results[0]["goal"] == "Write a python script"
    assert epi_results[0]["reflection"] == "Optimize loop next time"
    
    # Procedural memory test
    await mem.procedural_record("sed -i", True, "sed -i 's/foo/bar/g' file")
    p_mem = await mem.procedural_get("sed -i")
    assert p_mem is not None
    assert p_mem["success_count"] == 1
    assert p_mem["working_arguments"] == "sed -i 's/foo/bar/g' file"

@pytest.mark.asyncio
async def test_reflexion_engine():
    dispatcher = MagicMock()
    plan = AsyncMock()
    plan.execute.return_value = "Reflection: Avoid infinite while loops. Always include safety breaks."
    dispatcher.dispatch.return_value = plan
    
    mem = MemorySystem(db_path=TEST_MEMORY_DB)
    
    reflection = await ReflexionEngine.generate_reflection(
        dispatcher=dispatcher,
        memory=mem,
        goal="Run a daemon",
        trace=["Step 1: started loop", "Step 2: CPU spiked"],
        success=False
    )
    
    assert "infinite" in reflection
    epi_search = await mem.episodic_search("daemon")
    assert len(epi_search) == 1
    assert "daemon" in epi_search[0]["goal"]
    assert "infinite" in epi_search[0]["reflection"]
