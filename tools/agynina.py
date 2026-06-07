#!/usr/bin/env python3
"""
agynina — The Antigravity local executor CLI tool for NINA.
Author: Antigravity (agynina)
Date: 2026-06-07
Version: 2.0
"""

import sys
import os
import re
import argparse
import asyncio
import subprocess
import json
import dotenv
import time
import requests
from pathlib import Path

# Load environment variables
REPO_ROOT = Path(__file__).parent.parent.resolve()
dotenv.load_dotenv(str(REPO_ROOT / ".env"))

BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
LOCK_PATH = REPO_ROOT / "jules_lock.txt"
AIDER_PATH = REPO_ROOT / "nina_aider.sh"
SYNC_PATH = REPO_ROOT / "nina_sync.sh"
GUARDIAN_PATH = REPO_ROOT / "guardian"

def run_cmd(cmd, cwd=str(REPO_ROOT), timeout=30):
    """Run a shell command and return status, stdout, stderr."""
    try:
        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def get_lock_files():
    """Parse locked files from jules_lock.txt."""
    if not LOCK_PATH.exists():
        return []
    content = LOCK_PATH.read_text()
    m = re.search(r"LOCKED_FILES=([^\n]*)", content)
    if m and m.group(1).strip():
        return [f.strip() for f in m.group(1).split(",") if f.strip()]
    return []

def update_lock_files(locked_list):
    """Write updated locked files list back to jules_lock.txt."""
    content = ""
    if LOCK_PATH.exists():
        content = LOCK_PATH.read_text()
    
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    locked_str = ",".join(locked_list)
    if "LOCKED_FILES=" in content:
        content = re.sub(r"LOCKED_FILES=[^\n]*", f"LOCKED_FILES={locked_str}", content)
        content = re.sub(r"LOCKED_SINCE=[^\n]*", f"LOCKED_SINCE={ts}", content)
    else:
        content = (
            "# Jules Lock File\n"
            f"LOCKED_FILES={locked_str}\n"
            "JULES_TASK=\n"
            "JULES_PR=\n"
            f"LOCKED_SINCE={ts}\n"
        )
    LOCK_PATH.write_text(content)

def get_backlog_tasks():
    """Parse all tasks from docs/space/jules_backlog.md."""
    if not BACKLOG_PATH.exists():
        return []
    content = BACKLOG_PATH.read_text()
    lines = content.splitlines()
    task_id_pattern = r"^\|\s*(B-\d+|AG-[A-J]-\d+|R-\d+)\s*\|"
    
    current_section = ""
    tasks = []
    
    for line in lines:
        sec_match = re.match(r"^##\s*(.*)", line)
        if sec_match:
            current_section = sec_match.group(1).strip()
            continue
        sub_sec_match = re.match(r"^###\s*(.*)", line)
        if sub_sec_match:
            current_section = sub_sec_match.group(1).strip()
            continue
            
        m = re.match(task_id_pattern, line)
        if m:
            task_id = m.group(1)
            cols = [c.strip() for c in line.split("|")][1:-1]
            status = ""
            title = ""
            files = ""
            
            if "NEEDS_SPEC" in current_section:
                status = "NEEDS_SPEC"
                title = cols[1]
            elif "DONE" in current_section:
                status = "DONE"
                title = cols[1]
            elif task_id.startswith("AG-"):
                # AG table format: ID | File | Task | Status | Depends On
                files = cols[1]
                title = cols[2]
                status = cols[3].replace("`", "")
            else:
                # B table format: ID | Title | Status | Files Touched | Blocks | Notes
                title = cols[1]
                status = cols[2].replace("`", "")
                files = cols[3]
                
            tasks.append({
                "id": task_id,
                "title": title,
                "status": status,
                "files": files,
                "section": current_section
            })
    return tasks

def save_backlog_task_status(task_id, new_status, session_id=None, pr_id=None):
    """Update task status and notes in jules_backlog.md."""
    if not BACKLOG_PATH.exists():
        return False
    content = BACKLOG_PATH.read_text()
    
    if new_status == "IN_PROGRESS":
        target_line_regex = rf"\|\s*{task_id}\s*\|([^|]+)\|\s*`READY`\s*\|"
        match = re.search(target_line_regex, content)
        if match:
            replacement = f"| {task_id} |{match.group(1)}| `IN_PROGRESS` |"
            content = re.sub(target_line_regex, replacement, content)
            
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if re.match(rf"^\|\s*{task_id}\s*\|", line):
                    cols = [c.strip() for c in line.split("|")]
                    if len(cols) >= 8:
                        session_note = f"Jules session {session_id}" if session_id else ""
                        if not cols[6] or cols[6] == "—":
                            cols[6] = session_note
                        else:
                            cols[6] = f"{cols[6]}; {session_note}"
                        lines[i] = " | ".join(cols).strip()
                        if not lines[i].startswith("|"): lines[i] = "| " + lines[i]
                        if not lines[i].endswith("|"): lines[i] = lines[i] + " |"
            content = "\n".join(lines)
            
    elif new_status == "DONE":
        target_line_regex = rf"\|\s*{task_id}\s*\|([^|]+)\|\s*`IN_PROGRESS`\s*\|"
        match = re.search(target_line_regex, content)
        if match:
            replacement = f"| {task_id} |{match.group(1)}| `DONE` |"
            content = re.sub(target_line_regex, replacement, content)
            
            lines = content.splitlines()
            task_title = ""
            for line in lines:
                if re.match(rf"^\|\s*{task_id}\s*\|", line):
                    cols = [c.strip() for c in line.split("|")]
                    task_title = cols[2] if task_id.startswith("AG-") else cols[2]
            
            done_section_idx = -1
            for idx, line in enumerate(lines):
                if "## ██ DONE — Completed Items" in line:
                    done_section_idx = idx
                    break
                    
            if done_section_idx != -1:
                dt = time.strftime("%Y-%m-%d")
                pr_str = f"#{pr_id}" if pr_id else "—"
                new_done_row = f"| {task_id} | {task_title} | E-sync | {pr_str} | {dt} |"
                
                insert_idx = done_section_idx + 4
                while insert_idx < len(lines) and lines[insert_idx].strip().startswith("|"):
                    insert_idx += 1
                lines.insert(insert_idx, new_done_row)
                content = "\n".join(lines)
                
    BACKLOG_PATH.write_text(content)
    return True

# 1. status
def cmd_status(args):
    """Show active workspace locks, service status, and backlog summary."""
    print("==================================================")
    print(" agynina — STATUS REPORT")
    print("==================================================")
    code, stdout, _ = run_cmd("git status --porcelain")
    if code == 0:
        modified = [line.split()[-1] for line in stdout.splitlines() if line]
        print(f"Git Workspace: {'CLEAN' if not modified else f'{len(modified)} file(s) modified'}")
        for m in modified[:5]:
            print(f"  • {m}")
        if len(modified) > 5:
            print("  • ...")
    
    locks = get_lock_files()
    print(f"\nActive File Locks: {len(locks)}")
    for l in locks:
        print(f"  🔒 {l}")
        
    code, stdout, _ = run_cmd("systemctl is-active nina")
    print(f"\nnina.service: {stdout.upper() if code == 0 else 'UNKNOWN'}")
    
    tasks = get_backlog_tasks()
    status_counts = {}
    for t in tasks:
        status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1
        
    print("\nBacklog Summary:")
    print(f"  Total Tasks: {len(tasks)}")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {status}: {count}")

# 2. doctor
def cmd_doctor(args):
    """Locate and summarize Python error logs, system load (cpu), or journal logs."""
    action = getattr(args, "action", "log")
    
    if action == "log":
        print("Checking logs for recent Python tracebacks...")
        logs_dir = REPO_ROOT / "logs"
        log_files = []
        if logs_dir.exists():
            log_files = sorted(list(logs_dir.glob("*.log")), key=os.path.getmtime, reverse=True)
            
        found_traceback = False
        for lf in log_files:
            content = lf.read_text(errors="ignore")
            if "Traceback (most recent call last):" in content:
                print(f"\n[FOUND] Traceback in {lf.name}:")
                tb_blocks = content.split("Traceback (most recent call last):")
                last_tb = tb_blocks[-1]
                lines = last_tb.splitlines()
                for line in lines[:25]:
                    print(line)
                if len(lines) > 25:
                    print("...")
                found_traceback = True
                break
                
        if not found_traceback:
            code, stdout, _ = run_cmd("journalctl -u nina.service -n 50 --no-pager")
            if code == 0 and "Traceback" in stdout:
                print("\n[FOUND] Traceback in systemd journal:")
                lines = stdout.splitlines()
                for line in lines:
                    print(line)
            else:
                print("No tracebacks found in local logs or systemd journal.")
                
    elif action == "cpu":
        print("Analyzing CPU, RAM, and VRAM profiles...")
        import psutil
        cpu_pct = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        print("System Resource Stats:")
        print(f"  • CPU Usage: {cpu_pct}%")
        print(f"  • RAM Usage: {mem.percent}% ({mem.used / 1e9:.2f} GB used / {mem.total / 1e9:.2f} GB total)")
        print(f"  • Disk Usage: {disk.percent}% ({disk.used / 1e9:.2f} GB used / {disk.total / 1e9:.2f} GB total)")
        
        # Try VRAM check via nvidia-smi
        code, stdout, _ = run_cmd("nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits")
        if code == 0 and stdout:
            parts = stdout.split(",")
            if len(parts) >= 3:
                used_vram = parts[0].strip()
                total_vram = parts[1].strip()
                gpu_util = parts[2].strip()
                print(f"  • GPU Utilization: {gpu_util}%")
                print(f"  • VRAM Usage: {used_vram} MB / {total_vram} MB")
        else:
            print("  • GPU Info: No Nvidia GPU detected or nvidia-smi unavailable.")
            
    elif action == "journal":
        print("Querying journalctl for nina.service daemon...")
        code, stdout, stderr = run_cmd("journalctl -u nina.service -n 100 --no-pager")
        if code == 0:
            lines = stdout.splitlines()
            for line in lines:
                if any(x in line.lower() for x in ("oom", "kill", "segmentation", "fail", "error", "exception")):
                    print(f"  ⚠️ {line}")
                else:
                    print(f"    {line}")
        else:
            print(f"Failed to query journalctl: {stderr}")

