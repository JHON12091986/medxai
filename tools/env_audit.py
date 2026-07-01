#!/usr/bin/env python3
"""
tools/env_audit.py — NINA .env CI Gate

Exits 1 if the .env file contains any deprecated alias keys.
Also reports orphan env vars (defined in .env, never used in source).

Usage:
  python tools/env_audit.py           # strict: exit 1 on any violation
  python tools/env_audit.py --warn    # report violations but exit 0

Integrate in nina_sync.sh:
  python tools/env_audit.py || { echo 'Fix .env before syncing'; exit 1; }
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

# ---------------------------------------------------------------------------
# Alias definitions — single source: mirrors core/constants.CHAT_ID_ALIASES
# ---------------------------------------------------------------------------
CANONICAL_CHAT_ID = "TELEGRAM_CHAT_ID"
CHAT_ID_ALIASES: list[str] = [
    "TELEGRAMCHATID",
    "ALLOWED_USERS",
    "AUTHORIZED_USER_ID",
]

# Any other known dead/deprecated keys (add as they are retired)
DEAD_KEYS: list[str] = [
    "DEADMAN_PING_URL",      # typo variant — canonical is DEAD_MAN_PING_URL
    "ONEBRAIN_API_KEY",      # orphan — no source consumers
    "ONEBRAIN_API_BASE",     # orphan — no source consumers
]

ALL_VIOLATIONS: dict[str, str] = {
    **{alias: f"alias of {CANONICAL_CHAT_ID} — rename to {CANONICAL_CHAT_ID} and remove this key"
       for alias in CHAT_ID_ALIASES},
    **{key: "deprecated / orphan key — remove from .env"
       for key in DEAD_KEYS},
}


def _load_env_keys(path: Path) -> dict[str, str]:
    keys: dict[str, str] = {}
    if not path.exists():
        return keys
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        keys[k.strip()] = v.strip()
    return keys


def _scan_source_references() -> set[str]:
    """Return set of env-key-shaped strings found anywhere in .py / .sh source."""
    env_key_re = re.compile(r'\b([A-Z][A-Z0-9_]{3,})\b')
    skip_dirs = {".git", ".venv", "venv", "__pycache__", ".mypy_cache",
                 ".pytest_cache", ".ruff_cache", "node_modules", "logs"}
    refs: set[str] = set()
    for suffix in ("*.py", "*.sh"):
        for p in REPO_ROOT.rglob(suffix):
            if set(p.parts) & skip_dirs:
                continue
            try:
                for m in env_key_re.finditer(p.read_text(errors="ignore")):
                    refs.add(m.group(1))
            except Exception:
                pass
    return refs


def audit(warn_only: bool = False) -> int:
    env_path = REPO_ROOT / ".env"
    env_keys = _load_env_keys(env_path)

    if not env_keys:
        print(f"env_audit: .env not found or empty at {env_path}")
        return 0

    violations: list[str] = []
    warnings:   list[str] = []

    # 1. Alias / dead key check
    for key, reason in ALL_VIOLATIONS.items():
        if key in env_keys:
            violations.append(f"  ✗ {key}  —  {reason}")

    # 2. Orphan check: defined in .env, never referenced in any source file
    source_refs = _scan_source_references()
    ignore_orphan_prefixes = (
        "TELEGRAM_", "AUTHORIZED_", "API_",   # core infra — always keep
        "ANTHROPIC_", "OPENAI_", "GEMINI_",   # provider keys
        "GROQ_", "CEREBRAS_", "MISTRAL_",
        "DEEPSEEK_", "PERPLEXITY_", "TOGETHER_",
        "COHERE_", "FIREWORKS_", "XAI_",
        "SAMBANOVA_", "HYPERBOLIC_", "NOVITA_",
        "OPENROUTER_", "JULES_",
    )
    for key in env_keys:
        if key in ALL_VIOLATIONS:
            continue  # already flagged above
        if key in source_refs:
            continue
        if any(key.startswith(p) for p in ignore_orphan_prefixes):
            continue
        warnings.append(f"  ⚠  {key}  —  defined in .env but not referenced in source")

    # --- Report ---
    print(f"env_audit: scanning {env_path.relative_to(REPO_ROOT)} "
          f"({len(env_keys)} keys)")
    print()

    if violations:
        print("VIOLATIONS (must fix before sync):")
        for v in violations:
            print(v)
        print()

    if warnings:
        print("WARNINGS (review — may be intentional):")
        for w in warnings:
            print(w)
        print()

    if not violations and not warnings:
        print("env_audit: ✓ PASS — no alias keys, no orphans")
        return 0

    if violations:
        print(f"env_audit: ❌ FAIL — {len(violations)} violation(s) found")
        if not warn_only:
            print("  → Remove the alias/dead keys from .env and re-run.")
            return 1

    if warnings:
        print(f"env_audit: ⚠  {len(warnings)} orphan warning(s) — review manually")

    return 0


if __name__ == "__main__":
    warn_only = "--warn" in sys.argv
    sys.exit(audit(warn_only=warn_only))
