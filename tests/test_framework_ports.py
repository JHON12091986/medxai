"""
NINA Multi-Agent Framework Ports Verification Test Suite
Tests for: Swarm Handoffs, LangGraph Checkpoints, AutoGen Conversational Critique,
CrewAI Shared Memory, and Agno Schema Validation.
"""
import pytest
from core.swarm import SwarmAgent, SwarmHandoff, SwarmRunner
from core.checkpoint import SqliteCheckpointManager
from core.autogen import ConversationalCritiqueLoop
from core.crew import CrewAgent, CrewTask, Crew
from core.schema_val import extract_and_parse_json, validate_against_schema, SchemaValidationError

# ==================== 1. OPENAI SWARM TESTS ====================
def test_swarm_handoff():
    agent_a = SwarmAgent(name="AgentA", instructions="Focus on writing.")
    agent_b = SwarmAgent(name="AgentB", instructions="Focus on reviewing.")
    
    runner = SwarmRunner(
        agents={"AgentA": agent_a, "AgentB": agent_b},
        default_agent_name="AgentA"
    )
    
    # Test standard turn
    res = runner.run_step("AgentA", "Hello there", {})
    assert "Response from AgentA" in res
    
    # Test handoff trigger via keyword heuristic
    handoff_res = runner.run_step("AgentA", "Handoff to AgentB please", {})
    assert isinstance(handoff_res, SwarmHandoff)
    assert handoff_res.next_agent.name == "AgentB"
    assert "AgentA" in handoff_res.context_update["previous_agent"]


# ==================== 2. LANGGRAPH TESTS ====================
def test_langgraph_sqlite_checkpoint(tmp_path):
    db_file = tmp_path / "test_checkpoints.db"
    manager = SqliteCheckpointManager(db_path=str(db_file))
    
    session_id = "test-session-123"
    state_step_1 = {"current_node": "node_1", "buffer": "initial"}
    state_step_2 = {"current_node": "node_2", "buffer": "updated"}
    
    # Save step 1
    manager.save_checkpoint(session_id, step_id=1, state=state_step_1)
    # Save step 2
    manager.save_checkpoint(session_id, step_id=2, state=state_step_2)
    
    # Load latest
    latest = manager.load_latest_checkpoint(session_id)
    assert latest is not None
    step_id, loaded_state = latest
    assert step_id == 2
    assert loaded_state["current_node"] == "node_2"
    
    # Clear
    manager.clear_checkpoints(session_id)
    assert manager.load_latest_checkpoint(session_id) is None


# ==================== 3. AUTOGEN TESTS ====================
def test_autogen_conversational_correction():
    # Let's mock a coder function that returns incorrect code first,
    # then repairs it on receiving the critique feedback.
    coder_responses = [
        "def broken_syntax(:\n    pass",  # Invalid syntax
        "def broken_syntax():\n    pass"  # Valid syntax
    ]
    response_idx = 0
    
    def mock_coder(feedback, history):
        nonlocal response_idx
        res = coder_responses[response_idx]
        response_idx += 1
        return res
        
    loop = ConversationalCritiqueLoop(coder_func=mock_coder, max_turns=3)
    
    # Directly verify step functionality
    check1 = loop.verify_code("def foo(:\n    pass")
    assert check1["passed"] is False
    assert check1["error"] is not None
    
    check2 = loop.verify_code("def foo():\n    pass")
    assert check2["passed"] is True


# ==================== 4. CREWAI TESTS ====================
def test_crew_shared_memory():
    agent_exec = CrewAgent(
        name="Exec",
        role="Executor",
        goal="Generate a baseline",
        backstory="A precise executor"
    )
    
    task1 = CrewTask(
        description="Write a base component",
        expected_output="A python function",
        assigned_agent="Exec"
    )
    
    crew = Crew(agents=[agent_exec], tasks=[task1])
    
    # Shared memory read/write
    crew.set_shared_memory("framework", "NINA")
    assert crew.get_shared_memory("framework") == "NINA"
    
    # Execution
    def dummy_executor(prompt):
        assert "Role: Executor" in prompt
        assert "framework: NINA" in prompt
        return "def my_func(): pass"
        
    completed_tasks = crew.execute_sequential(dummy_executor)
    assert len(completed_tasks) == 1
    assert completed_tasks[0].completed is True
    assert completed_tasks[0].output == "def my_func(): pass"
    assert crew.get_shared_memory("last_task_output") == "def my_func(): pass"


