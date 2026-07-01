"""Stub tests for core/agy_briefing.py"""
import pytest


def test_agy_briefing_importable():
    """Module can be imported without error."""
    import importlib
    mod = importlib.import_module("core.agy_briefing")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when agy_briefing API is stable")
def test_agy_briefing_build_returns_string():
    pass


@pytest.mark.skip(reason="stub — implement when agy_briefing API is stable")
def test_agy_briefing_empty_context():
    pass
