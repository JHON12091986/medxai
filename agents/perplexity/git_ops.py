"""perplexity/git_ops.py — synchronous git wrapper for relay.py.

Note: tools/git_ops.py exists but is async and workspace-sandboxed.
This module wraps git directly via subprocess for relay's sync execution model,
with repo_root scoped to ~/nina rather than data/workspace.
Force-push is blocked here as defense-in-depth beneath safety.py.
"""
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger("nina.perplexity.git_ops")
REPO_ROOT = Path(__file__).parent.parent


def _run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    """Run a subprocess command, return (success, output_or_error)."""
    try:
        r = subprocess.run(
            cmd, cwd=str(cwd),
            capture_output=True, text=True, shell=False
        )
        if r.returncode != 0:
            return False, (r.stderr or r.stdout).strip()
        return True, (r.stdout or "").strip()
    except Exception as e:
        return False, str(e)


def git_status(repo_root: str) -> str:
    _, out = _run(["git", "status"], Path(repo_root))
    return out


def git_diff(repo_root: str) -> str:
    _, out = _run(["git", "diff"], Path(repo_root))
    return out


def git_add(repo_root: str, files: list[str]) -> tuple[bool, str]:
    return _run(["git", "add"] + files, Path(repo_root))


def git_commit(repo_root: str, message: str) -> tuple[bool, str]:
    """Commit with NINA conventional-commit format: type(scope): summary (WIRE-ID)."""
    return _run(["git", "commit", "-m", message], Path(repo_root))


def git_push(repo_root: str, branch: str, force: bool = False) -> tuple[bool, str]:
    """Push to remote. Force push is blocked here as defense-in-depth."""
    if force:
        # net-new: double-block force push even if called directly
        return False, "force push blocked by git_ops — not permitted"
    return _run(["git", "push", "origin", branch], Path(repo_root))


def git_branch_create(repo_root: str, branch_name: str) -> tuple[bool, str]:
    return _run(["git", "checkout", "-b", branch_name], Path(repo_root))


def git_merge_gated(repo_root: str, branch: str) -> tuple[bool, str]:
    """Merge only after rule0_audit, py_compile, and pyflakes all pass."""
    root = Path(repo_root)

    # 1. rule0_audit
    ok, out = _run(["python3", "rule0_audit.py"], root)
    if not ok:
        return False, f"git_merge_gated: rule0_audit.py failed: {out}"

    # 2. Collect changed Python files in branch diff
    ok, diff_out = _run(
        ["git", "diff", "--name-only", f"origin/{branch}...HEAD"],
        root
    )
    py_files = [f for f in diff_out.splitlines() if f.endswith(".py")] if ok else []

    # 3. py_compile each changed file
    for pyf in py_files:
        ok, out = _run(["python3", "-m", "py_compile", pyf], root)
        if not ok:
            return False, f"git_merge_gated: py_compile failed on {pyf}: {out}"

    # 4. pyflakes each changed file
    if py_files:
        ok, out = _run(["python3", "-m", "pyflakes"] + py_files, root)
        if not ok:
            return False, f"git_merge_gated: pyflakes failed: {out}"

    # 5. All checks passed — merge
    return _run(["git", "merge", branch], root)
