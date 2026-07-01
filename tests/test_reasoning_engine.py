import pytest
from unittest.mock import AsyncMock, MagicMock
from core.reasoning_engine import ReasoningEngine

@pytest.mark.asyncio
async def test_reasoning_engine_final_answer():
    mock_dispatcher = MagicMock()
    mock_plan = MagicMock()
    mock_plan.execute = AsyncMock(return_value='{"thought": "I have enough info.", "action_type": "FINAL_ANSWER", "action_name": "", "action_content": "The answer is 42, which is the ultimate answer to life, universe, and everything."}')
    mock_dispatcher.dispatch.return_value = mock_plan

    engine = ReasoningEngine(dispatcher=mock_dispatcher)
    result = await engine.reason("What is the meaning of life?")
    
    assert result.answer == "The answer is 42, which is the ultimate answer to life, universe, and everything."
    assert len(result.trace) == 1
    assert result.trace[0][0] == "thought"
