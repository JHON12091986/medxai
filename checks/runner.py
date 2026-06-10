import os
import sys
import json
import logging
import re
from pathlib import Path

# Setup global log to avoid undefined names
log = logging.getLogger("guardian")

NINA_DIR = Path("~/nina").expanduser().resolve()
JSON_MODE = "--json" in sys.argv
METRICS_MODE = "--metrics" in sys.argv

results = []
blocker_count = 0
warn_count = 0

def record(level, check_id, message, detail=None, fix=None):
    global blocker_count, warn_count
    if level == "BLOCKER":
        blocker_count += 1
    elif level == "WARN":
        warn_count += 1

    entry = {
        "level": level,
        "check_id": check_id,
        "title": message,
        "detail": detail or "",
        "fix": fix or "",
    }

    results.append(entry)

    if not JSON_MODE and not METRICS_MODE:
        color = ""
        reset = "\033[0m"
        if level == "PASS": color = "\033[92m"
        elif level == "INFO": color = "\033[94m"
        elif level == "WARN": color = "\033[93m"
        elif level == "DEBT": color = "\033[38;5;208m"
        elif level == "BLOCKER": color = "\033[91m"

        badge = f"{color}[{level:7}]{reset}"
        print(f"  {badge} {message}")
        if detail and level in ("WARN", "BLOCKER", "DEBT"):
            print(f"            └─ {detail}")
        if fix and level in ("WARN", "BLOCKER", "DEBT"):
            print(f"            └─ Fix: {fix}")

def emit_report():
    total  = len(results)
    passed = sum(1 for r in results if r["level"] == "PASS")

    if METRICS_MODE:
        pass
    elif JSON_MODE:
        output = {
            "healthcheck_version": "2.0",
            "timestamp": __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "python": sys.version,
            "blocker_count": blocker_count,
            "warn_count": warn_count,
            "pass_count": passed,
            "total_checks": total,
            "overall": "FAIL" if blocker_count > 0 else ("WARN" if warn_count > 0 else "PASS"),
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        print("")
        print("  " + "─" * 52)
        print(f"  Checks run  : {total}")
        print(f"  PASS        : {passed}")
        print(f"  WARN        : {warn_count}")
        print(f"  BLOCKER     : {blocker_count}")
        print("  " + "─" * 52)

        if blocker_count == 0:
            print("  ✔  PASS — all BLOCKER checks clear")
        else:
            print(f"  ✖  FAIL — {blocker_count} BLOCKER(s) must be resolved before deploy")
            print("")
            print("  Fixes required:")
            for r in results:
                if r["level"] == "BLOCKER":
                    print(f"    → [{r['check_id']}] {r['fix']}")

        print("")

    if not METRICS_MODE:
        return 0 if blocker_count == 0 else 1
    return 0

def get_prometheus_metrics():
    lines = []
    pid_file = NINA_DIR / "data" / "nina.pid"
    service_active = 0
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text(errors="replace").strip())
            if os.path.exists(f"/proc/{pid}"):
                service_active = 1
        except (ValueError, OSError):
            pass
    lines.append("# HELP nina_service_active NINA main service running status")
    lines.append("# TYPE nina_service_active gauge")
    lines.append(f"nina_service_active {service_active}")

    prov_file = NINA_DIR / "data" / "discoveredproviders.json"
    if prov_file.exists():
        try:
            providers = json.loads(prov_file.read_text(errors="replace"))
            lines.append("# HELP nina_provider_health Health status of AI providers")
            lines.append("# TYPE nina_provider_health gauge")
            for p in providers:
                pid_str = p.get("id", "UNKNOWN")
                healthy = 1 if p.get("healthy") else 0
                lines.append(f'nina_provider_health{{provider="{pid_str}"}} {healthy}')
        except (json.JSONDecodeError, OSError, ValueError) as e:
            log.error(f"Failed to read provider health metrics: {e}")
            pass

    mgr_path = NINA_DIR / "crons" / "manager.py"
    if mgr_path.exists():
        try:
            source = mgr_path.read_text(errors="replace")
            ids_found = re.findall(r"id\s*=\s*['\"]([^'\"]+)['\"]", source)
            lines.append("# HELP nina_cron_job_status Count of defined cron jobs")
            lines.append("# TYPE nina_cron_job_status gauge")
            lines.append(f'nina_cron_job_status{{status="defined"}} {len(ids_found)}')
        except (OSError, re.error) as e:
            log.warning(f"Failed to read cron job status metrics: {e}")
            pass
    return "\n".join(lines) + "\n"

def run_metrics_server(port=8000):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/metrics':
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; version=0.0.4')
                self.end_headers()
                metrics = get_prometheus_metrics()
                self.wfile.write(metrics.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")
        def log_message(self, format, *args):
            pass
    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    print(f"Serving Prometheus metrics on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

ENV_FILE    = NINA_DIR / ".env"
BLOCKER_EXCEPTIONS = (NameError, TypeError, AttributeError, ImportError, SyntaxError)
