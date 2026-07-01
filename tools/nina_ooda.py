#!/usr/bin/env python3
"""
NINA OODA Engine (OODA-001)
Autonomous priority calculation, decision loop, and action promoter.
"""

import json
import pathlib
import datetime
import asyncio
import subprocess

from tools.telegram_notify import send_message as tg_send_message

SEVERITY_WEIGHTS = {"BLOCKER": 100, "WARN": 10, "DEBT": 2, "FEATURE": 1}
STALE_READY_HOURS = 24
STALE_INPROGRESS_HOURS = 48
OODA_COOLDOWN_FILE = "data/ooda_state.json"

def append_session_note(note_text: str):
    log_path = pathlib.Path("docs/context/nina_session_log.md")
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
        
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    new_session = (
        f"## Session {now_str} | Agent: OODA | Task: OODA-001\n"
        f"Status: COMPLETE\n"
        f"Done: {note_text}\n"
        f"Commit: —\n"
        f"nina_sync.sh: —\n"
        f"Notes: Autonomous OODA cycle execution."
    )
    
    sessions.insert(0, new_session)
    sessions = sessions[:20]
    
    new_content = header
    for s in sessions:
        new_content += f"\n{s}\n\n---\n"
    if new_content.endswith("\n\n---\n"):
        new_content = new_content[:-6]
        
    log_path.write_text(new_content)

def load_cooldowns() -> dict:
    p = pathlib.Path(OODA_COOLDOWN_FILE)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def save_cooldowns(state: dict):
    p = pathlib.Path(OODA_COOLDOWN_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2))

def is_task_fixed(task_id: str) -> bool:
    commit_index = pathlib.Path("docs/generated/nina_commit_index.md")
    if not commit_index.exists():
        return False
    content = commit_index.read_text()
    for line in content.splitlines():
        if task_id in line and "| fix " in line:
            return True
    return False

# ━━━━━━ OBSERVE ━━━━━━

def observe() -> dict:
    graph_path = pathlib.Path("data/graphs/nina_context_graph.json")
    if not graph_path.exists() or (datetime.datetime.now() - datetime.datetime.fromtimestamp(graph_path.stat().st_mtime)).total_seconds() > 7200:
        subprocess.run(["python3", "tools/nina_context_graph.py"], capture_output=True, check=False)
        
    if not graph_path.exists():
        return {}
    try:
        return json.loads(graph_path.read_text())
    except Exception:
        return {}

# ━━━━━━ ORIENT ━━━━━━

def orient(graph: dict) -> list:
    if not graph:
        return []
        
    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])
    
    locked_files = []
    lock_path = pathlib.Path("juleslock.txt")
    if lock_path.exists():
        locked_files = [line.strip() for line in lock_path.read_text().splitlines() if line.strip()]
        
    backlog_path = pathlib.Path("docs/space/jules_backlog.md")
    backlog_content = backlog_path.read_text() if backlog_path.exists() else ""
    
    cooldowns = load_cooldowns()
    now = datetime.datetime.now()
    
    ranked_tasks = []
    for node_id, node in nodes.items():
        if node.get("type") != "task" or node.get("status") != "OPEN":
            continue
            
        severity = node.get("severity", "FEATURE")
        age_hours = node.get("age_hours", 24.0)
        
        target_files = [f.strip() for f in node.get("file", "").split(",") if f.strip()]
        is_locked = any(f in locked_files for f in target_files)
        if is_locked:
            continue
            
        if node_id in backlog_content:
            continue
            
        if is_task_fixed(node_id):
            continue
            
        if node_id in cooldowns:
            try:
                last_act_time = datetime.datetime.fromisoformat(cooldowns[node_id]["at"])
                if (now - last_act_time).total_seconds() < 21600:
                    continue
            except Exception:
                pass
                
        ast_risk_multiplier = 1.0
        try:
            from tools.predictive_ast import analyze_file_risk
            for f in target_files:
                risk_data = analyze_file_risk(f)
                if risk_data.get("status") == "OK":
                    risk_score = risk_data.get("risk_score", 1.0)
                    ast_risk_multiplier = max(ast_risk_multiplier, 1.0 + (risk_score / 100.0))
        except Exception:
            pass

        dep_count = sum(1 for e in edges if e.get("from") == node_id or e.get("to") == node_id)
        weight = SEVERITY_WEIGHTS.get(severity, 1)
        score = weight * age_hours * (1 + dep_count) * ast_risk_multiplier
        
        ranked_tasks.append({
            "id": node_id,
            "severity": severity,
            "issue": node.get("issue", ""),
            "file": node.get("file", ""),
            "score": score,
            "node": node
        })
        
    ranked_tasks.sort(key=lambda x: x["score"], reverse=True)
    return ranked_tasks

