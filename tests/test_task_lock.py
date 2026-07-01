"""Stub tests for core/planner/task_lock.py"""
import pytest


def test_task_lock_importable():
    import importlib
    mod = importlib.import_module("core.planner.task_lock")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when TaskLock API is stable")
def test_acquire_lock_succeeds():
    pass


@pytest.mark.skip(reason="stub — implement when TaskLock API is stable")
def test_double_acquire_raises():
    pass


@pytest.mark.skip(reason="stub — implement when TaskLock API is stable")
def test_release_allows_reacquire():
    pass
