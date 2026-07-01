"""
NINA v15 — Guardian Loop (The Snake Loop)
Every file change enters this loop. No exceptions.

FILE_PURPOSE:
  Why: Implements the permanent autonomous change propagation loop:
       Change → AST → Index → Docs → Registry → Redundancy → Memory → Health → Done
       This is the core of NINA v15 self-maintenance. Makes the system self-healing.
  Owner: NINA core / git post-commit hook
  Breaks if removed: All of v15 Layer 1 (Permanence Engine)
  Dependencies: core/indexer.py, core/canonicalization.py, core/file_registry.py
  Replaces: nina_fix.sh, nina_cleanup_sprint.sh (manual interventions)
"""

FILE_PURPOSE = {
    "why": "Autonomous change propagation: every git commit triggers the full snake loop",
    "owner": "git-hooks/post-commit",
    "breaks_if_removed": ["permanence engine", "self-maintenance", "auto-indexing"],
    "dependencies": ["core.indexer", "core.canonicalization", "core.file_registry"],
    "replaces": ["nina_fix.sh", "nina_cleanup_sprint.sh"],
}

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).parent.parent
LOOP_LOG = REPO_ROOT / "logs" / "guardian_loop.jsonl"


class LoopStep:
    def __init__(self, name: str, fn: Callable, critical: bool = False):
        self.name = name
        self.fn = fn
        self.critical = critical


def _log(entry: dict):
    LOOP_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOOP_LOG, "a") as f:
        f.write(json.dumps({"ts": time.time(), **entry}) + "\n")


# ─── Step implementations ──────────────────────────────────────────────────

def step_ast_scan(changed_files: list[str]) -> dict:
    """Step 1: Validate changed files parse cleanly."""
    import ast
    errors = []
    for f in changed_files:
        if not f.endswith(".py"):
            continue
        path = REPO_ROOT / f
        if not path.exists():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as e:
            errors.append({"file": f, "error": str(e)})
    return {"syntax_errors": errors, "checked": len(changed_files)}


def step_index_update(changed_files: list[str]) -> dict:
    """Step 2: Incrementally update the semantic symbol index."""
    try:
        from core.indexer import index_file, _get_db, INDEX_DB
        conn = _get_db()
        updated = 0
        for f in changed_files:
            if not f.endswith(".py"):
                continue
            path = REPO_ROOT / f
            if path.exists():
                n = index_file(path, conn)
                if n > 0:
                    updated += 1
        conn.close()
        return {"files_updated": updated, "db": str(INDEX_DB)}
    except Exception as e:
        return {"error": str(e)}


def step_doc_update(changed_files: list[str]) -> dict:
    """Step 3: Flag docs that may be stale due to changed files."""
    doc_candidates = []
    for f in changed_files:
        stem = Path(f).stem
        for doc_path in (REPO_ROOT / "docs").rglob(f"*{stem}*"):
            doc_candidates.append(str(doc_path.relative_to(REPO_ROOT)))
    return {"stale_doc_candidates": doc_candidates[:10]}


def step_registry_update(changed_files: list[str]) -> dict:
    """Step 4: Refresh the file registry for changed paths."""
    try:
        from core.file_registry import build_registry
        reg = build_registry()
        return {
            "orphans": len(reg["orphans"]),
            "missing_purpose": len(reg["missing_purpose"]),
            "coverage_pct": reg["stats"]["coverage_pct"],
        }
    except Exception as e:
        return {"error": str(e)}


def step_redundancy_scan(changed_files: list[str]) -> dict:
    """Step 5: Run canonicalization detection on changed constants."""
    try:
        from core.canonicalization import detect_alias_clusters
        clusters = detect_alias_clusters()
        return {"alias_clusters_found": len(clusters),
                "top": [c["canonical"] for c in clusters[:5]]}
    except Exception as e:
        return {"error": str(e)}


def step_memory_update(changed_files: list[str]) -> dict:
    """Step 6: Placeholder — signal memory consolidator to refresh changed module knowledge."""
    return {"signaled": len(changed_files), "note": "memory consolidator next run will pick up"}


def step_health_check(changed_files: list[str]) -> dict:
    """Step 7: Basic health check — import the changed modules."""
    import importlib
    failures = []
    for f in changed_files:
        if not f.endswith(".py"):
            continue
        mod = f.replace("/", ".").replace("\\", ".").removesuffix(".py")
        try:
            importlib.import_module(mod)
        except Exception as e:
            failures.append({"module": mod, "error": str(e)})
    return {"import_failures": failures}


# ─── Main Guardian Loop ────────────────────────────────────────────────────

STEPS = [
    LoopStep("ast_scan",        step_ast_scan,       critical=True),
    LoopStep("index_update",    step_index_update,   critical=False),
    LoopStep("doc_update",      step_doc_update,     critical=False),
    LoopStep("registry_update", step_registry_update,critical=False),
    LoopStep("redundancy_scan", step_redundancy_scan,critical=False),
    LoopStep("memory_update",   step_memory_update,  critical=False),
    LoopStep("health_check",    step_health_check,   critical=False),
]


def run(changed_files: list[str] | None = None, verbose: bool = False) -> dict:
    """
    Execute the full Guardian Loop for the given changed files.
    If changed_files is None, detects from git diff HEAD~1.
    """
    if changed_files is None:
        changed_files = _get_changed_files()

    if not changed_files:
        return {"status": "noop", "reason": "no changed files"}

    results: dict[str, dict] = {}
    t0 = time.time()
    aborted = False

    for step in STEPS:
        t_step = time.time()
        try:
            result = step.fn(changed_files)
        except Exception as e:
            result = {"error": str(e)}

        result["duration_ms"] = round((time.time() - t_step) * 1000, 1)
        results[step.name] = result

        if verbose:
            status = "✅" if "error" not in result else "⚠️"
            print(f"  {status} {step.name}: {json.dumps(result)}")

        if step.critical and "syntax_errors" in result and result["syntax_errors"]:
            print(f"[guardian] CRITICAL: syntax errors in {result['syntax_errors']} — aborting loop")
            aborted = True
            break

    summary = {
        "status": "aborted" if aborted else "ok",
        "files": changed_files,
        "steps": results,
        "total_ms": round((time.time() - t0) * 1000, 1),
    }
    _log(summary)
    return summary


def _get_changed_files() -> list[str]:
    """Get list of Python files changed in the last commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else None
    result = run(changed_files=files, verbose=True)
    print(f"\n[guardian] Loop complete in {result['total_ms']}ms — status: {result['status']}")
    if result["status"] == "aborted":
        sys.exit(1)
