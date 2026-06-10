"""Jules REST API tool for NINA. Dispatches tasks and polls PR status via Telegram."""

import os
import logging
import asyncio
import json
import requests

logger = logging.getLogger("nina.tools")

def get_api_key() -> str:
    """Read JULES_API_KEY from environment variables. Fail at call time only."""
    key = os.environ.get("JULES_API_KEY")
    if not key:
        raise ValueError("JULES_API_KEY environment variable is not set.")
    return key

def parse_arguments(cmd: str):
    """Normalize and parse the command and its arguments."""
    cmd = cmd.strip()
    if cmd.startswith("/"):
        cmd = cmd[1:].strip()
    if cmd.startswith("jules"):
        cmd = cmd[5:].strip()
    
    parts = cmd.split(None, 1)
    if not parts:
        return None, ""
    
    action = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    return action, arg

async def run(cmd: str) -> str:
    """Handles the /jules Telegram commands and calls the Jules REST API."""
    try:
        action, arg = parse_arguments(cmd)
        if not action:
            return (
                "Usage:\n"
                "/jules dispatch <task>\n"
                "/jules status\n"
                "/jules status <session_id>\n"
                "/jules sources"
            )

        api_key = get_api_key()
        base_url = "https://jules.googleapis.com/v1alpha"
        headers = {
            "X-Goog-Api-Key": api_key,
            "Content-Type": "application/json"
        }

        if action == "dispatch":
            if not arg:
                return "Error: task description required for dispatch"
            
            title = arg[:60]
            body = {
                "prompt": arg,
                "sourceContext": {
                    "source": "sources/github/aibony/nina",
                    "githubRepoContext": {
                        "startingBranch": "main"
                    }
                },
                "automationMode": "AUTO_CREATE_PR",
                "title": title
            }
            url = f"{base_url}/sessions"
            
            def make_request():
                return requests.post(url, headers=headers, json=body, timeout=30)
                
            response = await asyncio.to_thread(make_request)
            response.raise_for_status()
            data = response.json()
            
            session_id = data.get("id") or (data.get("name", "").split("/")[-1] if data.get("name") else "unknown")
            res_title = data.get("title", title)
            return f"Jules task started\nSession: {session_id}\nTitle: {res_title}"

        elif action == "status":
            if arg:
                # Get last 3 activities for session_id
                session_id = arg
                if session_id.startswith("sessions/"):
                    session_id = session_id[len("sessions/"):]
                url = f"{base_url}/sessions/{session_id}/activities"
                params = {"pageSize": 30}
                
                def make_request():
                    return requests.get(url, headers=headers, params=params, timeout=30)
                
                response = await asyncio.to_thread(make_request)
                response.raise_for_status()
                data = response.json()
                
                activities = data.get("activities", [])
                if not activities:
                    return "No activities found."
                
                # Format last 3 activities: "<type>: <content[:120]>"
                last_3 = activities[-3:]
                lines = []
                for act in last_3:
                    act_type = act.get("type") or act.get("originator") or "UNKNOWN"
                    act_content = act.get("content")
                    if isinstance(act_content, dict):
                        act_content = (
                            act_content.get("text") or 
                            act_content.get("message") or 
                            act_content.get("description") or 
                            json.dumps(act_content)
                        )
                    elif act_content is None:
                        act_content = act.get("description") or ""
                    else:
                        act_content = str(act_content)
                    trimmed = act_content[:120]
                    lines.append(f"{act_type}: {trimmed}")
                return "\n".join(lines)
            else:
                # Get last 5 sessions
                url = f"{base_url}/sessions"
                params = {"pageSize": 5}
                
                def make_request():
                    return requests.get(url, headers=headers, params=params, timeout=30)
                
                response = await asyncio.to_thread(make_request)
                response.raise_for_status()
                data = response.json()
                
                sessions = data.get("sessions", [])
                if not sessions:
                    return "No sessions found."
                
                lines = []
                for idx, session in enumerate(sessions, 1):
                    s_title = session.get("title", "Untitled")
                    s_state = session.get("state", "UNKNOWN")
                    pr_url = "no PR yet"
                    for output in session.get("outputs", []):
                        pr = output.get("pullRequest")
                        if pr and pr.get("url"):
                            pr_url = pr.get("url")
                            break
                    lines.append(f"#{idx} {s_title} — {s_state} — {pr_url}")
                return "\n".join(lines)

        elif action == "sources":
            url = f"{base_url}/sources"
            
            def make_request():
                return requests.get(url, headers=headers, timeout=30)
            
            response = await asyncio.to_thread(make_request)
            response.raise_for_status()
            data = response.json()
            
            sources = data.get("sources", [])
            lines = ["Available sources:"]
            for src in sources:
                if isinstance(src, dict):
                    name = src.get("name") or src.get("source")
                else:
                    name = str(src)
                if name:
                    lines.append(f"- {name}")
            return "\n".join(lines)
            
        else:
            return f"Unknown action: {action}. Supported: dispatch, status, sources"

    except requests.exceptions.RequestException as e:
        logger.error(f"jules_api_request_failed cmd={cmd!r} err={e}", extra={"log": "error.log", "tool_name": "jules_api"})
        return f"Jules API request failed: {e}"
    except (OSError, ValueError, TypeError, KeyError) as e:
        logger.error(f"jules_api_failed cmd={cmd!r} err={e}", extra={"log": "error.log", "tool_name": "jules_api"})
        return f"Jules API error: {e}"

class JulesAPI:
    """Class matching NINA's tool pattern for UpgradePipeline."""
    def __init__(self, config=None, router=None):
        self.config = config
        self.router = router

    async def run(self, cmd: str) -> str:
        return await run(cmd)

class JulesAPITool(JulesAPI):
    pass

class JulesTool(JulesAPI):
    pass

__all__ = ["run", "JulesAPI", "JulesAPITool", "JulesTool"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 -m tools.jules_api <command>")
        sys.exit(1)
    
    cmd_str = " ".join(sys.argv[1:])
    try:
        res = asyncio.run(run(cmd_str))
        print(res)
    except (OSError, ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"CLI Error: {e}", extra={"log": "error.log", "tool_name": "jules_api"})
        print(f"CLI Error: {e}")
