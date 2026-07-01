"""
core/canonicalizer.py
NINA Path Normalization Firewall

Ensures ~/nina/core, /home/user/nina/core, and ../nina/core
are all treated as the SAME canonical entity by every agent.
Without this, the Hive generates duplicate tasks for the same
file under different path representations.

Usage:
    from core.canonicalizer import canonicalize, canonical_key

    path = canonicalize("~/nina/core/../core/kernel.py")
    # → PosixPath('/home/user/nina/core/kernel.py')

    key = canonical_key("~/nina/core/kernel.py")
    # → 'nina:core:kernel.py'  (stable dict/DB key)
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Union

ROOT = Path(__file__).parent.parent.resolve()


def canonicalize(path: Union[str, Path]) -> Path:
    """Resolve any path representation to an absolute, normalized Path."""
    p = Path(os.path.expandvars(str(path))).expanduser().resolve()
    return p


def canonical_key(path: Union[str, Path]) -> str:
    """Return a stable, colon-separated string key for use in dicts/DBs.

    Examples:
        /home/user/nina/core/kernel.py  →  'nina:core:kernel.py'
        ~/nina/swarm/worker_intm.py     →  'nina:swarm:worker_intm.py'
    """
    p = canonicalize(path)
    try:
        rel = p.relative_to(ROOT)
        parts = list(rel.parts)
    except ValueError:
        # Path outside ROOT — use last 3 parts
        parts = list(p.parts[-3:])
    return ":".join(parts)


def same_file(a: Union[str, Path], b: Union[str, Path]) -> bool:
    """Return True if two path strings resolve to the same file."""
    return canonicalize(a) == canonicalize(b)


def normalize_text(text: str) -> str:
    """Normalize text for dedup/index: lowercase, collapse whitespace,
    strip punctuation noise. Used before Bloom filter and Trie insertion."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)   # strip punctuation
    text = re.sub(r"\s+", " ", text)        # collapse whitespace
    return text


def canonical_event_key(event_type: str, scope: str) -> str:
    """Stable key for dedup-checking events on the Blackboard.

    e.g. ('BLACKBOARD_MUTATION', '~/nina/core/kernel.py')
         → 'BLACKBOARD_MUTATION:nina:core:kernel.py'
    """
    return f"{event_type.upper()}:{canonical_key(scope)}"
