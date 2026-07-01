#!/usr/bin/env python3
"""
nina_ssot.py — NINA Single Source of Truth Engine v2.4
4 phases: DISCOVER → ANALYSE → WRITE → ENFORCE

Usage:
    python tools/nina_ssot.py --report        # full report, non-blocking
    python tools/nina_ssot.py --enforce       # exit 1 on violations
    python tools/nina_ssot.py                 # default: report + enforce

.env annotation:
    KEY=value  # ssot:exempt   → key excluded from orphan checking (pre-provisioned)
"""
from __future__ import annotations
import argparse, ast, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILES = [".env", ".env.local", ".env.production", ".env.staging"]
OUT_JSON = ROOT / "data" / "nina_ssot.json"
OUT_MD   = ROOT / "docs" / "nina_ssot.md"

_SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", "upgrades"}

# Files exempt from VIOLATION flagging (hardcode check only).
# These files ARE the mapping/definition layer — they're allowed to hold
# raw env key strings.  They still count as consumers.
_HARDCODE_EXEMPT_EXACT = {
    "core/constants.py",
    "core/hotreload.py",
    "core/vault.py",
    "checks/env_checks.py",
    "tools/env_audit.py",
    "interfaces/cli_interface.py",
}
_HARDCODE_EXEMPT_PREFIX = ("tests/",)

_GETENV_CALLS = {"getenv", "get", "get_secret", "environ"}

# Keys in constants.py whose string value appears as a dict/list literal
# in exempt files — these are the provider-key consumers.
# We extract them by scanning all string constants in core/constants.py.
_CONSTANTS_FILE = "core/constants.py"


def _is_hardcode_exempt(rel: str) -> bool:
    if rel in _HARDCODE_EXEMPT_EXACT:
        return True
    return any(rel.startswith(p) for p in _HARDCODE_EXEMPT_PREFIX)


# ════════════════════ PHASE 1 ════════════════════

def _iter_py(root: Path):
    for p in root.rglob("*.py"):
        if not any(s in p.parts for s in _SKIP_DIRS):
            yield p

def _iter_sh(root: Path):
    for p in root.rglob("*.sh"):
        if not any(s in p.parts for s in _SKIP_DIRS):
            yield p

def discover_env_vars(root: Path) -> tuple[dict, set]:
    """Returns (env_map, exempt_keys).
    env_map: {KEY: {value, sources}}
    exempt_keys: keys annotated with # ssot:exempt in .env
    """
    env_map: dict = {}
    exempt_keys: set = set()
    for name in ENV_FILES:
        path = root / name
        if not path.exists():
            continue
        for line in path.read_text(errors="replace").splitlines():
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            is_exempt = "# ssot:exempt" in raw
            key, _, rest = raw.partition("=")
            key = key.strip()
            val = rest.split("#")[0].strip().strip('"').strip("'")
            if key not in env_map:
                env_map[key] = {"value": val, "sources": []}
            env_map[key]["sources"].append(str(path.relative_to(root)))
            if is_exempt:
                exempt_keys.add(key)
    return env_map, exempt_keys

def _collect_getenv_args(tree: ast.AST) -> set[tuple[int, str]]:
    """Collect (lineno, key) for getenv-style calls and os.environ[key]."""
    found: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in _GETENV_CALLS:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    found.add((getattr(node.args[0], "lineno", 0), node.args[0].value))
        elif isinstance(node, ast.Subscript):
            if (isinstance(node.value, ast.Attribute) and node.value.attr == "environ"
                    and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)):
                found.add((getattr(node.slice, "lineno", 0), node.slice.value))
    return found

def _collect_string_constants(tree: ast.AST) -> set[str]:
    """Collect all plain string constant values in a file (for exempt-file consumer tracking)."""
    found: set = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value:
            found.add(node.value)
    return found

