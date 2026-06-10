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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8766)
