"""Stub tests for tools/guardian_engine.py"""
import pytest


def test_guardian_engine_importable():
    import importlib
    mod = importlib.import_module("tools.guardian_engine")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when GuardianEngine API is stable")
def test_scan_clean_repo_returns_no_violations():
    pass


@pytest.mark.skip(reason="stub — implement when GuardianEngine API is stable")
def test_scan_detects_untracked_governed_file():
    pass


@pytest.mark.skip(reason="stub — implement when GuardianEngine API is stable")
def test_scan_detects_missing_test_coverage():
    pass
