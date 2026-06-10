import pytest
import sys
from core.agent_loop import AgentLoop, think, plan, act, ThinkResult, PlanResult, ActResult
from unittest.mock import MagicMock, patch

def test_think_returns_think_result():
    res = think("check status", {})
    assert isinstance(res, ThinkResult)

def test_think_unknown_intent():
    res = think("xyzzy gibberish", {})
    assert res.intent == 'unknown'

def test_plan_returns_plan_result():
    t_res = ThinkResult(intent="search", confidence=0.8, raw_input="search something")
    res = plan(t_res, ['shell', 'search'])
    assert isinstance(res, PlanResult)

def test_plan_unknown_uses_shell():
    t_res = ThinkResult(intent="unknown", confidence=0.5, raw_input="xyzzy")
    res = plan(t_res, ['shell', 'search'])
    assert res.tool == 'shell'

def test_act_success():
    p_res = PlanResult(steps=[], tool="shell", estimated_tokens=10)
    res = act(p_res, {})
    assert res.ok is True

def test_act_records_to_hub():
    p_res = PlanResult(steps=[], tool="shell", estimated_tokens=10)

    # Create a mock for core.observability and get_hub
    mock_hub = MagicMock()
    mock_get_hub = MagicMock(return_value=mock_hub)
    mock_observability = MagicMock()
    mock_observability.get_hub = mock_get_hub

    # Patch sys.modules to return our mock for core.observability
    with patch.dict(sys.modules, {'core.observability': mock_observability}):
        res = act(p_res, {})
        assert res.ok is True
        mock_get_hub.assert_called_once()
        mock_hub.record_task.assert_called_once_with(ok=True)

@patch("core.agent_loop.think")
@patch("core.agent_loop.plan")
@patch("core.agent_loop.act")
def test_agent_loop_run_end_to_end(mock_act, mock_plan, mock_think):
    mock_think.return_value = ThinkResult(intent="search", confidence=0.8, raw_input="test input")
    mock_plan.return_value = PlanResult(steps=[], tool="shell", estimated_tokens=10)
    mock_act.return_value = ActResult(ok=True, output="", error=None, tokens_used=5)

    loop = AgentLoop(router=MagicMock(), tools=['shell'])
    res = loop.run("test input")
    assert isinstance(res, ActResult)
