"""
Surgical Merge Script v1.0
==========================
Surgically audits, rebases (if dirty), verifies, and merges all active open PRs.
"""

import sys
import json
import time
import subprocess
import asyncio
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from core.logger import get_logger
import tools.jules as jules

logger = get_logger("nina.tools.surgical_merge")

def _git(*args, check=True):
    res = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=str(REPO_ROOT))
    if check and res.returncode != 0:
        logger.error(f"Git command failed: git {' '.join(args)}\nStdout: {res.stdout}\nStderr: {res.stderr}")
    return res

def _gh(*args):
    res = subprocess.run(["gh"] + list(args), capture_output=True, text=True, cwd=str(REPO_ROOT))
    return res

async def verify_and_merge_pr(num: int, branch: str) -> bool:
    logger.info(f"Checking out PR #{num} (branch: {branch})...")
    _git("fetch", "origin", f"pull/{num}/head:{branch}", check=False)
    _git("checkout", branch)
    
    # Check if redundant (0 commits ahead of main)
    rev_res = _git("rev-list", "--count", "main..HEAD", check=False)
    if rev_res.returncode == 0:
        count = int(rev_res.stdout.strip())
        if count == 0:
            logger.info(f"PR #{num} has 0 commits ahead of main. Closing as redundant...")
            _gh("pr", "close", str(num), "-c", f"Closing redundant PR #{num} because all changes are already integrated into main.")
            _git("checkout", "main")
            return True

    # Run cognitive verification on the checked-out branch
    try:
        verified = await jules.verify_pr(num, branch)
    except Exception as e:
        logger.error(f"Error validating PR #{num}: {e}")
        verified = False
        
    _git("checkout", "main")
    
    if not verified:
        logger.warning(f"❌ PR #{num} failed cognitive verification.")
        return False
        
    logger.info(f"PR #{num} passed all checks. Merging...")
    m_res = _gh("pr", "merge", str(num), "--merge", "--delete-branch")
    if m_res.returncode == 0:
        logger.info(f"✅ PR #{num} successfully merged!")
        return True
    else:
        logger.error(f"❌ PR #{num} merge failed: {m_res.stderr.strip()}")
        return False

async def main():
    logger.info("Starting surgical merge process...")
    
    # Fetch latest remote changes
    _git("fetch", "origin", "main")
    _git("checkout", "main")
    _git("reset", "--hard", "origin/main")
    
    # List open PRs
    res = _gh("pr", "list", "--json", "number,headRefName,mergeable,mergeStateStatus,title")
    if res.returncode != 0:
        logger.error(f"Failed to list PRs: {res.stderr}")
        return
        
    all_prs = json.loads(res.stdout)
    logger.info(f"Found {len(all_prs)} open PRs.")
    
    for pr in all_prs:
        num = pr["number"]
        branch = pr["headRefName"]
        title = pr["title"]
        status = pr["mergeStateStatus"]
        
        logger.info(f"\n--- Auditing PR #{num}: {title} (branch: {branch}, status: {status}) ---")
        
        # Trigger GitHub mergeability check if UNKNOWN
        if status == "UNKNOWN":
            logger.info(f"Triggering mergeability refresh for PR #{num}...")
            # Query multiple times with sleep to let GitHub compute the state
            for attempt in range(3):
                refresh_res = _gh("pr", "view", str(num), "--json", "mergeStateStatus,mergeable")
                if refresh_res.returncode == 0:
                    data = json.loads(refresh_res.stdout)
                    status = data.get("mergeStateStatus", "UNKNOWN")
                    if status != "UNKNOWN":
                        logger.info(f"Mergeable status computed: {status}")
                        break
                time.sleep(2)
                
        if status == "DIRTY":
            logger.info(f"PR #{num} is DIRTY. Attempting automatic rebase...")
            # Fetch the branch locally
            _git("fetch", "origin", branch, check=False)
            _git("checkout", "-B", branch, f"origin/{branch}")
            rebase_res = _git("rebase", "main", check=False)
            if rebase_res.returncode != 0:
                _git("rebase", "--abort", check=False)
                logger.warning(f"❌ PR #{num} rebase failed. Manual resolution needed.")
                _git("checkout", "main")
                continue
                
            # Rebase succeeded, force push to update PR
            push_res = _git("push", "origin", branch, "--force-with-lease", check=False)
            _git("checkout", "main")
            if push_res.returncode == 0:
                logger.info(f"✅ PR #{num} successfully rebased and force-pushed. Checking verification...")
                # Verify and merge
                await verify_and_merge_pr(num, branch)
            else:
                logger.warning(f"❌ PR #{num} force-push failed.")
                
        elif status in ["CLEAN", "BEHIND", "BLOCKED", "UNKNOWN"]:
            # If BEHIND or clean, attempt to verify and merge.
            # If UNKNOWN, we still try checking it out and verifying/merging.
            await verify_and_merge_pr(num, branch)
            
    # Run sync at the very end (if not already invoked from within nina_sync.sh)
    import os
    if not os.environ.get("NINA_SYNC_ACTIVE"):
        logger.info("All PR audits completed. Synchronizing state...")
        subprocess.run(["bash", "scripts/nina_sync.sh"], cwd=str(REPO_ROOT))
    else:
        logger.info("All PR audits completed. (Invoked from nina_sync.sh, skipping re-entrant sync)")

if __name__ == "__main__":
    asyncio.run(main())
