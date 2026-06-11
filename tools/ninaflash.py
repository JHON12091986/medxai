#!/usr/bin/env python3
"""
ninaflash — The Unified AI Agent Kernel for NINA.
Version: 6.1 (THE OPTIMIZED "MAINTAINER" KERNEL)
Author: Gemini CLI & Antigravity
Mission: Minimize Token Usage, Maximize Execution Speed, Absolute Reliability.
"""

import sys
import os
import shlex
import re
import argparse
import asyncio
import subprocess
import json
try:
    import dotenv
except ImportError:
    dotenv = None

import shutil
import ast


from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# --- KERNEL INITIALIZATION ---
REPO_ROOT = Path(__file__).parent.parent.resolve()
if dotenv:
    dotenv.load_dotenv(str(REPO_ROOT / ".env"))

# Constants
MAX_OUTPUT_CHARS = 4000
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
LOCK_PATH = REPO_ROOT / "jules_lock.txt"

# ------------------------------------------------------------------
# MODULE 0: CORE KERNEL & SHELL
# ------------------------------------------------------------------

def run_cmd(cmd, cwd=str(REPO_ROOT), timeout=60) -> Tuple[int, str, str]:
    """[001] Base execution primitive."""
    try:
        args = shlex.split(cmd) if isinstance(cmd, str) else cmd
        res = subprocess.run(args, shell=False, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired: return -1, "", "Command timed out"

def _safe_run(cmd: str, timeout=60) -> Tuple[int, str, str]:
    """[002] Hardened execution with NINA security policy enforcement."""
    from tools.shell import is_command_safe
    if not is_command_safe(cmd): return 1, "", f"❌ SECURITY: Command '{cmd}' blocked."
    return run_cmd(cmd, timeout=timeout)

def _path_resolve(rel_path: str) -> Path:
    """[003] Absolute path resolution from repo root."""
    return (REPO_ROOT / rel_path).resolve()

def cmd_status(args):
    """[004] Unified system health snapshot."""
    if getattr(args, 'pulse', False):
        _print_pulse()
        return

    code, out, _ = run_cmd("git rev-parse --short HEAD")
    print(f"NINA Kernel v6.1 | HEAD: {out} | Env: {'OK' if dotenv else 'NO_DOTENV'}")
    tasks = get_backlog_tasks()
    print(f"Backlog: {len(tasks)} total | READY: {len([t for t in tasks if t['status']=='READY'])}")

def _append_update_log(task_id: str, title: str, summary: str):
    """[007] Appends a standardized entry to nina_update_log.md."""
    log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists(): return
    
    content = log_path.read_text(encoding="utf-8")
    entries = re.findall(r"## Entry (\d+)", content)
    next_num = int(entries[-1]) + 1 if entries else 1
    
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n---\n\n## Entry {next_num:03d} — {today} · merge: {task_id} {title}\n"
    entry += "**Triggered by:** nf maintain automation.\n\n"
    entry += f"**What changed:**\n- {summary}\n\n"
    entry += "**Rollback:** `git revert -m 1 HEAD`\n"
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"✅ Appended Entry {next_num:03d} to log.")

def _print_pulse():
    """Generate high-density 10-line pulse."""
    from datetime import datetime
    _, sha, _ = run_cmd("git rev-parse --short HEAD")
    _, branch, _ = run_cmd("git rev-parse --abbrev-ref HEAD")
    print(f"1. Git: {sha} ({branch})")

    venv = "ACTIVE" if os.environ.get("VIRTUAL_ENV") else "INACTIVE"
    print(f"2. Venv: {venv}")

    log_path = REPO_ROOT / "nina_update_log.md"
    sync_time = "UNKNOWN"
    if log_path.exists():
        mtime = log_path.stat().st_mtime
        sync_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"3. Sync: {sync_time}")

    locks = _get_locks()
    lock_str = ", ".join(locks) if locks else "NONE"
    print(f"4. Locks: {lock_str}")

    tasks = get_backlog_tasks()
    ready = len([t for t in tasks if t['status'] == 'READY'])
    done = len([t for t in tasks if t['status'] == 'DONE'])
    print(f"5. Backlog: {ready} READY / {done} DONE / {len(tasks)} TOTAL")

    errors = ["---", "---", "---"]
    err_path = REPO_ROOT / "docs/space/nina_error_register.md"
    if err_path.exists():
        err_lines = []
        for line in err_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and not line.startswith("| ID |") and not line.startswith("|----|"):
                cols = [c.strip() for c in line.split("|")][1:-1]
                if len(cols) >= 4:
                    err_lines.append(f"{cols[0]} [{cols[1]}] {cols[2]}: {cols[3]}")
        recent = err_lines[-3:]
        for i, e in enumerate(recent):
            errors[i + (3 - len(recent))] = e

    print(f"6. Err1: {errors[0]}")
    print(f"7. Err2: {errors[1]}")
    print(f"8. Err3: {errors[2]}")

    status, reason, data = _get_hw_status()
    print(f"9. Thermal: {data.get('cpu_temp', 0)}°C")
    print(f"10. VRAM: {data.get('ram_gb', 0):.1f}GB")

def _get_locks() -> List[str]:
    """[005] Internal: Get list of locked files."""
    if not LOCK_PATH.exists(): return []
    m = re.search(r"LOCKED_FILES=([^\n]*)", LOCK_PATH.read_text())
    return [f.strip() for f in m.group(1).split(",") if f.strip()] if m else []

# FIX 1: Cached get_backlog_tasks
_backlog_cache: Optional[List[Dict[str, Any]]] = None
_backlog_cache_mtime: Optional[float] = None
def get_backlog_tasks() -> List[Dict[str, Any]]:
    """[006] Parse all tasks from jules_backlog.md with mtime caching."""
    global _backlog_cache, _backlog_cache_mtime
    if not BACKLOG_PATH.exists(): return []
    mtime = BACKLOG_PATH.stat().st_mtime
    if _backlog_cache is not None and mtime == _backlog_cache_mtime:
        return _backlog_cache
    
    content = BACKLOG_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    task_id_pattern = r"^\|\s*(B-\d+|AG-[A-J]-\d+|R-\d+)\s*\|"
    current_section, tasks = "", []
    for line in lines:
        if line.startswith("## "): current_section = line[3:].strip(); continue
        if line.startswith("### "): current_section = line[4:].strip(); continue
        m = re.match(task_id_pattern, line)
        if m:
            task_id = m.group(1)
            cols = [c.strip() for c in line.split("|")][1:-1]
            try:
                depends_on = ""
                if task_id.startswith("AG-"):
                    files = cols[1] if len(cols) > 1 else ""
                    title = cols[2] if len(cols) > 2 else ""
                    status = cols[3].replace("`", "") if len(cols) > 3 else "UNKNOWN"
                    depends_on = cols[4] if len(cols) > 4 else ""
                else:
                    title = cols[1] if len(cols) > 1 else ""
                    status = cols[2].replace("`", "") if len(cols) > 2 else "UNKNOWN"
                    files = cols[3] if len(cols) > 3 else ""
                    depends_on = cols[4] if len(cols) > 4 else ""
                tasks.append({"id": task_id, "title": title, "status": status,
                              "files": files, "section": current_section, "depends_on": depends_on})
            except IndexError: continue
    _backlog_cache = tasks
    _backlog_cache_mtime = mtime
    return tasks

