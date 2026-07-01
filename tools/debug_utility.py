#!/usr/bin/env python3
"""
tools/debug_utility.py
Unified, interactive debugging utility that implements all 5 operational diagnostic modes:
1. Live Telemetry & TUI Dashboard
2. Live Systemd Journal Logs (stream tailing)
3. Application log files under logs/ (nina.log, router.log)
4. Interactive NinaGate Endpoint Diagnostics (v1/status & chat/completions loop verification)
5. Pre-flight Health & Governance Index Validation dry-runs
"""

import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# Color and style codes for pretty printing
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[H\033[2J"

REPO_ROOT = Path(__file__).parent.parent.resolve()
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3"

def print_header(title):
    print(CLEAR)
    print(f"{BLUE}{BOLD}" + "═" * 60)
    print(f"  NINA DEBUG UTILITY — {title}")
    print("═" * 60 + f"{RESET}\n")

def pause_and_continue():
    input(f"\n{YELLOW}Press Enter to return to the menu...{RESET}")

def launch_tui_dashboard():
    """Mode 1: Launch the TUI dashboard."""
    print_header("TUI Dashboard Launcher")
    dashboard_script = REPO_ROOT / "tools" / "nina_dashboard.py"
    if not dashboard_script.exists():
        print(f"{RED}❌ Error: TUI dashboard script not found at {dashboard_script}{RESET}")
        pause_and_continue()
        return

    print(f"{GREEN}🚀 Starting TUI Dashboard (python {dashboard_script})...{RESET}\n")
    try:
        subprocess.run([sys.executable, str(dashboard_script)], cwd=REPO_ROOT)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{RED}❌ Failed to start dashboard: {e}{RESET}")
        pause_and_continue()

def stream_systemd_logs():
    """Mode 2: Stream Systemd Journal Logs."""
    while True:
        print_header("Systemd Service Log Viewer")
        print("Select a service to tail logs:")
        print(f"1) {GREEN}nina.service{RESET}             - Main AI orchestrator")
        print(f"2) {GREEN}ninagate.service{RESET}         - Inbound proxy server")
        print(f"3) {GREEN}ninajulesgithub.service{RESET}  - Jules CI/CD pipeline")
        print(f"4) {GREEN}nina-dashboard.service{RESET}   - Live TUI background logger")
        print("5) Back to main menu")

        choice = input(f"\n{BOLD}Choice [1-5]:{RESET} ").strip()
        if choice == "5":
            break

        service_map = {
            "1": "nina.service",
            "2": "ninagate.service",
            "3": "ninajulesgithub.service",
            "4": "nina-dashboard.service"
        }

        service_name = service_map.get(choice)
        if not service_name:
            print(f"{RED}Invalid choice.{RESET}")
            time.sleep(1)
            continue

        print_header(f"Tailing logs for {service_name}")
        print(f"{YELLOW}Press Ctrl+C to stop streaming.{RESET}\n")
        try:
            subprocess.run(["journalctl", "-u", service_name, "-f", "-n", "50"])
        except KeyboardInterrupt:
            print(f"\n{GREEN}Stopped streaming.{RESET}")
            time.sleep(1.5)

def stream_app_logs():
    """Mode 3: Tail application logs under logs/."""
    while True:
        print_header("Application Log File Tailer")
        print("Select an application log file to tail:")
        print(f"1) {GREEN}logs/nina.log{RESET}       - Orchestrator reasoning & actions")
        print(f"2) {GREEN}logs/router.log{RESET}     - Routing tiers, latencies & fallbacks")
        print(f"3) {GREEN}telemetry.jsonl{RESET}     - Raw telemetry JSON records")
        print("4) Back to main menu")

        choice = input(f"\n{BOLD}Choice [1-4]:{RESET} ").strip()
        if choice == "4":
            break

        file_map = {
            "1": "logs/nina.log",
            "2": "logs/router.log",
            "3": "telemetry.jsonl"
        }

        file_path = file_map.get(choice)
        if not file_path:
            print(f"{RED}Invalid choice.{RESET}")
            time.sleep(1)
            continue

        full_path = REPO_ROOT / file_path
        if not full_path.exists():
            print(f"{RED}❌ Log file {file_path} does not exist yet.{RESET}")
            pause_and_continue()
            continue

        print_header(f"Tailing {file_path}")
        print(f"{YELLOW}Press Ctrl+C to stop tailing.{RESET}\n")
        try:
            subprocess.run(["tail", "-f", "-n", "50", str(full_path)])
        except KeyboardInterrupt:
            print(f"\n{GREEN}Stopped streaming.{RESET}")
            time.sleep(1.5)

def run_ninagate_diagnostics():
    """Mode 4: Interactive NinaGate Endpoint Diagnostics."""
    print_header("Interactive NinaGate Diagnostic Suite")
    
    # Check if NinaGate is reachable
    print(f"{BLUE}1. Ping-checking localhost:8080/v1/status...{RESET}")
    status_url = "http://localhost:8080/v1/status"
    try:
        req = urllib.request.Request(status_url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            print(f"{GREEN}✅ NinaGate is active and running!{RESET}")
            print(f"{BOLD}Status Payload:{RESET}")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"{RED}❌ NinaGate is unreachable or inactive: {e}{RESET}")
        print(f"{YELLOW}Pro-tip: Start the service with: sudo systemctl start ninagate.service{RESET}")
        pause_and_continue()
        return

    # Prompt user to run model routing checks
    print(f"\n{BLUE}2. Running Live Model Routing Verification...{RESET}")
    completions_url = "http://localhost:8080/v1/chat/completions"
    payload = {
        "model": "gemini-2.5-flash",
        "messages": [
            {"role": "system", "content": "You are a speed-test utility. Reply ONLY with 'OK' and nothing else."},
            {"role": "user", "content": "Ping test"}
        ],
        "temperature": 0.0
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending speed-test prompt payload to {GREEN}{completions_url}{RESET}...")
    try:
        start_time = time.time()
        data_encoded = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(completions_url, data=data_encoded, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = time.time() - start_time
            response_data = json.loads(resp.read().decode())
            print(f"\n{GREEN}✅ Response received successfully in {elapsed:.3f} seconds!{RESET}")
            reply = response_data["choices"][0]["message"]["content"]
            print(f"Model reply: {BOLD}{reply}{RESET}")
            print(f"Usage summary: {json.dumps(response_data.get('usage', {}))}")
    except Exception as e:
        print(f"\n{RED}❌ Model routing failed: {e}{RESET}")

    pause_and_continue()

def run_preflight_checks():
    """Mode 5: Run health check & governance index validation."""
    print_header("Pre-flight Health & Governance Diagnostics")
    
    print(f"{BLUE}1. Running Environment and Dependency Checks (healthcheck.py)...{RESET}")
    try:
        subprocess.run([sys.executable, "healthcheck.py"], cwd=REPO_ROOT, check=True)
        print(f"{GREEN}✅ Environment and dependencies are perfectly healthy!{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}❌ Healthcheck failed. Review errors above.{RESET}")
        
    print(f"\n{BLUE}2. Running Governance Index Schema Verification (validate_index.py)...{RESET}")
    try:
        subprocess.run([sys.executable, "tools/validate_index.py"], cwd=REPO_ROOT, check=True)
        print(f"{GREEN}✅ Governance index is perfectly valid and compliant!{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}❌ Governance validation flagged potential warnings/errors above.{RESET}")

    pause_and_continue()

def main_menu():
    while True:
        print_header("Unified System Diagnostics Panel")
        print("Please choose a debugging option:")
        print(f"1) {GREEN}Live Telemetry & TUI Dashboard{RESET}      - View real-time operations")
        print(f"2) {GREEN}Live Systemd Journal Logs{RESET}           - Stream service journals")
        print(f"3) {GREEN}Application Log File Viewer{RESET}         - Tail nina.log and router.log")
        print(f"4) {GREEN}NinaGate Endpoint Diagnostic Suite{RESET}  - Test endpoints & routing health")
        print(f"5) {GREEN}Pre-flight Health & Index Check{RESET}     - Dry-run validation checks")
        print("6) Exit debug panel")

        choice = input(f"\n{BOLD}Select option [1-6]:{RESET} ").strip()
        if choice == "6":
            print(f"\n{BLUE}Exiting diagnostic panel. Keep your code healthy!{RESET}")
            break
        elif choice == "1":
            launch_tui_dashboard()
        elif choice == "2":
            stream_systemd_logs()
        elif choice == "3":
            stream_app_logs()
        elif choice == "4":
            run_ninagate_diagnostics()
        elif choice == "5":
            run_preflight_checks()
        else:
            print(f"{RED}Invalid option, try again.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{BLUE}Exiting debug panel.{RESET}")
