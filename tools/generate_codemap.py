#!/usr/bin/env python3
"""
generate_codemap.py — full-repo AST-based codebase topology generator for NINA.
Scans ALL Python packages: tools/, core/, interfaces/, ninagate/, agy/, agent/,
crons/, scripts/, checks/, gemini/, perplexity/, upgrades/ + root *.py files.

Outputs:
  CODEBASE_MAP.md  → repo root  (human + agent readable)
  tools/nina_codemap.json → machine-readable (agents, ninaflash, etc.)

Status annotation: add a comment anywhere in a file:
  # NINA-STATUS: ✅ Active & justified
  # NINA-STATUS: ⚠️ Needs verification — possible duplicate of tools/nina_ooda.py
  # NINA-STATUS: 🔴 Duplicate — delete; canonical is tools/nina_cicd.py
  # NINA-STATUS: 🧹 Cleanup target — incident patch, check if still needed

Usage:
    python3 tools/generate_codemap.py           # writes CODEBASE_MAP.md at repo root
    python3 tools/generate_codemap.py --json    # also writes tools/nina_codemap.json
    python3 tools/generate_codemap.py <file>    # show codemap row for one file

Called automatically by scripts/nina_sync.sh after every sync.
"""

import ast
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

TOOLS_DIR   = Path(__file__).parent          # tools/
REPO_ROOT   = TOOLS_DIR.parent              # repo root
OUTPUT_MD   = REPO_ROOT / "CODEBASE_MAP.md"
OUTPUT_JSON = TOOLS_DIR / "nina_codemap.json"

# ── Directories to scan (relative to REPO_ROOT) ──────────────────────────────
SCAN_DIRS = [
    "tools",
    "core",
    "interfaces",
    "ninagate",
    "agy",
    "agent",
    "crons",
    "scripts",
    "checks",
    "gemini",
    "perplexity",
    "upgrades",
    "git-hooks",
    "dashboard",
    "deploy",
    "bin",
    "jules",
]

# Root-level .py files to include explicitly
SCAN_ROOT_PY = True

SKIP_DIRS  = {"__pycache__", ".git", ".venv", "venv", "node_modules",
              ".jules", ".gemini", "archive", "exports", "data", "tests",
              "templates", "docs", ".config", ".cursor", ".github"}
SKIP_FILES = {"generate_codemap.py"}

PURPOSE_HINTS = {
    "core/nina.py":                     "NinaOS orchestrator — central brain",
    "core/router.py":                   "HybridRouter V4 — provider routing + CircuitBreaker",
    "tools/ninaflash.py":               "ninaflash CLI dispatcher — 100+ tool functions",
    "ninagate/main.py":                 "OpenAI-compatible proxy at localhost:8080",
    "interfaces/telegram_interface.py": "Primary Telegram UI",
    "tools/guardian_engine.py":         "Forensic AST scanner + service health monitor",
    "tools/idleloop.py":                "Idle upgrade proposal loop — 7-topic rotation",
    "main.py":                          "Entry point — starts all services",
    "tools/ninajulesgithub.py":         "Jules PR watcher + auto-notify service",
    "tools/rule0_audit.py":             "Pre-commit audit — Rule 0 compliance checker",
    "tools/jules.py":                   "Jules Unified Engine v6 — one-file pipeline",
    "tools/nina_cicd.py":               "Autonomous CI/CD Orchestrator (CICD-001)",
    "tools/nina_ooda.py":               "OODA Engine (OODA-001) — observe/orient/decide/act",
    "tools/pipeline_autopilot.py":      "AGY Autonomous Mode — pipeline autopilot",
    "tools/ninaflash_core.py":          "ninaflash kernel — shell, git, find, edit primitives",
    "tools/surgical_merge.py":          "Surgical PR merge with verification",
    "tools/telegram_notify.py":         "Telegram notification helper",
    "tools/merge_resolver.py":          "Merge conflict resolver",
    "tools/nina_proxy.py":              "FastAPI proxy — routes requests to local/cloud LLMs",
}

# Confirmed duplicate pairs: (stale_file, canonical_file, action)
KNOWN_DUPLICATES = [
    ("core/nina_ooda.py",           "tools/nina_ooda.py",          "Delete core/ version; tools/ is canonical CLI"),
    ("core/reflexion.py",           "core/cognition/reflexion.py", "Deprecate root version; cognition/ is canonical"),
    ("scripts/nina_cicd.py",        "tools/nina_cicd.py",          "Delete scripts/ version; tools/ is canonical"),
    ("tools/sync_env.py",           "tools/nina_env_sync.py",      "Verify: sync_env syncs .env file, nina_env_sync syncs vault — may both be justified"),
    ("tools/observable_monitor.py", "tools/monitor.py",            "Verify: thin psutil wrapper; may merge into monitor.py"),
]