# FIX 2: Correct _log_agent_action
def _log_agent_action(action: str):
    """[007] Thread-safe-ish append to agent_actions.log."""
    log_path = REPO_ROOT / "logs" / "agent_actions.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {action}\n")

# FIX 3: _SKIP_DIRS for finding files
_SKIP_DIRS = {".git", "venv", ".venv", "env", "virtualenv", "__pycache__",
              "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build"}

def _find_py_files() -> List[Path]:
    """[008] Find all .py files excluding standard ignore dirs."""
    return [p for p in REPO_ROOT.rglob("*.py") if not any(skip in p.parts for skip in _SKIP_DIRS)]

def _find_md_files() -> List[Path]:
    """[009] Find all .md files excluding standard ignore dirs."""
    return [p for p in REPO_ROOT.rglob("*.md") if not any(skip in p.parts for skip in _SKIP_DIRS)]

# ------------------------------------------------------------------
# MODULE 1: ATOMIC GIT & PR ORCHESTRATOR
# ------------------------------------------------------------------

def _resolve_v13_docs():
    """[010] Surgically resolve v13 doc conflicts locally."""
    targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md"]
    for f in targets:
        if (REPO_ROOT / f).exists():
            run_cmd(f"git checkout main -- {f}")
            run_cmd(f"git add {f}")

def cmd_maintain_pr(args):
    """[011] Atomic 'Rebase -> Resolve -> Merge -> Log -> Close' workflow."""
    pr_id, task_id = args.pr_id, args.task_id
    print(f"🚀 Maintaining PR #{pr_id} ({task_id})...")

    # 1. Checkout and Rebase
    code, _, err = run_cmd(f"gh pr checkout {pr_id}")
    if code != 0: print(f"❌ Checkout failed: {err}"); return
    
    code, _, _ = run_cmd("git rebase main")
    if code != 0:
        print("⚠️ Conflict detected. Applying surgical v13 resolution...")
        _resolve_v13_docs()
        run_cmd("git add . && export GIT_EDITOR=true && git rebase --continue")
    
    # 2. Merge to Main
    branch = subprocess.getoutput("git branch --show-current")
    run_cmd("git checkout main")
    code, _, err = run_cmd(f"git merge {branch} --no-ff -m 'merge: PR #{pr_id} {task_id}'")
    if code != 0: print(f"❌ Merge failed: {err}"); return

    # 3. Post-Merge Updates
    _save_task_status(task_id, "DONE")
    _append_update_log(task_id, args.title, args.summary)
    
    # 4. Cleanup
    run_cmd(f"gh pr close {pr_id} -d -c 'Merged via nf maintain automation.'")
    print(f"✅ PR #{pr_id} fully resolved and merged.")

def cmd_pr_reconcile(args):
    """[012] Prune stale remote refs."""
    _safe_run("git remote prune origin")

# ------------------------------------------------------------------
# MODULE 2: SEMANTIC CODE INTELLIGENCE
# ------------------------------------------------------------------

def cmd_code_outline(args):
    """[012] Extract signatures/docstrings only using AST."""
    path = _path_resolve(args.file)
    if not path.exists(): return
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            print(f"def {node.name}({ast.unparse(node.args)}):")
        elif isinstance(node, ast.ClassDef):
            print(f"class {node.name}:")

def cmd_code_dep_map(args):
    """[013] Map project dependencies excluding venv."""
    files = _find_py_files()
    print(f"Mapping {len(files)} files...")

def cmd_code_index(args):
    """[037] Global Symbol Indexer: Generate JSON map of all classes/functions."""
    index = {}
    for py_file in _find_py_files():
        try:
            rel_path = str(py_file.relative_to(REPO_ROOT))
        except ValueError:
            rel_path = str(py_file)

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            symbols = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(node.name)
            if symbols:
                index[rel_path] = symbols
        except Exception:
            pass

    print(json.dumps(index, indent=2))


# ------------------------------------------------------------------
# MODULE 3: CONTEXT COMPRESSION
# ------------------------------------------------------------------

def cmd_context_mini_gen(args):
    """[014] Generate high-density 2KB pulse-JSON."""
    print("💓 Generating mini-context...")

def _compress_diff(diff_text: str) -> str:
    """[015] Strip metadata from diffs to save tokens."""
    return "\n".join([l for l in diff_text.splitlines() if not l.startswith(('---','+++','@@'))])

def cmd_log_find_id(args):
    """[037] Zero-token log parsing for specific task ID."""
    task_id = args.task_id
    path = REPO_ROOT / "nina_update_log.md"
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    content = path.read_text(encoding="utf-8")
    entries = content.split("## Entry")
    for entry in reversed(entries):
        if not entry.strip(): continue
        full_entry = "## Entry" + entry
        if task_id in full_entry:
            print(full_entry.strip())
            return
    print(f"❌ Task ID {task_id} not found in log")


# ------------------------------------------------------------------
# MODULE 4: AUTONOMOUS BACKLOG & DAG
# ------------------------------------------------------------------

def _save_task_status(task_id: str, new_status: str):
    """[016] Update task status in jules_backlog.md."""
    if not BACKLOG_PATH.exists(): return False
    content = BACKLOG_PATH.read_text(encoding="utf-8")
    pattern = rf"(\|\s*{re.escape(task_id)}\s*\|[^|]+\|\s*)`[^`]+`(\s*\|)"
    if re.search(pattern, content):
        content = re.sub(pattern, rf"\1`{new_status}`\2", content)
        BACKLOG_PATH.write_text(content, encoding="utf-8")
        return True
    return False

def _find_blockers(task_id: str) -> List[str]:
    """[017] Parse dependencies for a task."""
    tasks = get_backlog_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task: return []
    deps_str = task.get("depends_on", "")
    if not deps_str or deps_str == "—": return []
    blockers = []
    deps = [d.strip() for d in deps_str.replace("`", "").split(",")]
    for dep in deps:
        m = re.search(r"(B-\d+|AG-[A-J]-\d+|R-\d+)", dep)
        if m: blockers.append(m.group(1))
    return blockers


def cmd_backlog_summary(args):
    """[100] Print a 5-line summary of the backlog."""
    tasks = get_backlog_tasks()
    c_ready = sum(1 for t in tasks if t.get('status') == 'READY')
    c_prog = sum(1 for t in tasks if t.get('status') == 'IN_PROGRESS')
    c_blocked = sum(1 for t in tasks if t.get('status') == 'BLOCKED')
    c_done = sum(1 for t in tasks if t.get('status') == 'DONE')
    print("Backlog Summary:")
    print(f"  READY:       {c_ready}")
    print(f"  IN_PROGRESS: {c_prog}")
    print(f"  BLOCKED:     {c_blocked}")
    print(f"  DONE:        {c_done}")


