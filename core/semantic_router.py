# core/semantic_router.py — NINA Semantic Router
# Zero external deps. Pure regex/keyword routing replaces sentence_transformers.
# Fast (<1ms), deterministic, no model loading, no RAM overhead.

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Route table — (pattern, agent/file, skip_llm)
# Order matters: first match wins. More specific patterns go first.
# ---------------------------------------------------------------------------
_ROUTES: list[tuple[re.Pattern, str, bool]] = [
    # System / service control
    (re.compile(r"\b(restart|start|stop|status|systemctl|service|boot|reload)\b", re.I),
     "system", True),

    # Git / code operations
    (re.compile(r"\b(git|commit|push|pull|diff|branch|merge|patch|rebase)\b", re.I),
     "git", True),

    # File operations
    (re.compile(r"\b(file|read|write|delete|mkdir|move|copy|rename|path|directory)\b", re.I),
     "file", True),

    # Memory / knowledge
    (re.compile(r"\b(remember|memory|recall|forget|store|knowledge|fact)\b", re.I),
     "memory", False),

    # Tasks / planning
    (re.compile(r"\b(task|todo|plan|schedule|remind|goal|backlog|sprint|priority)\b", re.I),
     "task", False),

    # Search / lookup
    (re.compile(r"\b(search|find|lookup|query|index|grep|locate)\b", re.I),
     "search", True),

    # Code generation / analysis
    (re.compile(r"\b(code|function|class|refactor|implement|debug|fix|error|import)\b", re.I),
     "code", False),

    # Telegram / messaging
    (re.compile(r"\b(telegram|message|send|notify|alert|chat|bot)\b", re.I),
     "telegram", False),

    # Finance / bank (NINA's domain context)
    (re.compile(r"\b(bank|loan|credit|deposit|transaction|balance|account|finance)\b", re.I),
     "finance", False),

    # Health check / diagnostics
    (re.compile(r"\b(health|ping|check|diagnose|log|tail|monitor|metric)\b", re.I),
     "health", True),
]

# Fallback when no pattern matches
_FALLBACK_AGENT = "llm"


class NINASemanticRouter:
    """
    Regex-based semantic router. Replaces sentence_transformers (which required
    huggingface_hub, onnxruntime, tokenizers — ~400MB). This router is:
      - <1ms per call (vs ~200ms model load + inference)
      - Zero RAM overhead (no model weights)
      - Fully deterministic and debuggable
      - Extensible: add rows to _ROUTES above
    """

    def __init__(self, index_path: str = "data/ssot_index.json") -> None:
        self.index: Dict = {}
        _p = Path(index_path)
        if _p.exists():
            try:
                self.index = json.loads(_p.read_text())
            except Exception:
                pass

    def route(self, query: str, top_k: int = 5) -> Dict:
        """
        Route a query to the most relevant agent/files.

        Returns dict with:
          agent     — matched agent name (str)
          files     — relevant file paths from ssot_index (list, may be empty)
          scores    — match confidence per file [0.0–1.0] (list)
          skip_llm  — True if query can be handled without LLM call (bool)
          matched   — the regex pattern that fired (str, for debugging)
        """
        agent, skip_llm, matched = self._match(query)
        files, scores = self._lookup_files(agent, top_k)
        return {
            "agent": agent,
            "files": files,
            "scores": scores,
            "skip_llm": skip_llm,
            "matched": matched,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _match(self, query: str) -> tuple[str, bool, str]:
        """Return (agent, skip_llm, pattern_str) for first matching rule."""
        for pattern, agent, skip_llm in _ROUTES:
            if pattern.search(query):
                return agent, skip_llm, pattern.pattern
        return _FALLBACK_AGENT, False, "<fallback>"

    def _lookup_files(self, agent: str, top_k: int) -> tuple[list, list]:
        """Find files in ssot_index matching the agent tag."""
        if not self.index:
            return [], []
        matched = [
            path for path, meta in self.index.items()
            if isinstance(meta, dict) and meta.get("agent") == agent
        ]
        files = matched[:top_k]
        # Uniform confidence score — all keyword matches treated equally
        scores = [1.0] * len(files)
        return files, scores

    def add_route(
        self,
        pattern: str,
        agent: str,
        skip_llm: bool = False,
        flags: int = re.I,
    ) -> None:
        """Dynamically add a route at runtime (prepended — highest priority)."""
        _ROUTES.insert(0, (re.compile(pattern, flags), agent, skip_llm))

    def explain(self, query: str) -> str:
        """Return a human-readable routing explanation for debugging."""
        result = self.route(query)
        return (
            f"query   : {query!r}\n"
            f"agent   : {result['agent']}\n"
            f"skip_llm: {result['skip_llm']}\n"
            f"matched : {result['matched']}\n"
            f"files   : {result['files']}"
        )
