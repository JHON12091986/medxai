"""Stub tests for core/task_manager/watcher.py"""
import pytest


def test_watcher_importable():
    import importlib
    mod = importlib.import_module("core.task_manager.watcher")
    assert mod is not None


@pytest.mark.skip(reason="stub — requires filesystem events; implement in integration suite")
def test_watcher_fires_on_new_file():
    pass


@pytest.mark.skip(reason="stub — requires filesystem events; implement in integration suite")
def test_watcher_ignores_excluded_paths():
    pass
