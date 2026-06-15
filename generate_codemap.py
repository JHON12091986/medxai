#!/usr/bin/env python3
"""
generate_codemap.py — static AST-based codebase topology generator for NINA
Outputs nina_codemap.md: every Python file's purpose, imports, exports, and callers.

Usage:
    python3 generate_codemap.py           # writes nina_codemap.md
    python3 generate_codemap.py --json    # also writes nina_codemap.json
    python3 generate_codemap.py <file>    # show codemap row for one file

Called automatically by nina_sync.sh after every sync.
"""

import ast
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT = Path(__file__).parent
OUTPUT_MD = ROOT / "nina_codemap.md"
OUTPUT_JSON = ROOT / "nina_codemap.json"

# Files/dirs to skip
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".jules", ".gemini"}
SKIP_FILES = {"generate_codemap.py"}

# One-line purpose hints for well-known files (fallback if no docstring)
PURPOSE_HINTS = {
    "core/nina.py": "NinaOS orchestrator — central brain",
    "core/router.py": "HybridRouter V4 — provider routing + CircuitBreaker",
    "tools/ninaflash.py": "Universe-Mode kernel — 100+ tool functions",
    "ninagate/main.py": "OpenAI-compatible proxy at localhost:8080",
    "interfaces/telegram_interface.py": "Primary Telegram UI",
    "guardian_engine.py": "Forensic AST scanner + service health monitor",
    "idleloop.py": "Idle upgrade proposal loop — 7-topic rotation",
    "main.py": "Entry point — starts all services",
    "ninajulesgithub.py": "Jules PR watcher + auto-notify service",
    "rule0_audit.py": "Pre-commit audit — Rule 0 compliance checker",
}


def get_python_files():
    files = []
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT)
        parts = rel.parts
        if any(d in SKIP_DIRS for d in parts):
            continue
        if path.name in SKIP_FILES:
            continue
        files.append(path)
    return sorted(files)


def extract_file_info(path: Path) -> dict:
    rel = str(path.relative_to(ROOT))
    info = {
        "file": rel,
        "purpose": PURPOSE_HINTS.get(rel, ""),
        "imports": [],
        "exports": [],   # top-level defs: functions + classes
        "parse_error": False,
    }

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=rel)
    except SyntaxError as e:
        info["parse_error"] = str(e)
        return info

    # Extract docstring as purpose if no hint
    if not info["purpose"]:
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module,)):
                docstring = ast.get_docstring(node)
                if docstring:
                    # First line only, max 80 chars
                    info["purpose"] = docstring.splitlines()[0][:80]
                break

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                info["imports"].append(node.module)

    # Deduplicate, keep only local-looking imports (no stdlib)
    STDLIB_PREFIXES = {
        "os", "sys", "re", "json", "ast", "time", "math", "copy", "enum",
        "abc", "io", "pathlib", "typing", "collections", "functools",
        "itertools", "datetime", "logging", "threading", "asyncio",
        "subprocess", "hashlib", "base64", "urllib", "http", "socket",
        "signal", "traceback", "inspect", "dataclasses", "contextlib",
        "warnings", "weakref", "gc", "struct", "array", "queue",
        "concurrent", "multiprocessing", "unittest", "pytest",
    }
    local_imports = []
    for imp in info["imports"]:
        root_mod = imp.split(".")[0]
        if root_mod not in STDLIB_PREFIXES:
            local_imports.append(imp)
    info["imports"] = sorted(set(local_imports))

    # Extract top-level exports (functions + classes)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                info["exports"].append(f"def {node.name}")
        elif isinstance(node, ast.ClassDef):
            info["exports"].append(f"class {node.name}")

    return info


def build_caller_map(all_info: list) -> dict:
    """For each file, find which other files import it."""
    # Map module-name-like strings back to file paths
    # e.g. "core.router" or "core/router" -> "core/router.py"
    file_to_modnames = {}
    for info in all_info:
        f = info["file"]  # e.g. "core/router.py"
        stem = f.replace("/", ".").replace("\\", ".").removesuffix(".py")
        basename = Path(f).stem
        file_to_modnames[f] = {stem, basename, f}

    caller_map = defaultdict(list)  # file -> [callers]
    for info in all_info:
        for imp in info["imports"]:
            for target_file, modnames in file_to_modnames.items():
                if imp in modnames or any(imp.endswith(m) for m in modnames):
                    if target_file != info["file"]:
                        caller_map[target_file].append(info["file"])

    return dict(caller_map)


def write_markdown(all_info: list, caller_map: dict):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# NINA Codebase Map",
        f"> Auto-generated by `generate_codemap.py` — last updated: {now}",
        "> Do NOT edit manually. Re-run via `python3 generate_codemap.py` or `./nina_sync.sh`.",
        "",
        "## How to use",
        "Before any agy task touching `core/` or `interfaces/`, read the relevant rows below.",
        "Check **Called by** to know your blast radius before editing.",
        "",
        "---",
        "",
    ]

    for info in all_info:
        f = info["file"]
        callers = sorted(set(caller_map.get(f, [])))
        purpose = info["purpose"] or "_(no docstring)_"
        imports_str = ", ".join(f"`{i}`" for i in info["imports"]) or "none"
        callers_str = ", ".join(f"`{c}`" for c in callers) or "none"
        exports_str = ", ".join(f"`{e}`" for e in info["exports"][:8]) or "none"
        if len(info["exports"]) > 8:
            exports_str += f" _(+{len(info['exports'])-8} more)_"

        lines.append(f"### `{f}`")
        lines.append(f"**Purpose:** {purpose}  ")
        if info.get("parse_error"):
            lines.append(f"**⚠️ Parse error:** {info['parse_error']}  ")
        lines.append(f"**Imports:** {imports_str}  ")
        lines.append(f"**Called by:** {callers_str}  ")
        lines.append(f"**Exports:** {exports_str}  ")
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ nina_codemap.md written — {len(all_info)} files mapped")


def write_json(all_info: list, caller_map: dict):
    data = []
    for info in all_info:
        data.append({
            **info,
            "called_by": sorted(set(caller_map.get(info["file"], [])))
        })
    OUTPUT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✅ nina_codemap.json written")


def show_single_file(target: str, all_info: list, caller_map: dict):
    for info in all_info:
        if info["file"] == target or Path(info["file"]).name == target:
            callers = sorted(set(caller_map.get(info["file"], [])))
            print(f"\nFile    : {info['file']}")
            print(f"Purpose : {info['purpose'] or '(none)'}")
            print(f"Imports : {', '.join(info['imports']) or 'none'}")
            print(f"Called by: {', '.join(callers) or 'none'}")
            print(f"Exports : {', '.join(info['exports'][:10]) or 'none'}")
            return
    print(f"File not found in codemap: {target}")


def main():
    emit_json = "--json" in sys.argv
    single_file = next((a for a in sys.argv[1:] if not a.startswith("-")), None)

    files = get_python_files()
    all_info = [extract_file_info(f) for f in files]
    caller_map = build_caller_map(all_info)

    if single_file:
        show_single_file(single_file, all_info, caller_map)
        return

    write_markdown(all_info, caller_map)
    if emit_json:
        write_json(all_info, caller_map)


if __name__ == "__main__":
    main()
