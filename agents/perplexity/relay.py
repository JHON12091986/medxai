"""perplexity/relay.py — main orchestrator. Entry point for all Perplexity-authored tasks.

Usage:
  python3 perplexity/relay.py --file perplexity/tasks/PRX-XXX.json
  cat task.json | python3 perplexity/relay.py
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from perplexity import safety, git_ops, jules_bridge
from perplexity.log import log_action


def _last5(output: str) -> str:
    lines = [l for l in output.splitlines() if l.strip()]
    return "\n".join(lines[-5:])


def _print_done(task_id: str, task_summary: str, step_results: list[tuple[str, str]]):
    print(f"{task_id} — {task_summary}")
    for symbol, msg in step_results:
        print(f"{symbol} {msg}")
    print("\nSTATUS: DONE")


def _print_refused(task_id: str, task_summary: str, reason: str):
    print(f"{task_id} — {task_summary}")
    print(f"🛑 REFUSED: {reason}")
    print("\nSTATUS: REFUSED — fix the task JSON and re-run, or ask Perplexity to revise the spec")


def _print_failed(task_id: str, task_summary: str, step_results: list, failed_msg: str, rolled_back: list[str]):
    print(f"{task_id} — {task_summary}")
    for symbol, msg in step_results:
        print(f"{symbol} {msg}")
    print(f"❌ {failed_msg}")
    if rolled_back:
        print(f"↩️  ROLLBACK: {', '.join(rolled_back)} restored to pre-task state")
    print("\nSTATUS: FAILED — repo unchanged, paste this back to Perplexity")


def _print_pending(task_id: str, task_summary: str, jules_task_id: str):
    print(f"{task_id} — {task_summary}")
    print(f"✅ jules_submit: task {jules_task_id} created, spec logged")
    print("⏳ jules_poll: PR not yet ready")
    print("\nSTATUS: PENDING — re-run with jules_poll when you check back, or wait for Telegram alert")


def _apply_step(step: dict, repo_root: Path, staging: dict) -> tuple[bool, str]:
    """Execute a single step. Returns (success, summary_message)."""
    action = step.get("action", "")

    # ── file ops ───────────────────────────────────────────────────────────────────
    if action == "move":
        src = repo_root / step["from"]
        dst = repo_root / step["to"]
        if not src.exists():
            return False, f"move: source not found: '{step['from']}'"
        staging[str(src)] = shutil.copy2(src, tempfile.mktemp())
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True, f"move: {step['from']} → {step['to']}"

    elif action == "edit":
        target = repo_root / step["file"]
        # Guard: file must exist before we attempt to stage or edit it
        if not target.exists():
            return False, (
                f"edit: file not found: '{step['file']}' — "
                f"use action='create' to create a new file"
            )
        # Guard: find/replace fields are required for edit
        find = step.get("find", "")
        replace = step.get("replace", "")
        if not find and "content" not in step:
            return False, (
                "edit: step must include 'find'+'replace' fields OR a 'content' field "
                "(full file overwrite). Got neither."
            )
        staging[str(target)] = shutil.copy2(str(target), tempfile.mktemp())
        if find:
            content = target.read_text(encoding="utf-8")
            if find not in content:
                return False, f"edit: find string not found in '{step['file']}'"
            target.write_text(content.replace(find, replace, 1), encoding="utf-8")
            return True, f"edit: {step['file']} (find/replace applied)"
        else:
            # Full overwrite via 'content' field
            target.write_text(step["content"], encoding="utf-8")
            return True, f"edit: {step['file']} (full overwrite)"

    elif action == "create":
        target = repo_root / step["file"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(step.get("content", ""), encoding="utf-8")
        return True, f"create: {step['file']}"

    elif action == "delete":
        target = repo_root / step["file"]
        if not target.exists():
            return False, f"delete: file not found: '{step['file']}'"
        staging[str(target)] = shutil.copy2(str(target), tempfile.mktemp())
        target.unlink()
        return True, f"delete: {step['file']}"

    # ── git ops ───────────────────────────────────────────────────────────────────
    elif action == "git_add":
        ok, msg = git_ops.git_add(str(repo_root), step.get("files", ["."]))
        return ok, f"git_add: {msg if ok else msg}"

    elif action == "git_commit":
        ok, msg = git_ops.git_commit(str(repo_root), step["message"])
        return ok, f"git_commit: {msg[:80] if ok else msg}"

    elif action in ("git_push", "push"):
        ok, msg = git_ops.git_push(str(repo_root), step.get("branch", "main"),
                                    force=step.get("force", False))
        return ok, f"git_push: {msg[:80] if ok else msg}"

    elif action in ("git_branch", "git_branch_create"):
        ok, msg = git_ops.git_branch_create(str(repo_root), step["branch"])
        return ok, f"git_branch: {msg[:80] if ok else msg}"

    elif action in ("git_merge", "merge"):
        ok, msg = git_ops.git_merge_gated(str(repo_root), step["branch"])
        return ok, f"git_merge: {msg[:80] if ok else msg}"

    # ── jules ops ────────────────────────────────────────────────────────────────────
    elif action == "jules_submit":
        ok, jules_id, raw = jules_bridge.jules_submit(
            step.get("spec", ""), step.get("repo", "aibony/nina")
        )
        if ok or jules_id:
            return True, f"jules_submit: task {jules_id} queued"
        return False, f"jules_submit failed: {raw[:120]}"

    elif action == "jules_poll":
        status, detail = jules_bridge.jules_poll(
            step.get("task_id", ""), step.get("repo", "aibony/nina")
        )
        return status in ("pr_open",), f"jules_poll: {status} — {detail[:100]}"

    # ── shell verify ───────────────────────────────────────────────────────────────────
    elif action == "run":
        cmd = step.get("cmd", "")
        r = subprocess.run(
            cmd, shell=True, cwd=str(repo_root),
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            return False, f"run '{cmd[:60]}' failed:\n{_last5(r.stderr or r.stdout)}"
        return True, f"run: {cmd[:60]} — ok"

    else:
        return False, f"unknown action: '{action}'"


def main():
    parser = argparse.ArgumentParser(description="NINA Perplexity Relay")
    parser.add_argument("--file", help="Path to task JSON file")
    args = parser.parse_args()

    # Load task JSON from file or stdin
    if args.file:
        task_json = Path(args.file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        task_json = sys.stdin.read()
    else:
        print("Error: provide --file <path> or pipe JSON via stdin")
        sys.exit(1)

    try:
        task = json.loads(task_json)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}")
        sys.exit(1)

    task_id = task.get("id", "PRX-???")
    task_summary = task.get("task", "(no summary)")

    # Safety checks — ALL must pass before any step runs
    ok, reason = safety.run_all_checks(task, str(REPO_ROOT))
    if not ok:
        _print_refused(task_id, task_summary, reason)
        log_action(task_id, "relay", "refused", reason)
        sys.exit(2)

    # Execute steps sequentially with staging for rollback
    staging: dict[str, str] = {}   # {original_path: temp_backup_path}
    step_results: list[tuple[str, str]] = []
    rolled_back: list[str] = []

    for step in task.get("steps", []):
        success, msg = _apply_step(step, REPO_ROOT, staging)
        if success:
            step_results.append(("✅", msg))
            log_action(task_id, step.get("action", "?"), "ok", msg)
        else:
            # Rollback all staged files
            for orig, backup in staging.items():
                try:
                    shutil.copy2(backup, orig)
                    rolled_back.append(Path(orig).name)
                    os.unlink(backup)
                except Exception:
                    pass
            _print_failed(task_id, task_summary, step_results, msg, rolled_back)
            log_action(task_id, step.get("action", "?"), "failed", msg)
            sys.exit(3)

    # All steps passed — clean up temp backups
    for backup in staging.values():
        try:
            os.unlink(backup)
        except Exception:
            pass

    # Special: jules_submit pending state
    last_action = task["steps"][-1].get("action", "") if task["steps"] else ""
    if last_action in ("jules_submit", "jules_poll"):
        last_msg = step_results[-1][1] if step_results else ""
        jules_task_id = last_msg.split("task ")[-1].split()[0] if "task " in last_msg else "?"
        _print_pending(task_id, task_summary, jules_task_id)
    else:
        _print_done(task_id, task_summary, step_results)

    log_action(task_id, "relay", "done", f"{len(step_results)} steps completed")
    sys.exit(0)


if __name__ == "__main__":
    main()
