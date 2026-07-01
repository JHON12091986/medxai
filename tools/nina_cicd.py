#!/usr/bin/env python3
"""
NINA Autonomous CI/CD Orchestrator (CICD-001)
Bridges the full OODA feedback loop from backlog triage to PR merge and post-sync audit.
"""

import json
import re
import pathlib
import datetime
import asyncio
import subprocess

from tools import nina_ooda
from tools.telegram_notify import send_message as tg_send_message
import tools.jules as jules

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()

def update_backlog_status(task_id: str, new_status: str):
    backlog_path = REPO_ROOT / "docs/space/jules_backlog.md"
    if not backlog_path.exists():
        return
    content = backlog_path.read_text()
    
    blocks = re.split(r"^###\s+", content, flags=re.MULTILINE)
    new_blocks = []
    updated = False
    for block in blocks:
        if not block:
            continue
        lines = block.splitlines()
        header = lines[0]
        if task_id in header:
            block_content = "\n".join(lines[1:])
            block_content = re.sub(r"\*\*Status:\*\*\s*[\w-]+", f"**Status:** {new_status}", block_content)
            
            new_header = header
            for term in ["READY", "IN-PROGRESS", "PENDING_APPROVAL", "DONE"]:
                if term in header:
                    new_header = header.replace(term, new_status)
                    break
            else:
                new_header = f"{new_status} — {header.lstrip(' \t#-')}"
                
            block = new_header + "\n" + block_content
            updated = True
        new_blocks.append(block)
        
    if updated:
        new_content = blocks[0] + "### " + "### ".join(new_blocks)
        backlog_path.write_text(new_content)

