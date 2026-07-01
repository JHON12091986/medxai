import asyncio
import httpx
import time

PROMPTS = [
    "Write a python function to compute the 10th fibonacci number.",
    "Explain the concept of async/await in Python in one sentence.",
]


async def call_model(model_name: str, prompt: str):
    start = time.time()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8765/v1/chat/completions",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            latency = time.time() - start
            usage = data.get("usage", {})
            return {
                "model": model_name,
                "latency": latency,
                "tokens_in": usage.get("prompt_tokens", 0),
                "tokens_out": usage.get("completion_tokens", 0),
            }
    except Exception as e:
        return {"model": model_name, "error": str(e), "latency": time.time() - start}


async def run_benchmark():
    models = ["qwen2.5-coder:7b", "gemini-2.0-flash"]
    results = []

    for prompt in PROMPTS:
        print(f"Running benchmark for prompt: '{prompt[:50]}...'")
        for model in models:
            res = await call_model(model, prompt)
            print(res)
            results.append(res)

    print("\nBenchmark Summary:")
    for r in results:
        if "error" in r:
            print(f"[{r['model']}] ERROR: {r['error']} ({r['latency']:.2f}s)")
        else:
            print(
                f"[{r['model']}] Latency: {r['latency']:.2f}s | Tokens In/Out: {r['tokens_in']}/{r['tokens_out']}"
            )


if __name__ == "__main__":
    asyncio.run(run_benchmark())


# ── Continuous telemetry writer (NINA enhancement patch) ─────────────────────
# NINA_FEATURE: benchmark-routing-telemetry v1.0
# Run via cron: */30 * * * * cd ~/nina && python3 tools/benchmark_routing.py --telemetry

import json as _json, time as _time, statistics as _stats
from pathlib import Path as _Path

_TELEM_FILE = _Path.home() / "nina" / "data" / "router_telemetry.jsonl"

def record_telemetry(provider: str, latencies_ms: list[float], success_rate: float):
    """Append a telemetry row for dashboarding. One row per provider per run."""
    _TELEM_FILE.parent.mkdir(exist_ok=True)
    row = {
        "ts": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        "provider": provider,
        "p50_ms": round(_stats.median(latencies_ms), 1) if latencies_ms else None,
        "p95_ms": round(_stats.quantiles(latencies_ms, n=20)[-1], 1) if len(latencies_ms) >= 5 else None,
        "min_ms": round(min(latencies_ms), 1) if latencies_ms else None,
        "max_ms": round(max(latencies_ms), 1) if latencies_ms else None,
        "success_rate": round(success_rate, 3),
        "sample_n": len(latencies_ms),
    }
    with open(_TELEM_FILE, "a") as f:
        f.write(_json.dumps(row) + "\n")
    return row

def tail_telemetry(n: int = 20, provider: str = None) -> list:
    """Return last n telemetry rows, optionally filtered by provider."""
    if not _TELEM_FILE.exists(): return []
    rows = [_json.loads(l) for l in _TELEM_FILE.read_text().splitlines() if l.strip()]
    if provider:
        rows = [r for r in rows if r.get("provider") == provider]
    return rows[-n:]

def telemetry_summary() -> dict:
    """Return per-provider p50/p95 averages from last 100 entries."""
    rows = tail_telemetry(100)
    from collections import defaultdict
    buckets = defaultdict(list)
    for r in rows:
        if r.get("p50_ms"):
            buckets[r["provider"]].append(r["p50_ms"])
    return {p: {"avg_p50_ms": round(sum(v)/len(v), 1), "samples": len(v)}
            for p, v in buckets.items()}
