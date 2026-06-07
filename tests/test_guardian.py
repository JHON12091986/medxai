import subprocess
from unittest.mock import patch, MagicMock

import guardian_engine

def test_run_cmd_success():
    with patch("guardian_engine.subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.stdout = "ok"
        mock_process.stderr = ""
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        stdout, stderr, rc = guardian_engine.run_cmd("echo mock")

        assert stdout == "ok"
        assert stderr == ""
        assert rc == 0
        mock_run.assert_called_once()

def test_run_cmd_timeout():
    with patch("guardian_engine.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="mock", timeout=30)

        stdout, stderr, rc = guardian_engine.run_cmd("sleep 100")

        assert stdout == ""
        assert stderr == "TIMEOUT"
        assert rc == 1

def test_run_cmd_exception():
    with patch("guardian_engine.subprocess.run") as mock_run:
        mock_run.side_effect = Exception("error")

        stdout, stderr, rc = guardian_engine.run_cmd("invalid_cmd")

        assert stdout == ""
        assert stderr == "error"
        assert rc == 1

def test_match_signatures_basic_match():
    log_text = "RuntimeError: TELEGRAMBOTTOKEN is missing"
    env_keys = {"TELEGRAMBOTTOKEN": "test"}

    with patch("builtins.open"):
        findings = guardian_engine.match_signatures(log_text, env_keys)

    # Assert that a finding for config.missing_env.telegrambottoken is present
    telegram_finding = None
    for f in findings:
        if f["id"] == "config.missing_env.telegrambottoken":
            telegram_finding = f
            break

    assert telegram_finding is not None
    assert telegram_finding["severity"] == "BLOCKER"

def test_match_signatures_missing_env():
    log_text = ""
    env_keys = {}

    with patch("builtins.open"):
        findings = guardian_engine.match_signatures(log_text, env_keys)

    telegram_finding = None
    for f in findings:
        if f["id"] == "config.missing_env.telegrambottoken":
            telegram_finding = f
            break

    assert telegram_finding is not None
    assert telegram_finding["severity"] == "BLOCKER"
    # Verify the env_check evidence is added
    assert any("[env_check] TELEGRAMBOTTOKEN absent or empty" in e for e in telegram_finding["evidence"])
