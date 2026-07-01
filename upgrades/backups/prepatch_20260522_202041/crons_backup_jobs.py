
"""NINA v12 — Backup jobs"""
import logging, shutil, time, zipfile
from pathlib import Path

logger = logging.getLogger("nina.scheduler")

BACKUP_ROOT = Path("upgrades/backups")

async def run_memory_backup(nina_os):
    try:
        path = await nina_os.memory.backup()
        logger.info(f"memory_backup_ok dest={path}")
    except Exception as e:
        logger.warning(f"memory_backup_failed {e}")

async def run_py_backup(nina_os):
    try:
        ts = time.strftime("%Y%m%d%H%M%S")
        dest = BACKUP_ROOT / f"py_{ts}.zip"
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        root = Path(".")
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in root.rglob("*.py"):
                if ".venv" not in f.parts and "venv" not in f.parts:
                    zf.write(f)
        logger.info(f"py_backup_ok dest={dest}")
    except Exception as e:
        logger.warning(f"py_backup_failed {e}")
