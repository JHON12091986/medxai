"""
NinaJulesGitHub — Autonomous Jules/GitHub Pipeline Daemon v1.0
==============================================================
Self-sustaining 3-minute loop managing the Jules→PR→merge pipeline
independently of NINA. Never blocks Gemini CLI.
"""

import time
import subprocess
import logging
import json
import os
import fcntl
from pathlib import Path
from datetime import datetime

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

from core.config import load_config
from core.logger import get_logger
import tools.jules as jules

logger = get_logger("nina.pipeline.github")

REPO_ROOT = Path(__file__).parent.resolve()
LOCK_FILE = REPO_ROOT / "data" / "ninajulesgithub.lock"
JULESLOCK_TXT = REPO_ROOT / "juleslock.txt"
LOOP_INTERVAL = 180  # 3 minutes

def _git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=REPO_ROOT)

def _try_rebase(branch: str) -> tuple[bool, str]:
    """Attempt to rebase a Jules branch against main and force-push."""
    logger.info(f"Attempting rebase for branch: {branch}")
    
    if _git("fetch", "origin", branch).returncode != 0:
        return False, "fetch failed"

    # Stash any working-tree modifications (e.g. registry/responded JSON writes
    # from Phase 1) so git rebase can proceed cleanly.
    dirty = bool(_git("status", "--porcelain").stdout.strip())
    if dirty:
        _git("stash", "--include-untracked", "-q")

    _git("checkout", "-B", branch, f"origin/{branch}")
    rebase = _git("rebase", "origin/main")
    if rebase.returncode != 0:
        _git("rebase", "--abort")
        _git("checkout", "main")
        if dirty:
            _git("stash", "pop", "-q")
        return False, f"rebase conflict: {rebase.stderr[:200]}"

    push = _git("push", "origin", branch, "--force-with-lease")
    _git("checkout", "main")
    if dirty:
        _git("stash", "pop", "-q")
    if push.returncode != 0:
        return False, f"force-push failed: {push.stderr[:200]}"
        
    return True, "OK"

def audit_and_merge():
    """Main lifecycle: Audit open PRs, rebase, and merge if healthy."""
    try:
        # 1. Fetch latest state
        _git("fetch", "origin", "main")
        
        # 2. List open Jules PRs via gh CLI
        res = subprocess.run(["gh", "pr", "list", "--label", "jules", "--json", "number,headRefName,mergeable,mergeStateStatus,title"], capture_output=True, text=True)
        if res.returncode != 0:
            logger.error("Failed to list PRs via gh CLI")
            return
            
        prs = json.loads(res.stdout)
        if not prs:
            logger.info("No open Jules PRs found.")
            return

        for pr in prs:
            num = pr["number"]
            branch = pr["headRefName"]
            status = pr["mergeStateStatus"]
            
            logger.info(f"Auditing PR #{num} ({branch}) - Status: {status}")
            
            if status == "DIRTY":
                # Conflicting. Try automatic rebase.
                ok, msg = _try_rebase(branch)
                if not ok:
                    logger.warning(f"PR #{num} rebase failed: {msg}")
                    continue
                logger.info(f"PR #{num} rebase successful. Waiting for next cycle.")
                continue

            if status == "CLEAN":
                # Healthy. Merge it.
                logger.info(f"PR #{num} is CLEAN. Merging...")
                merge = subprocess.run(["gh", "pr", "merge", str(num), "--merge", "--delete-branch"], capture_output=True, text=True)
                if merge.returncode == 0:
                    logger.info(f"✅ PR #{num} merged successfully.")
                    # Run post-merge sync
                    subprocess.run(["bash", "./nina_sync.sh"], cwd=REPO_ROOT)
                else:
                    logger.error(f"❌ PR #{num} merge failed: {merge.stderr}")

    except Exception as e:
        logger.exception(f"Error in audit_and_merge cycle: {e}")

def main():
    # Ensure data directory exists
    (REPO_ROOT / "data").mkdir(exist_ok=True)
    
    with open(LOCK_FILE, "w") as lf:
        try:
            fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("NinaJulesGitHub started")
            while True:
                audit_and_merge()
                time.sleep(LOOP_INTERVAL)
        except BlockingIOError:
            logger.error("Another instance of NinaJulesGitHub is already running")
        except KeyboardInterrupt:
            logger.info("NinaJulesGitHub stopped by signal")
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)

if __name__ == "__main__":
    main()
