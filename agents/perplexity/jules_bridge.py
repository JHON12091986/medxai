"""perplexity/jules_bridge.py — thin wrapper for Jules task submission and polling.

Note: tools/jules.py exists (37KB) but operates via NINA's internal async pipeline.
This module wraps the Jules CLI directly via subprocess for relay's sync execution model,
and checks PR status via GitHub API for jules_poll.
"""
import subprocess
import logging
import os
import json
from pathlib import Path

from perplexity.log import log_action

logger = logging.getLogger("nina.perplexity.jules_bridge")
REPO_ROOT = Path(__file__).parent.parent


def jules_submit(spec_text: str, repo: str = "aibony/nina") -> tuple[bool, str, str]:
    """Submit a task to Jules CLI. Returns (success, task_id_or_empty, raw_output)."""
    # net-new: Jules CLI wrapper — tools/jules.py is async NINA pipeline, not CLI-based
    try:
        cmd = [
            "jules", "remote", "new",
            "--repo", repo,
            "--task", "start",
            "--session", spec_text[:4000]  # Jules CLI session limit guard
        ]
        r = subprocess.run(
            cmd, capture_output=True, text=True, shell=False,
            cwd=str(REPO_ROOT), timeout=30
        )
        raw = (r.stdout + r.stderr).strip()
        # Try to extract a task ID from output (format varies by Jules CLI version)
        task_id = ""
        for line in raw.splitlines():
            if "task" in line.lower() and any(c.isdigit() for c in line):
                # Extract last token that looks like an ID
                tokens = line.split()
                for tok in reversed(tokens):
                    if tok.strip("#:").isalnum():
                        task_id = tok.strip("#:")
                        break
            if task_id:
                break
        success = r.returncode == 0
        log_action(task_id or "unknown", "jules_submit", "ok" if success else "error",
                   f"repo={repo}")
        return success, task_id, raw
    except FileNotFoundError:
        msg = "jules CLI not found — is Jules installed and in PATH?"
        log_action("unknown", "jules_submit", "error", msg)
        return False, "", msg
    except Exception as e:
        log_action("unknown", "jules_submit", "error", str(e))
        return False, "", str(e)


def jules_poll(task_id: str, repo: str = "aibony/nina") -> tuple[str, str]:
    """Check Jules task status. Returns (status_string, detail). Non-blocking."""
    # net-new: poll via GitHub PR search by Jules' branch naming convention
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return "error", "GITHUB_TOKEN not set — cannot poll Jules PR status"
    try:
        import urllib.request
        url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=20"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "User-Agent": "nina-relay"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            prs = json.loads(resp.read().decode())
        # Jules typically creates branches like jules/task-<id> or jules-<id>
        for pr in prs:
            branch = pr.get("head", {}).get("ref", "")
            if task_id and task_id in branch:
                log_action(task_id, "jules_poll", "pr_open",
                           f"PR #{pr['number']}: {pr['title']}")
                return "pr_open", f"PR #{pr['number']}: {pr['title']}"
        log_action(task_id, "jules_poll", "not_found", "no matching open PR")
        return "not_found", "no matching open PR found"
    except Exception as e:
        log_action(task_id, "jules_poll", "error", str(e))
        return "error", str(e)