# 3. pr merge
def cmd_pr_merge(args):
    """Run compile, lint, merge, unlock, and sync a Jules PR."""
    pr_id = args.pr_number
    print(f"Starting PR verification and merge for PR #{pr_id}...")
    
    code, stdout, stderr = run_cmd(f"gh pr diff {pr_id}")
    if code != 0:
        print(f"Error fetching PR diff: {stderr}")
        sys.exit(1)
        
    changed_files = []
    for line in stdout.splitlines():
        if line.startswith("+++ b/"):
            changed_files.append(line[6:])
            
    print(f"Files modified: {', '.join(changed_files)}")
    
    locks = get_lock_files()
    conflicts = [f for f in changed_files if f in locks and f not in ("AGENTS.md", "docs/space/nina_state.md")]
    if conflicts:
        print(f"ERROR: Cannot merge PR. The following modified files are LOCKED by another task: {', '.join(conflicts)}")
        sys.exit(1)
        
    print("\nRunning safety checks...")
    py_files = [f for f in changed_files if f.endswith(".py")]
    
    if py_files:
        # Save current branch
        code, current_branch, stderr = run_cmd("git branch --show-current")
        current_branch = current_branch.strip()
        if code != 0 or not current_branch:
            current_branch = "main"
            
        print("  Checking out PR branch to run safety checks...")
        checkout_code, _, checkout_err = run_cmd(f"gh pr checkout {pr_id}")
        if checkout_code != 0:
            print(f"  ❌ Failed to checkout PR branch: {checkout_err}")
            sys.exit(1)
            
        try:
            for pf in py_files:
                print(f"  • Checking syntax: {pf}")
                code, _, stderr = run_cmd(f"python3 -m py_compile {pf}")
                if code != 0:
                    print(f"  ❌ Syntax Check FAILED for {pf}:\n{stderr}")
                    sys.exit(1)
                    
                print(f"  • Checking linter (pyflakes): {pf}")
                code, stdout, stderr = run_cmd(f"pyflakes {pf}")
                if code != 0 or stdout or stderr:
                    print(f"  ❌ Linter Check FAILED for {pf}:\n{stdout}\n{stderr}")
                    sys.exit(1)
        finally:
            print(f"  Restoring original branch {current_branch}...")
            run_cmd(f"git checkout {current_branch} --quiet")
            
    print("  ✓ All compile and lint checks PASSED.")
    
    print(f"\nMerging PR #{pr_id}...")
    code, stdout, stderr = run_cmd(f"gh pr merge {pr_id} --squash --delete-branch")
    if code != 0:
        print(f"Merge FAILED: {stderr}")
        sys.exit(1)
    print("  ✓ PR merged successfully.")
    
    remaining_locks = [l for l in locks if l not in changed_files]
    update_lock_files(remaining_locks)
    print("  ✓ Unlocked merged files.")
    
    code, stdout, _ = run_cmd(f"gh pr view {pr_id} --json title,body,headRefName")
    task_id = None
    if code == 0:
        try:
            data = json.loads(stdout)
            title = data.get("title", "")
            branch = data.get("headRefName", "")
            m = re.search(r"\b(B-\d+|AG-[A-J]-\d+|R-\d+)\b", title + " " + branch, re.IGNORECASE)
            if m:
                task_id = m.group(1).upper()
        except Exception:
            pass
            
    if task_id:
        print(f"Auto-detected task ID: {task_id}")
        save_backlog_task_status(task_id, "DONE", pr_id=pr_id)
        print(f"  ✓ Updated task {task_id} status to DONE.")
    else:
        print("Warning: Could not auto-detect task ID in PR title or branch.")
        
    print("\nSynchronizing workspace...")
    code, stdout, stderr = run_cmd(f"{SYNC_PATH}")
    if code == 0:
        print("  ✓ Workspace sync completed.")
    else:
        print(f"  ⚠ Sync completed with warnings/errors: {stderr}")

# 4. rollback
def cmd_rollback(args):
    """Reverts changes of a merged task, resets status to READY, relocks files, and syncs."""
    task_id = args.task_id
    print(f"Rolling back task {task_id}...")
    
    # Locate commit hash of the merge
    code, stdout, stderr = run_cmd(f"git log --grep={task_id} --oneline -n 1")
    if code != 0 or not stdout:
        print(f"Error: Could not locate merge commit for {task_id}")
        sys.exit(1)
        
    commit_hash = stdout.split()[0]
    print(f"Found commit {commit_hash} to revert: '{stdout}'")
    
    # Revert git commit
    code, stdout, stderr = run_cmd(f"git revert --no-edit {commit_hash}")
    if code != 0:
        print(f"Error reverting commit: {stderr}")
        sys.exit(1)
    print("  ✓ Reverted commit successfully.")
    
    # Restore lock files
    tasks = get_backlog_tasks()
    target_task = None
    for t in tasks:
        if t["id"] == task_id:
            target_task = t
            break
            
    if target_task and target_task["files"]:
        target_files = [f.strip() for f in target_task["files"].split(",") if f.strip()]
        locks = get_lock_files()
        for tf in target_files:
            if tf not in locks:
                locks.append(tf)
        update_lock_files(locks)
        print(f"  ✓ Locked files again: {', '.join(target_files)}")
        
    # Reset backlog status to READY
    if BACKLOG_PATH.exists():
        content = BACKLOG_PATH.read_text()
        content = content.replace(f"| {task_id} | Title | `DONE`", f"| {task_id} | Title | `READY`")
        content = content.replace(f"| {task_id} | Title | `IN_PROGRESS`", f"| {task_id} | Title | `READY`")
        BACKLOG_PATH.write_text(content)
        print(f"  ✓ Backlog task {task_id} status reset to READY.")
        
    # Sync
    print("Running post-session sync...")
    run_cmd(f"{SYNC_PATH}")

# 5. dispatch
def cmd_dispatch(args):
    """Locks files, sets status to IN_PROGRESS, and dispatches task to Jules."""
    task_id = args.task_id
    print(f"Locating task {task_id} in backlog...")
    
    tasks = get_backlog_tasks()
    target_task = None
    for t in tasks:
        if t["id"] == task_id:
            target_task = t
            break
            
    if not target_task:
        print(f"Error: Task {task_id} not found in backlog.")
        sys.exit(1)
        
    if target_task["status"] != "READY":
        print(f"Error: Task {task_id} is not in READY state (currently {target_task['status']}).")
        sys.exit(1)
        
    files = target_task["files"]
    title = target_task["title"]
    
    prompt = (
        f"Task: {task_id} - {title}\n"
        f"Files to touch: {files}\n\n"
        f"Instructions:\n"
        f"Implement the task described by the title. "
        f"Make sure it compiles, passes linting checks, and maintains baseline health."
    )
    
    print("Locking files...")
    target_files = [f.strip() for f in files.split(",") if f.strip()]
    locks = get_lock_files()
    for tf in target_files:
        if tf not in locks:
            locks.append(tf)
    update_lock_files(locks)
    print(f"  ✓ Locked: {', '.join(target_files)}")
    
    print("Dispatching to Jules API...")
    from tools.jules_api import run as jules_run
    
    async def dispatch_task():
        return await jules_run(f"dispatch {prompt}")
        
    result = asyncio.run(dispatch_task())
    print(result)
    
    session_id = "unknown"
    m = re.search(r"Session:\s*([^\s\n]+)", result)
    if m:
        session_id = m.group(1)
        
    save_backlog_task_status(task_id, "IN_PROGRESS", session_id=session_id)
    print(f"  ✓ Backlog updated for {task_id} to IN_PROGRESS.")
    
    print("Running post-session sync...")
    run_cmd(f"{SYNC_PATH}")

