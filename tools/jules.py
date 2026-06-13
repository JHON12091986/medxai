"""
Jules Unified Engine v6.2 (The One-File Pipeline).
Consolidates API, Registry, Watcher, and Orchestrator into a single module.
Supports Multi-File Mega Batching, Parallel PR Resolution, and Persistent State.
"""

import os
import re
import json
import asyncio
import logging
import requests
import subprocess
import shlex
import argparse
import dotenv

dotenv.load_dotenv()
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# --- Configuration & Constants ---
REPO_ROOT = Path(__file__).parent.parent.resolve()
REGISTRY_PATH = REPO_ROOT / "data" / "jules_registry.json"
SEEN_FILE = REPO_ROOT / "data" / "jules_seen_activities.json"
BACKLOG_PATH = REPO_ROOT / "docs/space" / "jules_backlog.md"
INDEX_PATH = REPO_ROOT / "docs/space" / "nina_index.json"
BEEP_SCRIPT = REPO_ROOT / "tools" / "alert_beep.py"

MAX_CONCURRENT_SESSIONS = 15
JULES_BASE_URL = "https://jules.googleapis.com/v1alpha"

TELEGRAM_TOKEN = os.environ.get("TELEGRAMBOTTOKEN")
CHAT_ID = os.environ.get("AUTHORIZEDUSERID")
API_KEY = os.environ.get("JULES_API_KEY")

logger = logging.getLogger("nina.tools.jules")
git_lock = asyncio.Lock()
_beep_proc = None

# --- Core API Utilities ---

def get_api_key() -> str:
    if not API_KEY:
        raise ValueError("JULES_API_KEY environment variable is not set.")
    return API_KEY

async def make_request(method: str, url: str, params: dict = None, json_data: dict = None, retries: int = 2):
    key = get_api_key()
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    last_exc = None
    for attempt in range(retries):
        try:
            def sync_req():
                return requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
            res = await asyncio.to_thread(sync_req)
            logger.info(f"API {method} {url} -> {res.status_code}")
            if res.status_code >= 400:
                logger.error(f"API Error: {res.text}")
            if res.status_code == 404: return {"error": "not_found", "status_code": 404}
            res.raise_for_status()
            return res.json() if method != "DELETE" else {"status": "ok"}
        except Exception as e:
            last_exc = e
            if attempt < retries - 1: await asyncio.sleep(1)
            else: raise e
    raise last_exc

# --- Registry Management ---

def load_registry() -> dict:
    if not REGISTRY_PATH.exists(): return {}
    try: return json.loads(REGISTRY_PATH.read_text())
    except: return {}

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
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        await asyncio.to_thread(lambda: requests.post(url, json=payload, timeout=10))
    except: pass

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
        try: seen = set(json.loads(SEEN_FILE.read_text()))
        except: pass

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

