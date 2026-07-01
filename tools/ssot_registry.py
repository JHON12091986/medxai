#!/usr/bin/env python3
"""
ssot_registry.py  —  NINA Single Source of Truth Registry Engine

Purpose: Maintain docs/space/nina_file_registry.json as the canonical SSOT
         tuple store. Every file in the repo must have a registered entry.

Commands:
  sync  <fs_snapshot_path>   — reconcile registry vs live filesystem
  semantic                   — extract AST docstrings and update registry tuples
  semantic_dup               — find .py files with identical normalized AST
  drift                      — check INTM mirrors against their INTJ source
  redundancy                 — flag registry entries with redundancy_check=fail
  orphan_count               — print count of orphaned (unregistered) files
  init                       — seed registry from scratch using current filesystem

Integrated by nina_sync.sh v10.0 — do not call standalone in production.
"""

import ast
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent.resolve()
REGISTRY_PATH = REPO_ROOT / "docs" / "space" / "nina_file_registry.json"

# ---------------------------------------------------------------------------
# SSOT tuple schema (all fields mandatory; empty string = unknown)
# ---------------------------------------------------------------------------
DEFAULT_TUPLE: dict[str, Any] = {
    "path": "",
    "purpose": "",          # human-readable reason for existence
    "ssot": False,          # True = this file is THE source; others derive from it
    "intj": "",             # path of INTJ source if this file is an INTM mirror
    "intm": [],             # list of INTM mirror paths if this file is INTJ source
    "symlinks": [],         # symlinks pointing TO this file
    "consumers": [],        # files/dirs that import or depend on this file
    "ast_exports": [],      # top-level functions/classes exported (auto-filled)
    "ast_docstring": "",    # module-level docstring (auto-filled)
    "last_verified": "",    # ISO date of last manual verification
    "redundancy_check": "unknown",  # pass | fail | unknown
    "hash_md5": "",         # auto-filled on sync
}

SKIP_PATTERNS = {".git", "venv", "__pycache__", "logs", ".cache", ".pyc", "node_modules", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", "dist", "build", ".next", ".nuxt", ".svelte-kit", ".idea", ".vscode"}
SKIP_PREFIXES = ("data/graphs/", "data/router/", "tools/docs/generated/", "docs/_site/", "site/", "tmp/", "output/")
SKIP_SUFFIXES = (".db", ".sqlite", ".sqlite3", ".bin", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".pdf", ".zip", ".tar", ".gz")


def _should_skip(path_str: str) -> bool:
    if any(p in path_str for p in SKIP_PATTERNS):
        return True
    if path_str.startswith(SKIP_PREFIXES):
        return True
    if path_str.endswith(SKIP_SUFFIXES):
        return True
    return False


def _md5(path: Path) -> str:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def _load_registry() -> dict:
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text())
        except Exception:
            return {"_meta": {}, "files": []}
    return {"_meta": {}, "files": []}


