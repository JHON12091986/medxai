"""
NINA v15 — Canonicalization Engine
Detects alias clusters (same concept, different names) and proposes SSOT consolidation.

FILE_PURPOSE:
  Why: NINA suffers from AUTHORIZED_USER_ID / TELEGRAM_CHAT_ID / TELEGRAMCHATID /
       ALLOWED_USERS proliferation. This engine detects many-names-one-concept clusters
       and proposes canonical renames. Eliminates the entire class of patch_*.sh emergency fixes.
  Owner: ARCHITECT OVERWATCH / guardian_loop
  Breaks if removed: Canonicalization step in Guardian Loop, SSOT enforcement
  Dependencies: core/indexer.py, ast, re, pathlib
  Replaces: patch_authorized_user_id.sh (proactive vs reactive)
"""

FILE_PURPOSE = {
    "why": "Detect alias clusters and propose canonical constant/config names",
    "owner": "guardian_loop",
    "breaks_if_removed": ["ssot enforcement", "guardian loop canonicalization step"],
    "dependencies": ["core.indexer", "ast", "re"],
    "replaces": "patch_authorized_user_id.sh",
}

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent

# Known alias groups — seed list, engine discovers more dynamically
SEED_ALIAS_GROUPS: list[list[str]] = [
    ["AUTHORIZED_USER_ID", "TELEGRAM_CHAT_ID", "TELEGRAMCHATID", "ALLOWED_USERS",
     "ALLOWED_USER_ID", "AUTH_USER_ID", "OWNER_CHAT_ID", "OWNER_ID"],
    ["TELEGRAM_BOT_TOKEN", "BOT_TOKEN", "TG_TOKEN", "TELEGRAM_TOKEN"],
    ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY", "GOOGLE_GEMINI_KEY"],
    ["CLAUDE_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_KEY", "CLAUDE_KEY"],
    ["OPENAI_API_KEY", "OPENAI_KEY", "GPT_API_KEY"],
    ["NINA_ROOT", "NINA_HOME", "NINA_BASE_DIR", "BASE_DIR", "PROJECT_ROOT"],
    ["MODEL_NAME", "DEFAULT_MODEL", "LLM_MODEL", "AI_MODEL", "GEMINI_MODEL"],
]


def _normalize(name: str) -> str:
    """Normalize a constant/variable name for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _build_similarity_clusters(names: list[str]) -> list[list[str]]:
    """
    Cluster names by normalized form + seed group membership.
    Returns list of clusters (each cluster = same concept).
    """
    # Map normalized → original names
    norm_map: dict[str, list[str]] = defaultdict(list)
    for n in names:
        norm_map[_normalize(n)].append(n)

    clusters: list[set[str]] = []

    # Seed groups first
    for group in SEED_ALIAS_GROUPS:
        cluster: set[str] = set()
        for alias in group:
            if alias in names:
                cluster.add(alias)
            norm = _normalize(alias)
            for match in norm_map.get(norm, []):
                cluster.add(match)
        if len(cluster) > 1:
            clusters.append(cluster)

    # Dynamic: group by normalized form (catches typos/variants)
    covered = {n for c in clusters for n in c}
    for norm, orig_names in norm_map.items():
        uncovered = [n for n in orig_names if n not in covered]
        if len(uncovered) > 1:
            clusters.append(set(uncovered))
            covered.update(uncovered)

    return [sorted(c) for c in clusters]


def scan_repo_constants() -> dict[str, list[str]]:
    """
    Scan all Python files for module-level constant assignments.
    Returns {constant_name: [file1, file2, ...]} mapping.
    """
    constant_files: dict[str, list[str]] = defaultdict(list)
    skip = {".git", "__pycache__", ".venv", "venv", "archive", "backups"}
    for py in REPO_ROOT.rglob("*.py"):
        if any(p in py.parts for p in skip):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.isupper():
                        constant_files[t.id].append(str(py.relative_to(REPO_ROOT)))
    return dict(constant_files)


def scan_env_keys() -> dict[str, list[str]]:
    """
    Scan .env files and os.environ / os.getenv calls for key names.
    Returns {key_name: [file, ...]}.
    """
    key_files: dict[str, list[str]] = defaultdict(list)
    skip = {".git", "__pycache__", ".venv", "venv", "archive", "backups"}

    # .env files
    for env_file in REPO_ROOT.rglob(".env*"):
        if env_file.is_file():
            for line in env_file.read_text(errors="replace").splitlines():
                m = re.match(r"^([A-Z][A-Z0-9_]+)\s*=", line.strip())
                if m:
                    key_files[m.group(1)].append(str(env_file.relative_to(REPO_ROOT)))

    # Python os.environ / os.getenv calls
    for py in REPO_ROOT.rglob("*.py"):
        if any(p in py.parts for p in skip):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r'os\.(?:environ\.get|getenv)\(["\']([A-Z][A-Z0-9_]+)["\']', src):
            key_files[m.group(1)].append(str(py.relative_to(REPO_ROOT)))

    return dict(key_files)


def detect_alias_clusters() -> list[dict]:
    """
    Main detection function. Returns list of alias cluster reports.
    Each report: {canonical: str, aliases: list, files: dict, action: str}
    """
    constants = scan_repo_constants()
    env_keys = scan_env_keys()
    all_names = list(set(list(constants.keys()) + list(env_keys.keys())))
    clusters = _build_similarity_clusters(all_names)

    reports = []
    for cluster in clusters:
        # Pick canonical: longest name OR seed group first entry if present
        canonical = cluster[0]
        for group in SEED_ALIAS_GROUPS:
            if any(a in cluster for a in group):
                for a in group:
                    if a in cluster:
                        canonical = a
                        break
                break

        file_map: dict[str, list[str]] = {}
        for name in cluster:
            files = list(set((constants.get(name, []) + env_keys.get(name, []))))
            if files:
                file_map[name] = files

        if len(file_map) > 1:
            reports.append(
                {
                    "canonical": canonical,
                    "aliases": [n for n in cluster if n != canonical],
                    "files": file_map,
                    "action": f"Rename all aliases → {canonical}",
                    "total_occurrences": sum(len(v) for v in file_map.values()),
                }
            )

    return sorted(reports, key=lambda r: -r["total_occurrences"])


def generate_rename_plan(reports: list[dict] | None = None) -> str:
    """Generate a human-readable rename plan for Jules/Gemini prompt injection."""
    if reports is None:
        reports = detect_alias_clusters()
    if not reports:
        return "✅ No alias clusters detected. Constants are canonical."

    lines = ["# NINA Canonicalization Report", ""]
    for i, r in enumerate(reports, 1):
        lines.append(f"## Cluster {i}: `{r['canonical']}`")
        lines.append(f"**Action**: {r['action']}")
        lines.append(f"**Aliases found**:")
        for alias in r["aliases"]:
            files = r["files"].get(alias, [])
            lines.append(f"  - `{alias}` in: {', '.join(files[:3])}"
                         + (f" (+{len(files)-3} more)" if len(files) > 3 else ""))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    reports = detect_alias_clusters()
    if "--json" in sys.argv:
        print(json.dumps(reports, indent=2))
    else:
        print(generate_rename_plan(reports))
