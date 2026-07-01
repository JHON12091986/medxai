#!/usr/bin/env python3
"""
NINA Context Graph Generator (OBS-003)
Builds a live JSON context graph representing the current state of NINA.
"""

import sys
import json
import re
import pathlib
import datetime
import subprocess

HIGH_RISK_FILES = [
    "core/router.py",
    "interfaces/telegram_interface.py",
    ".env",
    "main.py",
    "tools/guardian_engine.py",
    "tools/shell.py",
    "ninagate/main.py"
]

SEVERITY_WEIGHTS = {"BLOCKER": 100, "WARN": 10, "DEBT": 2, "FEATURE": 1}

def get_git_commit_sha(filepath: str) -> str:
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%H", filepath],
            capture_output=True, text=True, check=False
        )
        return res.stdout.strip()
    except Exception:
        return ""

def get_file_last_commit_details(filepath: str) -> tuple:
    sha = get_git_commit_sha(filepath)
    if not sha:
        return "", "unassigned", None
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%s", filepath],
            capture_output=True, text=True, check=False
        )
        msg = res.stdout.strip()
        last_agent = "agy"
        if "jules" in msg.lower() or "Jules" in msg:
            last_agent = "Jules"
            
        pr_match = re.search(r"#(\d+)", msg)
        last_pr = f"#{pr_match.group(1)}" if pr_match else None
        return sha, last_agent, last_pr
    except Exception:
        return sha, "unassigned", None

def check_service_status(service_name: str) -> tuple:
    try:
        res = subprocess.run(["systemctl", "is-active", service_name], capture_output=True, text=True, check=False)
        status = res.stdout.strip()
        if status == "active":
            return "running", "GREEN"
        elif status == "inactive":
            return "inactive", "DOWN"
        else:
            return status or "unknown", "DOWN"
    except Exception:
        return "unknown", "DOWN"

def find_imports(filepath: str) -> list:
    p = pathlib.Path(filepath)
    if not p.exists() or p.suffix != ".py":
        return []
    imports = []
    try:
        content = p.read_text()
        for line in content.splitlines():
            line = line.strip()
            m1 = re.match(r"^from\s+([\w\.]+)", line)
            if m1:
                imported = m1.group(1).replace(".", "/") + ".py"
                imports.append(imported)
            else:
                m2 = re.match(r"^import\s+([\w\.,\s]+)", line)
                if m2:
                    for name in m2.group(1).split(","):
                        name = name.strip()
                        imported = name.replace(".", "/") + ".py"
                        imports.append(imported)
    except Exception:
        pass
    
    valid_imports = []
    for imp in imports:
        if pathlib.Path(imp).exists():
            valid_imports.append(imp)
    return sorted(list(set(valid_imports)))[:10]

def parse_error_register() -> tuple:
    register_path = pathlib.Path("docs/space/nina_error_register.md")
    if not register_path.exists():
        return "2026-06-06", []
    
    content = register_path.read_text()
    updated_date = "2026-06-06"
    updated_match = re.search(r"updated:\s*([\d-]+)", content)
    if updated_match:
        updated_date = updated_match.group(1)
        
    tasks = []
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("|") or "ID | Severity" in line or "|---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 9:
            continue
        task_id = parts[1]
        severity_col = parts[2]
        component = parts[3]
        issue = parts[4]
        status = parts[5]
        assignee = parts[6]
        files_col = parts[8]
        
        is_open = "OPEN" in status or "OPEN" in severity_col or "PENDING" in status or status == "READY"
        if not is_open:
            continue
            
        severity = "FEATURE"
        if "BLOCKER" in severity_col:
            severity = "BLOCKER"
        elif "WARN" in severity_col:
            severity = "WARN"
        elif "DEBT" in severity_col:
            severity = "DEBT"
            
        files = [f.strip() for f in files_col.split(",") if f.strip()]
        
        tasks.append({
            "id": task_id,
            "severity": severity,
            "status": "OPEN",
            "component": component,
            "issue": issue,
            "files": files,
            "assignee": assignee if assignee != "unassigned" else None
        })
    return updated_date, tasks

def parse_backlog() -> list:
    backlog_path = pathlib.Path("docs/space/jules_backlog.md")
    if not backlog_path.exists():
        return []
        
    content = backlog_path.read_text()
    nodes = []
    blocks = re.split(r"^###\s+", content, flags=re.MULTILINE)
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        id_match = re.search(r"\b([A-Z]+-\d+[A-Z]*|[A-Z]-\d+)\b", header)
        if id_match:
            task_id = id_match.group(1)
        else:
            task_id = re.sub(r"[^a-zA-Z0-9-]", "_", header[:30]).strip("_")
            
        status = "PENDING"
        if "✅" in header or "DONE" in header:
            status = "DONE"
        elif "⚠️" in header or "PARTIAL" in header:
            status = "PENDING"
        elif "IN-PROGRESS" in header or "IN_PROGRESS" in header:
            status = "IN-PROGRESS"
        elif "READY" in header:
            status = "READY"
        elif any(emoji in header for emoji in ["🔴", "🟠", "🟡"]):
            status = "READY"
            
        impact = "MEDIUM"
        impact_match = re.search(r"impact:\s*(\w+)", block, re.IGNORECASE)
        if impact_match:
            impact = impact_match.group(1).upper()
            
        age_hours = 24.0
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", block)
        if date_match:
            try:
                date_val = datetime.datetime.strptime(date_match.group(1), "%Y-%m-%d")
                age_hours = (datetime.datetime.now() - date_val).total_seconds() / 3600.0
            except Exception:
                pass
                
        nodes.append({
            "id": task_id,
            "status": status,
            "impact": impact,
            "age_hours": age_hours,
            "title": header
        })
    return nodes