def discover_py_symbols(root: Path) -> tuple[dict, dict, dict, dict]:
    import_graph: dict = {}; symbol_map: dict = {}
    getenv_args: dict = {}   # non-exempt files: {rel: set((lineno, key))}
    exempt_strings: dict = {} # exempt files: {rel: set(str)}
    for py in _iter_py(root):
        rel = str(py.relative_to(root))
        try:
            tree = ast.parse(py.read_text(errors="replace"), filename=str(py))
        except SyntaxError:
            continue
        imports, functions, classes, constants = [], [], [], []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names: imports.append(a.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module: imports.append(node.module)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.isupper(): constants.append(t.id)
        import_graph[rel] = sorted(set(imports))
        symbol_map[rel]   = {"functions": functions, "classes": classes, "constants": constants}
        if _is_hardcode_exempt(rel):
            exempt_strings[rel] = _collect_string_constants(tree)
        else:
            getenv_args[rel] = _collect_getenv_args(tree)
    return import_graph, symbol_map, getenv_args, exempt_strings

def discover_sh_env_refs(root: Path) -> dict:
    pattern = re.compile(r"\$\{?([A-Z][A-Z0-9_]{2,})\}?")
    result: dict = {}
    for sh in _iter_sh(root):
        rel = str(sh.relative_to(root))
        refs = [(i, m.group(1)) for i, line in enumerate(sh.read_text(errors="replace").splitlines(), 1)
                for m in pattern.finditer(line)]
        if refs: result[rel] = refs
    return result


# ════════════════════ PHASE 2 ════════════════════

def _normalise(key: str) -> str:
    return re.sub(r"[_\-]", "", key).upper()

def analyse(env_map, exempt_keys, import_graph, symbol_map, getenv_args, exempt_strings, sh_refs) -> dict:
    violations: list = []; alias_clusters: dict = {}

    # Alias detection
    norm_to_keys: dict = {}
    for key in env_map:
        norm_to_keys.setdefault(_normalise(key), []).append(key)
    for n, keys in norm_to_keys.items():
        if len(keys) > 1:
            alias_clusters[n] = keys
            violations.append(f"ALIAS CLUSTER [{n}]: {', '.join(keys)} — keep only one canonical key")

    # Elect canonical
    canonical_map: dict = {}
    for n, keys in alias_clusters.items():
        usage = {k: 0 for k in keys}
        for file_args in getenv_args.values():
            for _, val in file_args:
                if val in usage: usage[val] += 1
        canonical = max(usage, key=lambda k: (usage[k], len(k)))
        for k in keys: canonical_map[k] = canonical

    # Consumer list:
    # - non-exempt files: tracked via getenv_args (AST-level call detection)
    # - exempt files: tracked via exempt_strings (any string constant matching env key)
    # - .sh files: tracked via sh_refs
    consumers: dict = {k: [] for k in env_map}
    for file, args in getenv_args.items():
        for _, val in args:
            if val in consumers and file not in consumers[val]:
                consumers[val].append(file)
    for file, strings in exempt_strings.items():
        for val in strings:
            if val in consumers and file not in consumers[val]:
                consumers[val].append(file)
    for file, refs in sh_refs.items():
        for _, varname in refs:
            if varname in consumers and file not in consumers[varname]:
                consumers[varname].append(file)

    # Hardcoded violations — only non-exempt files
    hardcoded: list = []
    env_keys_set = set(env_map.keys())
    for file, args in getenv_args.items():
        for lineno, val in args:
            if val in env_keys_set:
                hardcoded.append({"file": file, "line": lineno, "key": val})
                violations.append(f"HARDCODED env key '{val}' in {file}:{lineno} — use ENV_{val} constant")

    # Orphans — skip ssot:exempt keys
    orphans: list = []
    for key, cons in consumers.items():
        if key in exempt_keys:
            continue  # pre-provisioned, not yet wired
        if not cons:
            orphans.append(key)
            violations.append(f"ORPHAN env var '{key}' — defined in .env but never consumed")

    # Build env_vars output
    env_vars_out: dict = {}
    for key, meta in env_map.items():
        canon = canonical_map.get(key, key)
        aliases = [k for k in alias_clusters.get(_normalise(key), []) if k != key]
        status = "exempt" if key in exempt_keys else ("violation" if aliases else ("orphan" if key in orphans else "ok"))
        env_vars_out[key] = {
            "canonical": (canon == key), "canonical_name": canon,
            "aliases": aliases, "consumers": consumers.get(key, []),
            "sources": meta["sources"], "status": status,
            "exempt": key in exempt_keys,
        }

    return {"env_vars": env_vars_out, "alias_clusters": alias_clusters,
            "orphans": orphans, "hardcoded": hardcoded, "violations": violations}


# ════════════════════ PHASE 3 ════════════════════

def write_json(out, env_vars, import_graph, symbol_map, violations, alias_clusters, orphans, hardcoded):
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_meta": {"generated_at": datetime.now(timezone.utc).isoformat(),
                  "generator": "tools/nina_ssot.py", "version": "2.4"},
        "health": "FAIL" if violations else "OK",
        "violations": violations, "env_vars": env_vars,
        "alias_clusters": alias_clusters, "orphans": orphans,
        "hardcoded": hardcoded, "import_graph": import_graph, "symbols": symbol_map,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return payload

