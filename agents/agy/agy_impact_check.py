#!/usr/bin/env python3
"""
agy_impact_check.py — pre-commit cross-file impact validator for agy tasks

Checks:
  1. All callers of functions in <target_file> still have valid import chains
  2. No broken imports introduced by the change
  3. All functions exported by the file are still present (no accidental deletions)
  4. Reports blast radius: which files will be affected

Usage:
    python3 agy_impact_check.py <file>              # check one file
    python3 agy_impact_check.py <file> --baseline   # save current exports as baseline
    python3 agy_impact_check.py <file> --strict     # exit 1 if any callers found

Exit codes:
    0 = all checks passed
    1 = issues found (blocks commit)
    2 = file not found or parse error
"""

import ast
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent
BASELINE_DIR = ROOT / ".agy_baselines"
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}


def parse_exports(path: Path) -> list:
    """Return top-level public function/class names from a file."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, OSError) as e:
        print(f"  ❌ Parse error in {path}: {e}")
        sys.exit(2)

    exports = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                exports.append(node.name)
    return exports


def find_callers(target_file: str) -> list:
    """Find all Python files that import the target file."""
    target_path = Path(target_file)
    stem = target_path.stem  # e.g. "router"
    mod_dotted = str(target_path).replace("/", ".").replace("\\", ".").removesuffix(".py")

    callers = []
    for py_file in ROOT.rglob("*.py"):
        rel = py_file.relative_to(ROOT)
        if any(d in SKIP_DIRS for d in rel.parts):
            continue
        if str(rel) == target_file:
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == stem or alias.name == mod_dotted:
                        callers.append(str(rel))
                        break
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module == stem or
                                    node.module == mod_dotted or
                                    node.module.endswith(f".{stem}")):
                    callers.append(str(rel))
                    break

    return sorted(set(callers))


def check_caller_imports(caller_file: str, target_file: str, current_exports: list) -> list:
    """Check that everything imported from target still exists in current_exports."""
    issues = []
    target_stem = Path(target_file).stem
    target_dotted = target_file.replace("/", ".").removesuffix(".py")

    try:
        source = (ROOT / caller_file).read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and (node.module == target_stem or
                                node.module == target_dotted or
                                node.module.endswith(f".{target_stem}")):
                for alias in node.names:
                    if alias.name != "*" and alias.name not in current_exports:
                        issues.append(
                            f"    {caller_file} imports `{alias.name}` from {target_file} "
                            f"— but `{alias.name}` is NOT in current exports"
                        )
    return issues


def save_baseline(target_file: str, exports: list):
    BASELINE_DIR.mkdir(exist_ok=True)
    safe_name = target_file.replace("/", "__").replace("\\", "__")
    baseline_path = BASELINE_DIR / f"{safe_name}.json"
    baseline_path.write_text(json.dumps({"file": target_file, "exports": exports}), encoding="utf-8")
    print(f"  📸 Baseline saved: {len(exports)} exports from {target_file}")


def load_baseline(target_file: str) -> list | None:
    safe_name = target_file.replace("/", "__").replace("\\", "__")
    baseline_path = BASELINE_DIR / f"{safe_name}.json"
    if baseline_path.exists():
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
        return data.get("exports", [])
    return None


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 agy_impact_check.py <file> [--baseline] [--strict]")
        sys.exit(1)

    target_file = args[0]
    do_baseline = "--baseline" in args
    strict = "--strict" in args

    target_path = ROOT / target_file
    if not target_path.exists():
        print(f"  ❌ File not found: {target_file}")
        sys.exit(2)

    print(f"\n{'━'*50}")
    print(f" agy_impact_check: {target_file}")
    print(f"{'━'*50}")

    # 1. Parse current exports
    current_exports = parse_exports(target_path)
    print(f"  📦 Current exports ({len(current_exports)}): {', '.join(current_exports[:10]) or 'none'}")

    if do_baseline:
        save_baseline(target_file, current_exports)
        return

    # 2. Baseline comparison (detect accidental deletions)
    baseline_exports = load_baseline(target_file)
    removed = []
    if baseline_exports is not None:
        removed = [e for e in baseline_exports if e not in current_exports]
        added = [e for e in current_exports if e not in baseline_exports]
        if removed:
            print(f"  ⚠️  REMOVED exports (may break callers): {', '.join(removed)}")
        if added:
            print(f"  ✅ New exports: {', '.join(added)}")
    else:
        print("  ℹ️  No baseline found. Run with --baseline after confirming the file is correct.")

    # 3. Find callers
    callers = find_callers(target_file)
    if callers:
        print(f"  🔍 Blast radius — {len(callers)} caller(s): {', '.join(callers)}")
    else:
        print("  ✅ No callers found — isolated change")

    # 4. Check each caller's imports
    all_issues = []
    for caller in callers:
        issues = check_caller_imports(caller, target_file, current_exports)
        all_issues.extend(issues)

    # 5. Report
    print()
    if all_issues:
        print("  ❌ BROKEN IMPORTS DETECTED:")
        for issue in all_issues:
            print(issue)
        print(f"\n{'━'*50}")
        print(" RESULT: FAIL — fix broken imports before committing")
        print(f"{'━'*50}\n")
        sys.exit(1)
    elif removed:
        print("  ⚠️  Exports removed — callers may break at runtime even if imports look fine")
        print(f"\n{'━'*50}")
        print(" RESULT: WARN — review removed exports")
        print(f"{'━'*50}\n")
        if strict:
            sys.exit(1)
    else:
        print(f"{'━'*50}")
        print(" RESULT: PASS — no broken imports, blast radius declared")
        print(f"{'━'*50}\n")


if __name__ == "__main__":
    main()
