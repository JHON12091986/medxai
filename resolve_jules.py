import os
import asyncio
import json
import re
from tools import jules_api

async def send_feedback(sid, message):
    key = os.environ.get("JULES_API_KEY")
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities"
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    body = {
        "userMessaged": {
            "userMessage": message
        }
    }
    try:
        data = await jules_api.make_request_with_retry("POST", url, headers, json_data=body)
        print(f"Feedback sent to {sid}: {message}")
        return True
    except Exception as e:
        print(f"Error sending feedback to {sid}: {e}")
        return False

async def fetch_session_details(sid):
    key = os.environ.get("JULES_API_KEY")
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=50"
    headers = {"X-Goog-Api-Key": key}
    try:
        data = await jules_api.make_request_with_retry("GET", url, headers)
        activities = data.get("activities", [])
        
        question = "None found"
        for act in reversed(activities):
            if "agentMessaged" in act:
                question = act["agentMessaged"].get("agentMessage")
                break
                 
        error = "None found"
        for act in reversed(activities):
             if "taskFailed" in act:
                 error = act["taskFailed"].get("errorMessage", json.dumps(act["taskFailed"]))
                 break

        return {"question": question, "error": error}
    except Exception as e:
        return {"error": str(e)}

async def run():
    status_output = await jules_api.run("status")
    matches = re.findall(r'#(\d+) \[(\d+)\] (.*?) — ([A-Z_]+)', status_output)

    awaiting_sessions = []
    failed_sessions = []

    for idx, sid, title, state in matches:
        if state == "AWAITING_USER_FEEDBACK":
            awaiting_sessions.append((sid, title))
        elif state == "FAILED":
            failed_sessions.append((sid, title))

    print(f"Targeting {len(awaiting_sessions)} blocked and {len(failed_sessions)} failed sessions.")

    # 1. Resolve Session [#29] Sentinel Security Fix
    # Question: Are you ready for me to finalize the learning record and proceed with submitting the PR?
    # Resolution: Yes, proceed.
    sentinel_sid = "13484551090260534806"
    await send_feedback(sentinel_sid, "Yes, please finalize the learning record and proceed with submitting the PR. Ensure the commit message follows the project's conventional commit standard.")

    # 2. Resolve Session [#30] NinaGate Optimization
    # Status: Applying Batch 1 string modifications.
    # Resolution: Proceed with the modifications.
    ninagate_sid = "7766676870073617722"
    await send_feedback(ninagate_sid, "Proceed with applying Batch 1 of the string modifications to ninagate/main.py. Run pyflakes after the changes to ensure no syntax errors were introduced.")

    # 3. Resolve Session [#47] Global Context Filtering
    # Question: Should I review grep_search and other tools or is modifying _find_py_files sufficient?
    # Resolution: Modifying _find_py_files and _find_md_files is sufficient for now.
    sec_ignore_sid = "8261678623607038143"
    await send_feedback(sec_ignore_sid, "Modifying _find_py_files and _find_md_files is sufficient for the current scope. Please finalize the implementation and open the PR.")

    # 4. Resolve Session [#50] Sentinel Protection Agent
    # Question: Prioritize tightening scan rules or fixing browser SSRF issues?
    # Resolution: Tighten scan rules in upgradepipeline.py.
    sentinel_p_sid = "1574419446092272855"
    await send_feedback(sentinel_p_sid, "Please prioritize tightening the security scan rules in tools/upgradepipeline.py. Ensure that os.system and subprocess calls without list-style arguments are flagged.")

    # 5. Handle Failed Session [#33] System Bug Fixes
    # Resolution: Retry the task.
    failed_sid = "358132093278995322"
    print(f"Attempting to restart failed session {failed_sid}...")
    # Restart usually means creating a new task, but we'll try to provide feedback to see if it can recover
    await send_feedback(failed_sid, "The last run failed without a detailed error. Please retry the task, focusing on one fix at a time to isolate issues.")

    # 6. Resolve Session [#1] AG-N-09 Code Complexity
    complexity_sid = "1425400646310127773"
    await send_feedback(complexity_sid, "Proceed with the implementation of the complexity calculation logic. Ensure it handles nested functions correctly.")

    # 7. Resolve Session [#2] AG-N-08 Dependency Cycle
    cycle_sid = "2590444877765026733"
    await send_feedback(cycle_sid, "Proceed with the dependency cycle detection logic. Output the cycles in a clear table format in the PR description.")

if __name__ == "__main__":
    asyncio.run(run())
