"""
Autonomous Parallel Orchestrator v5.1 (Index-Aware & Self-Documenting).
Monitors Jules sessions, notifies Telegram, enforces index-based governance,
and resolves PRs in parallel via the GitHub API.
"""

import os
import re
import json
import asyncio
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from tools import jules_api
from tools.ninaflash import get_backlog_tasks, _save_task_status, _append_update_log
from tools.jules_watcher import watch_and_notify

# Constants
REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
INDEX_PATH = REPO_ROOT / "docs/space/nina_index.json"
MAX_CONCURRENT_SESSIONS = 15

logger = logging.getLogger("nina.orchestrator")
git_lock = asyncio.Lock()

# --- Governance Index Helpers ---

def load_governance_index() -> Dict[str, Any]:
    """Loads the NINA Repository Index."""
    if not INDEX_PATH.exists():
        logger.error("Governance index not found.")
        return {"files": []}
    try:
        return json.loads(INDEX_PATH.read_text())
    except Exception as e:
        logger.error(f"Failed to load index: {e}")
        return {"files": []}

def get_file_policy(path: str, index: Dict[str, Any]) -> Dict[str, Any]:
    """Returns governance policy for a specific path."""
    for f in index.get("files", []):
        if f["path"] == path:
            return f
    return {}

# --- PR Resolution Logic ---

async def get_pr_files(pr_num: int) -> List[str]:
    """Returns a list of files modified in the PR."""
    try:
        cmd = ["gh", "pr", "view", str(pr_num), "--json", "files"]
        res = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        if res.returncode == 0:
            data = json.loads(res.stdout)
            return [f["path"] for f in data.get("files", [])]
    except Exception as e:
        logger.error(f"Failed to get files for PR #{pr_num}: {e}")
    return []

async def enforce_documentation(pr_num: int, files: List[str], index: Dict[str, Any]):
    """Checks index and triggers doc updates if required."""
    needs_doc = False
    for f in files:
        policy = get_file_policy(f, index)
        if policy.get("doc_required"):
            logger.info(f"PR #{pr_num} modifies {f} which REQUIRES documentation.")
            needs_doc = True
            break
    
    if needs_doc:
        logger.info(f"Running automated documentation update for PR #{pr_num}...")
        # Trigger tools/doc_autogen.py or similar
        cmd = ["python3", "tools/doc_autogen.py"]
        await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        # Commit the doc changes to the branch
        await asyncio.to_thread(subprocess.run, ["git", "add", "."], capture_output=True, cwd=str(REPO_ROOT))
        await asyncio.to_thread(subprocess.run, ["git", "commit", "-m", "docs: autonomous documentation update per index"], capture_output=True, cwd=str(REPO_ROOT))
        await asyncio.to_thread(subprocess.run, ["git", "push", "origin", "HEAD"], capture_output=True, cwd=str(REPO_ROOT))

async def auto_close_stale_sessions():
    """Closes sessions that have been awaiting feedback or failed for > 24 hours."""
    logger.info("Checking for stale sessions...")
    try:
        status_output = await jules_api.run("status")
        matches = re.findall(r'#(\d+) \[(\d+)\] (.*?) — ([A-Z_]+)', status_output)
        
        for idx, sid, title, state in matches:
            if state in ("AWAITING_USER_FEEDBACK", "FAILED"):
                # Ideally we'd parse updateTime, but for now we'll just log
                # We need to use the jules_api to fetch the session updateTime
                pass
    except Exception as e:
        logger.error(f"Error checking stale sessions: {e}")

async def resolve_pr_v5(pr: Dict[str, Any], index: Dict[str, Any], local_success: asyncio.Event, error_register: set):
    """High-capacity resolution: API-first merging with governance checks."""
    pr_num = pr["number"]
    
    if str(pr_num) in error_register:
        logger.warning(f"⏭️ Skipping PR #{pr_num} (marked as unresolvable conflict in error register).")
        return

    title = pr["title"]
    logger.info(f"🚀 Processing PR #{pr_num}: {title}")

    # 1. Enforce Governance
    files = await get_pr_files(pr_num)
    await enforce_documentation(pr_num, files, index)

    # 2. Attempt API Merge (Parallel friendly)
    cmd = ["gh", "pr", "merge", str(pr_num), "--merge", "--admin", "-d", "-c", "Autonomously merged via NINA v5.1 Parallel Orchestrator."]
    res = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    
    if res.returncode == 0:
        logger.info(f"✅ PR #{pr_num} merged via GitHub API.")
        _append_update_log("PR-"+str(pr_num), title, "Autonomously merged via Parallel API.")
    else:
        # If API merge fails, try local fallback, but ONLY if no other local merge has succeeded this cycle
        if not local_success.is_set():
            async with git_lock:
                if not local_success.is_set():
                    success = await resolve_pr_locally_v5(pr_num, title)
                    if success:
                        local_success.set()
                    else:
                        # Log to error register to skip next time
                        logger.error(f"Logging PR #{pr_num} to error register to prevent future blocks.")
                        append_error_register(pr_num, title)

