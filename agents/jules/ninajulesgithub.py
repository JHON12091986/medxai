"""
NinaJulesGitHub — Autonomous Jules/GitHub Pipeline Daemon v1.0
==============================================================
Self-sustaining 3-minute loop managing the Jules→PR→merge pipeline
independently of NINA. Never blocks Gemini CLI.
"""

import time
import subprocess
import json
import fcntl
from pathlib import Path

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

from core.logger import get_logger
import tools.jules as jules

logger = get_logger("nina.pipeline.github")

REPO_ROOT = Path(__file__).parent.resolve()
LOCK_FILE = REPO_ROOT / "data" / "ninajulesgithub.lock"
JULESLOCK_TXT = REPO_ROOT / "juleslock.txt"
LOOP_INTERVAL = 180  # 3 minutes

def audit_and_merge():
    """Main lifecycle: Audit open PRs, rebase, and merge if healthy by delegating to tools/surgical_merge.py."""
    try:
        # Auto-unblock any awaiting sessions first
        try:
            import asyncio
            asyncio.run(jules.auto_unblock_awaiting())
        except Exception as e:
            logger.error(f"Auto-unblock failed in pipeline: {e}")

        # Watch and notify via Telegram of session failure/status updates
        try:
            import asyncio
            asyncio.run(jules.watch_cycle())
        except Exception as e:
            logger.error(f"Watch cycle failed in pipeline: {e}")

        # Delegate entirely to the robust, canonical surgical merge tool
        logger.info("Triggering unified surgical PR audit, rebase, and merge pipeline...")
        python_bin = str(REPO_ROOT / "venv" / "bin" / "python") if (REPO_ROOT / "venv" / "bin" / "python").exists() else "python3"
        subprocess.run([python_bin, "tools/surgical_merge.py"], cwd=REPO_ROOT)

    except Exception as e:
        logger.exception(f"Error in audit_and_merge cycle: {e}")

def main():
    # Ensure data directory exists
    (REPO_ROOT / "data").mkdir(exist_ok=True)
    
    event_bus_path = REPO_ROOT / "logs" / "event_bus.jsonl"
    
    # Initialize file pointer to end of file to ignore past events
    last_pos = 0
    if event_bus_path.exists():
        last_pos = event_bus_path.stat().st_size

    with open(LOCK_FILE, "w") as lf:
        try:
            fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("NinaJulesGitHub started (Event-Driven Hive Mind Mode)")
            
            # Initial run on startup
            audit_and_merge()
            from tools.heartbeat import write_heartbeat; write_heartbeat("ninajulesgithub.service")
            
            last_periodic_run = time.time()
            
            while True:
                # 1. Non-blocking watch of the shared event bus file
                run_audit = False
                now = time.time()
                
                # Force periodic run every 180 seconds even if no events
                if now - last_periodic_run >= LOOP_INTERVAL:
                    run_audit = True
                    last_periodic_run = now
                
                if event_bus_path.exists():
                    try:
                        current_size = event_bus_path.stat().st_size
                        if current_size > last_pos:
                            with open(event_bus_path, "r") as ef:
                                ef.seek(last_pos)
                                new_lines = ef.readlines()
                            last_pos = current_size
                            
                            for line in new_lines:
                                if not line.strip():
                                    continue
                                try:
                                    event_data = json.loads(line)
                                    topic = event_data.get("topic")
                                    if topic in ("TASK_VERIFIED", "TASK_COMPLETED", "PR_CREATED"):
                                        logger.info(f"Event received: {topic} from {event_data.get('sender')}. Triggering immediate audit.")
                                        run_audit = True
                                        break
                                except Exception:
                                    pass
                        elif current_size < last_pos:
                            # File truncated/rotated, reset position
                            last_pos = current_size
                    except Exception as e:
                        logger.error(f"Error reading event bus in pipeline loop: {e}")

                if run_audit:
                    audit_and_merge()
                    last_periodic_run = time.time()
                
                # Write heartbeat and sleep briefly
                write_heartbeat("ninajulesgithub.service")
                time.sleep(2)  # Check events every 2 seconds
                
        except BlockingIOError:
            logger.error("Another instance of NinaJulesGitHub is already running")
        except KeyboardInterrupt:
            logger.info("NinaJulesGitHub stopped by signal")
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)

if __name__ == "__main__":
    main()
