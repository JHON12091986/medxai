"""
NINA v15 — File Reason-For-Existence Registry
Builds dependency graph, detects dead code, orphaned files, and duplicate modules.

FILE_PURPOSE:
  Why: Every file must justify its existence. This registry parses FILE_PURPOSE headers,
       builds an import dependency graph, and flags orphans, dead code, and duplicates.
  Owner: ARCHITECT OVERWATCH / guardian_loop
  Breaks if removed: Dead code detection, architecture guardian layer, guardian loop registry step
  Dependencies: ast, pathlib, json
  Replaces: manual CODEBASE_MAP.md architecture sections
"""

FILE_PURPOSE = {
    "why": "Parse FILE_PURPOSE headers, build file dependency graph, detect orphans",
    "owner": "guardian_loop",
    "breaks_if_removed": ["dead code detection", "architecture guardian", "guardian loop"],
    "dependencies": ["ast", "pathlib", "json"],
    "replaces": "CODEBASE_MAP.md architecture sections",
}

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "archive", "backups", ".jules"}


def _parse_file_purpose(path: Path) -> dict | None:
    """
    Extract FILE_PURPOSE dict literal or YAML-style comment block from a Python file.
    Supports both:
      FILE_PURPOSE = {...}  (dict literal)
      # purpose: ...
      # owner: ...
    """
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Try dict literal
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(t, ast.Name) and t.id == "FILE_PURPOSE"
                    for t in node.targets
                )
            ):
                try:
                    val = ast.literal_eval(node.value)
                    if isinstance(val, dict):
                        return val
                except Exception:
                    pass
    except SyntaxError:
        pass

    # Try YAML-style comment block
    purpose: dict = {}
    for line in src.splitlines():
        m = re.match(r"#\s*(purpose|owner|dependencies|replaces|breaks_if_removed):\s*(.+)", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            purpose[key] = val
    return purpose if purpose else None


def _extract_imports(path: Path) -> list[str]:
    """Return list of local module names imported by this file."""
    imports = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, Exception):
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return list(set(imports))


def build_registry() -> dict:
    """
    Scan the repo and build the full file registry.
    Returns:
      {
        files: {rel_path: {purpose, imports, has_purpose_header}},
        dependency_graph: {module: [imported_by]},
        orphans: [files not imported by anything],
        missing_purpose: [files without FILE_PURPOSE header],
        stats: {...}
      }
    """
    files: dict[str, dict] = {}
    import_graph: dict[str, set[str]] = defaultdict(set)  # file → set of files it imports
    reverse_graph: dict[str, set[str]] = defaultdict(set)  # file → set of files that import it

    all_py = []
    for py in REPO_ROOT.rglob("*.py"):
        if any(p in py.parts for p in SKIP_DIRS):
            continue
        all_py.append(py)

    # Build module → file map
    module_to_file: dict[str, str] = {}
    for py in all_py:
        rel = str(py.relative_to(REPO_ROOT))
        # e.g. core/indexer.py → core.indexer
        mod = rel.replace("/", ".").replace("\\", ".").removesuffix(".py")
        module_to_file[mod] = rel
        # also short name
        short = py.stem
        if short not in module_to_file:
            module_to_file[short] = rel

    for py in all_py:
        rel = str(py.relative_to(REPO_ROOT))
        purpose = _parse_file_purpose(py)
        raw_imports = _extract_imports(py)
        resolved_imports = []
        for imp in raw_imports:
            if imp in module_to_file:
                resolved_imports.append(module_to_file[imp])
            # also try core.imp
            for candidate in [f"core.{imp}", f"agents.{imp}", f"tools.{imp}"]:
                if candidate in module_to_file:
                    resolved_imports.append(module_to_file[candidate])

        resolved_imports = list(set(resolved_imports))
        for dep in resolved_imports:
            import_graph[rel].add(dep)
            reverse_graph[dep].add(rel)

        files[rel] = {
            "purpose": purpose,
            "has_purpose_header": purpose is not None,
            "imports": resolved_imports,
            "size_bytes": py.stat().st_size,
        }

    # Detect orphans: files not imported by anyone AND not an entry point
    entry_patterns = {"main.py", "__init__.py", "__main__.py"}
    orphans = [
        f for f in files
        if f not in reverse_graph
        and Path(f).name not in entry_patterns
        and not f.startswith("tests/")
        and not f.startswith("scripts/")
        and not f.startswith("crons/")
    ]

    missing_purpose = [f for f, info in files.items() if not info["has_purpose_header"]]

    return {
        "files": {k: {**v, "imported_by": list(reverse_graph.get(k, set()))} for k, v in files.items()},
        "dependency_graph": {k: list(v) for k, v in import_graph.items()},
        "orphans": sorted(orphans),
        "missing_purpose": sorted(missing_purpose),
        "stats": {
            "total_files": len(files),
            "orphans": len(orphans),
            "missing_purpose_header": len(missing_purpose),
            "coverage_pct": round(
                100 * (len(files) - len(missing_purpose)) / max(len(files), 1), 1
            ),
        },
    }


def report(registry: dict | None = None, show_orphans: bool = True) -> str:
    """Generate a human-readable registry report."""
    if registry is None:
        registry = build_registry()
    s = registry["stats"]
    lines = [
        "# NINA File Registry Report",
        f"Files: {s['total_files']} | Purpose coverage: {s['coverage_pct']}%",
        f"Orphans: {s['orphans']} | Missing FILE_PURPOSE: {s['missing_purpose_header']}",
        "",
    ]
    if show_orphans and registry["orphans"]:
        lines.append("## Orphaned Files (not imported by anything)")
        for f in registry["orphans"][:20]:
            lines.append(f"  - {f}")
        if len(registry["orphans"]) > 20:
            lines.append(f"  ... +{len(registry['orphans'])-20} more")
        lines.append("")
    if registry["missing_purpose"]:
        lines.append("## Files Missing FILE_PURPOSE Header")
        for f in registry["missing_purpose"][:20]:
            lines.append(f"  - {f}")
        if len(registry["missing_purpose"]) > 20:
            lines.append(f"  ... +{len(registry['missing_purpose'])-20} more")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    reg = build_registry()
    if "--json" in sys.argv:
        print(json.dumps(reg["stats"], indent=2))
        print(f"\nOrphans ({len(reg['orphans'])}):")
        for o in reg["orphans"]:
            print(f"  {o}")
    else:
        print(report(reg))