def build_graph() -> dict:
    now = datetime.datetime.now().isoformat()
    
    locked_files = []
    lock_path = pathlib.Path("juleslock.txt")
    if lock_path.exists():
        locked_files = [line.strip() for line in lock_path.read_text().splitlines() if line.strip()]
        
    updated_date_str, open_tasks = parse_error_register()
    try:
        updated_date = datetime.datetime.strptime(updated_date_str, "%Y-%m-%d")
    except Exception:
        updated_date = datetime.datetime.now() - datetime.timedelta(days=10)
    register_age_hours = (datetime.datetime.now() - updated_date).total_seconds() / 3600.0
    
    open_bugs_map = {}
    for task in open_tasks:
        for f in task["files"]:
            open_bugs_map.setdefault(f, []).append(task["id"])
            
    nodes = {}
    edges = []
    
    stale_files = []
    for f in HIGH_RISK_FILES:
        path = pathlib.Path(f)
        exists = path.exists()
        last_modified = ""
        is_stale = False
        if exists:
            mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
            last_modified = mtime.isoformat()
            age_hours = (datetime.datetime.now() - mtime).total_seconds() / 3600.0
            if age_hours > 72.0:
                is_stale = True
                stale_files.append(f)
                
        sha, last_agent, last_pr = get_file_last_commit_details(f)
        
        nodes[f] = {
            "type": "file",
            "risk": "HIGH",
            "locked": f in locked_files,
            "last_modified": last_modified,
            "open_bugs": open_bugs_map.get(f, []),
            "last_agent": last_agent,
            "last_pr": last_pr,
            "is_stale": is_stale,
            "last_commit_sha": sha
        }
        
        for imp in find_imports(f):
            edges.append({
                "from": f,
                "to": imp,
                "relation": "imports"
            })
            
    open_blockers = 0
    for task in open_tasks:
        nodes[task["id"]] = {
            "type": "task",
            "severity": task["severity"],
            "status": "OPEN",
            "file": ", ".join(task["files"]),
            "age_hours": register_age_hours,
            "assigned_to": task["assignee"]
        }
        if task["severity"] == "BLOCKER":
            open_blockers += 1
            
        for f in task["files"]:
            edges.append({
                "from": task["id"],
                "to": f,
                "relation": "affects"
            })
            
    services = [
        {"name": "nina.service", "entry": "main.py"},
        {"name": "ninagate.service", "entry": "ninagate/main.py"},
        {"name": "ninajulesgithub.service", "entry": "ninajulesgithub.py"},
        {"name": "nina-dashboard.service", "entry": "tools/nina_dashboard.py"}
    ]
    services_healthy = 0
    services_down = []
    for s in services:
        status, health = check_service_status(s["name"])
        nodes[s["name"]] = {
            "type": "service",
            "status": status,
            "entry_point": s["entry"],
            "health": health
        }
        if health == "GREEN":
            services_healthy += 1
        else:
            services_down.append(s["name"])
            
        edges.append({
            "from": s["name"],
            "to": s["entry"],
            "relation": "runs"
        })
        
    backlog_items = parse_backlog()
    for item in backlog_items:
        nodes[item["id"]] = {
            "type": "backlog",
            "status": item["status"],
            "impact": item["impact"],
            "age_hours": item["age_hours"]
        }
        if item["id"] in nodes and nodes[item["id"]]["type"] == "task":
            edges.append({
                "from": item["id"],
                "to": item["id"],
                "relation": "implements"
            })
            
    if open_blockers > 0 or len(services_down) > 0:
        overall_health = "CRITICAL"
    elif len(open_tasks) > 0 or services_healthy < len(services):
        overall_health = "WARN"
    else:
        overall_health = "GREEN"
        
    top_priority = None
    highest_score = -1.0
    for node_id, node in nodes.items():
        if node["type"] == "task":
            severity = node["severity"]
            weight = SEVERITY_WEIGHTS.get(severity, 1)
            age = node["age_hours"]
            dep_count = sum(1 for e in edges if e["from"] == node_id or e["to"] == node_id)
            score = weight * age * (1 + dep_count)
            if score > highest_score:
                highest_score = score
                top_priority = node_id
                
    summary = {
        "health": overall_health,
        "top_priority": top_priority,
        "stale_files": stale_files,
        "locked_files": [f for f in HIGH_RISK_FILES if f in locked_files],
        "services_down": services_down
    }
    
    return {
        "meta": {
            "generated_at": now,
            "generator": "tools/nina_context_graph.py",
            "version": "1",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "open_blockers": open_blockers,
            "services_healthy": services_healthy
        },
        "nodes": nodes,
        "edges": edges,
        "summary": summary
    }

def main():
    graph = build_graph()
    output_path = pathlib.Path("data/graphs/nina_context_graph.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph, indent=2))
    print(f"Context graph updated -> {graph['meta']['node_count']} nodes, "
          f"health={graph['summary']['health']}, "
          f"top_priority={graph['summary']['top_priority']}")
    
    if graph["summary"]["health"] == "CRITICAL":
        sys.exit(2)
    elif graph["summary"]["health"] == "WARN":
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
