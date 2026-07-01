"""
Unit tests for NINA OpenTelemetry Observability.
"""
from __future__ import annotations
from core.observability_otel import otel_tracker

def test_otel_tracker_spans():
    span = otel_tracker.start_span("test_llm_call", {"model": "qwen2.5-coder"})
    assert span.name == "test_llm_call"
    assert span.attributes["model"] == "qwen2.5-coder"
    assert span.end_time is None

    span.set_attribute("status", "success")
    span.end()

    assert span.end_time is not None
    assert span.attributes["status"] == "success"
