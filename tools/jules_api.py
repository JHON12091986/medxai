"""Jules REST API tool for NINA. Dispatches tasks and polls PR status."""

import os
import re
import logging
import asyncio
import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("nina.tools.jules")

def get_api_key() -> str:
    """Read JULES_API_KEY from environment variables."""
    key = os.environ.get("JULES_API_KEY")
    if not key:
        raise ValueError("JULES_API_KEY environment variable is not set.")
    return key

async def make_request_with_retry(method: str, url: str, headers: dict, params: dict = None, json_data: dict = None, retries: int = 2):
    """Makes a request with a retry limit."""
    last_exc = None
    for attempt in range(retries):
        try:
            def sync_req():
                return requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
            
            response = await asyncio.to_thread(sync_req)
            if response.status_code == 404:
                return {"error": "not_found", "status_code": 404, "text": response.text}
            response.raise_for_status()
            return response.json() if method != "DELETE" else {"status": "ok"}
        except requests.exceptions.RequestException as e:
            last_exc = e
            if attempt < retries - 1:
                await asyncio.sleep(1)
                continue
            raise e
    raise last_exc

async def get_task_status(session_id: str) -> str:
    """Returns activity status for a session."""
    api_key = get_api_key()
    base_url = "https://jules.googleapis.com/v1alpha"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    
    sid = session_id.split("/")[-1]
    url = f"{base_url}/sessions/{sid}/activities"
    try:
        data = await make_request_with_retry("GET", url, headers, params={"pageSize": 30})
        activities = data.get("activities", [])
        if not activities: return f"No activities for session {sid}."
        
        lines = [f"Status for Session {sid}:"]
        for act in activities[-5:]:
            origin = act.get("originator", "SYSTEM")
            msg = "No message content"
            if "agentMessaged" in act:
                msg = act["agentMessaged"].get("agentMessage", "")
            elif "userMessaged" in act:
                msg = act["userMessaged"].get("userMessage", "")
            elif "planGenerated" in act:
                msg = "[Plan Generated]"
            elif "taskFailed" in act:
                msg = f"[FAILED] {act['taskFailed'].get('errorMessage')}"
            lines.append(f"{origin}: {msg[:100]}...")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

async def list_active_tasks() -> List[Dict[str, Any]]:
    """Returns a list of current active Jules sessions."""
    api_key = get_api_key()
    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    
    try:
        data = await make_request_with_retry("GET", url, headers, params={"pageSize": 50})
        return data.get("sessions", [])
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return []

async def provide_feedback(session_id: str, message: str):
    """Sends user feedback to a Jules session."""
    api_key = get_api_key()
    sid = session_id.split("/")[-1]
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
    body = {
        "userMessaged": {
            "userMessage": message
        }
    }
    return await make_request_with_retry("POST", url, headers, json_data=body)

async def run(cmd: str) -> str:
    """Entry point for CLI and other tools."""
    parts = cmd.strip().split(None, 1)
    if not parts: return "Usage: dispatch | status | feedback"
    
    action = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if action == "status":
        if arg: return await get_task_status(arg)
        sessions = await list_active_tasks()
        if not sessions: return "No sessions found."
        lines = ["Active Jules Sessions:"]
        for s in sessions:
            sid = s.get("name", "").split("/")[-1]
            lines.append(f"- [{sid}] {s.get('title', 'Untitled')} — {s.get('state')}")
        return "\n".join(lines)

    if action == "feedback":
        if not arg or " " not in arg: return "Usage: feedback [sid] [message]"
        sid, msg = arg.split(None, 1)
        res = await provide_feedback(sid, msg)
        return f"Feedback sent to {sid}: {msg}"

    if action == "dispatch":
        api_key = get_api_key()
        headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}
        url = "https://jules.googleapis.com/v1alpha/sessions"
        title = re.sub(r'[\r\n\t]+', ' ', arg).strip()[:100]
        body = {
            "prompt": arg,
            "sourceContext": {"source": "sources/github/aibony/nina", "githubRepoContext": {"startingBranch": "main"}},
            "automationMode": "AUTO_CREATE_PR",
            "title": title
        }
        data = await make_request_with_retry("POST", url, headers, json_data=body)
        sid = data.get("id") or data.get("name", "").split("/")[-1]
        return f"Jules task started: {sid}"

    return f"Unknown action: {action}"

if __name__ == "__main__":
    import sys
    cmd_str = " ".join(sys.argv[1:]) or "status"
    print(asyncio.run(run(cmd_str)))
