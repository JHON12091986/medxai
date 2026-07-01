"""Stub tests for core/task_manager/cli.py"""
import pytest


def test_cli_importable():
    import importlib
    mod = importlib.import_module("core.task_manager.cli")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement with Click test runner when CLI is stable")
def test_cli_help_exits_zero():
    pass


@pytest.mark.skip(reason="stub — implement with Click test runner when CLI is stable")
def test_cli_list_command():
    pass