STATUS_RE = re.compile(r"#\s*NINA-STATUS:\s*(.+)", re.IGNORECASE)

STDLIB_PREFIXES = {
    "os","sys","re","json","ast","time","math","copy","enum","abc","io",
    "pathlib","typing","collections","functools","itertools","datetime",
    "logging","threading","asyncio","subprocess","hashlib","base64",
    "urllib","http","socket","signal","traceback","inspect","dataclasses",
    "contextlib","warnings","weakref","gc","struct","array","queue",
    "concurrent","multiprocessing","unittest","pytest","__future__",
    "platform","shutil","tempfile","textwrap","pprint","string","random",
    "sqlite3","csv","configparser","argparse","shlex","fcntl","fnmatch",
    "uuid","glob","difflib","getpass","pwd","grp","zipfile","tarfile",
    "xml","html","email","smtplib","ftplib","telnetlib","ssl","hmac",
    "secrets","decimal","fractions","statistics","heapq","bisect",
    "operator","pickle","shelve","dbm","codecs","unicodedata","locale",
    "gettext","calendar","zoneinfo","zlib","bz2","lzma","gzip",
}


def get_python_files() -> list[Path]:
    files = []

    # Scan defined subdirectories
    for dir_name in SCAN_DIRS:
        dir_path = REPO_ROOT / dir_name
        if not dir_path.exists():
            continue
        for path in sorted(dir_path.rglob("*.py")):
            rel = path.relative_to(REPO_ROOT)
            if any(d in SKIP_DIRS for d in rel.parts):
                continue
            if path.name in SKIP_FILES:
                continue
            files.append(path)

    # Root-level .py files
    if SCAN_ROOT_PY:
        for path in sorted(REPO_ROOT.glob("*.py")):
            if path.name in SKIP_FILES:
                continue
            files.append(path)

    # Deduplicate while preserving order
    seen = set()
    result = []
    for f in files:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            result.append(f)
    return result


def extract_file_info(path: Path) -> dict:
    rel = str(path.relative_to(REPO_ROOT))
    info = {
        "file":        rel,
        "purpose":     PURPOSE_HINTS.get(rel, ""),
        "status":      "",
        "imports":     [],
        "exports":     [],
        "parse_error": False,
    }
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree   = ast.parse(source, filename=rel)
    except SyntaxError as e:
        info["parse_error"] = str(e)
        info["status"]      = "⚠️ Parse error"
        return info

    m = STATUS_RE.search(source)
    info["status"] = m.group(1).strip() if m else ""

    if not info["purpose"]:
        for node in ast.walk(tree):
            if isinstance(node, ast.Module):
                doc = ast.get_docstring(node)
                if doc:
                    info["purpose"] = doc.splitlines()[0][:80]
                break

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                info["imports"].append(node.module)

    info["imports"] = sorted({i for i in info["imports"]
                               if i.split(".")[0] not in STDLIB_PREFIXES})

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                info["exports"].append("def " + node.name)
        elif isinstance(node, ast.ClassDef):
            info["exports"].append("class " + node.name)

    return info


def build_caller_map(all_info: list) -> dict:
    file_to_modnames = {}
    for info in all_info:
        f    = info["file"]
        stem = f.replace("/", ".").replace("\\", ".").removesuffix(".py")
        file_to_modnames[f] = {stem, Path(f).stem, f}

    caller_map = defaultdict(list)
    for info in all_info:
        for imp in info["imports"]:
            for target_file, modnames in file_to_modnames.items():
                if imp in modnames or any(imp.endswith(m) for m in modnames):
                    if target_file != info["file"]:
                        caller_map[target_file].append(info["file"])
    return dict(caller_map)


def group_by_dir(all_info: list) -> dict:
    groups = defaultdict(list)
    for info in all_info:
        parts = Path(info["file"]).parts
        top   = parts[0] if len(parts) > 1 else "(root)"
        groups[top].append(info)
    return dict(groups)


