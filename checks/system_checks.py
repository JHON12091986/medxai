from checks.runner import record, NINA_DIR, log
import sys
import os
import subprocess
def check_data_dir():
    data_dir  = NINA_DIR / "data"
    lock_file = data_dir / "nina.lock"

    if not data_dir.exists():
        record(
            "WARN", "data_dir.missing",
            "data/ directory not found — will be created at startup",
            fix="Run: mkdir -p ~/nina/data",
        )
    else:
        record("PASS", "data_dir.present", "data/ directory present")

    if lock_file.exists():
        record(
            "INFO", "process.lock_file_present",
            "nina.lock file exists — normal if service is running",
        )

    pid_file = data_dir / "nina.pid"
    if pid_file.exists():
        pid_content = pid_file.read_text(errors="replace").strip()
        record("INFO", "process.pid_file", f"nina.pid contains: {pid_content}")

def check_log_dir():
    logs_dir = NINA_DIR / "logs"
    if not logs_dir.exists():
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            record("PASS", "logs_dir.created", "logs/ directory created")
        except OSError as e:
            log.warning(f"Could not create logs/ directory: {e}")
            record(
                "WARN", "logs_dir.create_fail",
                f"Could not create logs/ directory: {e}",
                fix="Run: mkdir -p ~/nina/logs && chmod 755 ~/nina/logs",
            )
    elif os.access(logs_dir, os.W_OK):
        record("PASS", "logs_dir.writable", "logs/ directory writable")
    else:
        record(
            "WARN", "logs_dir.not_writable",
            f"logs/ directory is not writable: {logs_dir}",
            fix="Run: chmod 755 ~/nina/logs",
        )

def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"

    if major < 3 or (major == 3 and minor < 10):
        record(
            "BLOCKER", "python.version_too_old",
            f"Python {version_str} is too old — NINA requires Python 3.10+",
            detail=f"Current: {sys.version}",
            fix="Activate the correct venv: source ~/nina/venv/bin/activate",
        )
    elif major == 3 and minor >= 14:
        record(
            "PASS", "python.version",
            f"Python {version_str} — meets requirement (3.14 confirmed compatible)",
        )
    else:
        record(
            "PASS", "python.version",
            f"Python {version_str} — OK",
        )

def check_ollama():
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "3", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and "models" in result.stdout.lower():
            record("PASS", "ollama.responding", "Ollama local inference responding")
        else:
            record(
                "INFO", "ollama.not_responding",
                "Ollama not responding at localhost:11434 (non-blocking — cloud fallback available)",
                fix="Run: sudo systemctl start ollama",
            )
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        log.warning(f"Ollama check failed: {e}")
        record(
            "INFO", "ollama.check_error",
            f"Ollama check failed: {e} (non-blocking)",
        )
