"""telemetry/tracker.py — OTel span tracker re-export shim.
Blueprint: nina_blueprint_23.06.2026.md § II
Pass 2 · 24 Jun 2026

Tracker wraps NinaTracer — the OpenTelemetry/Jaeger span emitter.
All logic lives in core/otel_tracer.py — this is a thin shim.
"""
try:
    from core.otel_tracer import NinaTracer as Tracker  # type: ignore[import]
except ImportError:
    # otel_tracer may not exist if opentelemetry-sdk is not installed
    import logging as _logging

    class Tracker:  # type: ignore[no-redef]
        """Null-object fallback when OTel is unavailable."""
        def __init__(self, *a, **kw):
            _logging.getLogger("nina.telemetry").warning(
                "OTel NinaTracer unavailable — using null tracker"
            )

        def start_span(self, name: str, **kw):
            return self

        def end_span(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

__all__ = ["Tracker"]
