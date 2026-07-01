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
import re
from dataclasses import dataclass
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
        pass

    @property
    def _semantic_type(self) -> str:
        return self.task_type


# ── Keyword tables ────────────────────────────────────────────────────────────

# Pure shell/mechanical ops — fire at fastest local model, no cloud needed
_LPU_HOTPATH = {
    "ls ", "ls -", "find ", "grep ", "head ", "tail ", "cat ",
    "wc ", "sed ", "awk ", "chmod ", "mkdir ", "touch ", "echo ",
    "python3 -m py_compile", "python3 -m pyflakes",
    "git status", "git diff", "git rev-parse", "git show",
    "nf monitor", "nf index", "nf memory", "nf query", "nf log",
}

# Simple: single-file, single-concept, short output expected
_SIMPLE_KEYWORDS = {
    "fix typo", "rename", "format", "add docstring", "add type hint",
    "add comment", "add import", "boilerplate", "sort imports",
    "remove unused", "lint", "compile check", "syntax check",
    "print ", "show ", "list ", "count ", "git status",
    "service status", "verify",
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
_RESEARCH_KEYWORDS = {"research", "compare", "search", "latest", "news", "survey"}
_MATH_KEYWORDS     = {"calculate", "equation", "math", "solve", "integral", "derivative", "matrix", "probability"}
_CREATIVE_KEYWORDS = {"write a", "draft", "story", "poem", "essay", "blog post", "creative"}
_DIAGNOSTIC_KEYWORDS = {
    "why is", "why does", "why did", "why isn't", "why doesn't",
    "what's wrong", "what is wrong", "not working", "broken",
    "deleted",
    "gets deleted",
    "was deleted",
    "keeps deleting",
    "being deleted",
    "file missing",
    "not persisting",
    "disappears after",
    "wiped by",
    "disappear", "missing file", "root cause",
    "troubleshoot", "debug why", "investigate why",
    "trace the ",
    "trace why",
    "trace how",
}

# Pre-compile regexes for fast matching in hot-path classify_task
_LPU_HOTPATH_REGEX = re.compile(
    r"^\s*(" + "|".join(re.escape(kw) for kw in _LPU_HOTPATH) + ")", re.IGNORECASE
)
_SIMPLE_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _SIMPLE_KEYWORDS) + ")", re.IGNORECASE
)
_COMPLEX_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _COMPLEX_KEYWORDS) + ")", re.IGNORECASE
)
_MASSIVE_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _MASSIVE_KEYWORDS) + ")", re.IGNORECASE
)
_SENSITIVE_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _SENSITIVE_KEYWORDS) + ")", re.IGNORECASE
)
_CODING_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _CODING_KEYWORDS) + ")", re.IGNORECASE
)
_RESEARCH_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _RESEARCH_KEYWORDS) + ")", re.IGNORECASE
)
_MATH_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _MATH_KEYWORDS) + ")", re.IGNORECASE
)
_CREATIVE_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _CREATIVE_KEYWORDS) + ")", re.IGNORECASE
)
_DIAGNOSTIC_KEYWORDS_REGEX = re.compile(
    r"(" + "|".join(re.escape(kw) for kw in _DIAGNOSTIC_KEYWORDS) + ")",
    re.IGNORECASE
)


def _estimate_tokens(text: str, messages: list) -> int:
    """Fast token estimate without tiktoken — 1 token ≈ 4 chars."""
    # Weight message history at 25% to avoid over-promoting history-heavy requests
    history_chars = sum(len(str(m.get("content", ""))) for m in messages)
    total_chars = len(text) + (history_chars // 4)
    return max(1, total_chars // CHARS_PER_TOKEN)


def _semantic_type(text: str) -> str:
    """Classify semantic task type independently of complexity."""
    if _SENSITIVE_KEYWORDS_REGEX.search(text):
        return "sensitive"
    if _DIAGNOSTIC_KEYWORDS_REGEX.search(text):
        return "diagnostic"
    if _CODING_KEYWORDS_REGEX.search(text):
        return "coding"
    if _MATH_KEYWORDS_REGEX.search(text):
        return "math"
    if _RESEARCH_KEYWORDS_REGEX.search(text):
        return "research"
    if _CREATIVE_KEYWORDS_REGEX.search(text):
        return "creative"
    return "quick"


def classify_task(
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
    est_tokens   = _estimate_tokens(text, messages)
    sem_type     = _semantic_type(text)
    n_turns      = len([m for m in messages if m.get("role") != "system"])

    # ── 1. Sensitive: always local, always SIMPLE output ─────────────────────
    if _SENSITIVE_KEYWORDS_REGEX.search(text):
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
    if _LPU_HOTPATH_REGEX.search(text):
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
    if est_tokens >= MASSIVE_TOKEN_FLOOR or _MASSIVE_KEYWORDS_REGEX.search(text):
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
    if _COMPLEX_KEYWORDS_REGEX.search(text) or est_tokens >= COMPLEX_TOKEN_FLOOR:
        return ClassifiedTask(
            task_type=sem_type,
            complexity=COMPLEX,
            estimated_tokens=est_tokens,
            recommended_tier=TIER_DEEP,
            # diagnostic+coding share TIER_DEEP; diagnostic-only stays TIER_DEEP
            is_parallel_candidate=sem_type in ("research", "analysis"),
            is_sensitive=False,
            max_tokens_cap=OUTPUT_CAPS[COMPLEX],
        )

    # ── 5. SIMPLE keyword match ───────────────────────────────────────────────
    if _SIMPLE_KEYWORDS_REGEX.search(text):
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
    if len(text) < 300 and n_turns <= 2 and sem_type in ("general", "creative", "quick"):
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
            is_parallel_candidate=sem_type in ("coding", "research") and sem_type != "diagnostic",
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
