"""
tools/nina_token_guard.py
=========================
Token Conservation Gate for agy / any LLM call.

PURPOSE
-------
Intercept every task BEFORE it reaches agy (or any cloud model) and:
  1. Classify complexity  → TRIVIAL | MEDIUM | COMPLEX
  2. Compress prompt      → strip boilerplate, trim context window
  3. Cache hit check      → return cached result immediately if available
  4. Route decision       → returns the optimal provider string

USAGE
-----
    from tools.nina_token_guard import TokenGuard
    guard = TokenGuard()

    decision = guard.evaluate(prompt="Fix the typo in line 42", context_files=["main.py"])
    # decision.provider  → "LOCALFAST" | "GROQ" | "GEMINI" | "AGY"
    # decision.prompt    → compressed version of prompt
    # decision.cached    → str | None  (if cached result exists)

    # Or as a CLI pre-check for shell wrappers:
    # python3 tools/nina_token_guard.py "add docstring to foo()"
"""

import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CACHE_PATH = Path("data/token_guard_cache.json")
QUOTA_PATH = Path("data/agy_quota.json")

# Task complexity thresholds (rough token estimates)
TRIVIAL_MAX_TOKENS  = 400   # → LOCALFAST (qwen2.5:1.5b)
MEDIUM_MAX_TOKENS   = 2000  # → GROQ / DEEPSEEK (free/cheap)
COMPLEX_MAX_TOKENS  = 8000  # → GEMINI Flash (cloud, not agy)
# Above COMPLEX_MAX → AGY (only when truly necessary)

# Keywords that force COMPLEX regardless of token count
FORCE_COMPLEX_PATTERNS = [
    r"\brefactor\b", r"\barchitect\b", r"\bmulti.?file\b",
    r"\bintegrat\b", r"\bmigrat\b", r"\bdesign\b.*\bsystem\b",
]

# Keywords that force TRIVIAL regardless of token count  
FORCE_TRIVIAL_PATTERNS = [
    r"\btypo\b", r"\brendame?\b", r"\bformat\b", r"\bdocstring\b",
    r"\bfix\s+typo\b", r"\bfix\s+indent\b", r"\bprint\b.*\bdebug\b",
    r"\badd.*line\b", r"\bfix.*indent\b",
]

# Boilerplate stripping patterns (reduce context sent to LLM)
STRIP_PATTERNS = [
    (r"#\s*={10,}.*?={10,}\n", ""),          # Banner/section dividers only
    (r"^\s*#(?!.*(?:critical|important|guard|lock|do not|don't|juleslock|F-\d|rule0)).*\n", "", re.MULTILINE),
    (r"\n{3,}", "\n\n"),                      # Excessive blank lines
    (r"\s+$", "", re.MULTILINE),              # Trailing whitespace
]

PROVIDER_MAP = {
    "TRIVIAL":  "LOCALFAST",
    "MEDIUM":   "GROQ",
    "COMPLEX":  "GEMINI",
    "CRITICAL": "AGY",
}


@dataclass
class GuardDecision:
    tier: str              # TRIVIAL | MEDIUM | COMPLEX | CRITICAL
    provider: str          # target provider
    prompt: str            # compressed prompt
    estimated_tokens: int
    cached: Optional[str] = None
    reason: str = ""