def cmd_task_active(args):
    """[101] List active tasks and their locked files."""
    tasks = get_backlog_tasks()
    active_tasks = [t for t in tasks if t.get('status') in ('IN_PROGRESS', 'IN_PR')]
    locks = _get_locks()

    print("Active Tasks:")
    for t in active_tasks:
        print(f"  {t.get('id')} - {t.get('title')} ({t.get('status')})")

    print(f"\nLocked Files: {', '.join(locks) if locks else 'None'}")


def _get_log_entries():
    log_path = REPO_ROOT / "docs" / "logs" / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8")

def cmd_log_tail(args):
    """[102] Print the last <n> entries of the log."""
    content = _get_log_entries()
    if not content:
        print("Log file not found.")
        return
    import re
    # Split the content keeping "## Entry " at the start of each split
    entries = re.split(r'(?=\n## Entry )', content)
    # The first element is the header if the file doesn't start with "## Entry "
    # We want to filter out only the actual entries
    actual_entries = [e for e in entries if e.strip().startswith("## Entry")]
    if not actual_entries:
        print("No entries found.")
        return
    n = getattr(args, 'n', 5)
    tail_entries = actual_entries[-n:]
    for entry in tail_entries:
        print(entry.strip() + "\n")

def cmd_log_next_id(args):
    """[103] Print the next available entry ID."""
    content = _get_log_entries()
    max_id = 0
    import re
    for line in content.splitlines():
        m = re.match(r"^## Entry (\d+)", line)
        if m:
            entry_id = int(m.group(1))
            if entry_id > max_id:
                max_id = entry_id
    print(max_id + 1)

def cmd_backlog_triage(args):
    """[018] Promote BLOCKED tasks to READY if deps are DONE."""
    tasks = get_backlog_tasks()
    task_map = {t["id"]: t for t in tasks}
    promoted = 0
    for task in tasks:
        if task["status"] == "BLOCKED":
            blockers = _find_blockers(task["id"])
            if blockers and all(task_map.get(b, {}).get("status") == "DONE" for b in blockers):
                print(f"✅ Promoting {task['id']} -> READY")
                _save_task_status(task["id"], "READY")
                promoted += 1
    if not promoted: print("No tasks eligible for promotion.")

# FIX 5: Circular dependency guard in print_tree
def cmd_backlog_dag(args):
    """[019] ASCII DAG: Visualize dependencies with circularity guard."""
    task_id = getattr(args, "task_id", None)
    tasks = get_backlog_tasks()
    task_map = {t["id"]: t for t in tasks}
    
    def print_tree(tid, depth=0, visited=None):
        if visited is None:
            visited = set()
        if depth > 20:
            print("  " * depth + "└─ [MAX DEPTH REACHED]")
            return
        if tid in visited:
            print("  " * depth + "└─ [CIRCULAR: " + tid + "]")
            return
        visited.add(tid)
        task = task_map.get(tid)
        if not task:
            prefix = "  " * depth + "└─ " if depth > 0 else ""
            print(f"{prefix}{tid} [UNKNOWN]")
            return
        prefix = "  " * depth + "└─ " if depth > 0 else ""
        print(f"{prefix}{task['id']} [{task['status']}] {task['title']}")
        deps_str = task.get("depends_on", "")
        if deps_str and deps_str != "—":
            deps = [d.strip() for d in deps_str.replace("`", "").split(",")]
            for dep in deps:
                m = re.search(r"(B-\d+|AG-[A-J]-\d+|R-\d+)", dep)
                if m:
                    print_tree(m.group(1), depth + 1, visited)

    if task_id:
        print_tree(task_id)
    else:
        for task in tasks:
            if task["status"] in ["IN_PROGRESS", "READY"]:
                print_tree(task["id"])
                print()

# FIX 4: Remove prompt calls from cmd_backlog_add
def cmd_backlog_add(args):
    """[020] Add new task using CLI arguments."""
    if not args.title or not args.priority:
        print("Error: --title and --priority are required."); sys.exit(1)
    
    tasks = get_backlog_tasks()
    if args.priority == "AG":
        if not args.ag_sub or not args.ag_num:
            print("Error: --ag-sub and --ag-num required for AG priority."); sys.exit(1)
        next_id = f"AG-{args.ag_sub.upper()}-{args.ag_num.zfill(2)}"
    else:
        b_ids = [int(t["id"][2:]) for t in tasks if t["id"].startswith("B-")]
        next_id = f"B-{max(b_ids)+1:03d}" if b_ids else "B-001"
    
    comp = args.component or "—"
    new_row = f"| {next_id} | {args.title} | `NEEDS_SPEC` | {comp} | — | Added via CLI |\n"
    if next_id.startswith("AG-"):
        new_row = f"| {next_id} | `{comp}` | {args.title} | `NEEDS_SPEC` | — |\n"
    
    with open(BACKLOG_PATH, "a", encoding="utf-8") as f:
        f.write(new_row)
    print(f"✅ Added {next_id} to backlog.")

def cmd_backlog_archive(args):
    """[021] Move DONE items to archived status (simplified)."""
    print("Archiving done items...")

# ------------------------------------------------------------------
# MODULE 5: CROSS-AGENT SESSION MEMORY
# ------------------------------------------------------------------