def write_markdown(all_info: list, caller_map: dict):
    now    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    groups = group_by_dir(all_info)

    # Directory order for output
    DIR_ORDER = ["(root)", "core", "tools", "interfaces", "ninagate",
                 "agy", "agent", "crons", "scripts", "checks",
                 "gemini", "perplexity", "upgrades", "git-hooks",
                 "dashboard", "deploy", "bin", "jules"]
    # Append any dirs not in order list
    for k in groups:
        if k not in DIR_ORDER:
            DIR_ORDER.append(k)

    lines = [
        "# NINA Codebase Map",
        f"> Auto-generated by `tools/generate_codemap.py` — last updated: {now}",
        "> Scans: `tools/` `core/` `interfaces/` `ninagate/` `agy/` `agent/` `crons/` `scripts/` `checks/` `gemini/` `perplexity/` `upgrades/` + root `*.py`",
        "> Do NOT edit manually. Re-run via `python3 tools/generate_codemap.py` or `./scripts/nina_sync.sh`.",
        "",
        "## How to use",
        "Before any agy/Jules task, read the relevant rows below.",
        "Check **Called by** to know your blast radius before editing.",
        "Add `# NINA-STATUS: <emoji> <reason>` anywhere in a file to set its status badge.",
        "",
        "**Status legend:** ✅ Active & justified | ⚠️ Needs review | 🔴 Duplicate/stale | 🧹 Cleanup target",
        "",
        "---",
        "",
    ]

    if KNOWN_DUPLICATES:
        lines += [
            "## 🔴 Known Duplicate Pairs (Resolve First)",
            "",
            "| Stale File | Canonical File | Action |",
            "|------------|----------------|--------|",
        ]
        for stale, canon, action in KNOWN_DUPLICATES:
            lines.append(f"| `{stale}` | `{canon}` | {action} |")
        lines += ["", "---", ""]

    for dir_name in DIR_ORDER:
        if dir_name not in groups:
            continue
        label = dir_name if dir_name != "(root)" else "root"
        lines += [f"## `{label}/`", ""]

        for info in groups[dir_name]:
            f           = info["file"]
            callers     = sorted(set(caller_map.get(f, [])))
            purpose     = info["purpose"] or "_(no docstring)_"
            status      = info["status"]  or "✅"
            imports_str = ", ".join("`" + i + "`" for i in info["imports"]) or "none"
            callers_str = ", ".join("`" + c + "`" for c in callers) or "none"
            exp8        = info["exports"][:8]
            exports_str = ", ".join("`" + e + "`" for e in exp8) or "none"
            if len(info["exports"]) > 8:
                exports_str += " _(+" + str(len(info["exports"]) - 8) + " more)_"

            lines.append("### `" + f + "`")
            lines.append("**Purpose:** " + purpose + "  ")
            lines.append("**Status:** " + status + "  ")
            if info.get("parse_error"):
                lines.append("**⚠️ Parse error:** " + str(info["parse_error"]) + "  ")
            lines.append("**Imports:** " + imports_str + "  ")
            lines.append("**Called by:** " + callers_str + "  ")
            lines.append("**Exports:** " + exports_str + "  ")
            lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ CODEBASE_MAP.md written → repo root — {len(all_info)} files mapped across {len(groups)} dirs")


def write_json(all_info: list, caller_map: dict):
    data = [{**i, "called_by": sorted(set(caller_map.get(i["file"], [])))} for i in all_info]
    OUTPUT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✅ tools/nina_codemap.json written — {len(data)} entries")


def show_single_file(target: str, all_info: list, caller_map: dict):
    for info in all_info:
        if info["file"] == target or Path(info["file"]).name == target:
            callers = sorted(set(caller_map.get(info["file"], [])))
            print("\nFile    :", info["file"])
            print("Purpose :", info["purpose"] or "(none)")
            print("Status  :", info["status"] or "✅ (default)")
            print("Imports :", ", ".join(info["imports"]) or "none")
            print("Called by:", ", ".join(callers) or "none")
            print("Exports :", ", ".join(info["exports"][:10]) or "none")
            return
    print("File not found in codemap:", target)


def main():
    emit_json   = "--json" in sys.argv
    single_file = next((a for a in sys.argv[1:] if not a.startswith("-")), None)

    files      = get_python_files()
    all_info   = [extract_file_info(f) for f in files]
    caller_map = build_caller_map(all_info)

    if single_file:
        show_single_file(single_file, all_info, caller_map)
        return

    write_markdown(all_info, caller_map)
    if emit_json:
        write_json(all_info, caller_map)


if __name__ == "__main__":
    main()