async def resolve_prs_parallel():
    """Concurrently resolves open PRs."""
    cmd = ["gh", "pr", "list", "--json", "number,title,state,headRefName"]
    res = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if res.returncode != 0: return
    
    prs = json.loads(res.stdout)
    open_prs = [p for p in prs if p["state"] == "OPEN"]
    
    async def resolve_one(pr):
        num = pr["number"]
        m_cmd = ["gh", "pr", "merge", str(num), "--merge", "--admin", "-d", "-c", "Automerged via Jules Unified Engine."]
        m_res = await asyncio.to_thread(subprocess.run, m_cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        if m_res.returncode == 0:
            logger.info(f"PR #{num} merged.")
        else:
            logger.warning(f"PR #{num} merge failed. Requires manual check.")

    if open_prs:
        await asyncio.gather(*(resolve_one(p) for p in open_prs))

async def run_dispatch(prompt: str, title: Optional[str] = None):
    """Core dispatch primitive."""
    if not title: title = prompt.strip()[:100]
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
    
    # --- GLOBAL PAUSE CHECK ---
    from pathlib import Path
    backlog_path = Path("docs/space/jules_backlog.md")
    if backlog_path.exists() and "GLOBAL PAUSE ACTIVE" in backlog_path.read_text():
        logger.warning("🛑 GLOBAL PAUSE ACTIVE: Skipping task dispatch.")
        await watch_cycle()
        await resolve_prs_parallel()
        return
    # --------------------------

    await watch_cycle()
    await resolve_prs_parallel()
    
    reg = load_registry()
    active_count = len([v for v in reg.values() if v["status"] in ("IN_PROGRESS", "AWAITING_USER_FEEDBACK")])
    slots = MAX_CONCURRENT_SESSIONS - active_count
    
    if slots > 0:
        from tools.ninaflash import get_backlog_tasks, _save_task_status
        ready = [t for t in get_backlog_tasks() if t.get("status") == "READY"]
        if ready:
            batch = ready[:5]
            tids = [t['id'] for t in batch]
            mega_prompt = "MEGA TASK BATCH\nExecute sequentially, no confirmation.\n"
            for t in batch:
                mega_prompt += f"\n--- {t['id']} ---\n{t['title']}\nFiles: {t['files']}\n"
            
            try:
                sid = await run_dispatch(mega_prompt, f"Mega Batch ({', '.join(tids)})")
                register_session(sid, batch, f"Mega Batch ({', '.join(tids)})")
                for t in batch: _save_task_status(t["id"], "IN_PROGRESS")
                logger.info(f"Dispatched batch {tids} -> SID: {sid}")
            except Exception as e:
                logger.error(f"Batch dispatch failed: {e}")

async def run_orchestrator_cycle(nina_os=None):
    """Compatibility handler for crons/manager.py."""
    await orchestrate_cycle()

# --- Unified Entry Point ---

async def run(cmd: str) -> str:
    """Unified entry point for string-based commands."""
    parts = cmd.strip().split(None, 1)
    if not parts: return "Usage: dispatch | status | feedback | cleanup | orchestrate"
    
    action = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if action == "status":
        if arg:
            data = await make_request("GET", f"{JULES_BASE_URL}/sessions/{arg}/activities", params={"pageSize": 100})
            if "error" in data: return f"Session {arg} not found."
            lines = [f"Status for Session {arg}:"]
            for act in data.get("activities", []):
                origin = act.get("originator", "SYSTEM")
                msg = act.get("agentMessaged", {}).get("agentMessage") or act.get("userMessaged", {}).get("userMessage") or "[SYSTEM EVENT]"
                lines.append(f"[{origin}] {msg[:500]}...")
            return "\n".join(lines)
        else:
            data = await make_request("GET", f"{JULES_BASE_URL}/sessions", params={"pageSize": 50})
            sessions = data.get("sessions", [])
            if not sessions: return "No active sessions."
            lines = ["Active Jules Sessions:"]
            for s in sessions:
                sid = s["name"].split("/")[-1]
                lines.append(f"- [{sid}] {s['title']} ({s['state']})")
            return "\n".join(lines)

    elif action == "feedback":
        if not arg or " " not in arg: return "Usage: feedback [sid] [message]"
        sid, msg = arg.split(None, 1)
        url = f"{JULES_BASE_URL}/sessions/{sid}:sendMessage"
        body = {"prompt": msg}
        res = await make_request("POST", url, json_data=body)
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
        # arg format: title="..." learning="..." action="..." history="..."
        return session_end(title=arg or "Session Complete", dry_run=False) or "Session end complete."

    return f"Unknown action: {action}"

# --- Session End (absorbed from tools/session_end.py) ---

def session_end(title: str = "Session Complete", learning: str = "No major learnings recorded.",
                action: str = "Continue standard operating procedure.",
                history: str = "", dry_run: bool = False) -> None:
    """Append session insights to .jules/bolt.md and AGENTS.md, then run nina_sync.sh."""
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
        subprocess.run(["bash", "./nina_sync.sh"], cwd=str(REPO_ROOT))
    else:
        logger.info("session_end dry-run: insights appended, sync skipped")


# --- Goal Intake (absorbed from tools/goal_intake.py) ---

def _next_backlog_id() -> str:
    """Generate the next B-NNN id from the backlog."""
    import re as _re
    if not BACKLOG_PATH.exists():
        return "B-001"
    text = BACKLOG_PATH.read_text()
    ids = _re.findall(r"^\|\s*(B-\d+)\s*\|", text, _re.M)
    if not ids:
        return "B-001"
    return f"B-{max(int(i.split('-')[1]) for i in ids) + 1:03d}"


async def goal_to_backlog(goal_text: str, auto_dispatch: bool = True) -> str:
    """Convert plain-English goal → backlog row → optionally dispatch to Jules."""
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


# --- CLI Implementation ---

async def cli_run():
    parser = argparse.ArgumentParser(description="Jules Unified Engine")
    parser.add_argument("cmd", help="Action (status|feedback|dispatch|watch|cleanup|orchestrate)")
    parser.add_argument("args", nargs="*", help="Arguments for the command")

    args = parser.parse_args()
    full_cmd = " ".join([args.cmd] + args.args)
    print(await run(full_cmd))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cli_run())
