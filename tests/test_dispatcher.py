"""Stub tests for core/task_manager/dispatcher.py"""
import pytest


def test_dispatcher_importable():
    import importlib
    mod = importlib.import_module("core.task_manager.dispatcher")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when Dispatcher API is stable")
def test_dispatch_queues_task():
    pass


@pytest.mark.skip(reason="stub — implement when Dispatcher API is stable")
def test_dispatch_unknown_type_raises():
    pass
