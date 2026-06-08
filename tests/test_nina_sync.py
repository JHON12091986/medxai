import os
import sys
import time
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.nina_sync import NINASync


def test_debounce_batches_rapid_changes(tmp_path):
    """10 rapid file changes → exactly 1 commit"""
    sync = NINASync(repo_path=tmp_path, dry_run=True)
    sync._do_commit_push = MagicMock()

    # Create fake files to test
    (tmp_path / ".ninaignore").write_text("")

    for i in range(10):
        filepath = str(tmp_path / f"file_{i}.txt")
        sync._schedule_commit(filepath)
        time.sleep(0.01) # rapid changes

    assert sync._do_commit_push.call_count == 0
    assert len(sync._pending_files) == 10

    # Wait for debounce
    time.sleep(5.1)

    # The timer should have called _do_commit_push
    assert sync._do_commit_push.call_count == 1


def test_ninaignore_excludes_env(tmp_path):
    """.env change must never reach git add"""
    sync = NINASync(repo_path=tmp_path, dry_run=True)

    ignore_path = tmp_path / ".ninaignore"
    ignore_path.write_text(".env\n")
    sync._ninaignore = sync._load_ninaignore()

    env_path = str(tmp_path / ".env")
    sync._schedule_commit(env_path)

    assert env_path not in sync._pending_files


@patch("tools.nina_sync.subprocess.run")
def test_stash_pull_pop_happy_path(mock_run, tmp_path):
    """Remote ahead by 1 commit → clean pull without conflict"""
    sync = NINASync(repo_path=tmp_path)

    # Mock successful git commands
    mock_run.return_value.stdout = "Success\n"
    mock_run.return_value.stderr = ""
    mock_run.return_value.returncode = 0

    sync._pull_remote()

    # Should call stash, pull, stash pop
    assert mock_run.call_count == 3
    calls = mock_run.call_args_list
    assert calls[0][0][0] == ["git", "stash"]
    assert calls[1][0][0] == ["git", "pull", "--no-edit", "origin", "main"]
    assert calls[2][0][0] == ["git", "stash", "pop"]


@patch("tools.nina_sync.subprocess.run")
def test_conflict_pauses_sync(mock_run, tmp_path):
    """stash pop conflict → sync_paused=True + Telegram called"""
    import subprocess

    sync = NINASync(repo_path=tmp_path)
    sync._handle_conflict = MagicMock()

    def side_effect(*args, **kwargs):
        if "pop" in args[0]:
            # Simulate a conflict error during pop
            raise subprocess.CalledProcessError(1, cmd=args[0], output="Merge conflict", stderr="conflict")
        # For stash and pull
        mock = MagicMock()
        mock.stdout = "Saved stash"
        return mock

    mock_run.side_effect = side_effect

    sync._pull_remote()

    assert sync._handle_conflict.call_count == 1
    assert "conflict" in sync._handle_conflict.call_args[0][0]


def test_dry_run_no_git_calls(tmp_path):
    """--dry-run logs actions but never calls subprocess"""
    sync = NINASync(repo_path=tmp_path, dry_run=True)

    with patch("tools.nina_sync.subprocess.run") as mock_run:
        result = sync._run_git(["add", "file.txt"])
        assert result == "dry-run"
        assert mock_run.call_count == 0


def test_rate_limiter_prevents_spam(tmp_path):
    """max 1 commit per 5s enforced"""
    sync = NINASync(repo_path=tmp_path, dry_run=True)
    sync._run_git = MagicMock()
    sync._check_secrets = MagicMock(return_value=False)

    # First commit
    sync._pending_files.add(str(tmp_path / "file1.txt"))
    sync._do_commit_push()
    assert sync._last_commit_time > 0
    first_commit_time = sync._last_commit_time

    # Second commit immediately after
    sync._pending_files.add(str(tmp_path / "file2.txt"))
    sync._do_commit_push()

    # Last commit time should not be updated since rate limit hit
    assert sync._last_commit_time == first_commit_time
    # Timer should be restarted
    assert sync._debounce_timer is not None
    assert sync._debounce_timer.is_alive()

    # Cancel timer so test doesn't hang
    sync._debounce_timer.cancel()

def test_cli_parsing():
    import argparse
    from tools.nina_sync import NINASync
    # Simulating simple initialization
    sync = NINASync(branch="test", interval=60, protect_main=True, dry_run=True)
    assert sync.branch == "test"
    assert sync.interval == 60
    assert sync.protect_main is True
    assert sync.dry_run is True

def test_setup_logging_rotation(tmp_path):
    import logging
    from logging.handlers import RotatingFileHandler
    sync = NINASync(repo_path=tmp_path, dry_run=True)

    logger = logging.getLogger("nina_sync")
    handlers = logger.handlers

    assert any(isinstance(h, RotatingFileHandler) for h in handlers)

    for h in handlers:
        if isinstance(h, RotatingFileHandler):
            assert h.maxBytes == 5 * 1024 * 1024
            assert h.backupCount == 3
            break
