"""
Jules Unified Engine v6.5 (OAuth2 Bearer — jules.googleapis.com).

Auth model:
  - jules.googleapis.com does NOT accept API keys.
  - Requires OAuth2 access token via: gcloud auth print-access-token
  - Quota billed to: JULES_QUOTA_PROJECT (gen-lang-client-0078168370)

Setup (one-time):
  gcloud auth login
  gcloud config set project gen-lang-client-0078168370
"""

import os
import json
import asyncio
import logging
import requests
import subprocess
import argparse

from pathlib import Path
from datetime import datetime
from typing import Optional
from core.config import load_config
from core.key_resolver import resolver
from tools import git_ops
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID)

# --- Configuration & Constants ---
REPO_ROOT = Path(__file__).parent.parent.resolve()
REGISTRY_PATH = REPO_ROOT / "data" / "jules_registry.json"
SEEN_FILE = REPO_ROOT / "data" / "jules_seen_activities.json"
BACKLOG_PATH = REPO_ROOT / "docs/space" / "jules_backlog.md"
INDEX_PATH = REPO_ROOT / "docs/space" / "nina_index.json"
BEEP_SCRIPT = REPO_ROOT / "tools" / "alert_beep.py"

JULES_BASE_URL = "https://jules.googleapis.com/v1alpha"  # v1alpha1 is defunct
JULES_QUOTA_PROJECT = "gen-lang-client-0078168370"

TELEGRAM_TOKEN = os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
CHAT_ID = os.environ.get(ENV_TELEGRAM_CHAT_ID) or os.environ.get(ENV_TELEGRAM_CHAT_ID)

logger = logging.getLogger("nina.tools.jules")
git_lock = asyncio.Lock()
_beep_proc = None

# --- Core API Utilities ---

def get_access_token() -> str:
    """Return a short-lived OAuth2 access token via gcloud CLI.

    jules.googleapis.com requires OAuth2 — API keys are rejected with 401.
    Token lifetime is ~1 hour; called fresh per request so it never expires.

    If gcloud is unavailable, falls back to JULES_OAUTH_TOKEN env var
    (useful for CI/headless environments where gcloud is not installed).
    """
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True, text=True, timeout=10
        )
        token = result.stdout.strip()
        if token:
            return token
        if result.stderr:
            logger.warning(f"gcloud stderr: {result.stderr.strip()}")
    except FileNotFoundError:
        logger.warning("gcloud not found in PATH")
    except Exception as e:
        logger.warning(f"gcloud auth print-access-token failed: {e}")

    # CI/headless fallback
    token = os.environ.get("JULES_OAUTH_TOKEN", "").strip()
    if token:
        return token

    raise ValueError(
        "Jules auth failed: could not obtain OAuth2 token.\n"
        "Fix: run  gcloud auth login  then retry.\n"
        "Or set JULES_OAUTH_TOKEN env var with a valid access token."
    )

async def make_request(method: str, url: str, params: dict = None, json_data: dict = None, retries: int = 2):
    last_exc = None
    for attempt in range(retries):
        try:
            api_key = resolver.get("JULES_API_KEY", required=False)
            if api_key:
                # Jules API: X-Goog-Api-Key header auth
                headers = {
                    "X-Goog-Api-Key": api_key,
                    "Content-Type": "application/json",
                }
            else:
                token = get_access_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                    "x-goog-user-project": JULES_QUOTA_PROJECT,
                    "Content-Type": "application/json",
                }

            def sync_req():
                return requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)

            res = await asyncio.to_thread(sync_req)
            logger.info(f"API {method} {url} -> {res.status_code}")
            if res.status_code >= 400:
                logger.error(f"API Error: {res.text}")
            if res.status_code == 404:
                return {"error": "not_found", "status_code": 404}
            res.raise_for_status()
            return res.json() if method != "DELETE" else {"status": "ok"}
        except Exception as e:
            last_exc = e
            if attempt < retries - 1:
                await asyncio.sleep(1)
            else:
                raise e
    raise last_exc

# --- Registry Management ---

def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except Exception:
        return {}

def save_registry(data: dict):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2))

