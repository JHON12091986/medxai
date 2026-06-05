import asyncio
import os
import sys
import fcntl
import time
import signal
import logging
from core.nina import NinaOS

logger = logging.getLogger("main")

def acquire_lock():
    os.makedirs("data", exist_ok=True)
    pid_file = "data/nina.pid"
    lock_file = "data/nina.lock"

    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
            if os.path.exists(f"/proc/{old_pid}"):
                logger.info("Ghost process %s is running. Sending SIGTERM.", old_pid)
                os.kill(old_pid, signal.SIGTERM)
                for _ in range(50):
                    time.sleep(0.1)
                    if not os.path.exists(f"/proc/{old_pid}"):
                        break
                else:
                    logger.warning("Process %s did not respond to SIGTERM after 5 seconds.", old_pid)
        except (ValueError, OSError):
            pass

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    global _lock_fd
    _lock_fd = open(lock_file, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.error("nina.lock held, cannot start")
        sys.exit(1)

async def main():
    nina = NinaOS()
    await nina.start()
    await asyncio.Event().wait()   # keep alive forever

if __name__ == "__main__":
    acquire_lock()
    asyncio.run(main())
