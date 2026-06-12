"""
Autonomous PR & Spec Orchestrator (Mega Task Loop).
Identifies undone Jules specs, packages them into mega-tasks, and resolves PRs.
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

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"

logger = logging.getLogger("nina.orchestrator")

async def fetch_undone_specs(limit=10) -> List[Dict[str, Any]]:
    """Fetches up to 'limit' tasks with status READY from the backlog."""
    tasks = get_backlog_tasks()
    ready_tasks = [t for t in tasks if t.get("status") == "READY"]
    return ready_tasks[:limit]

def build_mega_task(tasks: List[Dict[str, Any]]) -> str:
    """Combines multiple tasks into a single 'Mega Task' prompt."""
    if not tasks:
        return ""
    
    prompt = "MEGA TASK BATCH EXECUTION\n\n"
    prompt += "Objective: Execute the following batch of independent tasks sequentially.\n\n"
    
    for i, task in enumerate(tasks, 1):
        prompt += f"PHASE {i}: {task['id']} - {task['title']}\n"
        prompt += f"Files: {task['files']}\n"
        prompt += f"Instructions: Please implement the functionality for {task['title']} as described in the NINA backlog.\n\n"
    
    prompt += "Verification: Ensure all changes are syntactically correct and pass baseline checks."
    return prompt

async def dispatch_mega_task(ready_tasks: List[Dict[str, Any]]):
    """Dispatches a mega task and updates task statuses."""
    if not ready_tasks:
        return
    
    mega_prompt = build_mega_task(ready_tasks)
    logger.info(f"Dispatching Mega Task with {len(ready_tasks)} items.")
    
    # Use jules_api to dispatch
    result = await jules_api.run(f"dispatch {mega_prompt}")
    logger.info(f"Jules Dispatch Result: {result}")
    
    if "Jules task started" in result:
        for task in ready_tasks:
            _save_task_status(task["id"], "IN_PROGRESS")
            logger.info(f"Task {task['id']} set to IN_PROGRESS")

async def monitor_and_resolve_prs():
    """Checks for open GitHub PRs from Jules and attempts to merge them."""
    try:
        # 1. List open PRs
        cmd = ["gh", "pr", "list", "--json", "number,title,state,body,headRefName"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            logger.error(f"Failed to list PRs: {res.stderr}")
            return

        prs = json.loads(res.stdout)
        for pr in prs:
            if pr["state"] != "OPEN":
                continue
            
            pr_num = pr["number"]
            title = pr["title"]
            body = pr["body"]
            
            # Identify task ID from body or title
            task_id_match = re.search(r'(B-\d+|AG-[A-J]-\d+|R-\d+)', body + title)
            task_id = task_id_match.group(1) if task_id_match else "UNKNOWN"
            
            logger.info(f"Found open PR #{pr_num} for task {task_id}: {title}")
            
            # Resolve locally using ninaflash maintain logic (simplified for orchestrator)
            await resolve_pr_locally(pr_num, task_id, title)

    except Exception as e:
        logger.error(f"monitor_and_resolve_prs failed: {e}")

async def resolve_pr_locally(pr_num: int, task_id: str, title: str):
    """Executes the rebase -> merge -> log -> close cycle."""
    logger.info(f"🚀 Resolution cycle for PR #{pr_num} ({task_id})...")
    
    def run_cmd(cmd):
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))

    # 1. Checkout PR branch
    res = run_cmd(f"gh pr checkout {pr_num}")
    if res.returncode != 0:
        logger.error(f"Checkout failed: {res.stderr}")
        return

    # 2. Rebase and resolve docs
    res = run_cmd("git rebase main")
    if res.returncode != 0:
        logger.warning("Conflict detected. Forcing doc resolution.")
        targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md"]
        for f in targets:
            run_cmd(f"git checkout main -- {f}")
            run_cmd(f"git add {f}")
        run_cmd("export GIT_EDITOR=true && git rebase --continue")

    # 3. Merge
    branch = subprocess.check_output("git branch --show-current", shell=True, text=True).strip()
    run_cmd("git checkout main")
    res = run_cmd(f"git merge {branch} --no-ff -m 'merge: PR #{pr_num} {task_id}'")
    if res.returncode != 0:
        logger.error(f"Merge failed: {res.stderr}")
        return

    # 4. Success updates
    _save_task_status(task_id, "DONE")
    _append_update_log(task_id, title, f"Autonomously merged via Mega Orchestrator.")
    
    # 5. Close and Cleanup
    run_cmd(f"gh pr close {pr_num} -d -c 'Merged via autonomous orchestrator cycle.'")
    logger.info(f"✅ PR #{pr_num} merged and closed.")

async def run_orchestrator_cycle(nina_os=None):
    """The main 30-minute cycle entry point."""
    logger.info("--- Starting Orchestrator Cycle ---")
    
    # Phase A: Resolve pending PRs first to clear the workspace
    await monitor_and_resolve_prs()
    
    # Phase B: Feed the pipeline with new tasks
    ready_tasks = await fetch_undone_specs(limit=10)
    if ready_tasks:
        await dispatch_mega_task(ready_tasks)
    else:
        logger.info("No READY tasks in backlog.")
    
    logger.info("--- Orchestrator Cycle Complete ---")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(run_orchestrator_cycle())
