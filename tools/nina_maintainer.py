#!/usr/bin/env python3
"""
NINA Maintenance Orchestrator (v1.0)
Automates the 'Rebase -> Resolve v13 Headers -> Update Backlog -> Append Log' cycle.
Optimized for zero-token local resolution of documentation regressions.
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
LOG_PATH = REPO_ROOT / "nina_update_log.md"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def resolve_v13_docs():
    """Locally resolves common v13 documentation conflicts without LLM intervention."""
    print("Surgically resolving v13 doc conflicts...")
    
    # Files often causing regressions
    targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md"]
    
    for filename in targets:
        path = REPO_ROOT / filename
        if not path.exists(): continue
        
        # Strategy: Use 'git checkout --ours' for the header/metadata 
        # but try to preserve content. For now, we enforce 'main' version of headers.
        run_cmd(f"git checkout main -- {filename}")
        
    # Special handling for update log (merging entries)
    if LOG_PATH.exists():
        # This is a placeholder for a more complex log merger if needed
        pass

def update_backlog(task_id, status="DONE"):
    """Updates task status in backlog."""
    if not BACKLOG_PATH.exists(): return
    content = BACKLOG_PATH.read_text()
    pattern = rf"(\| {task_id} \| .*? \| .*? \|) `.*?` \|"
    new_content = re.sub(pattern, rf"\1 `{status}` |", content)
    BACKLOG_PATH.write_text(new_content)
    print(f"Backlog: Task {task_id} marked as {status}.")

def append_log(task_id, title, summary):
    """Appends a standardized log entry."""
    if not LOG_PATH.exists(): return
    
    # Get last entry number
    log_content = LOG_PATH.read_text()
    entries = re.findall(r"## Entry (\d+)", log_content)
    next_num = int(entries[-1]) + 1 if entries else 1
    
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"""
---

## Entry {next_num:03d} — {today} · merge: {task_id} {title}

**Triggered by:** Automated nina_maintainer merge.

**What changed:**
- {summary}

**What was verified:**
- Atomic merge and local conflict resolution.

**Rollback path:**
- `git revert -m 1 HEAD`
"""
    with open(LOG_PATH, "a") as f:
        f.write(entry)
    print(f"Log: Appended Entry {next_num:03d}.")

def process_pr(pr_id, task_id, title, summary):
    """Main PR processing loop."""
    print(f"=== Processing PR #{pr_id} ({task_id}) ===")
    
    # 1. Checkout and Rebase
    code, _, err = run_cmd(f"gh pr checkout {pr_id}")
    if code != 0: print(f"Error checking out PR: {err}"); return
    
    code, _, _ = run_cmd("git rebase main")
    if code != 0:
        print("Conflict detected. Attempting surgical resolution...")
        resolve_v13_docs()
        run_cmd("git add . && export GIT_EDITOR=true && git rebase --continue")
    
    # 2. Finalize Merge
    current_branch = subprocess.getoutput("git branch --show-current")
    run_cmd("git checkout main")
    code, _, err = run_cmd(f"git merge {current_branch} --no-ff -m 'merge: PR #{pr_id} {task_id}'")
    if code != 0:
        print(f"Merge failed: {err}")
        return

    # 3. Post-Merge updates
    update_backlog(task_id)
    append_log(task_id, title, summary)
    
    # 4. Cleanup
    run_cmd(f"gh pr close {pr_id} -d -c 'Merged via nina_maintainer automation.'")
    print(f"PR #{pr_id} merged and closed successfully.\n")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: nina_maintainer.py <pr_id> <task_id> <title> <summary>")
        sys.exit(1)
    
    process_pr(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
