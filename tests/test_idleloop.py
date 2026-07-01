import pytest
import asyncio
from core.idleloop import IdleProposalLoop

class MockConfig:
    idle_threshold_min = 0
    ram_guard_gb = 100
    idle_report_min = 0

class MockRouter:
    async def route(self, *args, **kwargs):
        return "IMPACT: High\n- Suggestion 1\n- Suggestion 2"

@pytest.mark.asyncio
async def test_idle_loop_single_iteration(nina_tmp_dir, monkeypatch):
    monkeypatch.setattr("core.idleloop.PROPOSALS_DIR", nina_tmp_dir / "proposals")

    loop_obj = IdleProposalLoop(config=MockConfig(), router=MockRouter(), telegram=None)

    class MockPlan:
        async def execute(self):
            return "IMPACT: High\n- Suggestion 1\n- Suggestion 2"

    monkeypatch.setattr(loop_obj.dispatcher, "dispatch", lambda *args, **kwargs: MockPlan())

    await loop_obj._generate_proposal()

    proposals_dir = nina_tmp_dir / "proposals"
    assert proposals_dir.exists()
    files = list(proposals_dir.glob("*.md"))
    assert len(files) == 1

    content = files[0].read_text()
    assert "Suggestion 1" in content
    assert "Suggestion 2" in content
    assert "Impact: High" in content

@pytest.mark.asyncio
async def test_idle_loop_handles_exception(nina_tmp_dir, monkeypatch):
    monkeypatch.setattr("core.idleloop.PROPOSALS_DIR", nina_tmp_dir / "proposals")

    loop_obj = IdleProposalLoop(config=MockConfig(), router=MockRouter(), telegram=None)

    call_count = 0

    async def mock_generate_proposal():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("Simulated failure")
        else:
            raise asyncio.CancelledError()

    monkeypatch.setattr(loop_obj, "_generate_proposal", mock_generate_proposal)

    original_sleep = asyncio.sleep
    async def mock_sleep(*args, **kwargs):
        return await original_sleep(0)
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    await loop_obj._loop()

    assert call_count == 2
