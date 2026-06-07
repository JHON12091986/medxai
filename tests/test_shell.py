import pytest
from unittest.mock import patch, MagicMock
from tools.shell import run

@pytest.mark.asyncio
async def test_allowlisted_bases():
    with patch('subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "dummy output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = await run("ls -la")
        assert result == "dummy output"

        result = await run("pwd")
        assert result == "dummy output"

        result = await run("df -h")
        assert result == "dummy output"

@pytest.mark.asyncio
async def test_blocked_bases():
    with patch('subprocess.run') as mock_run:
        result = await run("rm -rf /")
        assert "Blocked: 'rm' not in allowlist." in result

        result = await run("cd /tmp")
        assert "Blocked: 'cd' not in allowlist." in result

        result = await run("cat file.txt")
        assert "Blocked: 'cat' not in allowlist." in result

        result = await run("export VAR=value")
        assert "Blocked: 'export' not in allowlist." in result

        result = await run("VAR=value ls")
        assert "Blocked: 'VAR=value' not in allowlist." in result

        mock_run.assert_not_called()

@pytest.mark.asyncio
async def test_systemctl_allowlisted_subcommands():
    with patch('subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "active"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = await run("systemctl status nginx")
        assert result == "active"

        result = await run("systemctl start nginx")
        assert result == "active"

@pytest.mark.asyncio
async def test_systemctl_blocked_subcommands():
    with patch('subprocess.run') as mock_run:
        result = await run("systemctl isolate graphical.target")
        assert "Blocked: systemctl subcommand 'isolate' not allowed." in result

        result = await run("systemctl mask nginx")
        assert "Blocked: systemctl subcommand 'mask' not allowed." in result

        mock_run.assert_not_called()

@pytest.mark.asyncio
async def test_ollama_allowlisted_subcommands():
    with patch('subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "llama2"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = await run("ollama list")
        assert result == "llama2"

        result = await run("ollama run llama2")
        assert result == "llama2"

@pytest.mark.asyncio
async def test_ollama_blocked_subcommands():
    with patch('subprocess.run') as mock_run:
        result = await run("ollama cp /tmp/file /tmp/file2")
        assert "Blocked: ollama subcommand 'cp' not allowed." in result

        result = await run("ollama rm llama2")
        assert "Blocked: ollama subcommand 'rm' not allowed." in result

        mock_run.assert_not_called()

@pytest.mark.asyncio
async def test_illegal_shell_operators():
    with patch('subprocess.run') as mock_run:
        illegal_cmds = [
            "ls ; rm -rf /",
            "pwd && ls",
            "ls || pwd",
            "ls | grep txt",
            "echo `pwd`",
            "echo $(pwd)"
        ]

        for cmd in illegal_cmds:
            result = await run(cmd)
            assert "Blocked: shell operators not allowed in command." in result

        mock_run.assert_not_called()
