"""core/otel_tracer.py — OpenTelemetry trace wrapper for NINA vNext.

Provides lightweight span context around:
  - Every LLM call (model, tokens, latency, provider)
  - Every tool call (name, args digest, success/failure)
  - Every routing decision (router, model chosen, why)
  - Agent loop steps (THINK / PLAN / ACT / OBSERVE / ADAPT)

Export targets (configured via env):
  NINA_OTEL_EXPORT=console   → pretty-print spans to stdout (dev default)
  NINA_OTEL_EXPORT=otlp      → send to OTLP endpoint (e.g., Jaeger, Grafana)
  NINA_OTEL_EXPORT=none      → disable tracing entirely

Design rules:
  - All span operations fail open — a tracing failure must never crash NINA.
  - Use async context managers everywhere for clean span lifecycle.
  - Sensitive content (prompts, responses) is truncated to 256 chars.
  - Use NinaTracer as a singleton: tracer = NinaTracer.get()

Usage:
    from core.otel_tracer import NinaTracer
    tracer = NinaTracer.get()

    async with tracer.llm_span("gpt-4o", provider="openai") as span:
        response = await router.chat(messages)
        span.set_tokens(prompt=512, completion=128)

    async with tracer.tool_span("web_search", args={"q": "NINA AI"}) as span:
        result = await tools.web_search("NINA AI")
        span.set_result_ok()
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator

log = logging.getLogger("nina.otel")

NINA_OTEL_EXPORT   = os.getenv("NINA_OTEL_EXPORT", "console")
NINA_OTEL_ENDPOINT = os.getenv("NINA_OTEL_ENDPOINT", "http://localhost:4317")
NINA_SERVICE_NAME  = os.getenv("NINA_SERVICE_NAME",  "nina")
MAX_ATTR_LEN       = 256   # truncate sensitive text attributes


@dataclass
class NinaSpan:
    """Lightweight span wrapper. Wraps OTel span if available, else no-op."""
    name: str
    _otel_span:  Any = field(default=None, repr=False)
    _start_ns:   int = field(default_factory=lambda: time.time_ns())
    _attrs:      dict = field(default_factory=dict)
    _events:     list = field(default_factory=list)
    _status_ok:  bool = True
    _error_msg:  str = ""

    def set_attribute(self, key: str, value: Any) -> None:
        safe = str(value)[:MAX_ATTR_LEN] if isinstance(value, str) else value
        self._attrs[key] = safe
        if self._otel_span:
            try:
                self._otel_span.set_attribute(key, safe)
            except Exception:
                pass

    def add_event(self, name: str, attrs: dict | None = None) -> None:
        self._events.append({"name": name, "attrs": attrs or {}})
        if self._otel_span:
            try:
                self._otel_span.add_event(name, attributes=attrs or {})
            except Exception:
                pass

    def set_error(self, msg: str) -> None:
        self._status_ok = False
        self._error_msg = msg
        if self._otel_span:
            try:
                from opentelemetry.trace import StatusCode
                self._otel_span.set_status(StatusCode.ERROR, msg)
                self._otel_span.record_exception(Exception(msg))
            except Exception:
                pass

    def set_ok(self) -> None:
        self._status_ok = True
        if self._otel_span:
            try:
                from opentelemetry.trace import StatusCode
                self._otel_span.set_status(StatusCode.OK)
            except Exception:
                pass

    # Convenience setters
    def set_tokens(self, prompt: int = 0, completion: int = 0) -> None:
        self.set_attribute("llm.prompt_tokens",     prompt)
        self.set_attribute("llm.completion_tokens", completion)
        self.set_attribute("llm.total_tokens",      prompt + completion)

    def set_result_ok(self, value: Any = None) -> None:
        self.set_ok()
        if value is not None:
            self.set_attribute("result.preview", str(value)[:MAX_ATTR_LEN])

    def elapsed_ms(self) -> float:
        return (time.time_ns() - self._start_ns) / 1_000_000

    def _console_log(self) -> None:
        status = "✅" if self._status_ok else "❌"
        msg = (
            f"[SPAN] {status} {self.name} "
            f"{self.elapsed_ms():.1f}ms "
            + (" | ".join(f"{k}={v}" for k, v in self._attrs.items()))[:120]
        )
        log.info(msg)
        if self._error_msg:
            log.warning("  error: %s", self._error_msg)


class NinaTracer:
    """Singleton tracer. Call NinaTracer.get() everywhere."""

    _instance: "NinaTracer | None" = None
    _otel_tracer: Any = None

    def __init__(self):
        self._export_mode = NINA_OTEL_EXPORT.lower()
        if self._export_mode == "otlp":
            self._init_otel_otlp()
        elif self._export_mode == "console":
            self._init_otel_console()
        else:
            log.info("otel_tracer: tracing disabled (NINA_OTEL_EXPORT=none)")

    @classmethod
    def get(cls) -> "NinaTracer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ─ span factories ─────────────────────────────────────────────────────────

    @asynccontextmanager
    async def span(
        self, name: str, attrs: dict | None = None
    ) -> AsyncGenerator[NinaSpan, None]:
        """Generic span context manager."""
        nina_span = NinaSpan(name=name)
        for k, v in (attrs or {}).items():
            nina_span.set_attribute(k, v)

        otel_ctx = self._start_otel_span(name, attrs)
        nina_span._otel_span = otel_ctx.__enter__() if otel_ctx else None

        try:
            yield nina_span
        except Exception as exc:
            nina_span.set_error(str(exc))
            raise
        finally:
            if self._export_mode == "console":
                nina_span._console_log()
            if otel_ctx and nina_span._otel_span:
                try:
                    otel_ctx.__exit__(None, None, None)
                except Exception:
                    pass

    @asynccontextmanager
    async def llm_span(
        self,
        model: str,
        provider: str = "",
        task: str = "",
        prompt_preview: str = "",
    ) -> AsyncGenerator[NinaSpan, None]:
        """Span for a single LLM call."""
        attrs = {
            "llm.model":          model,
            "llm.provider":       provider,
            "llm.task":           task[:MAX_ATTR_LEN],
            "llm.prompt_preview": prompt_preview[:MAX_ATTR_LEN],
        }
        async with self.span(f"llm.{model}", attrs) as s:
            yield s

    @asynccontextmanager
    async def tool_span(
        self, tool_name: str, args: dict | None = None
    ) -> AsyncGenerator[NinaSpan, None]:
        """Span for a tool call."""
        args_digest = _digest(args or {})
        attrs = {
            "tool.name":        tool_name,
            "tool.args_digest": args_digest,
        }
        async with self.span(f"tool.{tool_name}", attrs) as s:
            yield s

    @asynccontextmanager
    async def route_span(
        self,
        model_chosen: str,
        task_type: str = "",
        reason: str = "",
    ) -> AsyncGenerator[NinaSpan, None]:
        """Span for a routing decision."""
        attrs = {
            "route.model":     model_chosen,
            "route.task_type": task_type,
            "route.reason":    reason[:MAX_ATTR_LEN],
        }
        async with self.span("router.decision", attrs) as s:
            yield s

    @asynccontextmanager
    async def agent_step_span(
        self, step: str, task: str = ""
    ) -> AsyncGenerator[NinaSpan, None]:
        """Span for one THINK/PLAN/ACT/OBSERVE/ADAPT step."""
        attrs = {
            "agent.step": step.upper(),
            "agent.task": task[:MAX_ATTR_LEN],
        }
        async with self.span(f"agent.{step.lower()}", attrs) as s:
            yield s

    # ─ OTel init ───────────────────────────────────────────────────────────────

    def _init_otel_console(self) -> None:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import SimpleSpanProcessor
            from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
                InMemorySpanExporter,
            )
            provider = TracerProvider()
            provider.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
            trace.set_tracer_provider(provider)
            self._otel_tracer = trace.get_tracer(NINA_SERVICE_NAME)
            log.info("otel_tracer: console mode initialised")
        except ImportError:
            log.info("otel_tracer: opentelemetry not installed, console-only mode")
        except Exception as exc:
            log.warning("otel_tracer: init failed: %s", exc)

    def _init_otel_otlp(self) -> None:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            exporter  = OTLPSpanExporter(endpoint=NINA_OTEL_ENDPOINT, insecure=True)
            provider  = TracerProvider()
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            self._otel_tracer = trace.get_tracer(NINA_SERVICE_NAME)
            log.info("otel_tracer: OTLP exporter → %s", NINA_OTEL_ENDPOINT)
        except ImportError:
            log.warning("otel_tracer: opentelemetry-exporter-otlp not installed")
        except Exception as exc:
            log.warning("otel_tracer: OTLP init failed: %s", exc)

    def _start_otel_span(self, name: str, attrs: dict | None) -> Any:
        if not self._otel_tracer:
            return None
        try:
            from opentelemetry.trace import use_span
            span = self._otel_tracer.start_span(name)
            for k, v in (attrs or {}).items():
                try:
                    span.set_attribute(k, v)
                except Exception:
                    pass
            return use_span(span, end_on_exit=True)
        except Exception:
            return None


# ── helpers ─────────────────────────────────────────────────────────────────

def _digest(obj: Any) -> str:
    """Short deterministic digest of a dict for span attributes (no secrets)."""
    try:
        raw = json.dumps(obj, sort_keys=True, default=str)[:512]
        return hashlib.sha1(raw.encode()).hexdigest()[:12]
    except Exception:
        return "unknown"
