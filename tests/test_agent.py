import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from core.agent import AgentLoop
from core.router import ClassifiedTask

# Disable Token Guard caching during tests to avoid cache hits in test runs
@pytest.fixture(autouse=True)
def disable_token_guard_cache():
    with patch('tools.nina_token_guard.TokenGuard._get_cached', return_value=None):
        yield

@pytest.fixture(autouse=True)
def mock_reflexion_engine():
    with patch('core.agent.ReflexionEngine.generate_reflection', new_callable=AsyncMock) as mock:
        yield mock

# Mock dependencies for AgentLoop
@pytest.fixture
def mock_config():
    mock = MagicMock()
    mock.agent_timeout_s = 60
    mock.ram_guard_gb = 999.0 # Set high to avoid physical host RAM skip during tests
    mock.thermal_critical_cpu = 90
    mock.thermal_critical_gpu = 80
    mock.thermal_guard_cpu = 70
    mock.thermal_guard_gpu = 60
    mock.thermal_warn_cpu = 50
    mock.thermal_warn_gpu = 40
    return mock

@pytest.fixture
def mock_router():
    mock = AsyncMock()
    mock.route.return_value = "FINAL: Test response"
    mock.single_turn.return_value = "Single turn response"
    return mock

@pytest.fixture
def mock_memory():
    mock = AsyncMock()
    mock.build_context.return_value = "mock_context"
    return mock

@pytest.fixture
def mock_tools():
    return {}

@pytest.fixture
def agent_loop(mock_config, mock_router, mock_memory, mock_tools):
    return AgentLoop(mock_config, mock_router, mock_memory, mock_tools)

