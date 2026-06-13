from typing import Any
import sys
from loguru import logger
from pathlib import Path

NINA_DIR = Path("~/nina").expanduser().resolve()
LOGS_DIR = NINA_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Remove default handler
logger.remove()

# Sink 1: stderr with colorized human-readable format
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Sink 2: logs/nina.jsonl with JSON format
logger.add(
    LOGS_DIR / "nina.jsonl",
    serialize=True,
    rotation="10 MB",
    retention="7 days",
)

def get_logger(name: Any=None) -> Any:
    if name:
        return logger.bind(name=name)
    return logger