def mark_error_register_fixed(task_id: str):
    register_path = REPO_ROOT / "docs/space/nina_error_register.md"
    if not register_path.exists():
        return
    content = register_path.read_text()
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"| {task_id} |") or line.strip().startswith(f"|{task_id}|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 9:
                parts[5] = "✅ FIXED"
                line = " | ".join(parts).strip()
                if not line.startswith("|"):
                    line = "| " + line
                if not line.endswith("|"):
                    line = line + " |"
        new_lines.append(line)
    register_path.write_text("\n".join(new_lines))

def append_feedback_log(health: str, top_priority: str, ranked_count: int, action: str, promoted: list, dispatched: list, merged: list):
    log_path = REPO_ROOT / "docs/context/nina_session_log.md"
    if not log_path.exists():
        return
    content = log_path.read_text()
    
    parts = content.split("---")
    if len(parts) > 1:
        header = parts[0] + "---\n"
        session_text = "---".join(parts[1:])
        sessions = [s.strip() for s in session_text.split("---") if s.strip()]
    else:
        header = content
        sessions = []
        
    now_iso = datetime.datetime.now().isoformat()
    
    new_session = (
        f"## OODA Cycle {now_iso} | Agent: nina_cicd\n"
        f"Observe: health={health} top_priority={top_priority or '—'}\n"
        f"Orient:  {ranked_count} actionable tasks ranked\n"
        f"Decide:  action={action}\n"
        f"Act:     promoted={promoted or '[]'} dispatched={dispatched or '[]'} merged={merged or '[]'}\n"
        f"Next:    {top_priority or 'system healthy'}"
    )
    
    sessions.insert(0, new_session)
    sessions = sessions[:20]
    
    new_content = header
    for s in sessions:
        new_content += f"\n{s}\n\n---\n"
    if new_content.endswith("\n\n---\n"):
        new_content = new_content[:-6]
        
    log_path.write_text(new_content)

# ━━━━━━ PIPELINE STAGES ━━━━━━

async def observe_and_orient() -> tuple:
    graph = nina_ooda.observe()
    ranked_tasks = nina_ooda.orient(graph)
    return graph, ranked_tasks

async def decide_and_promote(ranked_tasks: list) -> dict:
    decision = nina_ooda.decide(ranked_tasks)
    nina_ooda.act(decision)
    return decision

async def dispatch_ready_tasks() -> list:
    backlog_path = REPO_ROOT / "docs/space/jules_backlog.md"
    if not backlog_path.exists():
        return []
        
    content = backlog_path.read_text()
    ready_tasks = []
    blocks = re.split(r"^###\s+", content, flags=re.MULTILINE)
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        if "READY" in header:
            id_match = re.search(r"\b([A-Z]+-\d+[A-Z]*|[A-Z]-\d+)\b", header)
            if id_match:
                ready_tasks.append(id_match.group(1))
                
    dispatched = []
    
    locked_files = []
    lock_path = REPO_ROOT / "juleslock.txt"
    if lock_path.exists():
        locked_files = [line.strip() for line in lock_path.read_text().splitlines() if line.strip()]
        
    for task_id in ready_tasks:
        if task_id in locked_files:
            continue
        if nina_ooda.is_task_fixed(task_id):
            continue
            
        prompt = f"Address task {task_id} in the repository."
        try:
            print(f"Dispatching task {task_id} to Jules...")
            await jules.run_dispatch(prompt=prompt, title=f"Fix {task_id}")
            update_backlog_status(task_id, "IN-PROGRESS")
            dispatched.append(task_id)
        except Exception as e:
            print(f"Failed to dispatch {task_id}: {e}")
            
    return dispatched

async def poll_and_merge() -> list:
    backlog_path = REPO_ROOT / "docs/space/jules_backlog.md"
    if not backlog_path.exists():
        return []
        
    content = backlog_path.read_text()
    in_progress_tasks = []
    blocks = re.split(r"^###\s+", content, flags=re.MULTILINE)
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        if "IN-PROGRESS" in header:
            id_match = re.search(r"\b([A-Z]+-\d+[A-Z]*|[A-Z]-\d+)\b", header)
            if id_match:
                in_progress_tasks.append(id_match.group(1))
                
    awaiting_approval = []
    
    try:
        res = subprocess.run(
            ["gh", "pr", "list", "--label", "jules", "--json", "number,headRefName,title,url"],
            capture_output=True, text=True, check=False
        )
        if res.returncode == 0:
            prs = json.loads(res.stdout)
            for pr in prs:
                head = pr.get("headRefName", "")
                url = pr.get("url", "")
                title = pr.get("title", "")
                for task_id in in_progress_tasks:
                    if task_id.lower() in head.lower() or task_id.lower() in title.lower():
                        msg = (
                            f"🔔 PR ready for review: {task_id}\n"
                            f"PR URL: {url}\n"
                            f"Reply /merge {task_id} to approve or /skip {task_id} to defer"
                        )
                        tg_send_message(msg)
                        update_backlog_status(task_id, "PENDING_APPROVAL")
                        awaiting_approval.append(task_id)
    except Exception as e:
        print(f"Failed to poll PRs: {e}")
        
    return awaiting_approval

async def handle_approval(task_id: str) -> bool:
    print(f"Starting approval flow for {task_id}...")
    
    audit_res = subprocess.run(["python3", "tools/rule0_audit.py", "--hours", "8"], capture_output=True, check=False)
    if audit_res.returncode != 0:
        tg_send_message(f"⚠️ Pre-merge check failed for {task_id}: Rule 0 audit failed.")
        update_backlog_status(task_id, "READY")
        return False
        
    graph = nina_ooda.observe()
    node = graph.get("nodes", {}).get(task_id, {})
    files = [f.strip() for f in node.get("file", "").split(",") if f.strip()]
    for f in files:
        path = REPO_ROOT / f
        if path.exists() and path.suffix == ".py":
            compile_res = subprocess.run(["python3", "-m", "py_compile", str(path)], capture_output=True, check=False)
            if compile_res.returncode != 0:
                tg_send_message(f"⚠️ Pre-merge check failed for {task_id}: {f} failed to compile.")
                update_backlog_status(task_id, "READY")
                return False
                
            flakes_res = subprocess.run(["pyflakes", str(path)], capture_output=True, check=False)
            if flakes_res.returncode != 0:
                tg_send_message(f"⚠️ Pre-merge check failed for {task_id}: {f} failed pyflakes linting.")
                update_backlog_status(task_id, "READY")
                return False
                
    lock_path = REPO_ROOT / "juleslock.txt"
    if lock_path.exists():
        locked_files = [line.strip() for line in lock_path.read_text().splitlines() if line.strip()]
        if any(f in locked_files for f in files):
            tg_send_message(f"⚠️ Pre-merge check failed for {task_id}: Target file is currently locked.")
            update_backlog_status(task_id, "READY")
            return False
            
    try:
        res = subprocess.run(
            ["gh", "pr", "list", "--label", "jules", "--json", "number,headRefName,title"],
            capture_output=True, text=True, check=False
        )
        if res.returncode == 0:
            prs = json.loads(res.stdout)
            for pr in prs:
                head = pr.get("headRefName", "")
                title = pr.get("title", "")
                num = pr.get("number")
                if task_id.lower() in head.lower() or task_id.lower() in title.lower():
                    merge_res = subprocess.run(
                        ["gh", "pr", "merge", str(num), "--merge", "--delete-branch"],
                        capture_output=True, text=True, check=False
                    )
                    if merge_res.returncode == 0:
                        subprocess.run(["bash", "scripts/nina_sync.sh"], cwd=REPO_ROOT, check=False)
                        update_backlog_status(task_id, "DONE")
                        mark_error_register_fixed(task_id)
                        
                        nina_ooda.append_session_note(f"Merged PR for task {task_id} successfully.")
                        tg_send_message(f"✅ Merged + synced: {task_id}")
                        
                        subprocess.run(["python3", "tools/nina_context_graph.py"], capture_output=True, check=False)
                        return True
                    else:
                        tg_send_message(f"❌ gh pr merge failed for PR #{num}: {merge_res.stderr}")
                        return False
    except Exception as e:
        tg_send_message(f"❌ Exception merging PR for {task_id}: {e}")
        
    return False

# ━━━━━━ MAIN CYCLE ━━━━━━

async def run_cicd_cycle():
    graph, ranked = await observe_and_orient()
    decision = await decide_and_promote(ranked)
    
    dispatched = await dispatch_ready_tasks()
    awaiting = await poll_and_merge()
    
    action = decision.get("action", "NONE")
    health = graph.get("summary", {}).get("health", "GREEN") if graph else "GREEN"
    top_priority = graph.get("summary", {}).get("top_priority") if graph else None
    
    promoted = [decision["task_id"]] if action == "PROMOTE_TO_BACKLOG" else []
    
    append_feedback_log(
        health=health,
        top_priority=top_priority,
        ranked_count=len(ranked),
        action=action,
        promoted=promoted,
        dispatched=dispatched,
        merged=[]
    )
    
    print(f"CICD Cycle Complete: health={health}, action={action}, dispatched={dispatched}, awaiting={awaiting}")

def main():
    asyncio.run(run_cicd_cycle())

if __name__ == "__main__":
    main()