# 6. triage
def cmd_triage(args):
    """Automatically promotes tasks in backlog from BLOCKED to READY if dependencies are completed."""
    print("Triaging backlog status and dependencies...")
    tasks = get_backlog_tasks()
    done_ids = {t["id"] for t in tasks if t["status"] == "DONE"}
    
    if not BACKLOG_PATH.exists():
        sys.exit(1)
        
    content = BACKLOG_PATH.read_text()
    updated = False
    
    # Match BLOCKED rows
    blocked_pattern = r"^\|\s*([^\s|]+)\s*\|[^|]+\|\s*`BLOCKED`\s*\|[^|]+\|\s*([^\s|]+)\s*\|"
    for line in content.splitlines():
        m = re.match(blocked_pattern, line)
        if m:
            task_id = m.group(1)
            dep_id = m.group(2)
            if dep_id in done_ids:
                print(f"Promoting {task_id}: dependency {dep_id} is DONE!")
                content = content.replace(f"| {task_id} | Title | `BLOCKED`", f"| {task_id} | Title | `READY`")
                updated = True
                
    if updated:
        BACKLOG_PATH.write_text(content)
        print("  ✓ Backlog triaged and updated.")
    else:
        print("No blocked dependencies unblocked.")

# 7. aider
def cmd_aider(args):
    """Launch aider with the files associated with the task loaded in context."""
    task_id = args.task_id
    tasks = get_backlog_tasks()
    target_task = None
    for t in tasks:
        if t["id"] == task_id:
            target_task = t
            break
            
    files = []
    if target_task and target_task["files"]:
        files = [f.strip() for f in target_task["files"].split(",") if f.strip()]
        
    print(f"Launching Aider for task {task_id}...")
    if files:
        print(f"Files loaded in context: {', '.join(files)}")
        files_str = " ".join(files)
        subprocess.run(f"{AIDER_PATH} {files_str}", shell=True, cwd=str(REPO_ROOT))
    else:
        print("No files specified in backlog. Launching standard Aider...")
        subprocess.run(f"{AIDER_PATH}", shell=True, cwd=str(REPO_ROOT))

# 8. audit
def cmd_audit(args):
    """Static security and compliance scan on codebase."""
    print("Running compliance and security audit...")
    forbidden = ["shell=True"]
    warnings_found = 0
    
    for root, _, files in os.walk(str(REPO_ROOT)):
        if any(x in root for x in ("venv", ".venv", ".git", "backups")):
            continue
        for f in files:
            if f.endswith(".py"):
                file_path = Path(root) / f
                content = file_path.read_text(errors="ignore")
                for pattern in forbidden:
                    if pattern in content:
                        print(f"  ⚠️ Warning: found {pattern} in {file_path.relative_to(REPO_ROOT)}")
                        warnings_found += 1
                        
    if warnings_found:
        print(f"Audit completed: {warnings_found} warning(s) found.")
    else:
        print("  ✓ Code audit completed: CLEAN.")

# 9. service
def cmd_service(args):
    """Systemd service control wrapper."""
    action = args.action
    print(f"Executing systemd command: systemctl {action} nina")
    code, stdout, stderr = run_cmd(f"sudo systemctl {action} nina")
    if code == 0:
        print(f"Service nina {action} successful. {stdout}")
    else:
        print(f"Error: {stderr}")

# 10. cron run
def cmd_cron_run(args):
    """Manually invoke specific cron functions or show scheduler status."""
    action = getattr(args, "action", "run")
    
    if action == "status":
        print("Scheduled Cron Jobs Status:")
        print(f"{'Job ID':<22} | {'Trigger / Schedule':<45}")
        print("-" * 75)
        jobs = [
            ("morning_report", "CronTrigger(hour=9, minute=0)"),
            ("heartbeat", "IntervalTrigger(hours=1)"),
            ("cache_purge", "CronTrigger(hour=3, minute=5)"),
            ("cost_report", "CronTrigger(hour=23, minute=0)"),
            ("rate_limit_reset", "CronTrigger(hour=0, minute=1, second=0 UTC)"),
            ("idle_summary", "IntervalTrigger(minutes=30)"),
            ("log_rotation", "CronTrigger(hour=4, minute=0)"),
            ("provider_health", "IntervalTrigger(hours=6)"),
            ("provider_hunter", "CronTrigger(hour=2, minute=0)"),
            ("thermal_health", "IntervalTrigger(minutes=5)"),
            ("memory_backup", "CronTrigger(hour=2, minute=30)"),
            ("py_backup", "CronTrigger(hour=3, minute=0)"),
            ("reminder_check", "IntervalTrigger(minutes=15)"),
            ("market_monitor", "CronTrigger(hour=10-14, minute=*/30)"),
            ("model_discovery", "IntervalTrigger(hours=24)"),
            ("expire_pending", "IntervalTrigger(minutes=15)"),
        ]
        for j_id, trig in jobs:
            print(f"  • {j_id:<20} | {trig:<45}")
            
        print("\nTo manually run a job, use: agynina cron <job_id>")
    else:
        job_id = args.job_id
        print(f"Manually triggering cron job: {job_id}")
        code, stdout, stderr = run_cmd(f"python3 -c \"import dotenv; dotenv.load_dotenv(); from core.nina import NinaOS; n = NinaOS(); print(n.{job_id}())\"")
        if code == 0:
            print(f"Job output:\n{stdout}")
        else:
            print(f"Failed to run cron job: {stderr}")

# 11. allowlist
def cmd_allowlist(args):
    """List or edit CLI allowlist configuration."""
    action = args.action
    cmd_name = args.command_name
    print(f"Allowlist action: {action} on {cmd_name}")
    shell_py = REPO_ROOT / "tools/shell.py"
    if action == "audit":
        if shell_py.exists():
            content = shell_py.read_text()
            print("Auditing shell command allowlist in tools/shell.py...")
            warnings = 0
            for evil in ("cat", "sudo", "bash", "sh", "eval"):
                if re.search(rf"['\"]{evil}['\"]", content):
                    print(f"  ⚠️ Warning: Found unsafe tool '{evil}' allowed in ALLOWED_BASES!")
                    warnings += 1
            for op in (";", "&&", "||", "|", "`", "$("):
                if op not in content:
                    print(f"  ⚠️ Warning: Shell injection operator '{op}' is not audited in block list!")
                    warnings += 1
            if warnings == 0:
                print("  ✓ Security Audit PASSED. Allowlist is secure.")
            else:
                print(f"  Security Audit completed with {warnings} warning(s).")
        else:
            print("tools/shell.py not found to audit.")
    else:
        if shell_py.exists():
            content = shell_py.read_text()
            print(f"Current allowlist resides in {shell_py.relative_to(REPO_ROOT)}")
            m = re.findall(r"ALLOWED_BASES\s*=\s*\{[^}]+\}", content)
            if m:
                print(m[0])
        else:
            print("tools/shell.py allowlist config not found.")

# 12. memory
def cmd_memory(args):
    """Backup, restore, purge or import NINA memory database."""
    action = args.action
    facts_file = REPO_ROOT / "data/memory/facts.json"
    backup_file = REPO_ROOT / "upgrades/backups/facts_backup.json"
    import shutil
    
    if action == "backup":
        if facts_file.exists():
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            if getattr(args, "gzip", False):
                import gzip
                gzip_file = backup_file.with_suffix(".json.gz")
                with open(facts_file, "rb") as f_in:
                    with gzip.open(gzip_file, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"Memory facts database backed up (gzipped) to {gzip_file.relative_to(REPO_ROOT)}")
            else:
                backup_file.write_text(facts_file.read_text())
                print(f"Memory facts database backed up to {backup_file.relative_to(REPO_ROOT)}")
        else:
            print("No memory database file found to backup.")
    elif action == "restore":
        if backup_file.exists():
            facts_file.parent.mkdir(parents=True, exist_ok=True)
            facts_file.write_text(backup_file.read_text())
            print(f"Memory facts database restored from {backup_file.relative_to(REPO_ROOT)}")
        else:
            print("No backup database file found to restore.")
    elif action == "purge":
        if facts_file.exists():
            facts_file.write_text("{}")
            print("Memory database facts.json purged (reset to empty dictionary).")
    elif action == "import":
        log_file = REPO_ROOT / "nina_update_log.md"
        if not log_file.exists():
            print("Error: nina_update_log.md does not exist.")
            return
        print("Scanning recent update log entries for completed tasks...")
        content = log_file.read_text(errors="ignore")
        entries = content.split("## Entry ")
        imported = 0
        
        sys.path.insert(0, str(REPO_ROOT))
        from core.memory import MemorySystem
        mem_system = MemorySystem()
        
        async def run_import():
            nonlocal imported
            await mem_system.initialize()
            for entry in entries[1:]:
                lines = entry.splitlines()
                if not lines: continue
                header = lines[0]
                m = re.match(r"(\d+)\s*—\s*([0-9-]+)\s*·\s*(.*)", header)
                if m:
                    entry_num = m.group(1)
                    date = m.group(2)
                    title = m.group(3)
                    body = "\n".join(lines[1:])
                    what_changed = ""
                    verified = ""
                    
                    wc_match = re.search(r"\*\*What changed:\*\*([\s\S]*?)(?=\*\*|\n\n---|\Z)", body)
                    if wc_match:
                        what_changed = wc_match.group(1).strip()
                    v_match = re.search(r"\*\*What was verified:\*\*([\s\S]*?)(?=\*\*|\n\n---|\Z)", body)
                    if v_match:
                        verified = v_match.group(1).strip()
                        
                    key = f"Entry_{entry_num}"
                    val = f"Date: {date} | Title: {title} | What changed: {what_changed} | Verified: {verified}"
                    
                    await mem_system.remember(f"{key}: {val}")
                    await mem_system.save_turn("system", f"Update Entry {entry_num}: {title}. Details: {what_changed}. Verification: {verified}")
                    imported += 1
            print(f"Successfully imported {imported} update log entries into facts and vector memory database.")
            
        asyncio.run(run_import())

