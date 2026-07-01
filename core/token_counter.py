"""
core/token_counter.py
NINA Token Counter — count tokens BEFORE every LLM call using tiktoken.
Compress or reject if over budget. Works for Claude/GPT/Gemini models.

Usage:
    from core.token_counter import count_tokens, fits_budget, trim_to_budget

    n = count_tokens(my_prompt)
    if not fits_budget(my_prompt, max_tokens=4096):
        my_prompt = trim_to_budget(my_prompt, max_tokens=4096)
"""

from __future__ import annotations
from typing import Optional

_CHAR_RATIO = {"default": 3.8, "claude": 3.5, "gemini": 4.0}

_enc = None

def _get_encoder():
    global _enc
    if _enc is None:
        try:
            import tiktoken
            _enc = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            _enc = None
    return _enc

def count_tokens(text: str, model: str = "default") -> int:
    """Count tokens. Uses tiktoken if available, else char ratio fallback."""
    enc = _get_encoder()
    if enc:
        return len(enc.encode(text))
    ratio = _CHAR_RATIO.get(model, _CHAR_RATIO["default"])
    return max(1, int(len(text) / ratio))

def fits_budget(text: str, max_tokens: int = 4096, model: str = "default") -> bool:
    return count_tokens(text, model) <= max_tokens

def trim_to_budget(text: str, max_tokens: int = 4096, model: str = "default") -> str:
    """Trim text to fit within token budget. Preserves start of text."""
    enc = _get_encoder()
    if enc:
        tokens = enc.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return enc.decode(tokens[:max_tokens])
    ratio = _CHAR_RATIO.get(model, _CHAR_RATIO["default"])
    max_chars = int(max_tokens * ratio)
    return text[:max_chars] + "…" if len(text) > max_chars else text

def token_report(sections: dict, max_tokens: int = 8192) -> dict:
    """
    Report token usage per named section.
    sections: {"system": ..., "user": ..., "context": ...}
    """
    report = {}
    total = 0
    for name, text in sections.items():
        n = count_tokens(text)
        report[name] = n
        total += n
    report["TOTAL"] = total
    report["BUDGET_REMAINING"] = max_tokens - total
    report["OVER_BUDGET"] = total > max_tokens
    return report

if __name__ == "__main__":
    sample = "This is a test of the NINA token counter. " * 100
    print(f"Tokens: {count_tokens(sample)}")
    print(f"Fits 4096: {fits_budget(sample, 4096)}")
    trimmed = trim_to_budget(sample, 100)
    print(f"Trimmed ({count_tokens(trimmed)} tokens): {trimmed[:80]}…")
