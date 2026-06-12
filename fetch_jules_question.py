import os
import asyncio
import json
from tools import jules_api

async def run():
    key = os.environ.get("JULES_API_KEY")
    sid = "13484551090260534806"
    url = f"https://jules.googleapis.com/v1alpha/sessions/{sid}/activities?pageSize=100"
    headers = {"X-Goog-Api-Key": key}
    try:
        data = await jules_api.make_request_with_retry("GET", url, headers)
        activities = data.get("activities", [])
        for act in activities:
            if "agentMessaged" in act:
                 print(f"FULL MSG: {act['agentMessaged'].get('agentMessage')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