class TestAgentLoop:
    @pytest.mark.asyncio
    async def test_init(self, mock_config, mock_router, mock_memory, mock_tools):
        agent = AgentLoop(mock_config, mock_router, mock_memory, mock_tools)
        assert agent.config == mock_config
        assert agent.router == mock_router
        assert agent.memory == mock_memory
        assert agent.tools == mock_tools

    @pytest.mark.asyncio
    async def test_run_timeout(self, agent_loop, mock_config, mock_router):
        mock_config.agent_timeout_s = 0.01 # Set a very short timeout
        goal = "Test goal"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []

        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            result = await agent_loop.run(goal, task, session_history)
            assert "Task timed out" in result

    @pytest.mark.asyncio
    async def test_run_success(self, agent_loop, mock_router):
        goal = "Test goal"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []

        # Mock _inner to return a final response
        with patch.object(agent_loop, '_inner', new_callable=AsyncMock) as mock_inner:
            mock_inner.return_value = "FINAL: Success"
            result = await agent_loop.run(goal, task, session_history)
            assert result == "FINAL: Success"
            mock_inner.assert_called_once_with(goal, task, session_history)

    @pytest.mark.asyncio
    async def test_self_check_should_run_and_return_reviewed(self, agent_loop, mock_router):
        goal = "Original goal"
        draft = "Initial draft"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        mock_router.route.side_effect = ["verification plan", "REVISE: please fix", "Reviewed response", "PASS", "VERIFIED"]
        
        with patch.object(agent_loop, '_should_self_check', return_value=True):
            result = await agent_loop._self_check(goal, draft, task, force_local=False)
            assert result == "Reviewed response"
            assert mock_router.route.call_count == 5

    @pytest.mark.asyncio
    async def test_self_check_should_not_run(self, agent_loop, mock_router):
        goal = "Original goal"
        draft = "Initial draft"
        task = ClassifiedTask(task_type="execute", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False) # Task type that doesn't trigger self-check
        
        with patch.object(agent_loop, '_should_self_check', return_value=False):
            result = await agent_loop._self_check(goal, draft, task, force_local=False)
            assert result == draft
            mock_router.route.assert_not_called()

    @pytest.mark.asyncio
    async def test_self_check_returns_original_on_router_failure(self, agent_loop, mock_router):
        goal = "Original goal"
        draft = "Initial draft"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        mock_router.route.side_effect = Exception("Router error")
        
        with patch.object(agent_loop, '_should_self_check', return_value=True):
            result = await agent_loop._self_check(goal, draft, task, force_local=False)
            assert result == draft # Should return original draft on error
            assert mock_router.route.call_count > 0
    
    @pytest.mark.asyncio
    async def test_inner_ram_guard_triggered(self, agent_loop, mock_config, mock_router, mock_memory):
        goal = "Test goal"
        task = ClassifiedTask(task_type="research", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []
        
        # Mock system.get_ram_used_gb to trigger the guard
        with patch('tools.system.get_ram_used_gb', return_value=mock_config.ram_guard_gb + 1):
            with patch.object(agent_loop, '_log_to_hud') as mock_log_to_hud:
                result = await agent_loop._inner(goal, task, session_history)
                mock_router.single_turn.assert_called_once_with(goal, session_history) # Should call single_turn
                mock_log_to_hud.assert_not_called()
                assert result == "Single turn response"

    @pytest.mark.asyncio
    async def test_inner_thermal_critical_aborts(self, agent_loop, mock_config):
        goal = "Test goal"
        task = ClassifiedTask(task_type="research", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []

        # Mock system.get_temps to trigger critical thermal abort
        with patch('tools.system.get_temps', return_value={"cpu": mock_config.thermal_critical_cpu + 1, "gpu": 0}):
            with patch.object(agent_loop, '_log_to_hud') as mock_log_to_hud:
                result = await agent_loop._inner(goal, task, session_history)
                assert "Agent loop aborted." in result
                mock_log_to_hud.assert_not_called()

    @pytest.mark.asyncio
    async def test_inner_thermal_guard_forces_local(self, agent_loop, mock_config, mock_router, mock_memory):
        goal = "Test goal"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []

        # Mock system.get_temps to trigger thermal guard (not critical)
        with patch('tools.system.get_temps', return_value={"cpu": mock_config.thermal_guard_cpu + 1, "gpu": 0}):
            mock_router.route.return_value = "FINAL: Local response"
            
            with patch.object(agent_loop, '_log_to_hud') as mock_log_to_hud:
                await agent_loop._inner(goal, task, session_history)
                assert mock_router.route.call_count >= 4
                for call_args in mock_router.route.call_args_list:
                    assert call_args[1].get('force_local') is True
                mock_log_to_hud.assert_called()

    @pytest.mark.asyncio
    async def test_inner_final_response_self_checks(self, agent_loop, mock_router, mock_memory):
        goal = "Test goal"
        task = ClassifiedTask(task_type="coding", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []

        # Mock router to return a FINAL response (including self-optimization flow and multi-pass check)
        mock_router.route.side_effect = [
            "blueprint content",
            "FINAL: Draft answer",
            "FINAL: Optimized draft answer",
            "verification plan",
            "REVISE: please fix",
            "Reviewed Final Answer",
            "PASS",
            "VERIFIED"
        ]
        
        with patch('tools.system.get_temps', return_value={"cpu": 40, "gpu": 40}):
            with patch('core.agent.ReasoningKernel.get_system_frame', return_value="system_frame"):
                with patch.object(agent_loop, '_should_self_check', return_value=True):
                    with patch.object(agent_loop, '_log_to_hud') as mock_log_to_hud:
                        result = await agent_loop._inner(goal, task, session_history)
                        assert result == "Reviewed Final Answer"
                        assert mock_router.route.call_count == 8
                        mock_log_to_hud.assert_called()

    @pytest.mark.asyncio
    async def test_inner_tool_execution(self, agent_loop, mock_router, mock_memory):
        goal = "Test goal"
        task = ClassifiedTask(task_type="execute", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []
        
        mock_tool_instance = AsyncMock()
        mock_tool_instance.run.return_value = "Tool output: hello"
        agent_loop.tools["shell"] = mock_tool_instance

        with patch('tools.system.get_temps', return_value={"cpu": 40, "gpu": 40}):
            with patch('core.agent.ReasoningKernel.get_system_frame', return_value="system_frame"):
                with patch.object(agent_loop, '_log_to_hud') as mock_log_to_hud:
                    # Mock router's calls for tool + feedback loop + optimization
                    mock_router.route.side_effect = [
                        "TOOL:shell INPUT:echo hello",
                        "FINAL: Tool executed",
                        "FINAL: Tool executed"
                    ]
                    
                    result = await agent_loop._inner(goal, task, session_history)
                    assert result == "Tool executed"
                    mock_tool_instance.run.assert_called_once_with("echo hello")
                    mock_log_to_hud.assert_called()

    @pytest.mark.asyncio
    async def test_inner_surgical_mode_skips_self_check(self, agent_loop, mock_router, mock_memory):
        goal = "SURGICAL: Fix the bug"
        task = ClassifiedTask(task_type="execute", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
        session_history = []
        mock_router.route.side_effect = ["FINAL: Done"]
        with patch('core.agent.ReasoningKernel.get_system_frame', return_value="system_frame"):
            result = await agent_loop._inner(goal, task, session_history)
            assert result == "Done"

    @pytest.mark.asyncio
    async def test_inner_debug_phase_transitions_and_write_block(self, agent_loop, mock_router, mock_memory):
        from core.router import STEP_BUDGETS
        STEP_BUDGETS["execute"] = 10
        try:
            goal = "DEBUG: Solve problem"
            task = ClassifiedTask(task_type="execute", estimated_tokens=100, is_parallel_candidate=False, is_sensitive=False)
            session_history = []
            
            mock_tool = AsyncMock()
            mock_tool.run.return_value = "Wrote file"
            agent_loop.tools["write_to_file"] = mock_tool
            agent_loop.tools["writetofile"] = mock_tool

            mock_router.route.side_effect = [
                "TOOL:write_to_file INPUT:dummy.py", # will be blocked because debug phase is FINDINGS
                "ROOT_CAUSE found.", # transition to ROOT_CAUSE
                "SURGICAL_FIX planned.", # transition to SURGICAL_FIX
                "EXECUTE edit.", # transition to execute
                "TOOL:write_to_file INPUT:dummy.py", # should now pass
                "FINAL: verified"
            ]

            with patch('tools.system.get_temps', return_value={"cpu": 40, "gpu": 40}):
                with patch('core.agent.ReasoningKernel.get_system_frame', return_value="system_frame"):
                    result = await agent_loop._inner(goal, task, session_history)
                    assert result == "verified"
                    # Check that write was indeed called after phase transitions
                    mock_tool.run.assert_called_once_with("dummy.py")
        finally:
            STEP_BUDGETS.pop("execute", None)