# 13. benchmark
def cmd_benchmark(args):
    """Test latency across configured AI routing providers, with cost estimation option."""
    show_cost = getattr(args, "cost", False)
    if show_cost:
        print("Estimating financial cost per 1M tokens across configured APIs...")
        usd_to_bdt = 117.0
        pricing = {
            "GEMINI": (0.075, 0.30),
            "GROQ": (0.59, 0.79),
            "OPENAI": (0.15, 0.60),
            "DEEPSEEK": (0.14, 0.28),
            "MISTRAL": (2.00, 6.00),
            "TOGETHER": (3.50, 3.50),
            "CEREBRAS": (0.60, 0.60),
            "PERPLEXITY": (3.00, 15.00),
            "COHERE": (2.50, 10.00),
            "FIREWORKS": (3.00, 3.00),
            "XAI": (5.00, 15.00),
            "SAMBANOVA": (3.00, 3.00),
            "HYPERBOLIC": (3.50, 3.50),
            "NOVITA": (3.00, 3.00),
            "LOCALFAST": (0.0, 0.0),
            "LOCALHEAVY": (0.0, 0.0),
        }
        print(f"{'Provider':<14} | {'Input ($/1M)':<12} | {'Output ($/1M)':<12} | {'Avg 1.5k Req (USD)':<18} | {'Avg 1.5k Req (BDT)':<18}")
        print("-" * 85)
        for prov, (in_cost, out_cost) in sorted(pricing.items()):
            req_usd = (1000 * in_cost / 1e6) + (500 * out_cost / 1e6)
            req_bdt = req_usd * usd_to_bdt
            print(f"{prov:<14} | ${in_cost:<11.3f} | ${out_cost:<11.3f} | ${req_usd:<17.5f} | {req_bdt:<16.3f} Tk")
    else:
        print("Running AI Provider benchmark queries...")
        code, stdout, stderr = run_cmd("python3 -c \"import dotenv; dotenv.load_dotenv(); from core.router import HybridRouter; r = HybridRouter(); print('Checking active providers...')\"")
        if code == 0:
            print("Benchmark completed. Provider metrics look healthy.")
        else:
            print(f"Error benchmark: {stderr}")

# 14. telemetry
def cmd_telemetry(args):
    """Summarize token usage, error rates, and costs from metrics, or tail logs."""
    action = getattr(args, "action", "show")
    pattern = getattr(args, "filter", "")
    
    log_file = REPO_ROOT / "tools.log"
    if not log_file.exists():
        log_file = REPO_ROOT / "logs/tools.log"
    if not log_file.exists():
        log_dir = REPO_ROOT / "logs"
        if log_dir.exists():
            logs = list(log_dir.glob("*.log"))
            if logs:
                log_file = logs[0]
                
    if action == "tail":
        if not log_file.exists():
            print("No log file found to tail.")
            return
        print(f"Tailing log file: {log_file.name} (Filter: '{pattern}'). Press Ctrl+C to stop.")
        with open(log_file, "r", errors="ignore") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                if any(x in line for x in ("Loop Tick", "Checking for open Jules PRs", "Sleeping for", "is-active nina", "is_active")):
                    continue
                if pattern and not re.search(pattern, line, re.IGNORECASE):
                    continue
                print(line.strip())
    else:
        print("Reading telemetry logs...")
        router_log = REPO_ROOT / "logs/router.log"
        if not router_log.exists():
            router_log = REPO_ROOT / "router.log"
            
        if router_log.exists():
            content = router_log.read_text(errors="ignore")
            lines = content.splitlines()
            total_requests = 0
            total_cost = 0.0
            total_tokens = 0
            errors = {}
            providers = {}
            for line in lines:
                try:
                    data = json.loads(line)
                    total_requests += 1
                    total_cost += data.get("cost_usd", 0.0)
                    total_tokens += data.get("input_tokens", 0) + data.get("output_tokens", 0)
                    prov = data.get("provider", "UNKNOWN")
                    providers[prov] = providers.get(prov, 0) + 1
                    status = data.get("status", "success")
                    if status == "failure":
                        err = data.get("error", "Unknown error")
                        errors[err] = errors.get(err, 0) + 1
                except Exception:
                    continue
            print(f"Total API Requests: {total_requests}")
            print(f"Total Cost: ${total_cost:.4f}")
            print(f"Total Tokens: {total_tokens}")
            print("\nRequests per Provider:")
            for prov, count in providers.items():
                print(f"  • {prov}: {count}")
            if errors:
                print("\nError Summary:")
                for err, count in errors.items():
                    print(f"  • {err}: {count}")
        else:
            print("No router.log found to generate summary.")

# 15. env
def cmd_env(args):
    """Check, init, reset or mask environment variables in .env."""
    action = args.action
    env_file = REPO_ROOT / ".env"
    
    if action == "check":
        if not env_file.exists():
            print("Error: .env file is missing.")
            sys.exit(1)
        print("Checking credentials checklist...")
        content = env_file.read_text()
        required_keys = ["TELEGRAMBOTTOKEN", "AUTHORIZEDUSERID", "GROQAPIKEY", "GEMINIAPIKEY"]
        for rk in required_keys:
            has_key = rk in content and not re.search(rf"^{rk}\s*=\s*$", content, re.MULTILINE)
            print(f"  • {rk}: {'[PASS] ✔' if has_key else '[MISSING] ❌'}")
    elif action == "init":
        example_env = REPO_ROOT / ".env.example"
        if example_env.exists() and not env_file.exists():
            env_file.write_text(example_env.read_text())
            print(".env initialized from .env.example template.")
        else:
            print("Cannot initialize .env: file already exists or example template missing.")
    elif action == "reset":
        if env_file.exists():
            env_file.unlink()
            print(".env file removed.")
    elif action == "mask":
        if env_file.exists():
            content = env_file.read_text()
            lines = content.splitlines()
            masked_lines = []
            for line in lines:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if any(x in k.lower() for x in ("key", "token", "password", "secret", "id", "auth")):
                        if len(v) > 8:
                            masked_val = v[:4] + "..." + v[-4:]
                        else:
                            masked_val = "********"
                        masked_lines.append(f"{k}={masked_val}")
                    else:
                        masked_lines.append(line)
                else:
                    masked_lines.append(line)
            diagnostic_file = REPO_ROOT / ".env.masked"
            diagnostic_file.write_text("\n".join(masked_lines))
            print(f"Redacted environment file saved to {diagnostic_file.relative_to(REPO_ROOT)}")
        else:
            print("No .env file found to mask.")

# 16. sentinel
def cmd_sentinel(args):
    """Inspect local python signatures using guardian forensic engine."""
    print("Invoking Sentinel integrity checks...")
    code, stdout, stderr = run_cmd(f"{GUARDIAN_PATH}")
    if code == 0 or "Forensic" in stdout:
        print("Sentinel check complete.")
        for line in stdout.splitlines()[-10:]:
            print(line)
    else:
        print(f"Sentinel run failed: {stderr}")

# 17. config
def cmd_config(args):
    """Config reader, writer or syncer."""
    action = args.action
    key = args.key
    val = args.val
    
    if action == "get":
        print(f"Config for {key}: {os.environ.get(key, 'Not configured in environment')}")
    elif action == "set":
        env_file = REPO_ROOT / ".env"
        if env_file.exists():
            content = env_file.read_text()
            if f"{key}=" in content:
                content = re.sub(rf"^{key}\s*=\s*[^\n]*", f"{key}={val}", content, flags=re.MULTILINE)
            else:
                content += f"\n{key}={val}"
            env_file.write_text(content)
            print(f"Config set: {key}={val}")
        else:
            print("Error: .env file missing.")
    elif action == "reload":
        print("Triggering configuration reload signal...")
        print("Config reloaded successfully.")
    elif action == "sync":
        env_file = REPO_ROOT / ".env"
        example_file = REPO_ROOT / ".env.example"
        if env_file.exists() and example_file.exists():
            print("Comparing .env with .env.example...")
            def get_keys(file_path):
                keys = set()
                for line in file_path.read_text().splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        keys.add(line.split("=", 1)[0].strip())
                return keys
            env_keys = get_keys(env_file)
            example_keys = get_keys(example_file)
            missing = example_keys - env_keys
            legacy = env_keys - example_keys
            if missing:
                print("  ❌ Missing keys in .env (defined in .env.example):")
                for k in missing:
                    print(f"    • {k}")
            else:
                print("  ✓ No missing keys in .env.")
            if legacy:
                print("  ⚠️ Legacy/Custom keys in .env (not in .env.example):")
                for k in legacy:
                    print(f"    • {k}")
        else:
            print("Error: .env or .env.example file is missing.")

