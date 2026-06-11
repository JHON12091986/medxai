import pytest
from pathlib import Path
from tools.files import preview_diff
from tools.git_ops import status, diff, _safe


@pytest.mark.asyncio
async def test_preview_diff():
    # Setup
    test_file = Path("data/workspace/test_file.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("line 1\nline 2\n")

    new_content = "line 1\nline 2\nline 3\n"
    diff_output = await preview_diff("test_file.txt", new_content)

    assert "line 3" in diff_output
    assert "+line 3" in diff_output

    # Teardown
    test_file.unlink()


@pytest.mark.asyncio
async def test_git_status(monkeypatch):
    import subprocess

    class MockProcess:
        stdout = "On branch main"

    def mock_run(*args, **kwargs):
        return MockProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    output = await status()
    assert "On branch main" in output


@pytest.mark.asyncio
async def test_git_diff(monkeypatch):
    import subprocess

    class MockProcess:
        stdout = "--- a/file\n+++ b/file"

    def mock_run(*args, **kwargs):
        return MockProcess()

    monkeypatch.setattr(subprocess, "run", mock_run)

    output = await diff()
    assert "--- a/file" in output


def test_git_ops_safe_path():
    with pytest.raises(PermissionError):
        _safe("../../../etc/passwd")
