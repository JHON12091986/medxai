"""
Unit tests for SandboxedExecutor in core/sandbox.py.
"""
from __future__ import annotations
import pytest
from core.sandbox import SandboxedExecutor

@pytest.mark.asyncio
async def test_sandbox_run_python():
    executor = SandboxedExecutor()
    res = await executor.run_python("print('hello from sandbox')")
    assert res.success
    assert res.exit_code == 0
    assert "hello from sandbox" in res.stdout

@pytest.mark.asyncio
async def test_sandbox_run_python_syntax_error():
    executor = SandboxedExecutor()
    res = await executor.run_python("if true print('invalid')")
    assert not res.success
    assert res.exit_code != 0
    assert len(res.stderr) > 0
