"""NINA v12 — ProviderHunter. Discovers free providers, validates, writes discoveredproviders.json."""
import json, logging, time
from pathlib import Path
import httpx

logger = logging.getLogger("nina.providerhunter")
DISCOVERED = Path("data/discoveredproviders.json")

CANDIDATES = [
    {"id":"GROQ_FREE",    "base":"https://api.groq.com/openai/v1",  "model":"llama-3.3-70b-versatile","key_required":True},
    {"id":"CEREBRAS_FREE","base":"https://api.cerebras.ai/v1",       "model":"llama-3.3-70b",          "key_required":True},
]

async def hunt(router, config):
    results = []
    async with httpx.AsyncClient(timeout=15) as c:
        for p in CANDIDATES:
            try:
                r = await c.post(f"{p['base']}/chat/completions",
                    headers={"Authorization":"Bearer test","Content-Type":"application/json"},
                    json={"model":p["model"],"messages":[{"role":"user","content":"hi"}],"max_tokens":1})
                healthy = r.status_code not in (401, 403, 404)
            except Exception:
                healthy = False
            results.append({**p, "healthy": healthy, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S+0600")})

    DISCOVERED.write_text(json.dumps(results, indent=2))
    logger.info(f"provider_hunter found={len(results)}", extra={"log":"scheduler.log"})