# ==================== 5. AGNO TESTS ====================
def test_agno_schema_validation():
    raw_text = """
    Here is your structured JSON output:
    ```json
    {
        "status": "success",
        "code_score": 95,
        "is_approved": true
    }
    ```
    """
    
    parsed = extract_and_parse_json(raw_text)
    assert parsed["status"] == "success"
    assert parsed["code_score"] == 95
    assert parsed["is_approved"] is True
    
    # Successful validation
    validate_against_schema(parsed, {
        "status": str,
        "code_score": int,
        "is_approved": bool
    })
    
    # Failed validation on missing key
    with pytest.raises(SchemaValidationError) as exc:
        validate_against_schema(parsed, {"missing_key": str})
    assert "Missing required schema key" in str(exc.value)
    
    # Failed validation on type mismatch
    with pytest.raises(SchemaValidationError) as exc:
        validate_against_schema(parsed, {"code_score": str})
    assert "must be of type" in str(exc.value)


# ==================== 6. INTEGRATION TESTS FOR F-01 & F-06 ====================
@pytest.mark.asyncio
async def test_f01_agent_critique_integration(monkeypatch):
    # Mocking dispatcher and ClassifiedTask to test F-01 ConversationalCritiqueLoop in _self_check
    class MockPlan:
        async def execute(self):
            return "```python\ndef corrected_code():\n    return 42\n```"
            
    class MockDispatcher:
        def dispatch(self, prompt, force_tier=None):
            return MockPlan()

    class MockRouter:
        def __init__(self):
            self.dispatcher = None

    from core.agent import AgentLoop
    from core.router import ClassifiedTask
    
    agent = AgentLoop(config=None, router=MockRouter(), memory=None, tools={})
    agent.dispatcher = MockDispatcher()
    
    # Task configured to trigger self check
    task = ClassifiedTask(task_type="coding", complexity="SIMPLE")
    
    draft_with_syntax_error = "Here is some code:\n```python\ndef broken(:\n    pass\n```"
    
    # Execute self check
    corrected = await agent._self_check(
        goal="Write a dummy function",
        draft=draft_with_syntax_error,
        task=task
    )
    
    assert "def corrected_code()" in corrected
    assert "broken" not in corrected


@pytest.mark.asyncio
async def test_f06_reminder_context_propagation(tmp_path, monkeypatch):
    import json
    from datetime import datetime, timedelta
    from pathlib import Path
    from core.nina import Nina
    
    class MockConfig:
        def __init__(self):
            self.telegram_bot_token = "mock"
            self.authorized_user_id = "mock"
            self.telegram_chat_id = "mock"
            self.log_level = "INFO"
            self.dead_man_ping_url = None
            self.idle_auto_approve = False

    class MockRouter:
        def __init__(self, config=None):
            pass

    monkeypatch.setattr("core.nina.load_config", lambda: MockConfig())
    monkeypatch.setattr("core.nina.HybridRouter", MockRouter)
    
    nina = Nina()
    # Mock database path and reminders file path to use temporary directory
    nina.shared_memory_path = str(tmp_path / "crew_shared_memory.json")
    
    # Setup shared memory context
    nina.set_shared_memory("reminder_context", "Task focus: banking audit")
    
    # Write mock reminder to reminders.json
    rem_file = tmp_path / "reminders.json"
    reminders_data = [{
        "id": "test_rem_123",
        "text": "Check morning reports",
        "remind_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "repeat": "none",
        "fired": False
    }]
    
    rem_file.write_text(json.dumps(reminders_data), encoding="utf-8")
    
    # Mock send_message to inspect output
    sent_messages = []
    class MockTelegram:
        async def send_message(self, text):
            sent_messages.append(text)
            
    nina.telegram = MockTelegram()
    
    # Patch Path to point to our temp reminders file in check_reminders
    original_exists = Path.exists

    def mock_exists(self):
        if "reminders.json" in str(self):
            return original_exists(rem_file)
        return original_exists(self)

    import builtins
    original_open = builtins.open

    def mock_open(file, *args, **kwargs):
        if "reminders.json" in str(file):
            return original_open(rem_file, *args, **kwargs)
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(builtins, "open", mock_open)
    
    await nina.check_reminders()
    
    assert len(sent_messages) == 1
    assert "Check morning reports" in sent_messages[0]
    assert "*Shared Context*:" in sent_messages[0]
    assert "banking audit" in sent_messages[0]

