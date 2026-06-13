import pytest
from pathlib import Path

# Add project root to sys.path so we can import tools
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.files import _load_geminiignore as files_load_ignore, _is_ignored as files_is_ignored
from tools.ninaflash_core import _load_geminiignore as nina_load_ignore, _is_ignored as nina_is_ignored


def test_is_ignored_logic():
    # Test file implementations
    patterns = ['logs/', '*.pyc', 'data/plans/', '!data/session_checkpoint.json', 'venv/']

    assert files_is_ignored('logs/test.log', patterns) is True
    assert files_is_ignored('logs/subdir/test.log', patterns) is True
    assert files_is_ignored('main.pyc', patterns) is True
    assert files_is_ignored('some/path/test.pyc', patterns) is True
    assert files_is_ignored('data/plans/plan.txt', patterns) is True
    assert files_is_ignored('venv/lib/python.py', patterns) is True

    assert files_is_ignored('data/session_checkpoint.json', patterns) is False
    assert files_is_ignored('main.py', patterns) is False
    assert files_is_ignored('data/other.txt', patterns) is False

    # Test ninaflash implementations
    assert nina_is_ignored('logs/test.log', patterns) is True
    assert nina_is_ignored('main.pyc', patterns) is True
    assert nina_is_ignored('data/session_checkpoint.json', patterns) is False
    assert nina_is_ignored('main.py', patterns) is False


def test_load_geminiignore(tmp_path, monkeypatch):
    test_ignore = tmp_path / '.geminiignore'
    test_ignore.write_text("logs/\n*.pyc\n# comment\n!data/session_checkpoint.json\nvenv/")

    # monkeypatch Path('.geminiignore') for files
    import tools.files
    monkeypatch.setattr(tools.files, 'Path', lambda p: test_ignore if p == '.geminiignore' else Path(p))

    files_patterns = files_load_ignore()
    assert files_patterns == ['logs/', '*.pyc', 'venv/']

    # monkeypatch REPO_ROOT for ninaflash
    import tools.ninaflash_core
    monkeypatch.setattr(tools.ninaflash_core, 'REPO_ROOT', tmp_path)

    nina_patterns = nina_load_ignore()
    assert nina_patterns == ['logs/', '*.pyc', 'venv/']


@pytest.mark.asyncio
async def test_files_read_ignored(tmp_path, monkeypatch):
    import tools.files

    test_workspace = tmp_path / 'workspace'
    test_workspace.mkdir()
    (test_workspace / 'logs').mkdir()
    test_file = test_workspace / 'logs' / 'test.log'
    test_file.write_text("secret log data")

    # Mock WORKSPACE and _load_geminiignore
    monkeypatch.setattr(tools.files, 'WORKSPACE', test_workspace)
    monkeypatch.setattr(tools.files, '_load_geminiignore', lambda: ['logs/'])

    result = await tools.files.read('logs/test.log')
    assert "Access Denied:" in result
    assert "SEC-IGNORE (.geminiignore)" in result

    # Test allowed file
    test_allowed = test_workspace / 'main.py'
    test_allowed.write_text("print('hello')")
    result_allowed = await tools.files.read('main.py')
    assert result_allowed == "print('hello')"