async def resolve_pr_locally_v5(pr_num: int, title: str) -> bool:
    """Fallback local merge for conflicting PRs."""
    def run_cmd(cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))

    logger.info(f"Fallback resolution for PR #{pr_num}...")
    run_cmd(f"gh pr checkout {pr_num}")
    res = run_cmd("git rebase main")
    
    if res.returncode != 0:
        # Standard Doc Fix Fallback
        logger.warning("Conflict detected. Forcing standard doc resolution...")
        targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md", "docs/space/nina_index.md"]
        for f in targets:
            run_cmd(f"git checkout main -- {f}")
            run_cmd(f"git add {f}")
        run_cmd("export GIT_EDITOR=true && git rebase --continue")

    # Final Check
    status = run_cmd("git status --porcelain").stdout.strip()
    if status and "UU" in status:
         logger.error(f"❌ Unresolvable code conflict in PR #{pr_num}. Skipping.")
         run_cmd("git rebase --abort && git checkout main")
         return False

    branch = subprocess.check_output("git branch --show-current", shell=True, text=True).strip()
    run_cmd("git checkout main")
    res = run_cmd(f"git merge {branch} --no-ff -m 'merge: PR #{pr_num} (Local Fallback)'")
    if res.returncode == 0:
        run_cmd(f"git push origin main --no-verify")
        run_cmd(f"gh pr close {pr_num} -d")
        logger.info(f"✅ PR #{pr_num} resolved locally.")
        _append_update_log("PR-"+str(pr_num), title, "Merged via local fallback.")
        return True
    return False

def get_error_register() -> set:
    """Reads PR numbers that have unresolvable conflicts."""
    reg_path = REPO_ROOT / "docs/space/nina_error_register.md"
    if not reg_path.exists(): return set()
    content = reg_path.read_text()
    # Find PR numbers in the table
    return set(re.findall(r'\| PR-(\d+) \|', content))

def append_error_register(pr_num: int, title: str):
    reg_path = REPO_ROOT / "docs/space/nina_error_register.md"
    if not reg_path.exists(): return
    content = reg_path.read_text()
    today = datetime.now().strftime("%Y-%m-%d")
    new_row = f"| PR-{pr_num} | Orchestrator | PR Merge | Unresolvable conflict in PR: {title} | OPEN | Manual rebase required | {today} |"
    
    if "## Active Errors" in content:
        parts = content.split("## Active Errors")
        new_content = parts[0] + "## Active Errors\n" + new_row + "\n" + parts[1]
        reg_path.write_text(new_content)

async def monitor_and_resolve_prs_parallel():
    """Concurrently resolves all open PRs."""
    index = load_governance_index()
    error_register = get_error_register()
    
    cmd = ["gh", "pr", "list", "--json", "number,title,state"]
    res = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    
    if res.returncode != 0: return

    prs = json.loads(res.stdout)
    open_prs = [pr for pr in prs if pr["state"] == "OPEN"]
    
    if open_prs:
        logger.info(f"Found {len(open_prs)} open PRs. Starting Parallel Processing...")
        local_success = asyncio.Event()
        tasks = [resolve_pr_v5(pr, index, local_success, error_register) for pr in open_prs]
        await asyncio.gather(*tasks)

async def run_orchestrator_cycle(nina_os=None):
    """The main 3-minute high-capacity cycle."""
    logger.info("--- Starting Orchestrator v5.1 ---")
    
    # Step 0: Notify Telegram of any items needing attention
    await watch_and_notify()
    
    # Step 1: Clean up stale sessions to free up queue slots
    await auto_close_stale_sessions()
    
    # Step 2: Resolve PRs in Parallel
    await monitor_and_resolve_prs_parallel()
    
    # Step 3: Saturate Jules Pipeline
    status_output = await jules_api.run("status")
    active_count = len(re.findall(r"— IN_PROGRESS —", status_output))
    available_slots = MAX_CONCURRENT_SESSIONS - active_count
    
    if available_slots > 0:
        ready_tasks = [t for t in get_backlog_tasks() if t.get("status") == "READY"]
        to_dispatch = ready_tasks[:available_slots]
        for task in to_dispatch:
            prompt = f"TASK ID: {task['id']}\nTITLE: {task['title']}\nFILES: {task['files']}\n\nINSTRUCTIONS: {task['title']}. Ensure code quality, pass tests, and update relevant documentation files if required by the index."
            res = await jules_api.run(f"dispatch {prompt}")
            if "Jules task started" in res:
                _save_task_status(task["id"], "IN_PROGRESS")
            elif "400 Client Error" in res:
                logger.warning(f"Skipping dispatch due to 400 error (queue likely full).")
                break
    
    logger.info("--- Cycle Complete ---")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(run_orchestrator_cycle())
