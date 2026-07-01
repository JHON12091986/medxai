"""
NINA OpenTelemetry Observability (MT-8)
Traces LLM decision spans, latency metrics, and API payloads natively.
"""
from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nina.observability_otel")

@dataclass
class OTelSpan:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    children: List[OTelSpan] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def end(self):
        self.end_time = time.time()
        latency_ms = (self.end_time - self.start_time) * 1000.0
        logger.info(f"OTel Span '{self.name}' complete. Latency: {latency_ms:.2f}ms. Attributes: {self.attributes}")


class OTelTracker:
    """A standard compliant OpenTelemetry mockup tracer for tracing LLM execution spans."""
    def __init__(self):
        self.active_spans: List[OTelSpan] = []

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> OTelSpan:
        span = OTelSpan(name=name, attributes=attributes or {})
        self.active_spans.append(span)
        return span


# Global instance
otel_tracker = OTelTracker()
