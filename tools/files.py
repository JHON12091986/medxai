import logging
import psutil
from pathlib import Path

logger = logging.getLogger("nina.tools.files")
WORKSPACE = Path("data/workspace").resolve()
MAX_READ  = 1 * 1024 * 1024   # 1MB
MAX_WRITE = 5 * 1024 * 1024   # 5MB

def _safe(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    if not str(p).startswith(str(WORKSPACE)):
        raise PermissionError(f"Path traversal blocked: {path}")
    return p

def _disk_guard(config):
    pct = psutil.disk_usage("/").percent
    if pct >= config.disk_guard_pct:
        raise OSError(f"Disk {pct:.0f}% full — write blocked.")

async def read(path: str) -> str:
    p = _safe(path)
    if not p.exists(): return f"File not found: {path}"
    data = p.read_bytes()
    if len(data) > MAX_READ: return f"File too large (>{MAX_READ//1024}KB)."
    logger.info(f"file_read path={path!r}", extra={"log":"tools.log"})
    return data.decode(errors="replace")

async def write(path: str, content: str, config) -> str:
    _disk_guard(config)
    p = _safe(path)
    if len(content.encode()) > MAX_WRITE: return f"Content too large (>{MAX_WRITE//1024//1024}MB)."
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    logger.info(f"file_write path={path!r} bytes={len(content)}", extra={"log":"tools.log"})
    return f"Written: {path}"
