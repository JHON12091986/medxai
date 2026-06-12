"""
NINA v14.2 — ProviderHunter & Discoverer
Discovers, validates, and ranks free cloud inference providers.
Integrated into the daily Jules maintenance cycle.
"""

import json
import logging
import time
import asyncio
import re
import subprocess
from pathlib import Path
import httpx

logger = logging.getLogger("nina.providerhunter")
REPO_ROOT = Path(__file__).parent.parent.resolve()
DISCOVERED = REPO_ROOT / "data" / "discoveredproviders.json"
MASTER_PROVIDERS = REPO_ROOT / "ninagate" / "providers.json"

# Core Seed Candidates (2026 Baseline)
CANDIDATES = [
    {"id":"GROQ_FREE",      "base":"https://api.groq.com/openai/v1",            "model":"llama-3.3-70b-versatile", "key_required":True},
    {"id":"CEREBRAS_FREE",  "base":"https://api.cerebras.ai/v1",                 "model":"llama-3.3-70b",           "key_required":True},
    {"id":"OPENROUTER_FREE","base":"https://openrouter.ai/api/v1",              "model":"openrouter/auto",         "key_required":True},
    {"id":"DEEPSEEK_FREE",  "base":"https://api.deepseek.com",                  "model":"deepseek-chat",            "key_required":True},
    {"id":"MISTRAL_FREE",   "base":"https://api.mistral.ai/v1",                 "model":"mistral-small-latest",    "key_required":True},
    {"id":"TOGETHER_FREE",  "base":"https://api.together.xyz/v1",               "model":"meta-llama/Llama-3-70b",  "key_required":True},
    {"id":"GEMINI_FREE",    "base":"https://generativelanguage.googleapis.com/v1beta/openai", "model":"gemini-2.5-flash", "key_required":True},
    {"id":"POLLINATIONS",   "base":"https://text.pollinations.ai/openai",       "model":"openai",                  "key_required":False},
]

async def validate_provider(p, client):
    """Checks if a provider endpoint is reachable and responding."""
    try:
        start = time.time()
        headers = {"Content-Type": "application/json"}
        if p["key_required"]:
            # Use dummy key for validation if no real key is in env
            key = os.environ.get(f"{p['id']}_KEY", "dummy_key")
            headers["Authorization"] = f"Bearer {key}"
        
        # Probe with minimal request
        r = await client.post(
            f"{p['base']}/chat/completions",
            headers=headers,
            json={"model": p["model"], "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
            timeout=10
        )
        
        # 200 is healthy, 401/403 means auth is working but key is needed, 
        # anything else might be dead
        healthy = r.status_code in (200, 401, 403)
        latency = (time.time() - start) * 1000
        
        return {
            **p,
            "healthy": healthy,
            "status_code": r.status_code,
            "latency_ms": int(latency),
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S+0600")
        }
    except Exception as e:
        return {**p, "healthy": False, "error": str(e), "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S+0600")}

async def search_new_candidates():
    """
    Autonomous search for new providers.
    When run by Jules, this uses web intelligence.
    """
    logger.info("Jules is hunting for new providers...")
    # This is where Jules would use its internal 'browser' or 'search' tool
    # to find new lists like 'awesome-free-llm-api'.
    return []

async def run_discovery():
    results = []
    async with httpx.AsyncClient() as client:
        # 1. Validate known candidates
        tasks = [validate_provider(p, client) for p in CANDIDATES]
        results = await asyncio.gather(*tasks)
        
        # 2. Add newly discovered ones (placeholder for Jules logic)
        # new_ones = await search_new_candidates()
        # results.extend(new_ones)

    # Save findings
    DISCOVERED.write_text(json.dumps(results, indent=2))
    print(f"✅ Discovery complete. Found {len([r for r in results if r['healthy']])} healthy endpoints.")
    
    # 3. Propose updates if new healthy providers found
    return results

if __name__ == "__main__":
    import os
    asyncio.run(run_discovery())