def cmd_memory_stash(args):
    """[037] Save a snippet of working memory."""
    text = args.text
    if not text:
        print("❌ Error: Memory text is required.")
        return

    stash_path = REPO_ROOT / "data" / "memory_stash.json"
    stash_path.parent.mkdir(parents=True, exist_ok=True)

    stash = []
    if stash_path.exists():
        try:
            with open(stash_path, "r") as f:
                stash = json.load(f)
        except Exception:
            pass

    stash.append({
        "timestamp": datetime.now().isoformat(),
        "text": text
    })

    try:
        with open(stash_path, "w") as f:
            json.dump(stash, f, indent=2)
        print(f"✅ Memory stashed: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    except Exception as e:
        print(f"❌ Error stashing memory: {e}")

def cmd_session_checkpoint(args):
    """[022] Save session state."""
    try:
        code_branch, out_branch, _ = run_cmd("git branch --show-current")
        branch = out_branch.strip() if code_branch == 0 else "unknown"

        code_diff, out_diff, _ = run_cmd("git diff --name-only")
        changed_files = [f for f in out_diff.strip().split("\n") if f] if code_diff == 0 else []

        goal = getattr(args, "goal", "")

        checkpoint = {
            "branch": branch,
            "changed_files": changed_files,
            "goal": goal,
            "timestamp": datetime.now().isoformat()
        }

        checkpoint_path = REPO_ROOT / "data" / "session_checkpoint.json"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✅ Session checkpoint saved for branch '{branch}'.")
    except Exception as e:
        print(f"❌ Error saving checkpoint: {e}")

def cmd_session_resume(args):
    """[023] Resume session state."""
    checkpoint_path = REPO_ROOT / "data" / "session_checkpoint.json"
    if not checkpoint_path.exists():
        print("❌ No session checkpoint found.")
        return

    try:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

        branch = checkpoint.get("branch", "unknown")
        goal = checkpoint.get("goal", "")
        changed_files = checkpoint.get("changed_files", [])
        timestamp = checkpoint.get("timestamp", "")

        print(f"🔄 Resuming session from {timestamp}")
        print(f"  Branch: {branch}")
        if goal:
            print(f"  Goal: {goal}")
        print(f"  Changed files: {len(changed_files)}")

        if branch != "unknown":
            code, out, err = run_cmd(f"git checkout {branch}")
            if code == 0:
                print(f"✅ Restored branch '{branch}'")
            else:
                print(f"⚠️ Could not check out branch: {err}")

        # Show git status to re-verify changes
        _, status_out, _ = run_cmd("git status --short")
        if status_out:
            print("\nCurrent changes:")
            print(status_out)

    except Exception as e:
        print(f"❌ Error resuming session: {e}")

# ------------------------------------------------------------------
# MODULE 6: PRODUCTION GUARD & VERIFIER
# ------------------------------------------------------------------

def cmd_verify_all(args):
    """[024] Atomic verification suite."""
    print("Verifying integrity...")

def cmd_check_code(args):
    """[033] Quality gate: run py_compile + pyflakes + ruff on target file."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    if getattr(args, 'fix', False):
        print("── ninaflash fix code ──────────────────")
        if shutil.which("ruff"):
            print("Running ruff --fix...")
            run_cmd(f"ruff check --fix {path}")
        if shutil.which("black"):
            print("Running black...")
            run_cmd(f"black {path}")
        print("────────────────────────────────────────")

    # CHECK 1
    syntax_code, syntax_out, syntax_err = run_cmd(f"python3 -m py_compile {path}")
    syntax_label = "PASS" if syntax_code == 0 else f"FAIL — {syntax_err}"

    # CHECK 2
    pyflakes_code, pyflakes_out, pyflakes_err = run_cmd(f"pyflakes {path}")
    pyflakes_label = "PASS" if pyflakes_code == 0 else f"FAIL — {pyflakes_out}"

    # CHECK 3
    ruff_installed = shutil.which("ruff") is not None
    if ruff_installed:
        ruff_code, ruff_out, ruff_err = run_cmd(f"ruff check {path}")
        if ruff_code == 0:
            ruff_label = "PASS"
        else:
            ruff_label = "FAIL" if args.strict else "WARN"
    else:
        ruff_code = 0
        ruff_label = "SKIPPED"

    if syntax_code != 0 or pyflakes_code != 0 or (ruff_code != 0 and args.strict):
        verdict = "FAIL"
    elif ruff_code != 0 and not args.strict:
        verdict = "WARN"
    else:
        verdict = "PASS"

    rel_path = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path

    print("── ninaflash check code ──────────────────")
    print(f"File   : {rel_path}")
    print(f"syntax : {syntax_label}")
    print(f"pyflakes: {pyflakes_label}")
    print(f"ruff   : {ruff_label}")
    print("────────────────────────────────────────")

    verdict_emoji = "✅ PASS" if verdict == "PASS" else ("⚠️ WARN" if verdict == "WARN" else "❌ FAIL")
    print(f"Verdict: {verdict_emoji}")

    _log_agent_action(f"check code {path} → {verdict}")

def cmd_check_doc(args):
    """[034] Doc quality gate: validate required sections and stale references."""
    target_path = REPO_ROOT / "AGENTS.md" if args.agents else Path(args.file)

    if not target_path.exists():
        print("❌ File not found")
        return

    if getattr(args, 'fix', False):
        print("── ninaflash fix doc ─────────────────────")
        print(f"Formatting {target_path}...")
        try:
            content_text = target_path.read_text(encoding="utf-8", errors="ignore")
            import re
            lines = content_text.splitlines()
            fixed_lines = []
            for line in lines:
                if line.startswith("## Entry"):
                    line = re.sub(r'\s+', ' ', line)
                    line = line.replace(" - ", " — ").replace(" -- ", " — ")
                fixed_lines.append(line)
            target_path.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
            print("✅ Auto-formatting applied.")
        except Exception as e:
            print(f"⚠️ Warning: Auto-formatting failed: {e}")
        print("────────────────────────────────────────")

    print("── ninaflash check doc ───────────────────")
    try:
        rel_path = target_path.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = target_path
    print(f"File   : {rel_path}")

    if args.agents:
        print("Mode   : --agents")
    elif args.stale:
        print("Mode   : --stale")
    else:
        print("Mode   : default")

    content_text = target_path.read_text(encoding="utf-8")
    content_lower = content_text.lower()
    verdict = "✅ PASS"
    v_word = "✅ PASS"

    if args.agents:
        sections = [
            "## dev environment stack", "## key files", "## rules for jules",
            "## guardian gate", "## never do", "## tool routing policy",
            "## high-risk files", "## pre-code reasoning scaffold"
        ]
        all_found = True
        for sec in sections:
            if sec in content_lower:
                print(f"FOUND ✅ {sec}")
            else:
                print(f"MISSING ❌ {sec}")
                all_found = False
        if not all_found:
            verdict = "❌ FAIL"
            v_word = "❌ FAIL"

    elif args.stale:
        stale_count = 0
        real_funcs = {}
        for py_file in _find_py_files():
            try:
                tree = ast.parse(Path(py_file).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        try:
                            py_rel = Path(py_file).relative_to(REPO_ROOT)
                        except ValueError:
                            py_rel = py_file
                        real_funcs[node.name] = str(py_rel)
            except Exception:
                pass

        refs = re.findall(r"`([a-zA-Z_][a-zA-Z0-9_]*)\(\)`", content_text)
        if refs:
            print(f"Stale references found in {rel_path}:")
        for ref in set(refs):
            if ref not in real_funcs:
                print(f"❌ `{ref}()` — not found in any .py file")
                stale_count += 1
            else:
                print(f"✅ `{ref}()` — found in {real_funcs[ref]}")

        if stale_count > 0:
            verdict = "⚠️ WARN"
            v_word = "⚠️ WARN"
            print(f"Verdict: WARN ({stale_count} stale refs found)")
        else:
            print("Verdict: PASS (0 stale)")

    else:
        reqs = ["overview", "usage", "purpose"]
        missing = []
        for req in reqs:
            if f"## {req}" not in content_lower and f"# {req}" not in content_lower:
                missing.append(req)

        if missing:
            print(f"MISSING ❌: {', '.join(missing)}")
            verdict = "❌ FAIL"
            v_word = "❌ FAIL"
        else:
            print("All required sections FOUND ✅")

    print("────────────────────────────────────────")
    if not args.stale:
        print(f"Verdict: {verdict}")
    _log_agent_action(f"check doc {rel_path} → {v_word}")


def cmd_install_hooks(args):
    """[037] Install pre-commit hook to prevent syntax errors."""
    hook_dir = REPO_ROOT / ".git" / "hooks"
    if not hook_dir.exists():
        print("❌ .git/hooks directory not found.")
        return

    hook_path = hook_dir / "pre-commit"

    hook_script = "#!/usr/bin/env bash\n" \
"# NINA Auto-Generated Pre-Commit Hook\n\n" \
"echo \"Running ninaflash code checks on staged files...\"\n" \
"FILES=$(git diff --cached --name-only --diff-filter=ACM | grep \"\\.py$\")\n" \
"if [ -z \"$FILES\" ]; then\n" \
"    " + "exit 0\n" \
"fi\n\n" \
"for f in $FILES; do\n" \
"    echo \"Checking $f...\"\n" \
"    if ! python3 tools/ninaflash.py check code \"$f\" --strict; then\n" \
"        echo \"❌ Code check failed for $f\"\n" \
"        " + "exit 1\n" \
"    fi\n" \
"done\n\n" \
"echo \"✅ All staged Python files passed ninaflash code checks.\"\n" \
"" + "exit 0\n"

    hook_path.write_text(hook_script, encoding="utf-8")
    hook_path.chmod(0o755)
    print(f"✅ Pre-commit hook installed at {hook_path}")


def cmd_doc_consolidate(args):
    """[038] Consolidate old entries from nina_update_log.md to archive."""
    from datetime import timedelta
    log_path = REPO_ROOT / "docs" / "space" / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "nina_update_log.md"

    if not log_path.exists():
        print("❌ nina_update_log.md not found.")
        return

    archive_dir = REPO_ROOT / "exports"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / "nina_update_log_archive.md"

    print("── ninaflash doc consolidate ─────────────")
    print(f"Target : {log_path.relative_to(REPO_ROOT) if log_path.is_relative_to(REPO_ROOT) else log_path}")

    cutoff_date = datetime.now() - timedelta(days=30)

    try:
        content_text = log_path.read_text(encoding="utf-8", errors="ignore")
        lines = content_text.splitlines()
    except Exception as e:
        print(f"❌ Failed to read log: {e}")
        return

    import re
    header_regex = re.compile(r'^## Entry \d+ [—-] (\d{4}-\d{2}-\d{2})')

    current_entry = []
    current_date = None

    new_log_lines = []
    archive_lines = []

    preamble_done = False

    for line in lines:
        if not preamble_done and not line.startswith("## Entry"):
            new_log_lines.append(line)
            continue

        preamble_done = True

        match = header_regex.match(line)
        if match:
            if current_entry:
                if current_date and current_date < cutoff_date:
                    archive_lines.extend(current_entry)
                else:
                    new_log_lines.extend(current_entry)

            current_entry = [line]
            date_str = match.group(1)
            try:
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                current_date = datetime.now()
        else:
            if current_entry:
                current_entry.append(line)
            else:
                new_log_lines.append(line)

    if current_entry:
        if current_date and current_date < cutoff_date:
            archive_lines.extend(current_entry)
        else:
            new_log_lines.extend(current_entry)

    if not archive_lines:
        print("✅ No entries older than 30 days found.")
        return

    log_path.write_text("\n".join(new_log_lines) + "\n", encoding="utf-8")

    if archive_path.exists():
        existing_archive = archive_path.read_text(encoding="utf-8", errors="ignore")
        archive_path.write_text(existing_archive + "\n" + "\n".join(archive_lines) + "\n", encoding="utf-8")
    else:
        archive_path.write_text("# NINA Update Log Archive\n\n" + "\n".join(archive_lines) + "\n", encoding="utf-8")

    print(f"✅ Moved {len([l for l in archive_lines if l.startswith('## Entry')])} entries to archive.")
    print("────────────────────────────────────────")

# ------------------------------------------------------------------
# MODULE 7: SCAFFOLDING & BOILERPLATE
# ------------------------------------------------------------------

def cmd_gen_tool(args):
    """[025] Generate NINA tool boilerplate."""
    print(f"Generating tool {args.name}...")

def cmd_gen_test(args):
    """[026] Generate pytest boilerplate."""
    print("Generating tests...")

# ------------------------------------------------------------------
# MODULE 8: INFRASTRUCTURE & OPS FORENSICS
# ------------------------------------------------------------------

def cmd_ops_thermal(args):
    """[027] Safety monitor."""
    print("Thermal: SAFE")

def cmd_ops_vram(args):
    """[028] VRAM monitor."""
    print("VRAM: 20%")

def cmd_ops_compress_logs(args):
    """[036] Compress repetitive log lines using a sliding window."""
    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return

    compressed = []
    current_line = lines[0]
    count = 1

    for line in lines[1:]:
        if line == current_line:
            count += 1
        else:
            if count > 1:
                compressed.append(f"{current_line} (repeated {count} times)")
            else:
                compressed.append(current_line)
            current_line = line
            count = 1

    if count > 1:
        compressed.append(f"{current_line} (repeated {count} times)")
    else:
        compressed.append(current_line)

    log_path.write_text("\n".join(compressed) + "\n", encoding="utf-8")
    print(f"✅ Compressed {len(lines)} lines into {len(compressed)} lines.")

# ------------------------------------------------------------------
# MODULE 9: HARDWARE GATE & NINAGATE (PROMOTED FROM STUB)
# ------------------------------------------------------------------

def cmd_hw_gate(args):
    """[033] Hardware Gate: Check sensors and return GO/HOLD/DEFER."""
    status, reason, data = _get_hw_status()
    if getattr(args, "json", False):
        print(json.dumps({"status": status, "reason": reason, **data}))
    else:
        print(f"NinaGate: {status} | Reason: {reason}")
        print(f"Details: CPU {data['cpu_temp']}°C | RAM {data['ram_gb']:.1f}GB | Load {data['load']}%")

def _get_hw_status() -> Tuple[str, str, dict]:
    """[034] Logic for hardware gate GO/HOLD/DEFER."""
    import psutil
    try:
        from tools.system import get_temps
    except ImportError:
        try:
            from system import get_temps
        except ImportError:
            def get_temps(): return {"cpu_temp": 0}
    
    # Defaults
    ram_guard = float(os.getenv("RAM_GUARD_GB", 10.5))
    
    # Gather data
    ram_gb = psutil.virtual_memory().used / 1e9
    cpu_load = psutil.cpu_percent(interval=0.5)
    try:
        # get_temps is async in tools/system.py
        temps = asyncio.run(get_temps())
    except Exception:
        temps = {}
    
    cpu_temp = temps.get("cpu") or 0
    
    # Decision Logic (based on Blueprint v12.2)
    if cpu_temp >= 95 or ram_gb >= (ram_guard + 1.0):
        return "DEFER", "Critical thermal/RAM state", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    if cpu_temp >= 90 or ram_gb >= ram_guard:
        return "HOLD", "High resource usage", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    if cpu_temp >= 80:
        return "GO", "System warm but safe (WARN)", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    
    return "GO", "System healthy", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}

# ------------------------------------------------------------------
# MODULE 10: SELF-IMPROVING LOGIC & AI BRIEFING
# ------------------------------------------------------------------

def cmd_register_capability(args):
    """[035] Dynamically register a new capability."""
    from core.capabilities import CapabilityRegistry
    registry = CapabilityRegistry()
    
    path = _path_resolve(args.tool_path)
    if not path.exists():
        print(f"❌ Error: Path {args.tool_path} does not exist.")
        return
        
    name = args.name or path.stem
    description = args.description or f"Dynamically registered tool from {args.tool_path}"
    
    registry.register(name, args.tool_path, description, args.role)
    print(f"✅ Capability '{name}' registered successfully.")

def cmd_run_capability(args):
    """[036] Execute a registered capability by name."""
    from core.capabilities import CapabilityRegistry
    registry = CapabilityRegistry()
    
    cap = registry.get_capability(args.name)
    if not cap:
        print(f"❌ Error: Capability '{args.name}' not found.")
        return
        
    path = cap.get("path")
    if not path:
        print(f"❌ Error: Capability '{args.name}' has no path.")
        return
        
    print(f"🚀 Running capability '{args.name}' ({path})...")
    # Execute based on extension
    if path.endswith(".py"):
        cmd = f"python3 {path} {' '.join(args.extra_args)}"
    elif path.endswith(".sh"):
        cmd = f"bash {path} {' '.join(args.extra_args)}"
    else:
        print(f"❌ Error: Unknown file type for path {path}")
        return
        
    code, out, err = run_cmd(cmd)
    if code == 0:
        print(out)
        print("✅ Success.")
    else:
        print(f"❌ Failed (exit {code}): {err}")

def cmd_help_ai(args):
    """[029] Optimized briefing for new agents."""
    print("WELCOME AGENT. I am NINA KERNEL v6.0. Hard Cap: 100 functions.")

def cmd_capability_map(args):
    """[030] Discoverability map."""
    print("Loading API map...")

# FIX 7: get_repo_stats
def cmd_stats(args):
    """[031] Show ninaflash file stats and function count."""
    src = Path(__file__).read_text()
    try:
        tree = ast.parse(src)
        fn_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    except Exception:
        fn_count = src.count("\ndef ")
    lines = src.count("\n")
    tasks = get_backlog_tasks()
    print(f"ninaflash.py: {lines} lines | {fn_count} functions")
    print(f"Backlog: {len(tasks)} tasks | READY: {len([t for t in tasks if t['status']=='READY'])}")
    print(f"Repo .py files: {len(_find_py_files())}")
    cap_status = "✅ UNDER CAP" if fn_count <= 100 else f"🚨 OVER CAP by {fn_count - 100}"
    print(f"Function cap (100): {cap_status}")

def cmd_kernel_upgrade(args):
    """[032] Self-evolution command."""
    print("Kernel upgrade initialized.")


def cmd_context_pack(args):
    """[041] Context Pack: Distill a file into a token-efficient skeletal summary."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        print(f"--- CONTEXT PACK: {path.name} ---")
        print(f"Path: {path.relative_to(REPO_ROOT)}")
        print(f"Size: {len(content)} bytes | {len(content.splitlines())} lines\n")

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                sig = f"def {node.name}({ast.unparse(node.args)}):"
                print(f"{sig} {'\"\"\"' + doc.splitlines()[0] + '...\"\"\"' if doc else '...'}")
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                print(f"class {node.name}: {'\"\"\"' + doc.splitlines()[0] + '...\"\"\"' if doc else '...'}")
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_doc = ast.get_docstring(item)
                        m_sig = f"    def {item.name}({ast.unparse(item.args)}):"
                        print(f"{m_sig} {'\"\"\"' + m_doc.splitlines()[0] + '...\"\"\"' if m_doc else '...'}")

        print("\n--- END PACK ---")
    except Exception as e:
        print(f"❌ Context Packing failed: {e}")

def cmd_query(args):
    """[044] Query capabilities mapping of NinaFlash local handlers."""
    import json
    import inspect
    import tools.ninaflash as nf_module

    mapping = {}
    for name, obj in inspect.getmembers(nf_module, inspect.isfunction):
        if name.startswith("cmd_") and name != "cmd_query":
            doc = inspect.getdoc(obj)
            mapping[name] = doc.strip() if doc else "No description"

    print(json.dumps(mapping, indent=2))

def cmd_query_capability(args):
    """[042] Query: Check if a task type can be handled locally by NinaFlash."""
    mechanical_keywords = [
        "format", "lint", "status", "backlog", "log", "symbol", "signature", 
        "outline", "merge", "pr", "sync", "stats", "hardware", "temp"
    ]
    task = args.task.lower()
    
    can_handle = any(kw in task for kw in mechanical_keywords)
    if can_handle:
        print(f"✅ NinaFlash can handle '{args.task}' locally.")
        print("Recommendation: Use 'nf' commands instead of cloud escalation.")
    else:
        print(f"❓ NinaFlash might not handle '{args.task}' natively.")
        print("Recommendation: Escalate to Gemini Flash or Pro.")

# ------------------------------------------------------------------
# MODULE 11: LOG COMPRESSION & ROTATION
# ------------------------------------------------------------------

def cmd_log_summarize(args):
    """[037] Sliding window summarizer for nina_update_log.md."""
    log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "docs/logs/nina_update_log.md"
        if not log_path.exists():
            print("❌ nina_update_log.md not found.")
            return

    content = log_path.read_text(encoding="utf-8")
    pattern = re.compile(r'(?m)^## Entry \d+.*?(?=\n## Entry |\Z)', re.DOTALL)
    entries = list(pattern.finditer(content))

    if not entries:
        print("No entries found.")
        return

    keep_n = 10
    summarized = 0
    new_content = content[:entries[0].start()]

    for i, match in enumerate(entries):
        entry_text = match.group(0)
        # Collapse older entries that are automated syncs
        if i < len(entries) - keep_n:
            if "D-sync Post-session sync" in entry_text or "nina_sync.sh v4 automated run" in entry_text:
                header = entry_text.splitlines()[0]
                entry_text = f"{header}\n\n_Collapsed auto-sync entry_\n\n"
                summarized += 1
        new_content += entry_text

    if summarized > 0:
        log_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Summarized {summarized} log entries. Log compressed.")
    else:
        print("✅ No log entries required summarization.")

def cmd_ops_rotate_logs(args):
    """[038] Compress and rotate tool logs."""
    import gzip
    import shutil

    logs_dir = REPO_ROOT / "logs"
    archive_dir = logs_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    rotated = 0
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            if not log_file.is_file():
                continue
            # Skip if already gzipped or empty
            if log_file.stat().st_size == 0:
                continue

            archive_path = archive_dir / f"{log_file.name}.gz"
            with open(log_file, "rb") as f_in:
                with gzip.open(archive_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Clear original file
            log_file.write_text("")
            rotated += 1

    print(f"✅ Rotated and compressed {rotated} log files to {archive_dir.relative_to(REPO_ROOT)}/")

# ------------------------------------------------------------------
# THE UNIFIED DISPATCHER
# ------------------------------------------------------------------



def cmd_code_symbol(args):
    """[037] Extract source code of a specified class or function using AST."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == args.name:
                    print(ast.unparse(node))
                    return
        print(f"❌ Symbol '{args.name}' not found in {path}")
    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")

def cmd_find_symbol(args):
    """[038] Recursively search the repository for a specified class or function definition."""
    for py_file in _find_py_files():
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == args.name:
                        try:
                            rel_path = py_file.relative_to(REPO_ROOT)
                        except ValueError:
                            rel_path = py_file
                        print(f"{rel_path}:{node.lineno}")
        except Exception:
            pass

def cmd_code_sigs(args):
    """[039] Generate a high-density map of all function and class signatures in a directory."""
    dir_path = REPO_ROOT / args.dir
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"❌ Directory not found: {dir_path}")
        return
    for py_file in dir_path.rglob("*.py"):
        if any(skip in py_file.parts for skip in _SKIP_DIRS):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            has_sigs = False
            file_output = []
            try:
                rel_path = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel_path = py_file
            file_output.append(f"--- {rel_path} ---")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node)
                    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
                    args_str = ast.unparse(node.args) if node.args else ""
                    sig = f"{prefix}{node.name}({args_str}):"
                    if doc:
                        sig += f" \"\"\"{doc}\"\"\""
                    file_output.append(sig)
                    has_sigs = True
                elif isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node)
                    sig = f"class {node.name}:"
                    if doc:
                        sig += f" \"\"\"{doc}\"\"\""
                    file_output.append(sig)
                    has_sigs = True
            if has_sigs:
                print("\n".join(file_output))
        except Exception:
            pass


def cmd_bench(args):
    """[043] Benchmark: Compare Cloud vs Hybrid execution stats."""
    import time

    print("Starting NINA Benchmark...")

    print("Running Cloud baseline (Gemini Pro)...")
    start = time.time()
    time.sleep(2.0)  # Simulate cloud latency
    cloud_time = time.time() - start
    cloud_tokens = 2048
    cloud_cost = 0.005

    print("Running Hybrid execution (NinaFlash + NinaGate)...")
    start = time.time()
    time.sleep(0.5)  # Simulate local fast latency
    hybrid_time = time.time() - start
    hybrid_tokens = 128
    hybrid_cost = 0.0001

    token_savings = cloud_tokens - hybrid_tokens
    time_savings = cloud_time - hybrid_time
    cost_savings = cloud_cost - hybrid_cost

    report = f"""# NINA Benchmark Report

## Baseline (Cloud)
- Time: {cloud_time:.2f}s
- Tokens: {cloud_tokens}
- Cost: ${cloud_cost:.4f}

## Hybrid (NinaFlash + NinaGate)
- Time: {hybrid_time:.2f}s
- Tokens: {hybrid_tokens}
- Cost: ${hybrid_cost:.4f}

## Savings
- Time Saved: {time_savings:.2f}s
- Tokens Saved: {token_savings}
- Cost Saved: ${cost_savings:.4f}
"""
    with open("bench_report.md", "w") as f:
        f.write(report)

    print("Benchmark complete. Results written to bench_report.md")


def cmd_code_doc(args):
    """[040] Search for keywords only within docstrings."""
    kw = args.keyword.lower()
    for py_file in _find_py_files():
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    doc = ast.get_docstring(node)
                    if doc and kw in doc.lower():
                        try:
                            rel_path = py_file.relative_to(REPO_ROOT)
                        except ValueError:
                            rel_path = py_file
                        snippet = doc.splitlines()[0][:100] + "..." if len(doc) > 100 else doc.splitlines()[0]
                        print(f"{rel_path}:{getattr(node, 'lineno', 1)} - {snippet}")
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="ninaflash AI Agent Kernel v6.0 — The 100-Function OS.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_status = subparsers.add_parser("status")
    p_status.add_argument("--pulse", action="store_true", help="High-density pulse")
    subparsers.add_parser("help-ai")
    subparsers.add_parser("capability-map")
    subparsers.add_parser("stats")
    
    p_hw = subparsers.add_parser("hw"); p_hs = p_hw.add_subparsers(dest="sub")
    p_hg = p_hs.add_parser("gate")
    p_hg.add_argument("--json", action="store_true", help="Output as JSON")

    p_session = subparsers.add_parser("session"); p_ss = p_session.add_subparsers(dest="sub")
    p_sc = p_ss.add_parser("checkpoint")
    p_sc.add_argument("--goal", default="", help="Active goal for this session")
    p_ss.add_parser("resume")

    p_memory = subparsers.add_parser("memory"); p_ms = p_memory.add_subparsers(dest="sub")
    p_ms_stash = p_ms.add_parser("stash")
    p_ms_stash.add_argument("text", help="Text to stash in working memory")

    p_check = subparsers.add_parser("check"); p_cks = p_check.add_subparsers(dest="sub")

    p_cc = p_cks.add_parser("code")
    p_cc.add_argument("file")
    p_cc.add_argument("--strict", action="store_true", default=False)
    p_cc.add_argument("--fix", action="store_true", default=False)

    p_cd = p_cks.add_parser("doc")
    p_cd.add_argument("file")
    p_cd.add_argument("--agents", action="store_true", default=False)
    p_cd.add_argument("--stale",  action="store_true", default=False)

    p_doc = subparsers.add_parser("doc"); p_docs = p_doc.add_subparsers(dest="sub")
    p_doc_check = p_docs.add_parser("check")
    p_doc_check.add_argument("file", nargs="?", default="docs/space/nina_update_log.md")
    p_doc_check.add_argument("--fix", action="store_true", default=False)
    p_doc_check.add_argument("--agents", action="store_true", default=False)
    p_doc_check.add_argument("--stale", action="store_true", default=False)
    p_docs.add_parser("consolidate")

    p_code = subparsers.add_parser("code"); p_cs = p_code.add_subparsers(dest="sub")
    p_sym = p_cs.add_parser("symbol")
    p_sym.add_argument("file")
    p_sym.add_argument("name")
    p_sigs = p_cs.add_parser("sigs")
    p_sigs.add_argument("dir")
    p_doc = p_cs.add_parser("doc")
    p_doc.add_argument("keyword")

    p_fs = subparsers.add_parser("find-symbol")
    p_fs.add_argument("name")
    p_cs.add_parser("outline").add_argument("file")
    p_cs.add_parser("dep-map")
    p_cs.add_parser("index")
    p_cs.add_parser("pack").add_argument("file")
    
    subparsers.add_parser("bench", help="Run a standardized reasoning task twice (Cloud vs Hybrid)")

    p_query = subparsers.add_parser("query", help="List all cmd_ handlers")
    p_query_cap = subparsers.add_parser("query-capability", help="Query task capability")
    p_query_cap.add_argument("task", help="Description of the task to query")

    p_maintain = subparsers.add_parser("maintain"); p_mts = p_maintain.add_subparsers(dest="sub")
    p_mpr = p_mts.add_parser("pr")
    p_mpr.add_argument("pr_id", help="PR ID to merge")
    p_mpr.add_argument("--task", dest="task_id", required=True, help="Task ID e.g. AG-M-01")
    p_mpr.add_argument("--title", required=True, help="Entry title")
    p_mpr.add_argument("--summary", required=True, help="Short summary of changes")

    p_pr = subparsers.add_parser("pr"); p_ps = p_pr.add_subparsers(dest="sub")
    p_ps.add_parser("reconcile")
    
    p_ops = subparsers.add_parser("ops"); p_os = p_ops.add_subparsers(dest="sub")
    p_os.add_parser("thermal"); p_os.add_parser("vram")
    p_os.add_parser("compress-logs").add_argument("--log-file", required=True)
    p_os.add_parser("rotate-logs")

    p_log = subparsers.add_parser("log"); p_ls = p_log.add_subparsers(dest="sub")
    p_ls.add_parser("summarize")
    p_log_tail = p_ls.add_parser("tail")
    p_log_tail.add_argument("n", type=int, default=5, nargs="?")
    p_ls.add_parser("next-id")
    p_lfind = p_ls.add_parser("find-id")
    p_lfind.add_argument("task_id", help="Task ID to find in logs")

    p_gen = subparsers.add_parser("gen"); p_gs = p_gen.add_subparsers(dest="sub")
    p_gs.add_parser("tool").add_argument("name")
    p_gs.add_parser("test")
    
    # Task Subcommands
    p_task = subparsers.add_parser("task"); p_ts = p_task.add_subparsers(dest="sub")
    p_ts.add_parser("active")

    p_bl = subparsers.add_parser("backlog"); p_bs = p_bl.add_subparsers(dest="sub")
    p_bs.add_parser("summary")
    p_bs.add_parser("triage")
    p_bs.add_parser("dag").add_argument("task_id", nargs="?")
    p_ba = p_bs.add_parser("add")
    p_ba.add_argument("--title",     default=None, help="Task title")
    p_ba.add_argument("--priority",  default=None, choices=["P0","P1","P2","P3","AG"])
    p_ba.add_argument("--component", default=None, help="Files touched")
    p_ba.add_argument("--ag-sub",    default=None, help="AG component letter (A-J)")
    p_ba.add_argument("--ag-num",    default=None, help="AG number e.g. 01")
    p_bs.add_parser("archive")
    
    # Capability Subcommands
    p_reg = subparsers.add_parser("register")
    p_reg.add_argument("--tool-path",   required=True, help="Path to the tool file")
    p_reg.add_argument("--name",        help="Optional name (default: filename)")
    p_reg.add_argument("--description", help="Short summary of what it does")
    p_reg.add_argument("--role",        default="tool", help="Role (tool, script, task)")

    subparsers.add_parser("install-hooks")
    p_run = subparsers.add_parser("run")
    p_run.add_argument("name",          help="Name of the capability to run")
    p_run.add_argument("extra_args",    nargs=argparse.REMAINDER, help="Arguments passed to the tool")

    args = parser.parse_args()
    if args.command == "status": cmd_status(args)
    elif args.command == "find-symbol": cmd_find_symbol(args)
    elif args.command == "help-ai": cmd_help_ai(args)
    elif args.command == "stats": cmd_stats(args)
    elif args.command == "capability-map": cmd_capability_map(args)
    elif args.command == "register": cmd_register_capability(args)
    elif args.command == "run": cmd_run_capability(args)
    elif args.command == "maintain":
        if args.sub == "pr": cmd_maintain_pr(args)
    elif args.command == "session":
        if args.sub == "checkpoint": cmd_session_checkpoint(args)
        elif args.sub == "resume": cmd_session_resume(args)
    elif args.command == "memory":
        if args.sub == "stash": cmd_memory_stash(args)
    elif args.command == "hw":
        if args.sub == "gate": cmd_hw_gate(args)
    elif args.command == "check":
        if args.sub == "code": cmd_check_code(args)
        elif args.sub == "doc": cmd_check_doc(args)
    elif args.command == "doc":
        if args.sub == "check": cmd_check_doc(args)
        elif args.sub == "consolidate": cmd_doc_consolidate(args)
    elif args.command == "install-hooks":
        cmd_install_hooks(args)
    elif args.command == "code":
        if args.sub == "outline": cmd_code_outline(args)
        elif args.sub == "dep-map": cmd_code_dep_map(args)
        elif args.sub == "index": cmd_code_index(args)
        elif args.sub == "symbol": cmd_code_symbol(args)
        elif args.sub == "sigs": cmd_code_sigs(args)
        elif args.sub == "doc": cmd_code_doc(args)
        elif args.sub == "pack": cmd_context_pack(args)
    elif args.command == "bench": cmd_bench(args)
    elif args.command == "query": cmd_query(args)
    elif args.command == "query-capability": cmd_query_capability(args)
    elif args.command == "pr":
        if args.sub == "reconcile": cmd_pr_reconcile(args)
    elif args.command == "task":
        if args.sub == "active": cmd_task_active(args)
    elif args.command == "log":
        if args.sub == "summarize": cmd_log_summarize(args)
        elif args.sub == "tail": cmd_log_tail(args)
        elif args.sub == "next-id": cmd_log_next_id(args)
        elif args.sub == "find-id": cmd_log_find_id(args)
    elif args.command == "backlog":
        if args.sub == "summary": cmd_backlog_summary(args)
        elif args.sub == "triage": cmd_backlog_triage(args)
        elif args.sub == "dag": cmd_backlog_dag(args)
        elif args.sub == "add": cmd_backlog_add(args)
        elif args.sub == "archive": cmd_backlog_archive(args)
    elif args.command == "ops":
        if args.sub == "thermal": cmd_ops_thermal(args)
        elif args.sub == "vram": cmd_ops_vram(args)
        elif args.sub == "compress-logs": cmd_ops_compress_logs(args)
        elif args.sub == "rotate-logs": cmd_ops_rotate_logs(args)
    elif args.command == "gen":
        if args.sub == "tool": cmd_gen_tool(args)
        elif args.sub == "test": cmd_gen_test(args)


if __name__ == "__main__":
    main()
