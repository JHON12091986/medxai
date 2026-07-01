"""
MEGA-09 acceptance tests — agent namespace consolidation.

These tests verify:
1. agents/ is importable as a Python package
2. The old agent/ directory no longer exists in the repo working tree
3. No .py file under the repo root imports from the old `agent.` namespace
"""
from pathlib import Path
import importlib
import subprocess
import sys


def test_agent_namespace_importable():
    """agents package must import without raising."""
    import agents  # noqa: F401 — must not raise


def test_no_old_agent_directory():
    """Old agent/ directory must not exist in the working tree."""
    repo_root = Path(__file__).parent.parent
    old_dir = repo_root / "agent"
    assert not old_dir.exists(), (
        f"Old agent/ directory still present at {old_dir}. "
        "Run: git rm -r agent/  and commit."
    )


def test_no_old_agent_imports_in_codebase():
    """
    No .py file in the repo should contain `from agent.` or `import agent.`
    (the old singular-namespace import pattern).

    Excludes this test file itself and any __pycache__ directories.
    """
    repo_root = Path(__file__).parent.parent
    bad_patterns = ["from agent.", "import agent.", "from agent import"]
    violations = []

    for py_file in repo_root.rglob("*.py"):
        # Skip this file, venv, __pycache__, .git
        parts = py_file.parts
        if any(p in parts for p in ("__pycache__", ".git", "venv", "nina_venv", ".venv")):
            continue
        if py_file == Path(__file__):
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in bad_patterns:
            if pattern in text:
                violations.append(f"{py_file}: contains '{pattern}'")

    assert not violations, (
        "Old agent. namespace imports found — replace with agents.:\n"
        + "\n".join(violations)
    )
