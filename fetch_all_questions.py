import os
import asyncio
import json
import re
from tools import jules_api

async def fetch_session_details(sid):
    key = os.environ.get("JULES_API_KEY")
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=100"
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
    
    # Improved regex to handle different session IDs and titles
    matches = re.findall(r'#(\d+) \[(\d+)\] (.*?) — ([A-Z_]+)', status_output)

    print("--- SESSIONS STATUS REPORT ---")
    for idx, sid, title, state in matches:
        if state in ("AWAITING_USER_FEEDBACK", "FAILED"):
            details = await fetch_session_details(sid)
            print(f"\n[#{idx}] {sid}: {title}")
            print(f"STATE: {state}")
            if state == "AWAITING_USER_FEEDBACK":
                print(f"QUESTION: {details.get('question')}")
            else:
                print(f"ERROR: {details.get('error')}")

if __name__ == "__main__":
    asyncio.run(run())
