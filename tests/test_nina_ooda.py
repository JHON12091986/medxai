"""Stub tests for core/nina_ooda.py"""
import pytest


def test_nina_ooda_importable():
    import importlib
    mod = importlib.import_module("core.nina_ooda")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when NinaOODA API is stable")
def test_observe_returns_snapshot():
    pass


@pytest.mark.skip(reason="stub — implement when NinaOODA API is stable")
def test_orient_scores_priorities():
    pass


@pytest.mark.skip(reason="stub — implement when NinaOODA API is stable")
def test_decide_emits_task():
    pass


@pytest.mark.skip(reason="stub — implement when NinaOODA API is stable")
def test_act_dispatches_task():
    pass
