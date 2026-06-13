#!/usr/bin/env python3
"""ninaflash_backlog — Backlog DAG, triage, task management."""
from tools.ninaflash_core import REPO_ROOT, BACKLOG_PATH, get_backlog_tasks, _get_locks
import re
import sys
from typing import List

# --- _save_task_status ---
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

# --- _find_blockers ---
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
        m = re.search(r"(B-\d+|AG-[A-Z]-\d+|R-\d+)", dep)
        if m: blockers.append(m.group(1))
    return blockers

# --- cmd_backlog_summary ---
def cmd_backlog_summary(args):
    """[100] Print a 5-line summary of the backlog."""
    tasks = get_backlog_tasks()
    c_ready = sum(1 for t in tasks if t.get('status') == 'READY')
    c_prog = sum(1 for t in tasks if t.get('status') == 'IN_PROGRESS')
    c_blocked = sum(1 for t in tasks if t.get('status') == 'BLOCKED')
    c_done = sum(1 for t in tasks if t.get('status') == 'DONE')
    print(f"Backlog Summary:\n  READY: {c_ready}\n  IN_PROGRESS: {c_prog}\n  BLOCKED: {c_blocked}\n  DONE: {c_done}")

# --- cmd_task_active ---
def cmd_task_active(args):
    """[101] List active tasks and their locked files."""
    tasks = get_backlog_tasks()
    active = [t for t in tasks if t.get('status') in ('IN_PROGRESS', 'IN_PR')]
    locks = _get_locks()
    print("Active Tasks:")
    for t in active: print(f"  {t.get('id')} - {t.get('title')} ({t.get('status')})")
    print(f"\nLocked Files: {', '.join(locks) if locks else 'None'}")

# --- cmd_backlog_triage ---
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
                _save_task_status(task["id"], "READY"); promoted += 1
    if not promoted: print("No tasks eligible for promotion.")

# --- cmd_backlog_dag ---
def cmd_backlog_dag(args):
    """[019] ASCII DAG: Visualize dependencies with circularity guard."""
    task_id = getattr(args, "task_id", None)
    tasks = get_backlog_tasks()
    task_map = {t["id"]: t for t in tasks}
    def print_tree(tid, depth=0, visited=None):
        if visited is None: visited = set()
        if depth > 10 or tid in visited: return
        visited.add(tid); task = task_map.get(tid)
        if not task: return
        print("  " * depth + f"└─ {task['id']} [{task['status']}] {task['title']}")
        deps_str = task.get("depends_on", "")
        if deps_str and deps_str != "—":
            for dep in [d.strip() for d in deps_str.replace("`", "").split(",")]:
                m = re.search(r"(B-\d+|AG-[A-Z]-\d+|R-\d+)", dep)
                if m: print_tree(m.group(1), depth + 1, visited)
    if task_id: print_tree(task_id)
    else:
        for t in tasks:
            if t["status"] in ["IN_PROGRESS", "READY"]: print_tree(t["id"]); print()

# --- cmd_backlog_add ---
def cmd_backlog_add(args):
    """[020] Add new task using CLI arguments."""
    if not args.title or not args.priority: print("❌ Title/Priority required."); return
    tasks = get_backlog_tasks()
    if args.priority == "AG":
        next_id = f"AG-{args.ag_sub.upper()}-{args.ag_num.zfill(2)}"
    else:
        b_ids = [int(t["id"][2:]) for t in tasks if t["id"].startswith("B-")]
        next_id = f"B-{max(b_ids)+1:03d}" if b_ids else "B-001"
    row = f"| {next_id} | {args.title} | `NEEDS_SPEC` | {args.component or '—'} | — | Added via CLI |\n"
    with open(BACKLOG_PATH, "a", encoding="utf-8") as f: f.write(row)
    print(f"✅ Added {next_id}.")

# --- cmd_backlog_archive ---
def cmd_backlog_archive(args):
    """[021] Move DONE items to archived status."""
    print("Archiving done items...")
