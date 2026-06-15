# core/task_classifier.py
# NINA Task Classifier v2 — Speed & Token-Optimized
#
# Returns ClassifiedTask with:
#   - task_type:        semantic type (coding, research, math, etc.)
#   - complexity:       SIMPLE / MEDIUM / COMPLEX / MASSIVE
#   - estimated_tokens: rough input token budget estimate
#   - recommended_tier: which provider tier to prefer
#   - is_parallel_candidate: safe to fan out to multiple providers
#   - is_sensitive:     contains PII / secrets, local-only
#   - max_tokens_cap:   suggested output cap (None = no cap)
#
# Routing contract used by ninagate/main.py:
#   SIMPLE  → Cerebras / Groq / Ollama (≤512 output tokens)
#   MEDIUM  → Groq / DeepSeek          (≤2048 output tokens)
#   COMPLEX → Gemini / DeepSeek        (≤4096 output tokens)
#   MASSIVE → Gemini only (1M ctx)     (no output cap)

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("nina.task_classifier")

# ── Complexity tiers ─────────────────────────────────────────────────────────
SIMPLE  = "SIMPLE"
MEDIUM  = "MEDIUM"
COMPLEX = "COMPLEX"
MASSIVE = "MASSIVE"

# ── Provider tier labels (match providers.json tier field) ───────────────────
TIER_LOCAL  = "LOCAL"
TIER_FAST   = "FAST"    # Cerebras, Groq — low latency, low context
TIER_DEEP   = "DEEP"    # DeepSeek, Mistral — reasoning quality
TIER_LARGE  = "LARGE"   # Gemini — massive context window

# ── Token thresholds ─────────────────────────────────────────────────────────
CHARS_PER_TOKEN     = 4      # Conservative estimate
MEDIUM_TOKEN_FLOOR  = 500    # If estimated input > this → at least MEDIUM
COMPLEX_TOKEN_FLOOR = 4_000  # If estimated input > this → at least COMPLEX
MASSIVE_TOKEN_FLOOR = 30_000 # If estimated input > this → MASSIVE (Gemini only)

# ── Output caps per complexity ────────────────────────────────────────────────
OUTPUT_CAPS = {
    SIMPLE:  512,
    MEDIUM:  2048,
    COMPLEX: 4096,
    MASSIVE: None,   # No cap — let Gemini decide
}


@dataclass
class ClassifiedTask:
    task_type:            str
    complexity:           str = MEDIUM
    estimated_tokens:     int = 500
    recommended_tier:     str = TIER_FAST
    is_parallel_candidate: bool = False
    is_sensitive:         bool = False
    max_tokens_cap:       int | None = 2048
    # Legacy field — kept for backward compat with ninagate/main.py
    # which reads .task_type and expects SIMPLE/MEDIUM/COMPLEX
    # We alias complexity → task_type for the proxy router
    def __post_init__(self):
        # ninagate reads task_type for routing — expose complexity there too
        # so existing code `task_type == "SIMPLE"` still works
        if self.task_type not in (SIMPLE, MEDIUM, COMPLEX, MASSIVE):
            # Store semantic type separately, expose complexity as task_type
            self._semantic_type = self.task_type
            self.task_type = self.complexity
        else:
            self._semantic_type = self.task_type


# ── Keyword tables ────────────────────────────────────────────────────────────

# Pure shell/mechanical ops — fire at fastest local model, no cloud needed
_LPU_HOTPATH = {
    "ls ", "ls -", "find ", "grep ", "head ", "tail ", "cat ",
    "wc ", "sed ", "awk ", "chmod ", "mkdir ", "touch ", "echo ",
    "python3 -m py_compile", "python3 -m pyflakes",
    "git status", "git diff", "git log", "git rev-parse", "git show",
    "nf monitor", "nf index", "nf memory", "nf query", "nf log",
}

# Simple: single-file, single-concept, short output expected
_SIMPLE_KEYWORDS = {
    "fix typo", "rename", "format", "add docstring", "add type hint",
    "add comment", "add import", "boilerplate", "sort imports",
    "remove unused", "lint", "compile check", "syntax check",
    "print ", "show ", "list ", "count ", "status", "verify",
    "what is", "define ", "explain briefly", "one line",
    "git commit", "git push", "git pull", "git add",
    "summarize this", "summarise this", "tldr",
}

# Complex: multi-file, architectural, cross-cutting concerns
_COMPLEX_KEYWORDS = {
    "architect", "redesign", "refactor across", "migrate",
    "merge conflict", "multi-file", "system design",
    "dependency graph", "breaking change", "performance regression",
    "security audit", "rewrite", "across multiple", "end-to-end",
    "full pipeline", "integration test", "design pattern",
    "concurrency", "race condition", "memory leak", "profil",
    "benchmark", "scalab", "microservice", "orchestrat",
}

# Massive: RAG, full-repo context, document analysis
_MASSIVE_KEYWORDS = {
    "entire codebase", "whole repo", "full project", "all files",
    "repository-wide", "analyze the repo", "scan all",
    "read all", "index everything", "process the document",
    "parse this pdf", "entire conversation", "full history",
}

# Sensitive: never send to cloud
_SENSITIVE_KEYWORDS = {
    "password", "secret", "api key", "private key", "token",
    "confidential", "bank account", "credit card", "ssn",
    "social security", ".env", "credentials", "passphrase",
}