def write_md(out: Path, payload: dict):
    out.parent.mkdir(parents=True, exist_ok=True)
    ts = payload["_meta"]["generated_at"][:16].replace("T", " ")
    health_icon = "✅ OK" if payload["health"] == "OK" else f"❌ FAIL ({len(payload['violations'])} violations)"
    lines = [f"# NINA SSOT Report — {ts} UTC", "", f"## Health: {health_icon}", ""]

    clusters = payload.get("alias_clusters", {})
    if clusters:
        lines += ["## Env Var Aliases (must fix)", "", "| Normalised Key | Duplicate Keys | Used by |", "|---|---|---|",]
        for n, keys in clusters.items():
            ev = payload.get("env_vars", {})
            cons = sorted(set(c for k in keys for c in ev.get(k, {}).get("consumers", [])))
            lines.append(f"| `{n}` | {', '.join(f'`{k}`' for k in keys)} | {', '.join(cons) or '—'} |")
        lines.append("")

    violations = payload.get("violations", [])
    if violations:
        lines += ["## Violations", ""]
        for v in violations: lines.append(f"- ✗ {v}")
        lines.append("")
    else:
        lines += ["## Violations", "", "_None — repo is clean._", ""]

    orphans = payload.get("orphans", [])
    if orphans:
        lines += ["## Orphan Env Vars (unwired, not exempt)", ""]
        for o in orphans: lines.append(f"- `{o}`")
        lines.append("")

    hardcoded = payload.get("hardcoded", [])
    if hardcoded:
        lines += ["## Hardcoded Env Key Strings", ""]
        for h in hardcoded: lines.append(f"- `{h['key']}` in `{h['file']}` line {h['line']}")
        lines.append("")

    # Exempt summary
    exempt = [k for k, v in payload.get("env_vars", {}).items() if v.get("exempt")]
    if exempt:
        lines += ["## Pre-Provisioned (ssot:exempt)", "",
                  "_These keys are defined but not yet wired to any consumer._",
                  "_Remove `# ssot:exempt` when the consuming module is added._", ""]
        for e in exempt: lines.append(f"- `{e}`")
        lines.append("")

    clean = ([]
        + (["✓ 0 alias clusters"] if not clusters else [])
        + (["✓ 0 orphan env vars"] if not orphans else [])
        + (["✓ 0 hardcoded env key strings"] if not hardcoded else []))
    if clean:
        lines += ["## Clean", ""]
        for c in clean: lines.append(f"- {c}")
        lines.append("")

    out.write_text("\n".join(lines))


# ════════════════════ PHASE 4 ════════════════════

def enforce(violations: list, strict: bool = True) -> int:
    if not violations:
        print("[SSOT] ✅ Clean — 0 violations."); return 0
    print(f"[SSOT] ❌ {len(violations)} violation(s):")
    for v in violations: print(f"  ✗ {v}")
    return 1 if strict else 0


# ════════════════════ MAIN ════════════════════

def main():
    parser = argparse.ArgumentParser(description="NINA SSOT Engine v2.4")
    parser.add_argument("--report",    action="store_true")
    parser.add_argument("--enforce",   action="store_true")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--root",      default=str(ROOT))
    args = parser.parse_args()
    root   = Path(args.root).resolve()
    strict = args.enforce or (not args.report)

    print("[SSOT] Phase 1: DISCOVER")
    env_map, exempt_keys = discover_env_vars(root)
    print(f"  env vars found : {len(env_map)}")
    print(f"  ssot:exempt    : {len(exempt_keys)}")
    import_graph, symbol_map, getenv_args, exempt_strings = discover_py_symbols(root)
    print(f"  .py files      : {len(import_graph)}")
    sh_refs = discover_sh_env_refs(root)
    print(f"  .sh files      : {len(sh_refs)}")

    print("[SSOT] Phase 2: ANALYSE")
    result = analyse(env_map, exempt_keys, import_graph, symbol_map, getenv_args, exempt_strings, sh_refs)
    print(f"  violations     : {len(result['violations'])}")
    print(f"  alias clusters : {len(result['alias_clusters'])}")
    print(f"  orphans        : {len(result['orphans'])}")
    print(f"  hardcoded      : {len(result['hardcoded'])}")

    print("[SSOT] Phase 3: WRITE")
    payload = write_json(OUT_JSON, result["env_vars"], import_graph, symbol_map,
                         result["violations"], result["alias_clusters"],
                         result["orphans"], result["hardcoded"])
    print(f"  wrote → {OUT_JSON.relative_to(root)}")
    if not args.json_only:
        write_md(OUT_MD, payload)
        print(f"  wrote → {OUT_MD.relative_to(root)}")

    print("[SSOT] Phase 4: ENFORCE")
    sys.exit(enforce(result["violations"], strict=strict))

if __name__ == "__main__":
    main()
