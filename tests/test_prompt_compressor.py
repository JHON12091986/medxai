"""Stub tests for core/cache/prompt_compressor.py"""
import pytest


def test_prompt_compressor_importable():
    import importlib
    mod = importlib.import_module("core.cache.prompt_compressor")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when PromptCompressor API is stable")
def test_compress_reduces_length():
    pass


@pytest.mark.skip(reason="stub — implement when PromptCompressor API is stable")
def test_compress_empty_string():
    pass


@pytest.mark.skip(reason="stub — implement when PromptCompressor API is stable")
def test_compress_below_budget_unchanged():
    pass
