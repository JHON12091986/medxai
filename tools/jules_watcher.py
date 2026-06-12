"""
JulesWatcher: Monitors Jules sessions for questions and notifies Telegram.
Part of the NINA-Evolve Protocol.
"""

import os
import re
import json
import asyncio
import logging
import requests
import subprocess
from pathlib import Path
from typing import List, Dict, Any

from tools import jules_api

# Constants
REPO_ROOT = Path(__file__).parent.parent.resolve()
SEEN_FILE = REPO_ROOT / "data" / "jules_seen_activities.json"
TELEGRAM_TOKEN = os.environ.get("TELEGRAMBOTTOKEN")
CHAT_ID = os.environ.get("AUTHORIZEDUSERID")
BEEP_SCRIPT = REPO_ROOT / "tools" / "alert_beep.py"

logger = logging.getLogger("nina.tools.jules_watcher")
_beep_proc = None

def start_beep():
    global _beep_proc
    if _beep_proc is None or _beep_proc.poll() is not None:
        logger.info("Starting audio alert sequence...")
        _beep_proc = subprocess.Popen(["python3", str(BEEP_SCRIPT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_beep():
    global _beep_proc
    if _beep_proc and _beep_proc.poll() is None:
        _beep_proc.terminate()
        _beep_proc = None

def load_seen_activities() -> set:
    if SEEN_FILE.exists():
        try:
            return set(json.loads(SEEN_FILE.read_text()))
        except Exception:
            return set()
    return set()

def save_seen_activities(seen: set):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(list(seen)))

async def send_telegram_notification(message: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logger.error("Telegram credentials missing in environment.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        def sync_post():
            return requests.post(url, json=payload, timeout=10)
        await asyncio.to_thread(sync_post)
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")

async def watch_and_notify():
    logger.info("JulesWatcher: Checking sessions...")
    
    sessions = await jules_api.list_active_tasks()
    seen_activities = load_seen_activities()
    new_seen = set(seen_activities)
    
    key = os.environ.get("JULES_API_KEY")
    headers = {"X-Goog-Api-Key": key}

    for session in sessions:
        state = session.get("state")
        sid = session.get("name", "").split("/")[-1]
        title = session.get("title", "Untitled")

        if state == "AWAITING_USER_FEEDBACK":
            # Fetch latest activities to find the question
            url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=5"
            try:
                data = await jules_api.make_request_with_retry("GET", url, headers)
                activities = data.get("activities", [])
                
                for act in reversed(activities):
                    aid = act.get("id")
                    if aid in seen_activities:
                        continue
                    
                    if "agentMessaged" in act:
                        msg = act["agentMessaged"].get("agentMessage")
                        notification = (
                            f"🤖 *Jules Needs Input*\n\n"
                            f"*Session:* `{sid}`\n"
                            f"*Task:* {title}\n\n"
                            f"*Question:* {msg}\n\n"
                            f"Reply via me or Jules UI."
                        )
                        await send_telegram_notification(notification)
                        new_seen.add(aid)
                        start_beep()
                        logger.info(f"Notification sent for session {sid}, activity {aid}")
                        break # Only notify the latest question per session
            except Exception as e:
                logger.error(f"Failed to fetch activities for {sid}: {e}")
        
        elif state == "FAILED":
            # Check if we've already notified failure
            fid = f"fail_{sid}_{session.get('updateTime')}"
            if fid not in seen_activities:
                notification = (
                    f"❌ *Jules Session Failed*\n\n"
                    f"*Session:* `{sid}`\n"
                    f"*Task:* {title}\n"
                    f"Check logs for details."
                )
                await send_telegram_notification(notification)
                new_seen.add(fid)
                logger.info(f"Failure notification sent for session {sid}")

    save_seen_activities(new_seen)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(watch_and_notify())
