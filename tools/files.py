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

async def read(path: str, lines: str = None, symbol: str = None) -> str:
    p = _safe(path)
    if not p.exists(): return f"File not found: {path}"

    try:
        data = p.read_bytes()
    except Exception as e:
        return f"Error reading file: {e}"

    text = data.decode(errors="replace")

    if symbol:
        import ast
        try:
            tree = ast.parse(text)
            start_lineno, end_lineno = None, None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
                    start_lineno = node.lineno
                    end_lineno = node.end_lineno
                    break

            if start_lineno and end_lineno:
                file_lines = text.splitlines(keepends=True)
                start_idx = max(0, start_lineno - 1 - 5)
                end_idx = min(len(file_lines), end_lineno + 5)
                text = "".join(file_lines[start_idx:end_idx])
            else:
                return f"Symbol '{symbol}' not found in {path}"
        except Exception as e:
            return f"Error parsing for symbol: {e}"

    elif lines:
        try:
            start_str, end_str = lines.split("-")
            start = int(start_str.strip())
            end = int(end_str.strip())
            file_lines = text.splitlines(keepends=True)
            start_idx = max(0, start - 1 - 5)
            end_idx = min(len(file_lines), end + 5)
            text = "".join(file_lines[start_idx:end_idx])
        except Exception as e:
            return f"Error parsing lines argument: {e}"

    if len(text.encode('utf-8')) > MAX_READ: return f"File too large (>{MAX_READ//1024}KB)."
    logger.info(f"file_read path={path!r} lines={lines} symbol={symbol}", extra={"log":"tools.log", "tool_name": "files"})
    return text

async def write(path: str, content: str, config) -> str:
    _disk_guard(config)
    p = _safe(path)
    if len(content.encode()) > MAX_WRITE: return f"Content too large (>{MAX_WRITE//1024//1024}MB)."
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    logger.info(f"file_write path={path!r} bytes={len(content)}", extra={"log":"tools.log", "tool_name": "files"})
    return f"Written: {path}"