# Semantic type hints (secondary classification, doesn't affect routing tier)
_CODING_KEYWORDS   = {"code", "python", "bug", "traceback", "function", "class", "patch", "implement", "debug", "error"}
_RESEARCH_KEYWORDS = {"research", "compare", "search", "latest", "news", "find out", "investigate", "survey"}
_MATH_KEYWORDS     = {"calculate", "equation", "math", "solve", "integral", "derivative", "matrix", "probability"}
_CREATIVE_KEYWORDS = {"write a", "draft", "story", "poem", "essay", "blog post", "creative"}


def _estimate_tokens(text: str, messages: list) -> int:
    """Fast token estimate without tiktoken — 1 token ≈ 4 chars."""
    total_chars = len(text) + sum(len(str(m.get("content", ""))) for m in messages)
    return max(1, total_chars // CHARS_PER_TOKEN)


def _semantic_type(text_lower: str) -> str:
    """Classify semantic task type independently of complexity."""
    if any(k in text_lower for k in _SENSITIVE_KEYWORDS):
        return "sensitive"
    if any(k in text_lower for k in _CODING_KEYWORDS):
        return "coding"
    if any(k in text_lower for k in _MATH_KEYWORDS):
        return "math"
    if any(k in text_lower for k in _RESEARCH_KEYWORDS):
        return "research"
    if any(k in text_lower for k in _CREATIVE_KEYWORDS):
        return "creative"
    return "general"


async def classify_task(
    text: str,
    messages: list[dict[str, Any]],
) -> ClassifiedTask:
    """
    Classify a task into complexity tier + semantic type + routing metadata.

    Priority order (first match wins):
    1. Sensitive → local-only regardless of complexity
    2. LPU hotpath → SIMPLE + LOCAL instantly
    3. MASSIVE keywords or token count → MASSIVE + LARGE
    4. COMPLEX keywords or token count → COMPLEX + DEEP
    5. SIMPLE keywords → SIMPLE + FAST
    6. Short single-turn → SIMPLE + FAST
    7. Medium token range or multi-turn → MEDIUM + FAST
    8. Default → MEDIUM + FAST
    """
    text_lower   = text.lower().strip()
    est_tokens   = _estimate_tokens(text, messages)
    sem_type     = _semantic_type(text_lower)
    n_turns      = len([m for m in messages if m.get("role") != "system"])

    # ── 1. Sensitive: always local, always SIMPLE output ─────────────────────
    if any(k in text_lower for k in _SENSITIVE_KEYWORDS):
        return ClassifiedTask(
            task_type="sensitive",
            complexity=SIMPLE,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_LOCAL,
            is_parallel_candidate=False,
            is_sensitive=True,
            max_tokens_cap=OUTPUT_CAPS[SIMPLE],
        )

    # ── 2. LPU hotpath: pure shell mechanic, fire at local instantly ──────────
    if any(text_lower.startswith(kw) for kw in _LPU_HOTPATH):
        return ClassifiedTask(
            task_type="lpu_deterministic",
            complexity=SIMPLE,
            estimated_tokens=50,
            recommended_tier=TIER_LOCAL,
            is_parallel_candidate=False,
            is_sensitive=False,
            max_tokens_cap=256,
        )

    # ── 3. MASSIVE: token count or keyword → Gemini only ─────────────────────
    if est_tokens >= MASSIVE_TOKEN_FLOOR or any(k in text_lower for k in _MASSIVE_KEYWORDS):
        return ClassifiedTask(
            task_type=sem_type,
            complexity=MASSIVE,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_LARGE,
            is_parallel_candidate=False,
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[MASSIVE],
        )

    # ── 4. COMPLEX: keyword match or large token budget ───────────────────────
    if any(k in text_lower for k in _COMPLEX_KEYWORDS) or est_tokens >= COMPLEX_TOKEN_FLOOR:
        return ClassifiedTask(
            task_type=sem_type,
            complexity=COMPLEX,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_DEEP,
            is_parallel_candidate=True,
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[COMPLEX],
        )

    # ── 5. SIMPLE keyword match ───────────────────────────────────────────────
    if any(k in text_lower for k in _SIMPLE_KEYWORDS):
        return ClassifiedTask(
            task_type=sem_type,
            complexity=SIMPLE,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_FAST,
            is_parallel_candidate=False,
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[SIMPLE],
        )

    # ── 6. Short single-turn with no history → SIMPLE ────────────────────────
    if len(text) < 300 and n_turns <= 2:
        return ClassifiedTask(
            task_type=sem_type,
            complexity=SIMPLE,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_FAST,
            is_parallel_candidate=False,
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[SIMPLE],
        )

    # ── 7. Medium token range OR multi-turn conversation ─────────────────────
    if est_tokens >= MEDIUM_TOKEN_FLOOR or n_turns > 4:
        return ClassifiedTask(
            task_type=sem_type,
            complexity=MEDIUM,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_FAST,
            is_parallel_candidate=sem_type in ("coding", "research"),
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[MEDIUM],
        )

    # ── 8. Default: MEDIUM ────────────────────────────────────────────────────
    return ClassifiedTask(
        task_type=sem_type,
        complexity=MEDIUM,
        estimated_tokens=est_tokens,
        recommended_tier=TIER_FAST,
        is_parallel_candidate=False,
        is_sensitive=False,
        max_tokens_cap=OUTPUT_CAPS[MEDIUM],
    )
