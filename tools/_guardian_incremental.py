"""
Guardian incremental scan helpers.
NINA_FEATURE: guardian-incremental-ast v1.0
Import from guardian_engine.py: from tools._guardian_incremental import changed_py_files, baseline_needs_refresh
"""
import subprocess, time, json
from pathlib import Path

NINA_DIR   = Path.home() / "nina"
STAMP_FILE = NINA_DIR / ".cache" / "guardian_last_run.json"

def _git_changed_since(ref: str = "HEAD") -> list[Path]:
    """Return absolute paths of .py files changed vs HEAD (staged+unstaged)."""
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", ref],
            capture_output=True, text=True, cwd=NINA_DIR
        )
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=NINA_DIR
        )
        paths = set((r.stdout + staged.stdout).splitlines())
        return [NINA_DIR / p for p in paths if p.endswith(".py") and (NINA_DIR / p).exists()]
    except Exception:
        return []

def changed_py_files(full_tracked: list, force_full: bool = False) -> tuple[list, bool]:
    """
    Return (files_to_scan, is_full_scan).
    Uses git diff for incremental; falls back to full list if <3 files changed
    or force_full=True or cache is >6h old.
    """
    if force_full:
        return full_tracked, True

    stamp = {}
    if STAMP_FILE.exists():
        try: stamp = json.loads(STAMP_FILE.read_text())
        except: pass

    age = time.time() - stamp.get("ts", 0)
    if age > 21600:  # 6 hours → force full
        return full_tracked, True

    changed = _git_changed_since()
    # Filter to only files that are in TRACKED_PY_FILES
    tracked_set = {str(p) for p in full_tracked}
    relevant = [p for p in changed if str(p) in tracked_set]

    if len(relevant) == 0:
        return [], False   # nothing changed — skip entirely
    return relevant, False

def stamp_run(full: bool, scanned: int):
    STAMP_FILE.parent.mkdir(exist_ok=True)
    STAMP_FILE.write_text(json.dumps({"ts": time.time(), "full": full, "scanned": scanned}))

def baseline_needs_refresh(baseline_file: Path) -> bool:
    """True if baseline is missing or >24h old."""
    if not baseline_file.exists(): return True
    return (time.time() - baseline_file.stat().st_mtime) > 86400