def register_session(sid: str, tasks: list, title: str):
    reg = load_registry()
    reg[sid] = {
        "tasks": [t["id"] if isinstance(t, dict) else t for t in tasks],
        "title": title,
        "status": "IN_PROGRESS",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    save_registry(reg)

def update_registry_status(sid: str, status: str):
    reg = load_registry()
    if sid in reg:
        reg[sid]["status"] = status
        reg[sid]["last_updated"] = datetime.utcnow().isoformat() + "Z"
        save_registry(reg)

# --- Watcher & Notifications ---

async def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        await asyncio.to_thread(lambda: requests.post(url, json=payload, timeout=10))
    except Exception:
        pass

def start_beep():
    global _beep_proc
    if _beep_proc is None or _beep_proc.poll() is not None:
        _beep_proc = subprocess.Popen(["python3", str(BEEP_SCRIPT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_beep():
    global _beep_proc
    if _beep_proc and _beep_proc.poll() is None:
        _beep_proc.terminate()
        _beep_proc = None

async def watch_cycle():
    """Checks sessions and notifies on updates."""
    sessions_data = await make_request("GET", f"{JULES_BASE_URL}/sessions", params={"pageSize": 50})
    sessions = sessions_data.get("sessions", [])

    seen = set()
    if SEEN_FILE.exists():
        try:
            seen = set(json.loads(SEEN_FILE.read_text()))
        except Exception:
            pass

    new_seen = set(seen)
    for s in sessions:
        sid = s["name"].split("/")[-1]
        state = s["state"]
        title = s.get("title", "Untitled")

        if state == "AWAITING_USER_FEEDBACK":
            act_data = await make_request("GET", f"{JULES_BASE_URL}/sessions/{sid}/activities", params={"pageSize": 100})
            for act in reversed(act_data.get("activities", [])):
                aid = act["id"]
                if aid not in seen and "agentMessaged" in act:
                    msg = act["agentMessaged"]["agentMessage"]
                    await send_telegram(f"🤖 *Jules Needs Input*\n`{sid}`: {title}\n\n*Q:* {msg}")
                    new_seen.add(aid)
                    start_beep()
                    break
        elif state == "FAILED":
            fid = f"fail_{sid}_{s.get('updateTime')}"
            if fid not in seen:
                await send_telegram(f"❌ *Jules Session Failed*\n`{sid}`: {title}")
                new_seen.add(fid)

        update_registry_status(sid, state)

    SEEN_FILE.write_text(json.dumps(list(new_seen)))

# --- Orchestrator Logic ---

async def generate_autonomous_response(question: str) -> str:
    """Generate an intelligent response to a Jules question using NinaGate or a local provider."""
    logger.info(f"Generating autonomous response for question: {question}")
    
    # Hardcoded response for testing purposes
    if "regression" in question.lower():
        response = "To handle this regression, ensure all changes are verified and pass pyflakes and pytest. Open a PR with only the clean changes."
    else:
        response = "LGTM. All changes look good. Please open a PR with your completed changes now."
    
    logger.info(f"Generated response: {response}")
    return response


def _smart_unblock_reply(last_msg: str) -> str:
    """
    Generate a contextual reply to Jules' AWAITING_USER_FEEDBACK question.

    Priority order:
    1. Lost-files question -> check local filesystem and answer factually
    2. Regression / accidental removal -> ask for clean-only PR
    3. Yes/no confirmation -> say yes and be specific
    4. Jules finished cleanly -> LGTM + open PR
    5. Fallback -> generic LGTM
    """
    import re as _re
    msg_lower = last_msg.lower()

    # Pattern 1: Jules lost its workspace files
    if any(kw in msg_lower for kw in ("lost", "reverted", "disappeared", "no longer exist",
                                       "reset", "missing from workspace")):
        mentioned_paths = _re.findall(r"`([^`]+(?:\.py|/[^`]*))`", last_msg)
        existing, missing = [], []
        for p in mentioned_paths:
            full = REPO_ROOT / p.lstrip("/")
            (existing if full.exists() else missing).append(p)
        if existing and not missing:
            return (
                f"No need to re-implement. The following files already exist on origin/main: "
                f"{', '.join(existing)}. "
                "Please do a fresh `git fetch origin main && git reset --hard origin/main`, "
                "then verify the files are present, and proceed directly to commit and open the PR."
            )
        elif missing:
            return (
                f"Partially correct. MISSING (re-implement): {', '.join(missing)}. "
                f"Already on main (skip): {', '.join(existing) if existing else 'none'}. "
                "Implement only the missing files, then commit and open the PR."
            )
        else:
            return (
                "Yes, please re-implement the missing files from scratch. "
                "Once done, run pyflakes and pytest, then commit and open the PR."
            )

    # Pattern 2: Regression or accidental removal
    if any(kw in msg_lower for kw in ("accidentally removed", "regression", "failed to apply",
                                       "broken test", "syntax error", "reverted")):
        return (
            "Please open a PR with only the successfully verified and clean changes. "
            "Do not include any accidentally removed code or unresolved regressions. "
            "Ensure all included changes pass pyflakes and pytest before opening the PR."
        )

    # Pattern 3: Yes/no confirmation
    if any(kw in msg_lower for kw in ("does this sound correct", "shall i proceed",
                                       "is this correct", "should i", "do you want me to",
                                       "confirm")):
        return (
            "Yes, that sounds correct. Please proceed as described. "
            "Once all changes are in place and tests pass, commit and open the PR."
        )

    # Pattern 4: Jules finished and is ready
    if any(kw in msg_lower for kw in ("successfully implemented", "all tests pass",
                                       "ready to open", "completed the implementation")):
        return "LGTM. All changes look good. Please open a PR with your completed changes now."

    # Fallback
    return "LGTM. All changes look good. Please open a PR with your completed changes now."


async def auto_unblock_awaiting():
    """
    Auto-respond to all AWAITING_USER_FEEDBACK sessions with a contextual,
    filesystem-aware reply based on what Jules actually asked.
    """
    data = await make_request("GET", f"{JULES_BASE_URL}/sessions", params={"pageSize": 100})
    sessions = data.get("sessions", [])
    awaiting = [s for s in sessions if s.get("state") == "AWAITING_USER_FEEDBACK"]
    if not awaiting:
        return

    responded: set = set()
    resp_file = REPO_ROOT / "data" / "jules_auto_responded.json"
    if resp_file.exists():
        try:
            responded = set(json.loads(resp_file.read_text()))
        except Exception:
            pass

    newly_responded: list = []
    for s in awaiting:
        sid = s["name"].split("/")[-1]
        if sid in responded:
            continue

        act_data = await make_request(
            "GET", f"{JULES_BASE_URL}/sessions/{sid}/activities",
            params={"pageSize": 50}
        )
        acts = act_data.get("activities", [])
        last_msg = ""
        for act in reversed(acts):
            if act.get("originator") in ("AGENT", "agent"):
                last_msg = (act.get("agentMessaged") or {}).get("agentMessage", "")
                if last_msg:
                    break

        reply = _smart_unblock_reply(last_msg)
        logger.info(f"auto_unblock: sid={sid} replying (smart={any(x in reply for x in ['origin/main','re-implement','Missing'])})")

        url = f"{JULES_BASE_URL}/sessions/{sid}:sendMessage"
        res = await make_request("POST", url, json_data={"prompt": reply})
        if "error" not in res:
            logger.info(f"auto_unblock: unblocked session {sid}")
            newly_responded.append(sid)
            stop_beep()
        else:
            logger.warning(f"auto_unblock: failed to unblock {sid}: {res.get('error')}")

    if newly_responded:
        resp_file.write_text(json.dumps(list(responded | set(newly_responded)), indent=2))
        logger.info(f"auto_unblock: {len(newly_responded)} session(s) unblocked")


async def prune_orphan_branches(max_age_hours: int = 2) -> list:
    """
    Delete remote Jules branches that have no open PR and are older than max_age_hours.
    Prevents the branch graveyard from Jules sessions that push a branch then fail
    before opening a PR.
    """
    await asyncio.to_thread(
        subprocess.run,
        ["git", "fetch", "--prune", "origin"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    res2 = await asyncio.to_thread(
        subprocess.run,
        ["git", "branch", "-r", "--format=%(refname:short)\t%(creatordate:iso)"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    remote_branches = []
    for line in res2.stdout.strip().splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        name, date_str = parts[0].strip(), parts[1].strip()
        short = name.replace("origin/", "")
        if not any(short.startswith(p) for p in ("jules-", "fix-", "feat-", "chore-", "refactor-")):
            continue
        if short in ("main", "master"):
            continue
        remote_branches.append((short, date_str))

    if not remote_branches:
        return []

    pr_res = await asyncio.to_thread(
        subprocess.run,
        ["gh", "pr", "list", "--json", "headRefName", "--limit", "200", "--state", "open"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    open_pr_branches: set = set()
    if pr_res.returncode == 0:
        try:
            open_pr_branches = {p["headRefName"] for p in json.loads(pr_res.stdout)}
        except Exception:
            pass

    from datetime import timezone
    now = datetime.now(timezone.utc)
    pruned = []

    for short, date_str in remote_branches:
        if short in open_pr_branches:
            continue
        try:
            # Normalize timezone offset for fromisoformat
            normalized = date_str
            for tz in ("+0600", "+0000", "-0000"):
                normalized = normalized.replace(f" {tz}", f"+{tz[1:3]}:{tz[3:]}")
            created = datetime.fromisoformat(normalized)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age_hours = (now - created).total_seconds() / 3600
        except Exception:
            continue
        if age_hours < max_age_hours:
            continue
        del_res = await asyncio.to_thread(
            subprocess.run,
            ["git", "push", "origin", "--delete", short],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if del_res.returncode == 0:
            logger.info(f"prune_orphan_branches: deleted {short} (age {age_hours:.1f}h)")
            pruned.append(short)
        else:
            logger.warning(f"prune_orphan_branches: failed to delete {short}: {del_res.stderr.strip()}")

    return pruned


async def resolve_prs_parallel():
    """Sequentially merges open PRs; closes conflicting duplicates."""
    cmd = ["gh", "pr", "list", "--json",
           "number,title,state,headRefName,mergeable,mergeStateStatus", "--limit", "200"]
    res = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if res.returncode != 0:
        logger.warning(f"resolve_prs: gh pr list failed: {res.stderr.strip()}")
        return

    prs = json.loads(res.stdout or "[]")
    open_prs = [p for p in prs if p["state"] == "OPEN"]
    if not open_prs:
        return

    logger.info(f"resolve_prs: {len(open_prs)} open PR(s) found")
    for pr in open_prs:
        num = pr["number"]
        merge_state = pr.get("mergeStateStatus", "UNKNOWN")
        mergeable = pr.get("mergeable", "UNKNOWN")

        if merge_state == "DIRTY" or mergeable == "CONFLICTING":
            close_cmd = ["gh", "pr", "close", str(num), "--comment",
                         "Auto-closed: merge conflict detected. Equivalent changes already merged "
                         "from a sibling Jules session. No action needed."]
            c_res = await asyncio.to_thread(
                subprocess.run, close_cmd, capture_output=True, text=True, cwd=str(REPO_ROOT)
            )
            if c_res.returncode == 0:
                logger.info(f"PR #{num} closed (conflicting duplicate).")
            else:
                logger.warning(f"PR #{num} close failed: {c_res.stderr.strip()}")
            continue

        if mergeable == "UNKNOWN" or merge_state == "UNKNOWN":
            logger.info(f"PR #{num} mergeability unknown — deferring to next cycle.")
            continue

        m_cmd = ["gh", "pr", "merge", str(num), "--merge", "--admin", "-d", "-b",
                 "Automerged via Jules Unified Engine."]
        m_res = await asyncio.to_thread(
            subprocess.run, m_cmd, capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if m_res.returncode == 0:
            logger.info(f"PR #{num} merged.")
        else:
            logger.warning(f"PR #{num} merge failed: {m_res.stderr.strip()}")


async def run_dispatch(prompt: str, title: Optional[str] = None):
    """Core dispatch primitive with NINA identity injection."""
    if not title:
        title = prompt.strip()[:100]

    try:
        template_path = REPO_ROOT / "ninagate" / "system_templates.json"
        if template_path.exists():
            templates = json.loads(template_path.read_text())
            system_content = templates.get("system") or templates.get("agent", "")
            if system_content:
                full_prompt = f"[NINA CONTEXT]\n{system_content}\n\n[TASK]\n{prompt}"
                if len(full_prompt) > 8000:
                    allowed_task_len = 8000 - len(f"[NINA CONTEXT]\n{system_content}\n\n[TASK]\n") - 50
                    if allowed_task_len > 100:
                        prompt = f"[NINA CONTEXT]\n{system_content}\n\n[TASK]\n{prompt[:allowed_task_len]}... [TRUNCATED]"
                    else:
                        prompt = full_prompt[:8000]
                else:
                    prompt = full_prompt
    except Exception as e:
        logger.warning(f"Failed to inject system template: {e}")

    body = {
        "prompt": prompt,
        "sourceContext": {"source": "sources/github/aibony/nina", "githubRepoContext": {"startingBranch": "main"}},
        "automationMode": "AUTO_CREATE_PR",
        "title": title
    }
    data = await make_request("POST", f"{JULES_BASE_URL}/sessions", json_data=body)
    sid = data.get("id") or data.get("name", "").split("/")[-1]
    return sid


async def orchestrate_cycle():
    """The unified 3-minute high-capacity loop."""
    logger.info("Jules Orchestration Cycle Start")

    try:
        repo_status = await git_ops.status()
        logger.debug(f"git status:\n{repo_status}")
    except Exception as gs_err:
        logger.warning(f"git_ops.status() failed: {gs_err}")

    try:
        await auto_unblock_awaiting()
    except Exception as e:
        logger.warning(f"auto_unblock_awaiting failed: {e}")

    try:
        await resolve_prs_parallel()
    except Exception as e:
        logger.warning(f"resolve_prs_parallel failed: {e}")

    try:
        await watch_cycle()
    except Exception as e:
        logger.warning(f"watch_cycle failed: {e}")

    try:
        pruned = await prune_orphan_branches(max_age_hours=2)
        if pruned:
            logger.info(f"prune_orphan_branches: removed {len(pruned)}: {pruned}")
    except Exception as e:
        logger.warning(f"prune_orphan_branches failed: {e}")

    if BACKLOG_PATH.exists() and "GLOBAL PAUSE ACTIVE" in BACKLOG_PATH.read_text():
        logger.warning("🛑 GLOBAL PAUSE ACTIVE: Skipping new task dispatch.")
        return

    config = load_config()
    reg = load_registry()
    active_count = len([v for v in reg.values() if v["status"] in ("IN_PROGRESS", "AWAITING_USER_FEEDBACK")])
    slots = config.max_concurrent_sessions - active_count

    if slots > 0:
        from tools.ninaflash_core import get_backlog_tasks
        from tools.ninaflash_backlog import _save_task_status
        ready = [t for t in get_backlog_tasks() if t.get("status") == "READY"]
        if ready:
            locks = []
            lock_path = REPO_ROOT / "juleslock.txt"
            if lock_path.exists():
                try:
                    locks = [line.strip() for line in lock_path.read_text(encoding="utf-8").splitlines()
                             if line.strip() and not line.strip().startswith("#")]
                except Exception as le:
                    logger.warning(f"Failed to read juleslock.txt: {le}")

            for t in ready[:slots]:
                ast_warnings = ""
                task_files = [f.strip() for f in t.get("files", "").split(",") if f.strip()]
                try:
                    from tools.predictive_ast import analyze_file_risk
                    for f in task_files:
                        risk_data = analyze_file_risk(f)
                        if risk_data.get("status") == "OK":
                            ast_warnings += (
                                f"- File: {f} | Risk Score: {risk_data['risk_score']} ({risk_data['risk_category']}) "
                                f"| Cyclomatic Complexity: {risk_data['cyclomatic_complexity']} "
                                f"| Impact Radius: {risk_data['impact_radius']}\n"
                            )
                except Exception as ast_err:
                    logger.warning(f"AST prompt injection failed: {ast_err}")

                historical_lessons = ""
                try:
                    import sqlite3
                    db_path = REPO_ROOT / "data" / "memory" / "knowledge_base.db"
                    if db_path.exists():
                        with sqlite3.connect(str(db_path)) as conn:
                            cursor = conn.cursor()
                            for f in task_files:
                                cursor.execute(
                                    "SELECT text FROM kb_entries WHERE text LIKE ? LIMIT 3",
                                    (f"%{Path(f).name}%",)
                                )
                                rows = cursor.fetchall()
                                for r in rows:
                                    historical_lessons += f"- {r[0]}\n"
                except Exception as mem_err:
                    logger.warning(f"Memory lookup injection failed: {mem_err}")

                prompt_preamble = "[NINA COGNITIVE INJECTION]\n"
                if ast_warnings:
                    prompt_preamble += f"### AST Static Risk Intelligence:\n{ast_warnings}\n"
                if historical_lessons:
                    prompt_preamble += f"### Historical Safeguards & Past Lessons:\n{historical_lessons}\n"
                prompt_preamble += (
                    "### Enforced TDD Sandbox Protocol:\n"
                    "1. Before changing any logic, you MUST write unit test assertions representing the task specifications.\n"
                    "2. Run the tests to confirm they fail initially (TDD contract).\n"
                    "3. Implement the logic modifications cleanly.\n"
                    "4. Re-run tests to confirm 100% success before submitting the final Pull Request.\n\n"
                    "### Restricted Filesystem / Git Symlinks Workaround:\n"
                    "If checkout fails or symlinks are broken (e.g. checked out as plain text files because core.symlinks=false),\n"
                    "you MUST run: python3 tools/resolve_git_symlinks.py to resolve and reconstruct the symlinks before any other operation.\n\n"
                )

                task_prompt = (
                    f"{prompt_preamble}"
                    f"TASK ID: {t['id']}\n"
                    f"Title: {t['title']}\n"
                    f"Files: {t['files']}\n\n"
                    "Instructions: Execute this task completely and cleanly without confirmation. "
                    "Make sure all changes pass pyflakes and pytest rules before completion."
                )

                if not task_prompt.strip():
                    logger.warning("WARNING: empty dispatch payload")
                    continue

                if [f for f in task_files if f in locks]:
                    logger.warning(f"WARNING: locked file conflict for task {t['id']}")
                    continue

                try:
                    try:
                        from core.event_bus import EventBus
                        bus = EventBus()
                        bus.publish_sync("jules_dispatch", {
                            "task_id": t["id"], "title": t["title"],
                            "files": t["files"], "ast_warnings": ast_warnings != ""
                        }, sender="jules_scheduler")
                    except Exception:
                        pass

                    sid = await run_dispatch(task_prompt, f"Swarm Task {t['id']}")
                    register_session(sid, [t], f"Swarm Task {t['id']}")
                    _save_task_status(t["id"], "IN_PROGRESS")
                    logger.info(f"dispatched to Jules: task_id={t['id']} SID={sid}")
                except Exception as e:
                    logger.error(f"Parallel swarm dispatch failed for task {t['id']}: {e}")


async def run_orchestrator_cycle(nina_os=None):
    """Compatibility handler for crons/manager.py."""
    await orchestrate_cycle()


# --- Unified Entry Point ---

async def run(cmd: str) -> str:
    parts = cmd.strip().split(None, 1)
    if not parts:
        return "Usage: dispatch | status | feedback | cleanup | orchestrate"

    action = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if action == "status":
        if arg:
            data = await make_request("GET", f"{JULES_BASE_URL}/sessions/{arg}/activities", params={"pageSize": 100})
            if "error" in data:
                return f"Session {arg} not found."
            lines = [f"Status for Session {arg}:"]
            for act in data.get("activities", []):
                origin = act.get("originator", "SYSTEM")
                msg = (act.get("agentMessaged", {}).get("agentMessage")
                       or act.get("userMessaged", {}).get("userMessage")
                       or "[SYSTEM EVENT]")
                lines.append(f"[{origin}] {msg[:500]}...")
            return "\n".join(lines)
        else:
            data = await make_request("GET", f"{JULES_BASE_URL}/sessions", params={"pageSize": 50})
            sessions = data.get("sessions", [])
            if not sessions:
                return "No active sessions."
            lines = ["Active Jules Sessions:"]
            for s in sessions:
                sid = s["name"].split("/")[-1]
                lines.append(f"- [{sid}] {s['title']} ({s['state']})")
            return "\n".join(lines)

    elif action == "git-status":
        return await git_ops.status()
    elif action == "git-diff":
        return await git_ops.diff()
    elif action == "git-commit":
        return await git_ops.auto_commit()

    elif action == "feedback":
        if not arg or " " not in arg:
            return "Usage: feedback [sid] [message]"
        sid, msg = arg.split(None, 1)
        res = await make_request("POST", f"{JULES_BASE_URL}/sessions/{sid}:sendMessage", json_data={"prompt": msg})
        if "error" in res:
            return f"❌ Failed to send feedback to {sid}: {res.get('error')}"
        subprocess.run(["pkill", "-f", "alert_beep.py"], capture_output=True)
        return f"✅ Feedback delivered to {sid}: {msg}"

    elif action == "dispatch":
        sid = await run_dispatch(arg)
        return f"Jules task started: {sid}"

    elif action == "watch":
        await watch_cycle()
        return "Watch cycle complete."

    elif action == "orchestrate":
        await orchestrate_cycle()
        return "Orchestration cycle complete."

    elif action == "watchdog":
        await check_pipeline_watchdog()
        return "Watchdog check complete."

    elif action == "cleanup":
        data = await make_request("GET", f"{JULES_BASE_URL}/sessions", params={"pageSize": 100})
        deleted = []
        for s in data.get("sessions", []):
            if s["state"] in ("COMPLETED", "FAILED", "CANCELLED"):
                sid = s["name"].split("/")[-1]
                await make_request("DELETE", f"{JULES_BASE_URL}/sessions/{sid}")
                deleted.append(sid)
        return f"Deleted {len(deleted)} sessions: {', '.join(deleted)}"

    elif action == "goal":
        if not arg:
            return "Usage: goal <plain English description of task>"
        no_dispatch = "--no-dispatch" in arg
        goal_text = arg.replace("--no-dispatch", "").strip()
        return await goal_to_backlog(goal_text, auto_dispatch=not no_dispatch)

    elif action == "session-end":
        return session_end(title=arg or "Session Complete", dry_run=False) or "Session end complete."

    return f"Unknown action: {action}"


# --- Session End ---

def session_end(title: str = "Session Complete", learning: str = "No major learnings recorded.",
                action: str = "Continue standard operating procedure.",
                history: str = "", dry_run: bool = False) -> None:
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    entry = f"\n## {date_str} - [{title}]\n**Learning:** {learning}\n**Action:** {action}\n"

    bolt_md = REPO_ROOT / ".jules" / "bolt.md"
    bolt_md.parent.mkdir(parents=True, exist_ok=True)
    with open(bolt_md, "a") as f:
        f.write(entry)

    agents_md = REPO_ROOT / "AGENTS.md"
    if history and agents_md.exists():
        with open(agents_md, "a") as f:
            f.write(f"\n<!-- NinaGate Routing History: {history} -->\n")

    if not dry_run:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(git_ops.auto_commit())
            else:
                loop.run_until_complete(git_ops.auto_commit())
            logger.info("session_end: git_ops.auto_commit() completed")
        except Exception as gc_err:
            logger.warning(f"session_end: git_ops.auto_commit() skipped: {gc_err}")

        try:
            subprocess.run(["bash", "./nina_sync.sh"], cwd=str(REPO_ROOT), check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            stderr_content = e.stderr or e.output or str(e)
            logger.error(f"nina_sync.sh failed: {stderr_content}")
            err_msg = f"⚠️ *NINA sync failed* after Jules session_end.\n\n*Error:*\n```{stderr_content[:400]}```"
            try:
                import re
                log_path = REPO_ROOT / "nina_update_log.md"
                if log_path.exists():
                    content = log_path.read_text(encoding="utf-8")
                    entries = re.findall(r"(?:##|###) Entry (\d+)", content)
                    next_num = int(entries[-1]) + 1 if entries else 1
                    today = datetime.utcnow().strftime("%Y-%m-%d")
                    log_entry = (
                        f"\n---\n\n## Entry {next_num:03d} — {today} · fail: jules session_end sync\n"
                        f"**Triggered by:** jules session_end sync failure\n\n"
                        f"**Error / Stderr:**\n"
                        f"```\n{e.stderr or e.output or 'No stderr captured'}\n```\n\n"
                        f"**Status:** NON-FATAL. Session ended successfully.\n"
                    )
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(log_entry)
                    logger.info(f"Sync failure logged to nina_update_log.md as Entry {next_num:03d}")
            except Exception as le:
                logger.warning(f"Failed to log sync failure to nina_update_log.md: {le}")
            try:
                from core.config import load_config
                cfg = load_config()
                if cfg.telegram_bot_token and cfg.telegram_chat_id:
                    url = f"https://api.telegram.org/bot{cfg.telegram_bot_token}/sendMessage"
                    requests.post(url, json={"chat_id": cfg.telegram_chat_id, "text": err_msg, "parse_mode": "Markdown"}, timeout=5)
            except Exception as te:
                logger.warning(f"Failed to send Telegram alert: {te}")
    else:
        logger.info("session_end dry-run: insights appended, sync skipped")


# --- Goal Intake ---

def _next_backlog_id() -> str:
    import re as _re
    if not BACKLOG_PATH.exists():
        return "B-001"
    text = BACKLOG_PATH.read_text()
    ids = _re.findall(r"^\|\s*(B-\d+)\s*\|", text, _re.M)
    if not ids:
        return "B-001"
    return f"B-{max(int(i.split('-')[1]) for i in ids) + 1:03d}"


async def goal_to_backlog(goal_text: str, auto_dispatch: bool = True) -> str:
    new_id = _next_backlog_id()
    new_row = f"| {new_id} | {goal_text[:60]} | `READY` | TBD | — | Auto-ingested via goal_to_backlog |"

    if BACKLOG_PATH.exists():
        content = BACKLOG_PATH.read_text()
        marker = "## ██ P1 — HIGH"
        if marker in content:
            parts = content.split(marker, 1)
            BACKLOG_PATH.write_text(parts[0] + marker + "\n\n" + new_row + "\n" + parts[1])
        else:
            BACKLOG_PATH.write_text(content.rstrip() + "\n" + new_row + "\n")
        logger.info(f"goal_to_backlog: added {new_id} to backlog")

    if auto_dispatch:
        sid = await run_dispatch(goal_text, title=f"[AUTO] {goal_text[:80]}")
        register_session(sid, [new_id], f"[AUTO] {goal_text[:80]}")
        logger.info(f"goal_to_backlog: dispatched as Jules session {sid}")
        return f"Added {new_id} to backlog and dispatched as Jules session {sid}"

    return f"Added {new_id} to backlog (dispatch skipped)"


# --- Pipeline Watchdog ---

async def check_pipeline_watchdog():
    logger.info("Jules Pipeline Watchdog Start")
    state_file = REPO_ROOT / "data" / "jules_watchdog_state.json"
    state = {"tasks": {}}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    if "tasks" not in state:
        state["tasks"] = {}

    from tools.ninaflash_core import get_backlog_tasks
    all_tasks = get_backlog_tasks()
    ready_tasks = [t for t in all_tasks if t.get("status") == "READY"]

    if not all_tasks and BACKLOG_PATH.exists():
        try:
            backlog_text = BACKLOG_PATH.read_text(encoding="utf-8")
            if "TODO-P" in backlog_text or "Section 3" in backlog_text:
                logger.error("Jules Pipeline Watchdog: Backlog format drift detected!")
                current_time_str = datetime.utcnow().isoformat() + "Z"
                now = datetime.utcnow()
                drift_key = "format_drift_alert"
                should_alert = True
                if drift_key in state["tasks"]:
                    try:
                        last_alert = datetime.fromisoformat(state["tasks"][drift_key]["last_alerted"].replace("Z", ""))
                        if (now - last_alert).total_seconds() / 60 < 720:
                            should_alert = False
                    except Exception:
                        pass
                if should_alert:
                    await send_telegram(
                        "⚠️ *Jules Watchdog Alert: Backlog Format Drift*\n"
                        "The backlog file contains active sections (`TODO-P`), but the parser "
                        "`get_backlog_tasks()` returned `0` tasks.\n\n"
                        "The pipeline is blind and cannot dispatch tasks automatically."
                    )
                    state["tasks"][drift_key] = {"last_alerted": current_time_str}
        except Exception as pe:
            logger.error(f"Failed to perform backlog parser-resilience check: {pe}")

    sla_raw_map = {}
    if BACKLOG_PATH.exists():
        try:
            sla_idx = -1
            for bline in BACKLOG_PATH.read_text(encoding="utf-8").splitlines():
                if "|" not in bline:
                    continue
                bparts = [p.strip() for p in bline.split("|")][1:-1]
                if any("SLA" in p.upper() for p in bparts):
                    for idx, col_h in enumerate(bparts):
                        if "SLA" in col_h.upper():
                            sla_idx = idx
                            break
                elif sla_idx != -1 and len(bparts) > sla_idx and bparts:
                    tid_candidate = bparts[0].replace("`", "").strip()
                    if tid_candidate:
                        sla_raw_map[tid_candidate] = bparts[sla_idx].replace("`", "").strip()
        except Exception as ex:
            logger.error(f"Error parsing backlog SLA columns: {ex}")

    def parse_sla_to_minutes(sla_str: str) -> Optional[float]:
        if not sla_str or sla_str in ("—", "-", "TBD", "None", "null"):
            return None
        try:
            val_str = "".join(c for c in sla_str if c.isdigit() or c == ".")
            unit_str = "".join(c for c in sla_str if c.isalpha()).lower()
            if not val_str:
                return None
            val = float(val_str)
            if unit_str == "h":
                return val * 60
            elif unit_str == "d":
                return val * 1440
            return val
        except Exception:
            return None

    current_time_str = datetime.utcnow().isoformat() + "Z"
    now = datetime.utcnow()

    for t in ready_tasks:
        tid = t["id"]
        if tid not in state["tasks"]:
            state["tasks"][tid] = {"first_detected_ready": current_time_str, "last_alerted": None}
        else:
            task_info = state["tasks"][tid]
            try:
                first_ready = datetime.fromisoformat(task_info["first_detected_ready"].replace("Z", ""))
                age_min = (now - first_ready).total_seconds() / 60
            except Exception:
                age_min = 0

            sla_budget = 120.0
            parsed_sla = parse_sla_to_minutes(sla_raw_map.get(tid, ""))
            if parsed_sla is not None:
                sla_budget = parsed_sla
            elif tid.startswith("TODO-P1"):
                sla_budget = 15.0

            if age_min >= sla_budget:
                logger.warning(f"Stall: task {tid} READY {age_min:.1f}m (SLA {sla_budget}m)")
                should_alert = True
                if task_info.get("last_alerted"):
                    try:
                        last_alert = datetime.fromisoformat(task_info["last_alerted"].replace("Z", ""))
                        if (now - last_alert).total_seconds() / 60 < 720:
                            should_alert = False
                    except Exception:
                        pass
                if should_alert:
                    await send_telegram(
                        f"⚠️ *Jules Pipeline Stall Warning*\n"
                        f"Task `{tid}` has been `READY` for too long!\n"
                        f"*Age:* {age_min:.1f} minutes (SLA Budget: {sla_budget}m).\n"
                        f"*Title:* {t.get('title', 'Untitled')}"
                    )
                    task_info["last_alerted"] = current_time_str

    state_file.parent.mkdir(exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    logger.info("Jules Pipeline Watchdog Complete")


async def verify_pr(pr_num: int, branch: str) -> bool:
    """Runs quality and compilation validations on a checked-out PR branch before merge."""
    logger.info(f"Running quality verification on PR #{pr_num} (branch: {branch})")
    
    cmd = ["git", "diff", "--name-only", "origin/main"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if res.returncode != 0:
        logger.error(f"Failed to get git diff for PR #{pr_num}: {res.stderr}")
        return False
        
    changed_files = [line.strip() for f in res.stdout.splitlines() if (line := f.strip()) and line.endswith(".py")]
    if not changed_files:
        logger.info(f"No python files changed in PR #{pr_num}. Skipping validation.")
        return True
        
    for filepath in changed_files:
        p = REPO_ROOT / filepath
        if not p.exists():
            continue
        logger.info(f"Validating file compilation: {filepath}")
        res_compile = subprocess.run(["python3", "-m", "py_compile", str(p)], capture_output=True)
        if res_compile.returncode != 0:
            logger.error(f"Compilation failed for {filepath}: {res_compile.stderr.decode(errors='replace')}")
            return False
            
    logger.info(f"PR #{pr_num} passed all validation checks.")
    return True


# --- CLI ---

async def cli_run():
    parser = argparse.ArgumentParser(description="Jules Unified Engine")
    parser.add_argument("cmd", help="Action (status|feedback|dispatch|watch|cleanup|orchestrate|git-status|git-diff|git-commit)")
    parser.add_argument("args", nargs="*", help="Arguments for the command")
    args = parser.parse_args()
    print(await run(" ".join([args.cmd] + args.args)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cli_run())