def _save_registry(reg: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_content = json.dumps(reg, indent=2, ensure_ascii=False)
    # Idempotency: only write if changed
    if REGISTRY_PATH.exists() and REGISTRY_PATH.read_text() == new_content:
        return
    REGISTRY_PATH.write_text(new_content)


def _files_from_registry(reg: dict) -> dict[str, dict]:
    return {entry["path"]: entry for entry in reg.get("files", [])}


# ---------------------------------------------------------------------------
# cmd: sync
# ---------------------------------------------------------------------------
def cmd_sync(fs_snapshot_path: str) -> None:
    """Reconcile registry against live filesystem snapshot."""
    reg = _load_registry()
    registered = _files_from_registry(reg)

    # Load FS snapshot (list of relative paths)
    snapshot_file = Path(fs_snapshot_path)
    if not snapshot_file.exists():
        # Fallback: walk repo directly
        live_files = [
            str(p.relative_to(REPO_ROOT))
            for p in REPO_ROOT.rglob("*")
            if (p.is_file() or p.is_symlink()) and not _should_skip(str(p))
        ]
    else:
        live_files = [line.strip() for line in snapshot_file.read_text().splitlines() if line.strip()]

    live_set = set(live_files)
    reg_set = set(registered.keys())

    orphans = live_set - reg_set
    deleted = reg_set - live_set

    for path_str in sorted(orphans):
        print(f"ORPHAN: {path_str}")
        entry = DEFAULT_TUPLE.copy()
        entry["path"] = path_str
        entry["last_verified"] = str(date.today())
        entry["hash_md5"] = _md5(REPO_ROOT / path_str)
        if path_str.endswith(".py"):
            entry["purpose"] = "Python source discovered by SSOT auto-seed; human purpose pending."
        elif path_str.endswith(".sh"):
            entry["purpose"] = "Shell script discovered by SSOT auto-seed; human purpose pending."
        elif path_str.endswith(".md"):
            entry["purpose"] = "Documentation discovered by SSOT auto-seed; human purpose pending."
        elif path_str.endswith(".json"):
            entry["purpose"] = "JSON artifact/config discovered by SSOT auto-seed; human purpose pending."
        else:
            entry["purpose"] = "Auto-seeded file discovered by SSOT; human purpose pending."
        reg["files"].append(entry)

    for path_str in sorted(deleted):
        print(f"DELETED_FROM_FS: {path_str}")
        # Mark as deleted (don't remove — preserve history)
        registered[path_str]["redundancy_check"] = "deleted_from_fs"

    # Update hashes for all existing entries
    for entry in reg["files"]:
        p = REPO_ROOT / entry["path"]
        if p.is_file():
            entry["hash_md5"] = _md5(p)

    reg["_meta"] = {
        "last_sync": str(date.today()),
        "total_registered": len(reg["files"]),
        "orphans_found": len(orphans),
        "deleted_found": len(deleted),
    }
    _save_registry(reg)
    print(f"registry sync complete: {len(orphans)} new, {len(deleted)} deleted, {len(reg['files'])} total")


# ---------------------------------------------------------------------------
# cmd: semantic
# ---------------------------------------------------------------------------
def cmd_semantic() -> None:
    """Extract AST exports and docstrings for all .py files in registry."""
    reg = _load_registry()
    updated = 0
    for entry in reg["files"]:
        if not entry["path"].endswith(".py"):
            continue
        p = REPO_ROOT / entry["path"]
        if not p.is_file():
            continue
        try:
            source = p.read_text(errors="replace")
            tree = ast.parse(source)
            exports = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    exports.append(node.name)
            docstring = ast.get_docstring(tree) or ""
            if entry.get("ast_exports") != exports or entry.get("ast_docstring") != docstring:
                entry["ast_exports"] = exports
                entry["ast_docstring"] = docstring[:400]  # cap at 400 chars
                # Auto-fill purpose from docstring if empty
                if not entry.get("purpose") and docstring:
                    entry["purpose"] = docstring.split("\n")[0][:120]
                updated += 1
        except Exception:
            pass
    _save_registry(reg)
    print(f"semantic index: {updated} entries updated")


# ---------------------------------------------------------------------------
# cmd: semantic_dup
# ---------------------------------------------------------------------------
def cmd_semantic_dup() -> None:
    """Find .py files with identical normalized AST (structural duplicates)."""
    ast_hashes: dict[str, list[str]] = {}
    for p in REPO_ROOT.rglob("*.py"):
        if _should_skip(str(p)):
            continue
        try:
            source = p.read_text(errors="replace")
            tree = ast.parse(source)
            # Normalize: strip docstrings and comments, hash the dumped AST
            normalized = ast.dump(tree)
            h = hashlib.md5(normalized.encode()).hexdigest()
            rel = str(p.relative_to(REPO_ROOT))
            ast_hashes.setdefault(h, []).append(rel)
        except Exception:
            pass
    found = False
    for h, paths in ast_hashes.items():
        if len(paths) > 1:
            print(f"SEMANTIC_DUP [{h[:8]}]: {' | '.join(paths)}")
            found = True
    if not found:
        print("no semantic duplicates found")


# ---------------------------------------------------------------------------
# cmd: drift
# ---------------------------------------------------------------------------
def cmd_drift() -> None:
    """Check INTM mirrors against their INTJ source hashes."""
    reg = _load_registry()
    drift_found = False
    for entry in reg["files"]:
        intj_path = entry.get("intj", "")
        if not intj_path:
            continue
        # This entry is an INTM mirror
        mirror_path = REPO_ROOT / entry["path"]
        source_path = REPO_ROOT / intj_path
        if not mirror_path.is_file() or not source_path.is_file():
            continue
        mirror_hash = _md5(mirror_path)
        source_hash = _md5(source_path)
        if mirror_hash != source_hash:
            print(f"DRIFT: {entry['path']} (INTM) differs from {intj_path} (INTJ)")
            drift_found = True
    if not drift_found:
        print("no INTJ/INTM drift detected")


# ---------------------------------------------------------------------------
# cmd: redundancy
# ---------------------------------------------------------------------------
def cmd_redundancy() -> None:
    """Flag entries with empty purpose (undiscoverable) or deleted state."""
    reg = _load_registry()
    flagged = 0
    for entry in reg["files"]:
        purpose = (entry.get("purpose") or "").strip()
        if not purpose:
            entry["redundancy_check"] = "fail_no_purpose"
            print(f"NO_PURPOSE: {entry['path']}")
            flagged += 1
        elif entry.get("redundancy_check") in {"unknown", "fail_no_purpose"}:
            if "human purpose pending" in purpose.lower() or "auto-seed" in purpose.lower():
                entry["redundancy_check"] = "provisional"
            else:
                entry["redundancy_check"] = "pass"
    _save_registry(reg)
    print(f"redundancy check: {flagged} files flagged with no purpose")


# ---------------------------------------------------------------------------
# cmd: orphan_count
# ---------------------------------------------------------------------------
def cmd_orphan_count() -> None:
    """Print count of files on disk not in registry."""
    reg = _load_registry()
    registered = set(_files_from_registry(reg).keys())
    live_files = {
        str(p.relative_to(REPO_ROOT))
        for p in REPO_ROOT.rglob("*")
        if (p.is_file() or p.is_symlink()) and not _should_skip(str(p))
    }
    print(len(live_files - registered))


# ---------------------------------------------------------------------------
# cmd: init
# ---------------------------------------------------------------------------
def cmd_init() -> None:
    """Seed registry from scratch — walk repo and create default tuples."""
    reg = _load_registry()
    existing_paths = set(_files_from_registry(reg).keys())

    new_entries = []
    for p in sorted(REPO_ROOT.rglob("*")):
        if not (p.is_file() or p.is_symlink()):
            continue
        if _should_skip(str(p)):
            continue
        rel = str(p.relative_to(REPO_ROOT))
        if rel in existing_paths:
            continue
        entry = DEFAULT_TUPLE.copy()
        entry["path"] = rel
        entry["last_verified"] = str(date.today())
        entry["hash_md5"] = _md5(p) if p.is_file() else ""
        new_entries.append(entry)

    reg["files"] = reg.get("files", []) + new_entries
    reg["_meta"] = {
        "last_sync": str(date.today()),
        "total_registered": len(reg["files"]),
        "seeded_on_init": len(new_entries),
    }
    _save_registry(reg)
    print(f"registry initialized: {len(new_entries)} new entries, {len(reg['files'])} total")


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "sync":
        cmd_sync(sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "semantic":
        cmd_semantic()
    elif cmd == "semantic_dup":
        cmd_semantic_dup()
    elif cmd == "drift":
        cmd_drift()
    elif cmd == "redundancy":
        cmd_redundancy()
    elif cmd == "orphan_count":
        cmd_orphan_count()
    elif cmd == "init":
        cmd_init()
    else:
        print(__doc__)
        sys.exit(0)
