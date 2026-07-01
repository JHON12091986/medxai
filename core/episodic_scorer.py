"""core/episodic_scorer.py — Episodic memory importance scorer for NINA vNext.

Provides a fast heuristic importance score (0.0–1.0) for any memory entry.
Used by:
  - crons/memory_consolidation.py  (prune / cluster decisions)
  - core/reflexion.py              (recall ranking)
  - core/memory (future retrieval re-ranking)

No LLM call needed — signal-based scoring only.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

# Signal keyword groups and their weights
_IMPORTANCE_SIGNALS: list[tuple[list[str], float]] = [
    (["remember", "important", "critical", "must", "always", "never"], 0.10),
    (["prefer", "favourite", "favorite", "like", "dislike"],           0.08),
    (["goal", "objective", "mission", "target", "deadline"],           0.10),
    (["error", "bug", "fix", "fail", "issue", "problem"],              0.07),
    (["learned", "discovered", "realised", "realized", "found"],       0.06),
    (["user preference", "user wants", "user needs"],                   0.12),
]

_NOISE_SIGNALS: list[str] = [
    "thank", "ok", "okay", "yes", "no", "sure", "got it", "understood",
    "hello", "hi", "bye", "goodbye",
]


def score(
    text: str,
    role: str = "user",
    timestamp_iso: str = "",
    recency_weight: float = 0.2,
    window_days: int = 30,
) -> float:
    """Score a memory entry on importance 0.0–1.0.

    Args:
        text:            Raw memory text.
        role:            "user" or "assistant".
        timestamp_iso:   ISO-8601 timestamp of when this entry was created.
        recency_weight:  How much to boost recent entries (0.0–0.3 recommended).
        window_days:     Entries older than this are penalised.

    Returns:
        Float in [0.0, 1.0].
    """
    t = text.lower()
    s = 0.5  # base

    # signal boosts
    for keywords, weight in _IMPORTANCE_SIGNALS:
        if any(kw in t for kw in keywords):
            s += weight

    # noise penalty
    word_count = len(t.split())
    if word_count < 5 or any(n in t for n in _NOISE_SIGNALS):
        s -= 0.25

    # role boost — user instructions carry more weight than assistant drafts
    if role == "user":
        s += 0.05

    # recency
    if timestamp_iso:
        try:
            created = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - created).days
            if age_days < 7:
                s += recency_weight
            elif age_days < 14:
                s += recency_weight * 0.5
            elif age_days > window_days:
                s -= 0.15
        except Exception:
            pass

    # length bonus — very short entries are usually low value
    if word_count >= 20:
        s += 0.05
    if word_count >= 60:
        s += 0.05

    return max(0.0, min(1.0, s))


def rank(
    entries: list[dict],
    text_key: str = "document",
    meta_key: str = "metadata",
    top_k: int | None = None,
) -> list[tuple[float, dict]]:
    """Rank a list of memory entry dicts by importance score.

    Args:
        entries:  List of dicts, each with at least `text_key`.
        text_key: Key for the text content in each entry.
        meta_key: Key for the metadata dict (used for role, timestamp).
        top_k:    Return only the top-k entries if specified.

    Returns:
        List of (score, entry) sorted descending.
    """
    scored = []
    for entry in entries:
        text  = entry.get(text_key, "")
        meta  = entry.get(meta_key, {})
        role  = meta.get("role", "user") if isinstance(meta, dict) else "user"
        ts    = meta.get("timestamp", "") if isinstance(meta, dict) else ""
        s     = score(text=text, role=role, timestamp_iso=ts)
        scored.append((s, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k] if top_k else scored
