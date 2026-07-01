"""Stub tests for core/cognition/per_loop.py"""
import pytest


def test_per_loop_importable():
    import importlib
    mod = importlib.import_module("core.cognition.per_loop")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when PerLoop API is stable")
def test_loop_single_step():
    pass


@pytest.mark.skip(reason="stub — implement when PerLoop API is stable")
def test_loop_halts_on_done():
    pass
