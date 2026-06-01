# DEPRECATED — logging initialised in core/nina.py start(). Safe to delete.

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
LOG_DIR = Path('logs')

def setup_logger(name: str = "nina") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Rotating file
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(
        LOG_DIR / "nina.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

log = setup_logger()