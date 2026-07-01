# Busca esto o algo parecido en tu main.py
# nina_os.telegram_interface.send_message("NINA ready...") 
# O cualquier línea que llame a .send_message al arrancar
import asyncio
import os
import sys
import time
import signal
import logging
from core.nina import Nina

# --- Bloque de compatibilidad para Windows ---
try:
    import fcntl
except ImportError:
    class FcntlMock:
        def flock(self, fd, op): pass
        LOCK_EX = 0
        LOCK_SH = 0
        LOCK_NB = 0
    fcntl = FcntlMock()

logger = logging.getLogger("main")

def acquire_lock():
    os.makedirs("data", exist_ok=True)
    pid_file = "data/nina.pid"
    lock_file = "data/nina.lock"

    # Solo intentamos gestionar procesos 'fantasma' si estamos en un entorno tipo Unix
    if sys.platform != 'win32' and os.path.exists(pid_file):
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
<<<<<<< HEAD
=======
                else:
                    logger.warning("Process %s did not respond to SIGTERM, sending SIGKILL.", old_pid)
                    try:
                        os.kill(old_pid, signal.SIGKILL)
                        time.sleep(0.5)
                    except OSError:
                        pass
            else:
                logger.info("Stale pid file for dead process %s — clearing.", old_pid)
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730
        except (ValueError, OSError):
            pass
        try:
            os.remove(pid_file)
        except OSError:
            pass
        try:
            os.remove(lock_file)
        except OSError:
            pass

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    global _lock_fd
    _lock_fd = open(lock_file, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
<<<<<<< HEAD
    except (BlockingIOError, AttributeError):
        logger.error("nina.lock held, cannot start")
=======
    except BlockingIOError:
        logger.error("nina.lock held by another live process, cannot start")
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730
        sys.exit(1)

async def watchdog_loop():
    try:
        from scripts.nina_watchdog_ping import watchdog_ping_async, notify_ready
        notify_ready()
        while True:
            await watchdog_ping_async()
            await asyncio.sleep(30)
    except Exception as e:
        logger.warning(f"Watchdog ping failed: {e}")

async def main():
    nina = Nina()
    # Cambiamos la forma de iniciar para evitar llamadas automáticas de reporte
    await nina.start()
<<<<<<< HEAD
    logger.info("NINA sistema en espera. Servicio activo.") 
    await asyncio.Event().wait()
=======
    ping_task = asyncio.create_task(watchdog_loop())
    try:
        await asyncio.Event().wait()   # keep alive forever
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Shutdown signal received — exiting cleanly.")
    finally:
        ping_task.cancel()
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730

if __name__ == "__main__":
    acquire_lock()
    try:
        asyncio.run(main())
<<<<<<< HEAD
    except KeyboardInterrupt:
        logger.info("NINA detenido por el usuario.")
=======
    except (KeyboardInterrupt, SystemExit):
        pass
    sys.exit(0)
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730