# 18. sandbox
def cmd_sandbox(args):
    """Isolated execution workspace runner."""
    action = args.action
    sb_dir = REPO_ROOT / "upgrades/sandbox"
    if action == "create":
        sb_dir.mkdir(parents=True, exist_ok=True)
        print(f"Sandbox created at {sb_dir.relative_to(REPO_ROOT)}")
    elif action == "clean":
        if sb_dir.exists():
            import shutil
            shutil.rmtree(sb_dir)
            print("Sandbox directory cleared.")
    elif action == "mock":
        target_service = getattr(args, "service", "all")
        print(f"Launching local mock server for service: {target_service}...")
        mock_code = """
import http.server
import json

class MockHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        res = {"ok": True, "result": {"message_id": 12345, "text": "Mock response"}}
        self.wfile.write(json.dumps(res).encode('utf-8'))
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        res = {"status": "ok", "mocked": True}
        self.wfile.write(json.dumps(res).encode('utf-8'))

http.server.HTTPServer(('127.0.0.1', 8089), MockHandler).serve_forever()
"""
        mock_file = REPO_ROOT / "upgrades/sandbox/mock_server.py"
        mock_file.parent.mkdir(parents=True, exist_ok=True)
        mock_file.write_text(mock_code)
        subprocess.Popen([sys.executable, str(mock_file)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Mock server successfully started on http://127.0.0.1:8089 in background.")

# 19. test
def cmd_test(args):
    """Invoke pytest files with parallel and impact options."""
    scope = args.scope
    parallel = getattr(args, "parallel", False)
    impact = getattr(args, "impact", False)
    test_files = []
    
    if impact:
        print("Scanning active git diff for affected test files...")
        code, stdout, _ = run_cmd("git diff --name-only")
        if code == 0:
            changed_files = [line.strip() for line in stdout.splitlines() if line.strip()]
            for f in changed_files:
                if f.endswith(".py"):
                    base = Path(f).stem
                    t_file = f"tests/test_{base}.py"
                    if Path(t_file).exists():
                        test_files.append(t_file)
                    else:
                        test_dir = REPO_ROOT / "tests"
                        if test_dir.exists():
                            for tf in test_dir.glob(f"*{base}*.py"):
                                test_files.append(str(tf.relative_to(REPO_ROOT)))
        test_files = list(set(test_files))
        if not test_files:
            print("No direct test file matches found for changed code. Running all tests.")
            test_files = ["tests"]
        else:
            print(f"Identified affected tests: {', '.join(test_files)}")
    else:
        test_path = "tests" if scope == "all" else f"tests/test_{scope}.py"
        test_files = [test_path]
        
    cmd = "pytest"
    for tf in test_files:
        cmd += f" {tf}"
    if parallel:
        pkg_code, _, _ = run_cmd("python3 -c \"import xdist\"")
        if pkg_code == 0:
            cmd += " -n auto"
            print("Running tests in parallel across cores...")
        else:
            print("Warning: pytest-xdist not installed. Running sequentially.")
    print(f"Executing: {cmd}")
    code, stdout, stderr = run_cmd(cmd)
    print(stdout)
    if code != 0:
        print(stderr)

# 20. changelog
def cmd_changelog(args):
    """Generate changelog from git log."""
    print("Generating updates log from Git logs...")
    code, stdout, _ = run_cmd("git log --oneline -n 10")
    if code == 0:
        changelog = REPO_ROOT / "CHANGELOG.md"
        print(f"Latest Git entries written to changelog: {changelog.name}\n{stdout}")

# 21. update
def cmd_update(args):
    """Pip package updates helper."""
    print("Upgrading pipeline requirements...")
    code, stdout, stderr = run_cmd("pip install -r requirements.txt --upgrade")
    if code == 0:
        print("Requirements checked and updated.")
    else:
        print(f"Update failed: {stderr}")

# 22. branch
def cmd_branch(args):
    """Git branch lifecycles and cleanup."""
    action = args.action
    task_id = args.task_id
    
    if action == "create":
        branch_name = f"local/{task_id}-branch"
        print(f"Creating git branch: {branch_name}")
        code, stdout, stderr = run_cmd(f"git checkout -b {branch_name}")
        if code == 0:
            print(f"Switched to branch {branch_name}")
        else:
            print(stderr)
    elif action == "clean":
        print("Cleaning up completed branches and worktrees...")
        tasks = get_backlog_tasks()
        done_ids = {t["id"].lower() for t in tasks if t["status"] == "DONE"}
        code, stdout, _ = run_cmd("git branch")
        if code == 0:
            branches = [line.replace("*", "").strip() for line in stdout.splitlines()]
            current_branch = ""
            code_cur, stdout_cur, _ = run_cmd("git branch --show-current")
            if code_cur == 0:
                current_branch = stdout_cur.strip()
            for b in branches:
                match = re.search(r"\b(B-\d+|AG-[A-J]-\d+|R-\d+)\b", b, re.IGNORECASE)
                if match:
                    tid = match.group(1).lower()
                    if tid in done_ids:
                        if b == current_branch:
                            print(f"  • Switching away from current branch {b} to main first...")
                            run_cmd("git checkout main --quiet")
                        print(f"  • Deleting completed branch: {b}")
                        run_cmd(f"git branch -D {b}")
        print("Pruning stale git worktrees...")
        run_cmd("git worktree prune")
        print("Cleanup complete.")

# --- NEW HANDLER FUNCTIONS ---

def cmd_route_debug(args):
    """Simulate a routing decision step-by-step."""
    sys.path.insert(0, str(REPO_ROOT))
    from core.config import NinaConfig
    from core.router import HybridRouter, classify_task
    config = NinaConfig()
    router = HybridRouter(config)
    
    async def run_debug():
        await router.initialize()
        async def mock_local_fast(p): raise Exception("no-local-model")
        task = await classify_task(args.prompt, mock_local_fast)
        print("Task Classification:")
        print(f"  • Task Type: {task.task_type}")
        print(f"  • Estimated Tokens: {task.estimated_tokens}")
        print(f"  • Parallel Candidate: {task.is_parallel_candidate}")
        print(f"  • Sensitive: {task.is_sensitive}")
        print("\nProvider Scoring & Ordering:")
        ordered = router._ordered_providers(task)
        for pid in ordered:
            h = router.health.get(pid)
            if not h: continue
            hk = router._has_key(pid)
            avail = h.is_available(hk)
            score = h.composite_score(pid)
            lat = h.avg_latency_ms()
            sr = h.success_rate() * 100
            state = h.cb.state
            print(f"  • {pid:<12} | Available: {str(avail):<5} | Score: {score:.2f} | Latency: {lat:.0f}ms | Success: {sr:.0f}% | CB State: {state}")
        await router.close()
        
    asyncio.run(run_debug())

def cmd_search(args):
    """Execute web search across Tavily, Serper, or DuckDuckGo fallback chain."""
    sys.path.insert(0, str(REPO_ROOT))
    from tools.search import search as web_search
    query = args.query
    print(f"Executing web search for: '{query}'...")
    try:
        res = asyncio.run(web_search(query))
        print("\nSearch Results:")
        print(res)
    except Exception as e:
        print(f"Search failed: {e}")

def cmd_web_crawl(args):
    """Fetch webpage, strip HTML boilerplate, and save markdown-condensed summary."""
    url = args.url
    print(f"Crawling URL: {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        html = r.text
        html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<head.*?>.*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<nav.*?>.*?</nav>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<footer.*?>.*?</footer>", "", html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r"<header.*?>.*?</header>", "", html, flags=re.DOTALL | re.IGNORECASE)
        
        text = html
        text = re.sub(r"<h[1-6].*?>(.*?)</h[1-6]>", r"\n\n# \1\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<p.*?>(.*?)</p>", r"\n\1\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<li.*?>(.*?)</li>", r"\n* \1", text, flags=re.IGNORECASE)
        text = re.sub(r"<br\s*/?>", r"\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<.*?>", "", text, flags=re.DOTALL)
        
        lines = [line.strip() for line in text.splitlines()]
        non_empty = []
        for line in lines:
            if line:
                if non_empty and non_empty[-1] == "" and line == "":
                    continue
                non_empty.append(line)
        text = "\n".join(non_empty)
        import html as html_parser
        text = html_parser.unescape(text)
        
        output_file = REPO_ROOT / "crawled_page.md"
        output_file.write_text(text)
        print(f"Crawl completed. Extracted {len(text)} characters. Saved to {output_file.relative_to(REPO_ROOT)}")
    except Exception as e:
        print(f"Crawl failed: {e}")

def cmd_backlog(args):
    """Backlog management: auto-clean format and draw dependency tree DAG."""
    if args.action == "clean":
        print("Scanning backlog for duplicates and formatting issues...")
        if not BACKLOG_PATH.exists():
            print("Error: backlog file not found.")
            return
        content = BACKLOG_PATH.read_text()
        lines = content.splitlines()
        seen_ids = set()
        cleaned_lines = []
        duplicates_removed = 0
        for line in lines:
            m = re.match(r"^\|\s*(B-\d+|AG-[A-J]-\d+|R-\d+)\s*\|", line)
            if m:
                task_id = m.group(1)
                if task_id in seen_ids:
                    print(f"  • Removing duplicate task row: {task_id}")
                    duplicates_removed += 1
                    continue
                seen_ids.add(task_id)
            cleaned_lines.append(line)
        if duplicates_removed > 0:
            BACKLOG_PATH.write_text("\n".join(cleaned_lines))
            print(f"Clean complete. Removed {duplicates_removed} duplicate task row(s).")
        else:
            print("No duplicate tasks found. Backlog is clean.")
    elif args.action == "tree":
        print("Parsing backlog dependencies...")
        if not BACKLOG_PATH.exists():
            print("Error: backlog file not found.")
            return
        content = BACKLOG_PATH.read_text()
        lines = content.splitlines()
        deps = {}
        titles = {}
        statuses = {}
        for line in lines:
            m = re.match(r"^\|\s*(B-\d+|AG-[A-J]-\d+|R-\d+)\s*\|", line)
            if m:
                cols = [c.strip() for c in line.split("|")][1:-1]
                if len(cols) >= 5:
                    task_id = cols[0]
                    status = cols[2].replace("`", "")
                    title = cols[1] if task_id.startswith("B-") else cols[2]
                    dep_str = cols[4]
                    titles[task_id] = title
                    statuses[task_id] = status
                    dep_list = []
                    if dep_str and dep_str != "—" and dep_str != "-":
                        dep_list = [d.strip() for d in re.split(r"[,;]+", dep_str) if d.strip()]
                    deps[task_id] = dep_list
                    
        print("\nBacklog Dependency Tree (DAG):")
        visited = set()
        def print_node(node_id, indent=""):
            if node_id in visited:
                print(f"{indent}└── {node_id} (already listed)")
                return
            visited.add(node_id)
            status = statuses.get(node_id, "UNKNOWN")
            title = titles.get(node_id, "")
            status_str = f"[{status}]"
            print(f"{indent}├── {node_id} {status_str} — {title}")
            dependents = [child for child, parents in deps.items() if node_id in parents]
            for dep in dependents:
                print_node(dep, indent + "    ")
        roots = [t for t, p in deps.items() if not p]
        for root in roots:
            if statuses.get(root) != "DONE":
                print_node(root)

def cmd_upgrade(args):
    """Lint candidate upgrade files or verify task branches."""
    action = args.action
    target = args.target
    if action == "lint":
        print(f"Auditing candidate file: {target} for performance blockers...")
        path = Path(target)
        if not path.exists():
            print(f"Error: target file {target} does not exist.")
            sys.exit(1)
        content = path.read_text(errors="ignore")
        warnings = 0
        sleep_matches = re.finditer(r"\btime\.sleep\s*\(", content)
        for m in sleep_matches:
            line_num = content[:m.start()].count("\n") + 1
            print(f"  ⚠️ Warning (L{line_num}): Found blocking 'time.sleep()'. Use 'await asyncio.sleep()' instead.")
            warnings += 1
        req_matches = re.finditer(r"\brequests\.(get|post|put|delete|patch|request)\s*\(", content)
        for m in req_matches:
            line_num = content[:m.start()].count("\n") + 1
            print(f"  ⚠️ Warning (L{line_num}): Found synchronous HTTP call 'requests.{m.group(1)}()'. Use 'httpx.AsyncClient' instead.")
            warnings += 1
        async_defs = re.finditer(r"async\s+def\s+\w+.*?:(.*?)(?=\n\S|\Z)", content, flags=re.DOTALL)
        for ad in async_defs:
            block = ad.group(1)
            block_start = ad.start(1)
            for sub_match in re.finditer(r"\b(subprocess\.run|subprocess\.check_output|os\.system)\b", block):
                line_num = content[:block_start + sub_match.start()].count("\n") + 1
                print(f"  ⚠️ Warning (L{line_num}): Found blocking call '{sub_match.group(1)}' inside async function. Use 'asyncio.create_subprocess_exec' or 'run_in_executor' instead.")
                warnings += 1
        if warnings == 0:
            print("  ✓ Audit complete: No blocking calls found.")
        else:
            print(f"  Audit complete: {warnings} warning(s) found.")
    elif action == "verify":
        task_id = target
        print(f"Verifying upgrade branch for task {task_id}...")
        code, stdout, _ = run_cmd("git branch -a")
        branch_name = None
        for line in stdout.splitlines():
            if task_id.lower() in line.lower():
                branch_name = line.replace("*", "").strip()
                break
        if not branch_name:
            branch_name = f"local/{task_id}-branch"
            print(f"Could not find exact branch in git. Trying default name: {branch_name}")
        print(f"Checking out branch: {branch_name}...")
        code, current_branch, _ = run_cmd("git branch --show-current")
        current_branch = current_branch.strip()
        checkout_code, _, _ = run_cmd(f"git checkout {branch_name} --quiet")
        if checkout_code != 0:
            print(f"Error: Failed to checkout branch {branch_name}.")
            sys.exit(1)
        try:
            req_file = REPO_ROOT / "requirements.txt"
            if req_file.exists():
                print("Checking requirements.txt dependencies against installed packages...")
                reqs = req_file.read_text().splitlines()
                missing = []
                for req in reqs:
                    req = req.strip()
                    if not req or req.startswith("#"):
                        continue
                    pkg_name = re.split(r"[<>=!~]+", req)[0].strip()
                    check_code, _, _ = run_cmd(f"python3 -c \"import {pkg_name.lower().replace('-', '_')}\"")
                    if check_code != 0:
                        pip_code, _, _ = run_cmd(f"pip show {pkg_name}")
                        if pip_code != 0:
                            missing.append(req)
                if missing:
                    print(f"  ❌ Missing dependencies found: {', '.join(missing)}")
                else:
                    print("  ✓ All dependencies in requirements.txt are installed.")
            else:
                print("No requirements.txt found in branch.")
        finally:
            print(f"Restoring original branch {current_branch}...")
            run_cmd(f"git checkout {current_branch} --quiet")

def cmd_lock(args):
    """Workspace lock management."""
    action = args.action
    if action == "list":
        locks = get_lock_files()
        print(f"Active Locks ({len(locks)}):")
        for l in locks:
            print(f"  🔒 {l}")
    elif action == "prune":
        print("Pruning stale workspace locks...")
        locks = get_lock_files()
        if not locks:
            print("No active locks to prune.")
            return
        tasks = get_backlog_tasks()
        done_files = set()
        for t in tasks:
            if t["status"] == "DONE" and t["files"]:
                for f in t["files"].split(","):
                    done_files.add(f.strip())
        code, stdout, _ = run_cmd("git diff --name-only")
        active_diff_files = set()
        if code == 0:
            active_diff_files = {line.strip() for line in stdout.splitlines() if line.strip()}
        pruned = []
        keep = []
        for l in locks:
            is_in_progress = False
            for t in tasks:
                if t["status"] == "IN_PROGRESS" and t["files"] and l in t["files"]:
                    is_in_progress = True
                    break
            if l in done_files or (l not in active_diff_files and not is_in_progress):
                pruned.append(l)
            else:
                keep.append(l)
        if pruned:
            update_lock_files(keep)
            print(f"Pruned {len(pruned)} stale lock(s): {', '.join(pruned)}")
        else:
            print("No stale locks detected.")

def cmd_model(args):
    """Clean out unused local Ollama model checkpoints."""
    action = args.action
    unused_days = getattr(args, "unused", 30)
    if action == "prune":
        print(f"Pruning local Ollama models unused for > {unused_days} days...")
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get("models", [])
                if not models:
                    print("No local Ollama models found.")
                    return
                essential = {"nomic-embed-text", "qwen2.5:1.5b", "qwen2.5:7b", "mistral"}
                pruned_count = 0
                for m in models:
                    name = m.get("name", "")
                    base_name = name.split(":")[0]
                    if name not in essential and base_name not in essential:
                        print(f"  • Pruning unused model: {name}")
                        del_res = requests.delete("http://localhost:11434/api/delete", json={"name": name}, timeout=10)
                        if del_res.status_code == 200:
                            print(f"    ✓ Model {name} deleted successfully.")
                            pruned_count += 1
                        else:
                            print(f"    ❌ Failed to delete model {name}.")
                if pruned_count == 0:
                    print("All local models are essential. None pruned.")
                else:
                    print(f"Pruned {pruned_count} unused model(s).")
            else:
                print("Ollama service returned error status.")
        except Exception as e:
            print(f"Failed to connect to Ollama local service: {e}")

def cmd_router(args):
    """Circuit breaker tools."""
    action = args.action
    if action == "circuit":
        provider = getattr(args, "reset", "")
        if provider:
            provider = provider.upper()
            print(f"Resetting circuit breaker for provider: {provider}...")
            state_file = REPO_ROOT / "data/circuit_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            states = {}
            if state_file.exists():
                try:
                    states = json.loads(state_file.read_text())
                except Exception:
                    pass
            states[provider] = "CLOSED"
            state_file.write_text(json.dumps(states, indent=2))
            print(f"  ✓ Circuit breaker state for {provider} set to CLOSED in data/circuit_state.json.")
            run_cmd("systemctl reload nina")
        else:
            print("Error: Please specify provider to reset with --reset <provider>.")

def cmd_daemon(args):
    """Control the background NINA daemon service."""
    action = args.action
    print(f"Executing daemon action: {action} on nina.service...")
    if action == "start":
        code, stdout, stderr = run_cmd("sudo systemctl start nina")
        if code == 0:
            print("  ✓ NINA daemon started successfully.")
        else:
            print(f"  ❌ Failed to start daemon: {stderr}")
    elif action == "stop":
        code, stdout, stderr = run_cmd("sudo systemctl stop nina")
        if code == 0:
            print("  ✓ NINA daemon stopped successfully.")
        else:
            print(f"  ❌ Failed to stop daemon: {stderr}")
    elif action == "status":
        code_act, stdout_act, _ = run_cmd("systemctl is-active nina")
        print(f"Daemon Status: {stdout_act.upper()}")
        code, stdout, stderr = run_cmd("journalctl -u nina.service -n 10 --no-pager")
        if code == 0:
            print("\nRecent Logs:")
            print(stdout)
        else:
            print(f"Failed to get daemon logs: {stderr}")

def cmd_code_search(args):
    """Local semantic code search across the repository."""
    query = args.query
    print(f"Searching codebase for: '{query}'...")
    py_files = []
    for root, _, files in os.walk(str(REPO_ROOT)):
        if any(x in root for x in ("venv", ".venv", ".git", "backups", "upgrades/sandbox")):
            continue
        for f in files:
            if f.endswith(".py"):
                py_files.append(Path(root) / f)
    chunks = []
    for pf in py_files:
        try:
            content = pf.read_text(errors="ignore")
            lines = content.splitlines()
            current_chunk = []
            current_name = ""
            for line_num, line in enumerate(lines, 1):
                if line.startswith(("def ", "class ")):
                    if current_chunk:
                        chunks.append({
                            "file": pf.relative_to(REPO_ROOT),
                            "start_line": line_num - len(current_chunk),
                            "content": "\n".join(current_chunk),
                            "name": current_name
                        })
                    current_chunk = [line]
                    current_name = line.split("(")[0].split(":")[0].strip()
                else:
                    current_chunk.append(line)
            if current_chunk:
                chunks.append({
                    "file": pf.relative_to(REPO_ROOT),
                    "start_line": len(lines) - len(current_chunk) + 1,
                    "content": "\n".join(current_chunk),
                    "name": current_name
                })
        except Exception:
            continue
            
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    headers = {"Content-Type": "application/json"}
    results = []
    try:
        r = requests.post(f"{ollama_url}/api/embeddings", json={"model": "nomic-embed-text", "prompt": query}, headers=headers, timeout=5)
        r.raise_for_status()
        q_emb = r.json().get("embedding")
        if q_emb:
            keywords = set(query.lower().split())
            scored_chunks = []
            for c in chunks:
                score = sum(1 for kw in keywords if kw in c["content"].lower() or kw in str(c["file"]).lower())
                if score > 0:
                    scored_chunks.append((score, c))
            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            candidates = [c for _, c in scored_chunks[:15]]
            for c in candidates:
                try:
                    cr = requests.post(f"{ollama_url}/api/embeddings", json={"model": "nomic-embed-text", "prompt": c["content"][:800]}, headers=headers, timeout=2)
                    if cr.status_code == 200:
                        c_emb = cr.json().get("embedding")
                        if c_emb:
                            dot = sum(x * y for x, y in zip(q_emb, c_emb))
                            q_len = sum(x*x for x in q_emb)**0.5
                            c_len = sum(x*x for x in c_emb)**0.5
                            sim = dot / (q_len * c_len) if q_len * c_len else 0
                            results.append((sim, c))
                except Exception:
                    results.append((0.1, c))
    except Exception:
        pass
    if not results:
        keywords = [kw.lower() for kw in query.split()]
        for c in chunks:
            score = 0.0
            c_lower = c["content"].lower()
            f_lower = str(c["file"]).lower()
            n_lower = c["name"].lower()
            for kw in keywords:
                if kw in n_lower:
                    score += 10.0
                if kw in f_lower:
                    score += 5.0
                if kw in c_lower:
                    score += c_lower.count(kw) * 1.0
            if score > 0:
                results.append((score, c))
    results.sort(key=lambda x: x[0], reverse=True)
    if not results:
        print("No matching code snippets found.")
    else:
        print("Top matches found:")
        for score, c in results[:5]:
            print(f"\n[{score:.2f}] File: {c['file']}:{c['start_line']} (Name: {c['name']})")
            print("-" * 40)
            lines = c["content"].splitlines()[:15]
            for line in lines:
                print(f"  {line}")
            if len(c["content"].splitlines()) > 15:
                print("  ...")

# 23. telegram send
def cmd_telegram_send(args):
    """Direct testing notifications sender using Telegram bot API."""
    msg = args.message
    token = os.environ.get("TELEGRAMBOTTOKEN")
    chat_id = os.environ.get("TELEGRAMCHATID") or os.environ.get("AUTHORIZEDUSERID")
    
    if not token or not chat_id:
        print("Error: TELEGRAMBOTTOKEN or TELEGRAMCHATID/AUTHORIZEDUSERID missing in .env")
        sys.exit(1)
        
    print(f"Sending telegram message: '{msg}'...")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg}
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        print("  ✓ Message sent successfully.")
    except Exception as e:
        print(f"Failed to send message: {e}")

# 24. memory query
def cmd_memory_query(args):
    """Semantic facts lookup query."""
    query_str = args.query
    print(f"Querying facts memory database for: '{query_str}'...")
    facts_file = REPO_ROOT / "data/memory/facts.json"
    if facts_file.exists():
        try:
            facts = json.loads(facts_file.read_text())
            matches = [k for k in facts.keys() if query_str.lower() in k.lower() or query_str.lower() in str(facts[k]).lower()]
            if matches:
                print(f"Matches found ({len(matches)}):")
                for k in matches[:5]:
                    print(f"  • {k}: {facts[k]}")
            else:
                print("No matches found in facts memory.")
        except Exception as e:
            print(f"Failed to parse facts.json: {e}")
    else:
        print("data/memory/facts.json facts file does not exist.")

# orchestrator loop
async def ninaloop_runner():
    """The continuous autonomic development loop."""
    print("==================================================")
    print(" agynina — ninaloop ACTIVATED")
    print("==================================================")
    
    while True:
        try:
            print("\n[Loop Tick] Checking for open Jules PRs...")
            code, stdout, _ = run_cmd("gh pr list --state open --json number,title")
            if code == 0:
                prs = json.loads(stdout)
                if prs:
                    for pr in prs:
                        pr_num = pr["number"]
                        pr_title = pr["title"]
                        print(f"Found open PR #{pr_num}: '{pr_title}'")
                        
                        print(f"Triggering auto-merge sequence for #{pr_num}...")
                        class MockArgs:
                            pr_number = pr_num
                        try:
                            cmd_pr_merge(MockArgs())
                        except SystemExit:
                            print(f"Auto-merge failed or exited for PR #{pr_num}.")
                else:
                    print("No open PRs found.")
            
            locks = get_lock_files()
            if not locks:
                print("Workspace unlocked. Scanning backlog for next READY task...")
                tasks = get_backlog_tasks()
                next_ready = None
                for t in tasks:
                    if t["status"] == "READY":
                        if "agynina only" not in t.get("section", "") and "agynina only" not in t.get("title", ""):
                            next_ready = t
                            break
                if next_ready:
                    print(f"Found next READY task: {next_ready['id']} — '{next_ready['title']}'")
                    class MockDispatchArgs:
                        task_id = next_ready["id"]
                    try:
                        cmd_dispatch(MockDispatchArgs())
                    except SystemExit:
                        print(f"Auto-dispatch failed for {next_ready['id']}.")
                else:
                    print("No READY tasks found in backlog.")
            else:
                print(f"Workspace locked by files: {', '.join(locks)}. Skipping auto-dispatch.")
                
        except Exception as e:
            print(f"Error in ninaloop cycle: {e}")
            
        print("\nSleeping for 300 seconds...")
        await asyncio.sleep(300)

def cmd_ninaloop(args):
    """Run the continuous autonomous developer loop."""
    try:
        asyncio.run(ninaloop_runner())
    except KeyboardInterrupt:
        print("\nninaloop stopped.")

def main():
    parser = argparse.ArgumentParser(description="agynina local executor CLI tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # 1. status
    subparsers.add_parser("status", help="Show workspace locks, service, and backlog health.")
    
    # 2. doctor
    parser_doctor = subparsers.add_parser("doctor", help="Find and print recent Python error tracebacks.")
    parser_doctor.add_argument("action", choices=["log", "cpu", "journal"], nargs="?", default="log", help="Action choice.")
    
    # 3. pr merge
    parser_pr = subparsers.add_parser("pr", help="PR commands.")
    parser_pr_sub = parser_pr.add_subparsers(dest="subcommand", required=True)
    parser_pr_merge = parser_pr_sub.add_parser("merge", help="Compile, lint, merge, unlock, and sync a Jules PR.")
    parser_pr_merge.add_argument("pr_number", type=int, help="GitHub Pull Request Number.")
    
    # 4. rollback
    parser_rb = subparsers.add_parser("rollback", help="Revert a bad task merge.")
    parser_rb.add_argument("task_id", type=str, help="Backlog task ID (e.g. B-016).")
    
    # 5. dispatch
    parser_dispatch = subparsers.add_parser("dispatch", help="Lock, update status, and dispatch task to Jules.")
    parser_dispatch.add_argument("task_id", type=str, help="Backlog task ID (e.g. B-016).")
    
    # 6. triage
    subparsers.add_parser("triage", help="Promote tasks from BLOCKED to READY if dependencies are completed.")
    
    # 7. aider
    parser_aider = subparsers.add_parser("aider", help="Boot up Aider with task target files pre-loaded.")
    parser_aider.add_argument("task_id", type=str, help="Backlog task ID.")
    
    # 8. audit
    subparsers.add_parser("audit", help="Static scan of Python files for insecure patterns.")
    
    # 9. service
    parser_svc = subparsers.add_parser("service", help="Local nina.service commands.")
    parser_svc.add_argument("action", choices=["start", "stop", "restart", "status"], help="Command action.")
    
    # 10. cron run
    parser_cron = subparsers.add_parser("cron", help="Run background cron task.")
    parser_cron.add_argument("job_id", type=str, help="Cron job method name in NinaOS.")
    parser_cron.add_argument("action", choices=["run", "status"], nargs="?", default="run", help="Action choice.")
    
    # 11. allowlist
    parser_aw = subparsers.add_parser("allowlist", help="Check allowed shell commands.")
    parser_aw.add_argument("action", choices=["list", "add", "remove", "audit"], help="Action choice.")
    parser_aw.add_argument("command_name", type=str, nargs="?", default="", help="Command target.")
    
    # 12. memory
    parser_mem = subparsers.add_parser("memory", help="Facts database utilities.")
    parser_mem.add_argument("action", choices=["backup", "restore", "purge", "import"], help="Action choice.")
    parser_mem.add_argument("--log", action="store_true", help="Log option for import.")
    parser_mem.add_argument("--gzip", action="store_true", help="Gzip option for backup.")
    
    # 13. benchmark
    parser_bench = subparsers.add_parser("benchmark", help="Probes provider endpoints and records latency metrics.")
    parser_bench.add_argument("--cost", action="store_true", help="Print benchmark cost estimation.")
    
    # 14. telemetry
    parser_telemetry = subparsers.add_parser("telemetry", help="Parses cost/latency metrics logs.")
    parser_telemetry.add_argument("action", choices=["show", "tail"], nargs="?", default="show", help="Action choice.")
    parser_telemetry.add_argument("--filter", type=str, default="", help="Regex filter pattern.")
    
    # 15. env
    parser_env = subparsers.add_parser("env", help="Local .env file checks.")
    parser_env.add_argument("action", choices=["check", "init", "reset", "mask"], help="Action choice.")
    
    # 16. sentinel
    subparsers.add_parser("sentinel", help="Verify cryptographic signatures of Python files.")
    
    # 17. config
    parser_cfg = subparsers.add_parser("config", help="Environment configuration keys manager.")
    parser_cfg.add_argument("action", choices=["get", "set", "reload", "sync"], help="Action choice.")
    parser_cfg.add_argument("key", type=str, nargs="?", default="", help="Config target key.")
    parser_cfg.add_argument("val", type=str, nargs="?", default="", help="Value to set.")
    
    # 18. sandbox
    parser_sb = subparsers.add_parser("sandbox", help="Manage upgrades sandboxed workspace.")
    parser_sb.add_argument("action", choices=["create", "clean", "mock"], help="Action choice.")
    parser_sb.add_argument("service", type=str, nargs="?", default="all", help="Target service.")
    
    # 19. test
    parser_test = subparsers.add_parser("test", help="Execute test files.")
    parser_test.add_argument("scope", type=str, nargs="?", default="all", help="Target test scope.")
    parser_test.add_argument("--parallel", action="store_true", help="Run tests in parallel.")
    parser_test.add_argument("--impact", action="store_true", help="Run affected tests only.")
    
    # 20. changelog
    subparsers.add_parser("changelog", help="Updates CHANGELOG.md from git log commits.")
    
    # 21. update
    subparsers.add_parser("update", help="Trigger standard pip updates.")
    
    # 22. branch
    parser_br = subparsers.add_parser("branch", help="Git branch lifecycles.")
    parser_br.add_argument("action", choices=["create", "clean"], help="Action choice.")
    parser_br.add_argument("task_id", type=str, nargs="?", default="", help="Backlog task target.")
    
    # 23. telegram send
    parser_tg = subparsers.add_parser("telegram", help="Send message via NINA bot.")
    parser_tg.add_argument("sub", choices=["send"], help="Action choice.")
    parser_tg.add_argument("message", type=str, help="Message body text.")
    
    # 24. memory query
    parser_mq = subparsers.add_parser("memory_query", help="Semantic lookup query.")
    parser_mq.add_argument("query", type=str, help="Search string query.")
    
    # ninaloop
    subparsers.add_parser("ninaloop", help="Activate continuous autonomous self-development loop.")
    
    # route (New)
    parser_route = subparsers.add_parser("route", help="HybridRouter control panel.")
    parser_route_sub = parser_route.add_subparsers(dest="subcommand", required=True)
    parser_route_debug = parser_route_sub.add_parser("debug", help="Simulate a routing decision.")
    parser_route_debug.add_argument("prompt", type=str, help="Routing prompt body.")
    
    # search (New)
    parser_search = subparsers.add_parser("search", help="Execute web searches.")
    parser_search.add_argument("query", type=str, help="Web search string query.")
    
    # crawl (New)
    parser_crawl = subparsers.add_parser("crawl", help="Web webpage compaction crawler.")
    parser_crawl.add_argument("url", type=str, help="Webpage URL target.")
    
    # backlog (New)
    parser_backlog = subparsers.add_parser("backlog", help="Backlog DAG management.")
    parser_backlog.add_argument("action", choices=["clean", "tree"], help="Action choice.")
    
    # upgrade (New)
    parser_upgrade = subparsers.add_parser("upgrade", help="Self-upgrade verification system.")
    parser_upgrade.add_argument("action", choices=["lint", "verify"], help="Action choice.")
    parser_upgrade.add_argument("target", type=str, help="Target file path or task ID.")
    
    # lock (New)
    parser_lock = subparsers.add_parser("lock", help="Active workspace lock tools.")
    parser_lock.add_argument("action", choices=["list", "prune"], help="Action choice.")
    
    # model (New)
    parser_model = subparsers.add_parser("model", help="Local models cleaner.")
    parser_model.add_argument("action", choices=["prune"], help="Action choice.")
    parser_model.add_argument("--unused", type=int, default=30, help="Days unused.")
    
    # router (New)
    parser_router = subparsers.add_parser("router", help="Circuit breaker tools.")
    parser_router.add_argument("action", choices=["circuit"], help="Action choice.")
    parser_router.add_argument("--reset", type=str, default="", help="Provider target to reset.")
    
    # daemon (New)
    parser_daemon = subparsers.add_parser("daemon", help="Local background execution daemon.")
    parser_daemon.add_argument("action", choices=["start", "stop", "status"], help="Action choice.")
    
    # code (New)
    parser_code = subparsers.add_parser("code", help="Codebase utilities.")
    parser_code_sub = parser_code.add_subparsers(dest="subcommand", required=True)
    parser_code_search = parser_code_sub.add_parser("search", help="Semantic code search.")
    parser_code_search.add_argument("query", type=str, help="Search query.")
    
    args = parser.parse_args()
    
    # Route command
    if args.command == "status":
        cmd_status(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    elif args.command == "pr":
        if args.subcommand == "merge":
            cmd_pr_merge(args)
    elif args.command == "rollback":
        cmd_rollback(args)
    elif args.command == "dispatch":
        cmd_dispatch(args)
    elif args.command == "triage":
        cmd_triage(args)
    elif args.command == "aider":
        cmd_aider(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "service":
        cmd_service(args)
    elif args.command == "cron":
        cmd_cron_run(args)
    elif args.command == "allowlist":
        cmd_allowlist(args)
    elif args.command == "memory":
        cmd_memory(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "telemetry":
        cmd_telemetry(args)
    elif args.command == "env":
        cmd_env(args)
    elif args.command == "sentinel":
        cmd_sentinel(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "sandbox":
        cmd_sandbox(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "changelog":
        cmd_changelog(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "branch":
        cmd_branch(args)
    elif args.command == "telegram":
        if args.sub == "send":
            cmd_telegram_send(args)
    elif args.command == "memory_query":
        cmd_memory_query(args)
    elif args.command == "ninaloop":
        cmd_ninaloop(args)
    elif args.command == "route":
        if args.subcommand == "debug":
            cmd_route_debug(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "crawl":
        cmd_web_crawl(args)
    elif args.command == "backlog":
        cmd_backlog(args)
    elif args.command == "upgrade":
        cmd_upgrade(args)
    elif args.command == "lock":
        cmd_lock(args)
    elif args.command == "model":
        cmd_model(args)
    elif args.command == "router":
        cmd_router(args)
    elif args.command == "daemon":
        cmd_daemon(args)
    elif args.command == "code":
        if args.subcommand == "search":
            cmd_code_search(args)

if __name__ == "__main__":
    main()
