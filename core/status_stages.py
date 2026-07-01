"""
core/status_stages.py — Canonical live-status message strings.
Pass 0 · 25 Jun 2026 · Nina Live Status Display

All pipeline stages use these constants so:
  1. No magic strings scattered across the codebase.
  2. Emoji/wording changes happen in one place.
  3. Tests can assert on known strings.

Usage
-----
    from core.status_stages import S
    from core.status_bus import push

    await push(S.routing(provider="GEMINI"))
    await push(S.generating(model="gemini-2.0-flash"))
    await push(S.fallback(from_provider="GEMINI", to_provider="LOCAL"))
    await push(S.error(provider="GEMINI", reason="quota exceeded"))
    await push(S.done(provider="GEMINI", latency_ms=430))

    # opencode multi-step:
    await push(S.opencode_step(n=2, total=5, label="OpenCode executing"))
"""
from __future__ import annotations


class S:  # noqa: N801 — short name intentional
    """Static factory methods for status strings."""

    # ── Core pipeline ───────────────────────────────────────────────────────

    @staticmethod
    def thinking() -> str:
        return "\u23f3 Thinking..."

    @staticmethod
    def routing(provider: str = "") -> str:
        suffix = f" \u2192 {provider}" if provider else ""
        return f"\U0001f500 Routing{suffix}"

    @staticmethod
    def generating(model: str = "") -> str:
        suffix = f" {model} \xb7" if model else ""
        return f"\U0001f9e0{suffix} generating..."

    @staticmethod
    def streaming(model: str = "", tokens: int = 0) -> str:
        tok = f" ({tokens}t)" if tokens else ""
        return f"\u26a1 {model or 'streaming'}{tok}"

    @staticmethod
    def fallback(from_provider: str = "", to_provider: str = "") -> str:
        arrow = f"{from_provider} \u2192 {to_provider}" if from_provider and to_provider else "next provider"
        return f"\u26a0\ufe0f Fallback \u2192 {arrow}"

    @staticmethod
    def error(provider: str = "", reason: str = "") -> str:
        who = f"{provider} " if provider else ""
        why = f": {reason[:80]}" if reason else ""
        return f"\u274c {who}failed{why}"

    @staticmethod
    def done(provider: str = "", latency_ms: int = 0) -> str:
        who = f" ({provider})" if provider else ""
        lat = f" \xb7 {latency_ms}ms" if latency_ms else ""
        return f"\u2705 Done{who}{lat}"

    # ── NinaGate ────────────────────────────────────────────────────────────

    @staticmethod
    def ninagate_auth() -> str:
        return "\U0001f511 NinaGate \u2192 auth check"

    @staticmethod
    def ninagate_dispatch(provider: str = "") -> str:
        suffix = f" \u2192 {provider}" if provider else ""
        return f"\U0001f6aa NinaGate dispatching{suffix}"

    @staticmethod
    def circuit_open(provider: str = "") -> str:
        return f"\U0001f534 Circuit OPEN \u2014 {provider or 'provider'} paused"

    @staticmethod
    def circuit_closed(provider: str = "") -> str:
        return f"\U0001f7e2 Circuit CLOSED \u2014 {provider or 'provider'} recovered"

    # ── OpenCode / NDEV multi-step ───────────────────────────────────────────

    @staticmethod
    def opencode_step(n: int, total: int, label: str = "") -> str:
        bar = ("\u2588" * n) + ("\u2591" * (total - n))
        lab = f" \xb7 {label}" if label else ""
        return f"\u2699\ufe0f [{bar}] {n}/{total}{lab}"

    @staticmethod
    def opencode_done(duration_s: float) -> str:
        return f"\u2705 OpenCode done \xb7 {duration_s:.1f}s"

    @staticmethod
    def opencode_failed(reason: str = "") -> str:
        r = f": {reason[:80]}" if reason else ""
        return f"\u274c OpenCode failed{r}"

    # ── Agent / task ─────────────────────────────────────────────────────────

    @staticmethod
    def agent_step(n: int, label: str = "") -> str:
        lab = f" \u2014 {label}" if label else ""
        return f"\U0001f916 Agent step {n}{lab}"

    @staticmethod
    def tool_call(tool: str = "") -> str:
        return f"\U0001f527 Tool: {tool or 'unknown'}"
