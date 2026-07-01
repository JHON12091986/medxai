import pytest
from unittest.mock import AsyncMock, MagicMock
from core.reasoning_engine import ReasoningEngine
from core.cognitive import registry, CognitivePlanner
from core.agents import agent_mesh, A2AMessage
from core.graph_rag import graph_rag
from core.autonomy_ratchet import autonomy_ratchet, AutonomyTier
from tools.unsloth_exporter import UnslothExporter

@pytest.mark.asyncio
async def test_lt1_modular_cognitive_layer():
    # Verify cognitive planner hot-swapping & planning
    mock_router = MagicMock()
    mock_router.route = AsyncMock(return_value='[{"id": "t1", "label": "test", "description": "desc", "dependencies": []}]')
    
    planner = CognitivePlanner(router=mock_router)
    plan = await planner.generate_plan("Do something", {})
    assert len(plan) == 1
    assert plan[0]["id"] == "t1"
    
    # Verify reasoning engine hot swapping
    engine = ReasoningEngine(router=mock_router)
    assert registry.has("cognitive_planner")
    
    class CustomPlanner:
        @property
        def name(self): return "cognitive_planner"
        @property
        def version(self): return "2.0.0"
        async def generate_plan(self, goal, context):
            return [{"id": "custom", "label": "custom_task", "description": "desc", "dependencies": []}]
            
    custom_planner = CustomPlanner()
    engine.hot_swap_module("cognitive_planner", custom_planner)
    assert engine.planner == custom_planner
    assert registry.get("cognitive_planner") == custom_planner

@pytest.mark.asyncio
async def test_lt2_multi_agent_mesh():
    # Verify agent A2A message exchange
    msg = A2AMessage(
        sender="PlannerAgent",
        recipient="ResearchAgent",
        subject="Request Search",
        content="NINA autonomy"
    )
    reply = await agent_mesh.send_message(msg)
    assert reply is not None
    assert reply.sender == "ResearchAgent"
    assert "Successfully researched" in reply.content

@pytest.mark.asyncio
async def test_lt3_graph_rag():
    # Verify GraphRAG query execution
    res = await graph_rag.hybrid_query("autonomy")
    assert "query" in res
    assert "db_results" in res
    assert "context" in res

def test_lt4_autonomy_ratchet():
    # Verify risk classification and execution checks
    from core.autonomy_ratchet import ActionRisk, Rung
    # OBSERVE (0) risk should always be allowed
    assert autonomy_ratchet.can_execute(ActionRisk.OBSERVE)
    # Rung ceiling checks
    assert autonomy_ratchet.rung <= Rung.STAGED

def test_lt5_unsloth_exporter():
    # Verify Unsloth exporter instantiation and execution
    exporter = UnslothExporter()
    success = exporter.export_to_alpaca("data/test_alpaca_dataset.json")
    assert success
