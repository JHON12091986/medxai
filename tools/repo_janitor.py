import subprocess
import json
import os
import sys

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def cleanup():
    print("=== NINA REPO JANITOR ===")
    
    # 1. Close redundant PRs
    print("-> Checking for redundant/conflicting PRs...")
    prs_json = run_cmd("gh pr list --json number,title,mergeable,mergeStateStatus")
    if prs_json:
        prs = json.loads(prs_json)
        for pr in prs:
            if pr['mergeable'] == 'CONFLICTING' or pr['mergeStateStatus'] == 'DIRTY':
                print(f"   ! Closing conflicting PR #{pr['number']}: {pr['title']}")
                run_cmd(f"gh pr close {pr['number']} --comment 'Auto-closed by Janitor: Conflicting duplicate.'")

    # 2. Delete merged branches
    print("-> Pruning merged local branches...")
    run_cmd("git branch --merged main | grep -v 'main' | xargs -r git branch -d")
    
    # 3. Prune remote branches
    print("-> Pruning remote branches...")
    run_cmd("git remote prune origin")
    
    # 4. Force delete stale jules branches (remote)
    print("-> Force deleting stale Jules branches on remote...")
    remote_branches = run_cmd("git branch -r | grep 'origin/jules-'")
    for rb in remote_branches.splitlines():
        branch = rb.strip().replace("origin/", "")
        # Check if PR exists for this branch
        if not run_cmd(f"gh pr list --head {branch}"):
            print(f"   ! Deleting orphan remote branch: {branch}")
            run_cmd(f"git push origin --delete {branch}")

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    cleanup()
