# Usage: python3 tools/nina_dashboard.py
# Access: http://localhost:8766
# Read-only — no write operations performed

import os
import sys
import subprocess
import urllib.request
import datetime
from pathlib import Path
from flask import Flask, render_template, send_file

# Resolve absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Ensure the parent directory is in sys.path so we can import core and crons
sys.path.append(str(BASE_DIR))

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

@app.route('/ninaui')
def ninaui():
    return send_file(str(DASHBOARD_DIR / "ninaui.html"))

@app.route('/health')
def health():
    from core.observability import get_hub
    import json
    data = get_hub().to_dict()
    return app.response_class(
        response=json.dumps(data, indent=2),
        status=200,
        mimetype='application/json'
    )

@app.route('/')
def index():
    # 1. NINA service status
    try:
        service_status = subprocess.check_output(['systemctl', 'is-active', 'nina.service']).decode('utf-8').strip()
    except Exception:
        service_status = "unavailable"

    # 2. Provider health
    try:
        req = urllib.request.Request('http://localhost:8080/metrics')
        with urllib.request.urlopen(req, timeout=2) as response:
            provider_health = response.read().decode('utf-8') if response.getcode() == 200 else "unavailable"
    except Exception:
        provider_health = "unavailable"

    # 3. Active tasks summary
    try:
        from core.task_store import TaskStore
        tasks_summary = TaskStore().format_tasks_summary()
    except Exception:
        tasks_summary = "unavailable"

    # 4. Cron job metrics
    try:
        from crons.manager import get_job_metrics
        cron_metrics = get_job_metrics()
    except Exception:
        cron_metrics = "unavailable"

    # 5. Last sync time
    try:
        latest_sync = Path(os.path.expanduser('~/nina/docs/space/nina_latest.md'))
        if latest_sync.exists():
            mtime = latest_sync.stat().st_mtime
            last_sync_time = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_sync_time = "unavailable (file not found)"
    except Exception:
        last_sync_time = "unavailable"

    page_load_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template(
        'dashboard.html',
        service_status=service_status,
        provider_health=provider_health,
        tasks_summary=tasks_summary,
        cron_metrics=cron_metrics,
        last_sync_time=last_sync_time,
        page_load_time=page_load_time
    )

@app.route('/api/godvision')
def api_godvision():
    import json
    import re
    
    response_data = {
        "context_graph": {},
        "backlog_stats": {"DONE": 0, "TODO_P1": 0, "TODO_P2": 0, "TODO_P3": 0, "NEEDS_SPEC": 0},
        "errors": {"open_count": 0, "items": []},
        "queue": {"active": [], "waiting": []},
        "system_status": {
            "nina": "inactive",
            "ninagate": "inactive",
            "ninajulesgithub": "inactive",
            "nina_dashboard": "inactive"
        }
    }

    # 1. Load context graph
    try:
        graph_path = BASE_DIR / "nina_context_graph.json"
        if graph_path.exists():
            with open(graph_path, 'r') as f:
                response_data["context_graph"] = json.load(f)
    except Exception:
        pass

    # 2. Parse jules_backlog.md for stats
    try:
        backlog_path = BASE_DIR / "docs/space/jules_backlog.md"
        if backlog_path.exists():
            with open(backlog_path, 'r') as f:
                content = f.read()
                response_data["backlog_stats"]["DONE"] = len(re.findall(r'✅ DONE', content)) + len(re.findall(r'✅ Confirmed done', content))
                response_data["backlog_stats"]["TODO_P1"] = len(re.findall(r'🔴 TODO-P1', content)) + len(re.findall(r'🔴 P1', content))
                response_data["backlog_stats"]["TODO_P2"] = len(re.findall(r'🟠 TODO-P2', content)) + len(re.findall(r'🟠 P2', content))
                response_data["backlog_stats"]["TODO_P3"] = len(re.findall(r'🟡 TODO-P3', content)) + len(re.findall(r'🟡 P3', content))
                response_data["backlog_stats"]["NEEDS_SPEC"] = len(re.findall(r'📋 NEEDS SPEC', content)) + len(re.findall(r'📋 Needs spec', content))
    except Exception:
        pass

    # 3. Parse nina_error_register.md for open errors
    try:
        error_path = BASE_DIR / "docs/space/nina_error_register.md"
        if error_path.exists():
            with open(error_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "OPEN" in line:
                        response_data["errors"]["open_count"] += 1
                        # extract brief description
                        parts = [p.strip() for p in line.split('|') if p.strip()]
                        if len(parts) > 1:
                            response_data["errors"]["items"].append(parts[1])
    except Exception:
        pass

    # 4. Parse jules_queue.md for active / waiting tasks
    try:
        queue_path = BASE_DIR / "docs/space/jules_queue.md"
        if queue_path.exists():
            with open(queue_path, 'r') as f:
                content = f.read()
                # Parse ACTIVE table
                active_section = re.search(r'## ACTIVE.*?(?=## QUEUE|## COMPLETED|$)', content, re.DOTALL)
                if active_section:
                    for line in active_section.group(0).split('\n'):
                        if '|' in line and 'File' not in line and '---' not in line and '_empty_' not in line:
                            parts = [p.strip() for p in line.split('|') if p.strip()]
                            if len(parts) >= 3:
                                response_data["queue"]["active"].append({"file": parts[0], "task_id": parts[1], "session": parts[2]})
    except Exception:
        pass

    # 5. Service statuses
    for svc in ["nina", "ninagate", "ninajulesgithub", "nina-dashboard"]:
        try:
            status = subprocess.check_output(['systemctl', 'is-active', f'{svc}.service'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
            response_data["system_status"][svc] = status
        except Exception:
            response_data["system_status"][svc] = "inactive"

    return app.response_class(
        response=json.dumps(response_data, indent=2),
        status=200,
        mimetype='application/json'
    )

def run_dashboard_heartbeat():
    import threading, time
    from tools.heartbeat import write_heartbeat
    def hb_loop():
        while True:
            time.sleep(60)
            write_heartbeat("nina-dashboard.service")
    threading.Thread(target=hb_loop, daemon=True).start()

if __name__ == '__main__':
    run_dashboard_heartbeat()
    app.run(host='127.0.0.1', port=8766)

