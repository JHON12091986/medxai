from checks.runner import record
import importlib.util

REQUIRED_PACKAGES = [
    ("telegram",    "python-telegram-bot",  "BLOCKER"),
    ("apscheduler", "APScheduler",          "BLOCKER"),
    ("pydantic",    "pydantic",             "BLOCKER"),
    ("dotenv",      "python-dotenv",        "BLOCKER"),
    ("aiohttp",     "aiohttp",              "BLOCKER"),
    ("aiofiles",    "aiofiles",             "BLOCKER"),
    ("psutil",      "psutil",               "BLOCKER"),
    ("numpy",       "numpy",                "BLOCKER"),
    ("pyflakes",    "pyflakes",             "WARN"),
    ("mypy",        "mypy",                 "WARN"),
]
def check_packages():
    for import_name, pip_name, level in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            record("PASS", f"pkg.{import_name}", f"Package present: {import_name}")
        else:
            record(
                level, f"pkg.{import_name}_missing",
                f"Package missing: {import_name} ({pip_name})",
                detail=f"import {import_name} failed — module not found in current Python path.",
                fix=f"Run: source ~/nina/venv/bin/activate && pip install {pip_name}",
            )
