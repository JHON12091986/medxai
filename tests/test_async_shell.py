"""Stub tests for core/executor/async_shell.py"""
import pytest


def test_async_shell_importable():
    import importlib
    mod = importlib.import_module("core.executor.async_shell")
    assert mod is not None


@pytest.mark.skip(reason="stub — requires live subprocess; implement in integration suite")
def test_run_echo_command():
    pass


@pytest.mark.skip(reason="stub — requires live subprocess; implement in integration suite")
def test_run_nonexistent_command_raises():
    pass


@pytest.mark.skip(reason="stub — requires live subprocess; implement in integration suite")
def test_timeout_cancels_command():
    pass
