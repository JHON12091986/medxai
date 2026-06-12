"""
Autonomous PR & Spec Orchestrator (Mega Task Loop).
Identifies undone Jules specs, dispatches up to 15 parallel sessions, and resolves PRs.
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

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
MAX_CONCURRENT_SESSIONS = 15

logger = logging.getLogger("nina.orchestrator")

async def get_active_session_count() -> int:
    """Queries Jules API to find how many sessions are currently IN_PROGRESS."""
    try:
        status_output = await jules_api.run("status")
        # Sessions are listed as: #N [ID] Title — STATE — URL
        active_count = len(re.findall(r"— IN_PROGRESS —", status_output))
        logger.info(f"Currently active Jules sessions: {active_count}")
        return active_count
    except Exception as e:
        logger.error(f"Failed to check active sessions: {e}")
        return 0

async def fetch_ready_tasks(limit=15) -> List[Dict[str, Any]]:
    """Fetches up to 'limit' tasks with status READY from the backlog."""
    tasks = get_backlog_tasks()
    ready_tasks = [t for t in tasks if t.get("status") == "READY"]
    return ready_tasks[:limit]

async def dispatch_parallel_tasks(ready_tasks: List[Dict[str, Any]]):
    """Dispatches each task as a separate Jules session."""
    active_count = await get_active_session_count()
    available_slots = MAX_CONCURRENT_SESSIONS - active_count
    
    if available_slots <= 0:
        logger.info("Jules queue is full (15/15 sessions active). Skipping dispatch.")
        return

    to_dispatch = ready_tasks[:available_slots]
    logger.info(f"Saturating queue: Dispatching {len(to_dispatch)} new sessions.")

    for task in to_dispatch:
        prompt = f"TASK ID: {task['id']}\nTITLE: {task['title']}\nFILES: {task['files']}\n\nINSTRUCTIONS: Please implement the functionality for {task['title']} as described in the NINA backlog. Ensure full test coverage and compliance with AGENTS.md."
        
        logger.info(f"Dispatching session for {task['id']}...")
        result = await jules_api.run(f"dispatch {prompt}")
        
        if "Jules task started" in result:
            _save_task_status(task["id"], "IN_PROGRESS")
            logger.info(f"✅ {task['id']} successfully dispatched and set to IN_PROGRESS")
        else:
            logger.error(f"❌ Failed to dispatch {task['id']}: {result}")

async def monitor_and_resolve_prs():
    """Checks for open GitHub PRs from Jules and attempts to merge them."""
    try:
        cmd = ["gh", "pr", "list", "--json", "number,title,state,body,headRefName"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            logger.error(f"Failed to list PRs: {res.stderr}")
            return

        prs = json.loads(res.stdout)
        for pr in prs:
            if pr["state"] != "OPEN": continue
            
            pr_num = pr["number"]
            title = pr["title"]
            body = pr["body"]
            
            task_id_match = re.search(r'(B-\d+|AG-[A-J]-\d+|R-\d+)', body + title)
            task_id = task_id_match.group(1) if task_id_match else "UNKNOWN"
            
            logger.info(f"Found open PR #{pr_num} for task {task_id}: {title}")
            await resolve_pr_locally(pr_num, task_id, title)

    except Exception as e:
        logger.error(f"monitor_and_resolve_prs failed: {e}")

async def resolve_pr_locally(pr_num: int, task_id: str, title: str):
    """Executes the rebase -> merge -> log -> close cycle."""
    logger.info(f"🚀 Starting resolution cycle for PR #{pr_num}...")
    
    def run_cmd(cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))

    # 1. Checkout
    res = run_cmd(f"gh pr checkout {pr_num}")
    if res.returncode != 0:
        logger.error(f"Checkout failed for PR #{pr_num}")
        return

    # 2. Rebase & Doc Fixes
    res = run_cmd("git rebase main")
    if res.returncode != 0:
        logger.warning("Conflict detected. Forcing NINA doc resolution standard.")
        targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md"]
        for f in targets:
            run_cmd(f"git checkout main -- {f}")
            run_cmd(f"git add {f}")
        run_cmd("export GIT_EDITOR=true && git rebase --continue")

    # 3. Merge to Main
    branch = subprocess.check_output("git branch --show-current", shell=True, text=True).strip()
    run_cmd("git checkout main")
    res = run_cmd(f"git merge {branch} --no-ff -m 'merge: PR #{pr_num} {task_id}'")
    if res.returncode != 0:
        logger.error(f"Merge failed for {task_id}")
        return

    # 4. Status Update
    _save_task_status(task_id, "DONE")
    _append_update_log(task_id, title, "Autonomously merged via NINA Parallel Orchestrator.")
    
    # 5. Cleanup Remote
    run_cmd(f"gh pr close {pr_num} -d -c 'Merged via autonomous cycle.'")
    logger.info(f"✅ PR #{pr_num} merged and closed.")

async def run_orchestrator_cycle(nina_os=None):
    """The main 30-minute cycle entry point."""
    logger.info("--- Starting Parallel Orchestrator Cycle ---")
    
    # Phase 0: Notify Telegram of any items needing attention
    await watch_and_notify()
    
    # Phase 1: Clear current PRs
    await monitor_and_resolve_prs()
    
    # Phase 2: Refill the pipeline to 15 concurrent sessions
    ready_tasks = await fetch_ready_tasks(limit=MAX_CONCURRENT_SESSIONS)
    if ready_tasks:
        await dispatch_parallel_tasks(ready_tasks)
    else:
        logger.info("No READY tasks available in backlog.")
    
    logger.info("--- Orchestrator Cycle Complete ---")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(run_orchestrator_cycle())