class TokenGuard:
    def __init__(self) -> None:
        self._cache: dict = {}
        self._load_cache()
        self._quota: dict = {}
        self._load_quota()

    # ── Cache ────────────────────────────────────────────────────────────────

    def _load_cache(self) -> None:
        if CACHE_PATH.exists():
            try:
                raw = json.loads(CACHE_PATH.read_text())
                now = time.time()
                self._cache = {k: v for k, v in raw.items()
                               if now < v.get("expires_at", 0)}
            except Exception:
                self._cache = {}

    def _save_cache(self) -> None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(self._cache, indent=2))

    def _cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.strip().encode()).hexdigest()

    def cache_result(self, prompt: str, result: str, ttl: int = 3600) -> None:
        k = self._cache_key(prompt)
        self._cache[k] = {"result": result, "expires_at": time.time() + ttl}
        self._save_cache()

    def _get_cached(self, prompt: str) -> Optional[str]:
        k = self._cache_key(prompt)
        entry = self._cache.get(k)
        if entry and time.time() < entry.get("expires_at", 0):
            return entry["result"]
        return None

    # ── Quota awareness ──────────────────────────────────────────────────────

    def _load_quota(self) -> None:
        if QUOTA_PATH.exists():
            try:
                self._quota = json.loads(QUOTA_PATH.read_text())
            except Exception:
                self._quota = {}

    def _agy_exhausted(self) -> bool:
        """Returns True if agy Pro quota >90% or manually marked exhausted."""
        pro_pct = self._quota.get("pro_pct", 0)
        flash_pct = self._quota.get("flash_pct", 0)
        exhausted = self._quota.get("exhausted", False)
        return exhausted or (pro_pct >= 90 and flash_pct >= 90)

    def _preferred_cloud(self) -> str:
        """Pick best cloud provider based on live quota."""
        pro_pct = self._quota.get("pro_pct", 0)
        flash_pct = self._quota.get("flash_pct", 0)
        flash_lite_pct = self._quota.get("flash_lite_pct", 0)
        if flash_lite_pct < 50:
            return "GEMINI"   # Flash Lite has headroom
        if flash_pct < 70:
            return "GEMINI"   # Flash has headroom
        if pro_pct < 80:
            return "GROQ"     # Avoid Pro, use Groq
        return "DEEPSEEK"     # Last resort cloud

    # ── Prompt compression ───────────────────────────────────────────────────

    @staticmethod
    def compress(text: str, max_chars: int = 4000) -> str:
        """Strip noise and truncate to max_chars."""
        for pattern, repl, *flags in STRIP_PATTERNS:
            f = flags[0] if flags else 0
            text = re.sub(pattern, repl, text, flags=f)
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... [truncated by TokenGuard]"
        return text.strip()

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough estimate: 1 token ≈ 4 chars."""
        return max(1, len(text) // 4)

    # ── Classification ───────────────────────────────────────────────────────

    @staticmethod
    def classify(prompt: str, estimated_tokens: int) -> str:
        p = prompt.lower()
        for pat in FORCE_COMPLEX_PATTERNS:
            if re.search(pat, p):
                return "COMPLEX"
        for pat in FORCE_TRIVIAL_PATTERNS:
            if re.search(pat, p):
                return "TRIVIAL"
        if estimated_tokens <= TRIVIAL_MAX_TOKENS:
            return "TRIVIAL"
        if estimated_tokens <= MEDIUM_MAX_TOKENS:
            return "MEDIUM"
        if estimated_tokens <= COMPLEX_MAX_TOKENS:
            return "COMPLEX"
        return "CRITICAL"

    # ── Main entry ───────────────────────────────────────────────────────────

    def evaluate(
        self,
        prompt: str,
        context: str = "",
        force_tier: Optional[str] = None,
    ) -> GuardDecision:
        full_input = (prompt + "\n" + context).strip()
        _max_chars_by_tier = {
            "TRIVIAL":  2000,
            "MEDIUM":   6000,
            "COMPLEX":  16000,
            "CRITICAL": 48000,
        }
        _pre_tier = force_tier or self.classify(prompt, self._estimate_tokens(full_input))
        _max_chars = _max_chars_by_tier.get(_pre_tier, 6000)
        compressed = self.compress(full_input, max_chars=_max_chars)
        tokens = self._estimate_tokens(compressed)

        # 1. Cache check (always first)
        cached = self._get_cached(compressed)
        if cached:
            return GuardDecision(
                tier="TRIVIAL", provider="CACHE",
                prompt=compressed, estimated_tokens=0,
                cached=cached, reason="cache_hit"
            )

        # 2. Classify
        tier = force_tier or self.classify(prompt, tokens)

        # 3. Quota-aware provider selection
        if tier == "CRITICAL" and self._agy_exhausted():
            tier = "COMPLEX"
            provider = self._preferred_cloud()
            reason = "agy_exhausted→downgrade_to_cloud"
        elif tier in ("COMPLEX", "CRITICAL"):
            provider = PROVIDER_MAP.get(tier, "GEMINI")
            reason = f"tier={tier}"
        else:
            provider = PROVIDER_MAP.get(tier, "LOCALFAST")
            reason = f"tier={tier}"

        return GuardDecision(
            tier=tier, provider=provider,
            prompt=compressed, estimated_tokens=tokens,
            reason=reason,
        )


# ── CLI usage ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TokenGuard CLI")
    parser.add_argument("prompt", nargs="?", default="", help="Task prompt")
    parser.add_argument("--context", default="", help="Additional context text")
    parser.add_argument("--force-tier", choices=["TRIVIAL","MEDIUM","COMPLEX","CRITICAL"], default=None)
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not args.prompt:
        prompt = sys.stdin.read()
    else:
        prompt = args.prompt

    guard = TokenGuard()
    decision = guard.evaluate(prompt, context=args.context, force_tier=args.force_tier)

    if args.json:
        print(json.dumps({
            "tier": decision.tier,
            "provider": decision.provider,
            "tokens": decision.estimated_tokens,
            "reason": decision.reason,
            "cached": bool(decision.cached),
        }))
    else:
        print(f"Tier:     {decision.tier}")
        print(f"Provider: {decision.provider}")
        print(f"Tokens:   {decision.estimated_tokens}")
        print(f"Reason:   {decision.reason}")
        if decision.cached:
            print("CACHED:   YES (returning stored result)")
