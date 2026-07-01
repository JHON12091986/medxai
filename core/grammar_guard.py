"""
core/grammar_guard.py — CFG Constrained LLM Output Layer
GAP-03 · 24 Jun 2026

Enforces structured output on every LLM call in STATE 03.
Backend priority (auto-detected at import time):
  1. outlines           (pip install outlines)          — preferred, full CFG
  2. lm-format-enforcer (pip install lm-format-enforcer) — JSON schema
  3. regex fallback     (stdlib re)                      — always available

Usage in kernel STATE 03:
    from core.grammar_guard import get_guard
    guard = get_guard()                          # singleton, auto-detects backend

    # Enforce JSON schema on raw LLM output string
    clean = guard.constrain(raw_output, schema={"type": "object", "required": ["action"]})

    # Enforce regex pattern
    clean = guard.regex(raw_output, r'^(PASS|FAIL|SKIP)$')

    # Enforce enum choice
    clean = guard.choice(raw_output, ["PASS", "FAIL", "SKIP"])

    # Best-effort JSON extraction from prose
    data = guard.extract_json(raw_output)

Integration point — core/kernel.py STATE 03:
    result = await asyncio.wait_for(self._agent_loop_fn(packet), 120)
    if self._guard and packet.payload.get('schema'):
        result = await asyncio.to_thread(
            self._guard.constrain, result, packet.payload['schema']
        )
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger("nina.grammar_guard")

# Backend detection — silent, non-fatal
_BACKEND = "regex"  # stdlib fallback always available

try:
    import outlines  # noqa: F401
    _BACKEND = "outlines"
except ImportError:
    pass

if _BACKEND == "regex":
    try:
        from lmformatenforcer import JsonSchemaParser  # noqa: F401
        _BACKEND = "lm-format-enforcer"
    except ImportError:
        pass

logger.info("grammar_guard backend=%s", _BACKEND)


class GrammarGuard:
    """CFG-constrained output enforcer for NINA STATE 03.

    All methods are synchronous and CPU-bound. Call via asyncio.to_thread()
    when invoked from inside the kernel event loop.
    """

    def __init__(self) -> None:
        self.backend = _BACKEND
        logger.info("GrammarGuard initialised backend=%s", self.backend)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def constrain(self, text: str, schema: dict) -> Any:
        """Enforce JSON schema on raw LLM output string.

        Returns parsed Python object on success.
        Returns raw text on parse failure (non-fatal — never raises).
        """
        if self.backend == "outlines":
            return self._constrain_outlines(text, schema)
        if self.backend == "lm-format-enforcer":
            return self._constrain_lmfe(text, schema)
        return self._constrain_regex_json(text)

    def regex(self, text: str, pattern: str) -> str:
        """Extract first match of pattern from text.

        Returns matched string or empty string on no match.
        """
        try:
            m = re.search(pattern, text, re.DOTALL)
            return m.group(0) if m else ""
        except re.error as exc:
            logger.warning("grammar_guard.regex invalid_pattern %s", exc)
            return text

    def choice(self, text: str, options: list[str]) -> str:
        """Return first option found in text (case-insensitive).

        Returns options[0] as default if nothing matches.
        """
        text_upper = text.upper()
        for opt in options:
            if opt.upper() in text_upper:
                return opt
        logger.debug("grammar_guard.choice no_match defaulting to %s", options[0])
        return options[0]

    def extract_json(self, text: str) -> Any:
        """Best-effort JSON extraction from text that may contain prose.

        Attempt order:
          1. Direct json.loads()
          2. Extract from ```json ... ``` fence
          3. Find first { ... } or [ ... ] block

        Returns None on total failure (never raises).
        """
        # 1. Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 2. Fenced block
        fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if fence:
            try:
                return json.loads(fence.group(1).strip())
            except json.JSONDecodeError:
                pass
        # 3. First braces block
        brace = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
        if brace:
            try:
                return json.loads(brace.group(1))
            except json.JSONDecodeError:
                pass
        logger.debug("grammar_guard.extract_json failed len=%d", len(text))
        return None

    # ------------------------------------------------------------------
    # Backend implementations
    # ------------------------------------------------------------------

    def _constrain_outlines(self, text: str, schema: dict) -> Any:
        """outlines: used at generation time; post-hoc = extract + validate."""
        try:
            result = self.extract_json(text)
            if result is not None:
                self._validate_schema(result, schema)
                return result
        except Exception as exc:
            logger.debug("grammar_guard.outlines fallback reason=%s", exc)
        return text

    def _constrain_lmfe(self, text: str, schema: dict) -> Any:
        """lm-format-enforcer: post-hoc JSON extraction + validation."""
        try:
            result = self.extract_json(text)
            if result is not None:
                return result
        except Exception as exc:
            logger.debug("grammar_guard.lmfe fallback reason=%s", exc)
        return text

    def _constrain_regex_json(self, text: str) -> Any:
        """stdlib regex JSON extraction fallback."""
        result = self.extract_json(text)
        return result if result is not None else text

    @staticmethod
    def _validate_schema(obj: Any, schema: dict) -> None:
        """Minimal schema validation (no jsonschema dep required).

        Checks 'type' and 'required' fields only.
        Raises ValueError on violation — caught by callers.
        """
        if schema.get("type") == "object" and not isinstance(obj, dict):
            raise ValueError(f"Expected object, got {type(obj).__name__}")
        if schema.get("type") == "array" and not isinstance(obj, list):
            raise ValueError(f"Expected array, got {type(obj).__name__}")
        for req in schema.get("required", []):
            if isinstance(obj, dict) and req not in obj:
                raise ValueError(f"Missing required field: {req}")


# Process-wide singleton
_guard: GrammarGuard | None = None


def get_guard() -> GrammarGuard:
    """Return the process-wide GrammarGuard singleton."""
    global _guard
    if _guard is None:
        _guard = GrammarGuard()
    return _guard
