import asyncio
import os
import json
import requests

async def test():
    key = os.environ.get("JULES_API_KEY")
    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    
    # Try with NO headRefName (some APIs fail if startingBranch is main)
    body = {
        "prompt": "Test Prompt",
        "sourceContext": {"source": "sources/github/aibony/nina"},
        "automationMode": "AUTO_CREATE_PR",
        "title": "Test Title"
    }
    
    print("Sending request...")
    r = requests.post(url, headers=headers, json=body)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")

if __name__ == "__main__":
    asyncio.run(test())
