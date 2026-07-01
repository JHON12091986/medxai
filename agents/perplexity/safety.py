"""perplexity/safety.py — refusal/validation layer. Called BEFORE any step executes.

Check function return convention:
  - validate_schema, validate_paths_exist  → (ok: bool, reason: str)
      True  = passed, empty reason
      False = failed, reason explains why
  - check_high_risk, check_locked,
    check_git_safety, check_confirmation_required  → (blocked: bool, reason: str)
      True  = BLOCKED, reason explains why
      False = clear, empty reason

run_all_checks() handles both conventions correctly.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Hard-blocked files — never touched by relay under any circumstance
HIGH_RISK_FILES: set[str] = {
    "interfaces/telegram_interface.py",
    ".env",
    "core/router.py",
    "main.py",
    "guardian_engine.py",
    "tools/shell.py",
    "ninagate/main.py",
}


def _normalize(path: str) -> str:
    return os.path.normpath(path).lstrip(os.sep).replace("\\", "/")


def _all_paths_in_task(task: dict) -> list[tuple[int, str, str]]:
    paths = []
    for top_field in ("target_files",):
        for p in task.get(top_field, []):
            paths.append((-1, top_field, p))
    for idx, step in enumerate(task.get("steps", [])):
        for field in ("file", "from", "to"):
            if field in step:
                paths.append((idx, field, step[field]))
    return paths


# ────────────────────────────────────────────────────────────────────────
# Validator checks — return (ok: bool, reason: str)
# ok=True means PASSED. ok=False means FAILED (relay refuses).
# ────────────────────────────────────────────────────────────────────────

def validate_schema(task: dict) -> tuple[bool, str]:
    """Returns (ok, reason). ok=True means schema is valid."""
    for field in ("id", "task", "type", "steps"):
        if field not in task:
            return False, f"Missing required field: '{field}'"
    valid_types = {"file_op", "git_op", "jules_op", "inspect", "compound"}
    if task["type"] not in valid_types:
        return False, f"Invalid task type '{task['type']}'. Must be one of: {valid_types}"
    if not isinstance(task["steps"], list):
        return False, "'steps' must be a list"
    for i, step in enumerate(task["steps"]):
        if "action" not in step:
            return False, f"Step[{i}] missing required field 'action'"
    return True, ""


def validate_paths_exist(task: dict, repo_root: str = None) -> tuple[bool, str]:
    """Returns (ok, reason). ok=True means all paths are valid."""
    root = Path(repo_root) if repo_root else REPO_ROOT
    for idx, step in enumerate(task.get("steps", [])):
        action = step.get("action", "")
        if action in ("edit", "move"):
            src = step.get("from") or step.get("file")
            if src and not (root / src).exists():
                return False, (
                    f"Step[{idx}] action='{action}': source file not found: '{src}' — "
                    f"use action='create' to create a new file"
                )
        if action == "create":
            target = step.get("file") or step.get("to")
            if target and (root / target).exists():
                return False, (
                    f"Step[{idx}] action='create': file already exists: '{target}' — "
                    f"use action='edit' with find/replace fields to modify it"
                )
    return True, ""


# ────────────────────────────────────────────────────────────────────────
# Blocker checks — return (blocked: bool, reason: str)
# blocked=True means BLOCKED (relay refuses). blocked=False means clear.
# ────────────────────────────────────────────────────────────────────────

def check_high_risk(task: dict) -> tuple[bool, str]:
    """Returns (blocked, reason). blocked=True means HIGH_RISK_FILE hit."""
    for idx, field, path in _all_paths_in_task(task):
        if _normalize(path) in {_normalize(p) for p in HIGH_RISK_FILES}:
            loc = f"step[{idx}].{field}" if idx >= 0 else field
            return True, f"HIGH_RISK_FILE blocked: '{path}' at {loc}"
    return False, ""


def check_locked(task: dict, juleslock_path: str = None) -> tuple[bool, str]:
    """Returns (blocked, reason). blocked=True means locked file hit."""
    lock_file = Path(juleslock_path) if juleslock_path else REPO_ROOT / "juleslock.txt"
    locked: set[str] = set()
    if lock_file.exists():
        for line in lock_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                locked.add(_normalize(line))
    for idx, field, path in _all_paths_in_task(task):
        if _normalize(path) in locked:
            loc = f"step[{idx}].{field}" if idx >= 0 else field
            return True, f"LOCKED_FILE blocked: '{path}' at {loc} (listed in juleslock.txt)"
    return False, ""


def check_git_safety(task: dict) -> tuple[bool, str]:
    """Returns (blocked, reason). blocked=True means unsafe git op."""
    step_actions = [s.get("action", "") for s in task.get("steps", [])]
    for idx, step in enumerate(task.get("steps", [])):
        action = step.get("action", "")
        if action in ("git_push", "push") and step.get("force"):
            return True, f"Step[{idx}]: force push is not permitted"
        if action in ("git_merge", "merge"):
            preceding = step_actions[:idx]
            if "run" not in preceding and "git_audit" not in preceding:
                return True, (
                    f"Step[{idx}]: merge step requires a preceding 'run' audit step "
                    "(rule0_audit.py + py_compile + pyflakes) before merge is allowed"
                )
    return False, ""


def check_confirmation_required(task: dict) -> tuple[bool, str]:
    """Returns (blocked, reason). blocked=True means confirmation missing."""
    irreversible_actions = {"git_push", "push", "jules_submit"}
    has_irreversible = any(
        step.get("action", "") in irreversible_actions
        for step in task.get("steps", [])
    )
    if has_irreversible and task.get("confirmed") is not True:
        return True, (
            'This task includes an irreversible action (push/jules_submit). '
            'Add "confirmed": true to the task JSON only after you have reviewed '
            'this specific task, then re-run.'
        )
    return False, ""


# ────────────────────────────────────────────────────────────────────────
# Orchestrator — the ONLY function relay.py calls
# ────────────────────────────────────────────────────────────────────────

def run_all_checks(task: dict, repo_root: str = None) -> tuple[bool, str]:
    """Run all safety checks. Returns (ok, reason).
    ok=True  → all checks passed, relay may proceed.
    ok=False → at least one check failed/blocked, reason explains why.

    Handles two check conventions:
      validators (validate_*): (ok, reason)    — ok=False means refuse
      blockers   (check_*):    (blocked, reason) — blocked=True means refuse
    """
    # Each entry: (name, fn, is_validator)
    # is_validator=True  → fn returns (ok, reason):      refuse when ok=False
    # is_validator=False → fn returns (blocked, reason):  refuse when blocked=True
    checks: list[tuple[str, object, bool]] = [
        ("validate_schema",             lambda: validate_schema(task),                    True),
        ("check_high_risk",             lambda: check_high_risk(task),                    False),
        ("check_locked",                lambda: check_locked(task),                       False),
        ("validate_paths_exist",        lambda: validate_paths_exist(task, repo_root),    True),
        ("check_git_safety",            lambda: check_git_safety(task),                   False),
        ("check_confirmation_required", lambda: check_confirmation_required(task),        False),
    ]
    for name, fn, is_validator in checks:
        try:
            result, reason = fn()
        except Exception as exc:
            return False, f"{name} raised an unexpected error: {type(exc).__name__}: {exc}"

        if is_validator:
            # result = ok; refuse when False
            if not result:
                return False, reason or f"{name} failed (no reason returned)"
        else:
            # result = blocked; refuse when True
            if result:
                return False, reason or f"{name} blocked (no reason returned)"

    return True, ""