# ━━━━━━ DECIDE ━━━━━━

def decide(ranked_tasks: list) -> dict:
    if not ranked_tasks:
        return {"action": "NONE", "reason": "system healthy"}
        
    top = ranked_tasks[0]
    severity = top["severity"]
    
    if severity == "BLOCKER":
        return {
            "action": "ALERT_BOSTAMI",
            "task_id": top["id"],
            "message": f"🔴 BLOCKER: {top['id']} — {top['issue']}\nFile: {top['file']}\nImmediate action required.",
            "urgency": "HIGH"
        }
    elif severity == "WARN":
        return {
            "action": "PROMOTE_TO_BACKLOG",
            "task_id": top["id"],
            "status": "READY",
            "severity": "WARN",
            "issue": top["issue"],
            "message": f"🟠 WARN promoted to READY: {top['id']}"
        }
    else:
        return {
            "action": "PROMOTE_TO_BACKLOG",
            "task_id": top["id"],
            "status": "READY",
            "severity": severity,
            "issue": top["issue"],
            "message": f"🔵 {top['id']} queued as READY"
        }

# ━━━━━━ ACT ━━━━━━

def act(decision: dict) -> bool:
    action = decision.get("action")
    if action == "NONE":
        return True
        
    task_id = decision.get("task_id")
    now_iso = datetime.datetime.now().isoformat()
    
    if action == "ALERT_BOSTAMI":
        tg_send_message(decision.get("message", ""))
        
    elif action == "PROMOTE_TO_BACKLOG":
        backlog_path = pathlib.Path("docs/space/jules_backlog.md")
        if backlog_path.exists():
            content = backlog_path.read_text()
            if task_id not in content:
                severity = decision.get("severity", "FEATURE")
                issue = decision.get("issue", "")
                card = (
                    f"\n---\n\n### READY — {task_id}: {issue}\n"
                    f"**Status:** READY\n"
                    f"**Severity:** {severity}\n"
                    f"**Date Promoted:** {now_iso}\n"
                )
                
                if "## Summary Snapshot" in content:
                    parts = content.split("## Summary Snapshot")
                    new_content = parts[0] + card + "\n## Summary Snapshot" + parts[1]
                else:
                    new_content = content + card
                backlog_path.write_text(new_content)
                
    cooldowns = load_cooldowns()
    cooldowns[task_id] = {
        "last_action": action,
        "at": now_iso
    }
    save_cooldowns(cooldowns)
    return True

# ━━━━━━ MAIN CYCLE ━━━━━━

async def ooda_cycle() -> dict:
    graph = observe()
    ranked = orient(graph)
    decision = decide(ranked)
    act(decision)
    
    health = graph.get("summary", {}).get("health", "GREEN") if graph else "GREEN"
    action_val = decision.get("action")
    task_val = decision.get("task_id", "—")
    note = f"OODA cycle: action={action_val} task={task_val} health={health}"
    append_session_note(note)
    
    return decision

def main():
    decision = asyncio.run(ooda_cycle())
    print(f"OODA Cycle Decision: {decision}")

if __name__ == "__main__":
    main()
