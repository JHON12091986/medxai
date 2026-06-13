import json
import logging
from typing import Any, List, Dict
from dataclasses import dataclass

logger = logging.getLogger("nina.task_classifier")

TASK_TYPES = (
    "sensitive",
    "coding",
    "research",
    "math",
    "multilingual",
    "document",
    "vision",
    "quick",
    "general",
)

@dataclass
class ClassifiedTask:
    task_type: str
    estimated_tokens: int
    is_parallel_candidate: bool
    is_sensitive: bool


async def classify_task(text: str, messages: List[Dict[str, Any]]) -> ClassifiedTask:
    # Use ninagate's keyword lists as they seem more comprehensive for initial classification
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    total_history_chars = sum(len(m.get("content", "")) for m in messages)

    SIMPLE_KEYWORDS = [
        "cat ", "head ", "tail ", "wc ", "ls ", "find ", "grep",
        "sed ", "awk ", "chmod ", "mkdir ", "touch ", "echo ",
        "git log", "git diff", "git status", "git blame", "git show",
        "fix", "rename", "format", "docstring", "type hint", "boilerplate",
        "sort", "read", "show", "list", "print", "check", "verify",
        "compile", "status", "outline", "symbol", "signature",
        "sync", "commit", "import", "lint",
        "nf file", "nf git", "nf code", "nf log", "nf query",
        "summarize", "summarise", "index", "count", "move", "copy",
        "delete", "clean", "patch", "diff",
    ]
    if any(kw in text_lower for kw in SIMPLE_KEYWORDS):
        return ClassifiedTask("quick", 300, False, False) # Using "quick" for SIMPLE tasks

    # Short single-turn with no conversation history → SIMPLE
    if len(text) < 300 and len(messages) <= 2:
        return ClassifiedTask("quick", 300, False, False) # Using "quick" for SIMPLE tasks

    COMPLEX_KEYWORDS = [
        "architect", "redesign", "refactor across", "migrate", "merge conflict",
        "multi-file", "system design", "dependency graph", "breaking change",
        "performance regression", "security audit", "rewrite",
        "across multiple", "end-to-end", "full pipeline",
    ]
    if any(kw in text_lower for kw in COMPLEX_KEYWORDS):
        return ClassifiedTask("research", 1500, True, False) # Using "research" for COMPLEX tasks

    # Large accumulated conversation context → COMPLEX
    if total_history_chars > 8000:
        return ClassifiedTask("research", 1500, True, False) # Using "research" for COMPLEX tasks

    # Fallback to logic from core/router.py for specific task types if not classified as SIMPLE/COMPLEX
    if any(k in text_lower for k in ("password", "secret", "token", "private", "confidential", "bank", "account")):
        return ClassifiedTask("sensitive", 300, False, True)
    if any(k in text_lower for k in ("code", "python", "bug", "traceback", "function", "class", "patch")):
        return ClassifiedTask("coding", 800, True, False)
    if any(k in text_lower for k in ("research", "compare", "search", "latest", "find", "news")):
        return ClassifiedTask("research", 1200, True, False)
    if any(k in text_lower for k in ("calculate", "equation", "math", "solve")):
        return ClassifiedTask("math", 700, False, False)

    # Default to general
    return ClassifiedTask("general", 500, False, False)
