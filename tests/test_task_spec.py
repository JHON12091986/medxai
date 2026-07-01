"""Stub tests for core/task_manager/task_spec.py"""
import pytest


def test_task_spec_importable():
    import importlib
    mod = importlib.import_module("core.task_manager.task_spec")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when TaskSpec schema is stable")
def test_task_spec_valid_construction():
    pass


@pytest.mark.skip(reason="stub — implement when TaskSpec schema is stable")
def test_task_spec_missing_required_field_raises():
    pass


@pytest.mark.skip(reason="stub — implement when TaskSpec schema is stable")
def test_task_spec_serialise_roundtrip():
    pass
