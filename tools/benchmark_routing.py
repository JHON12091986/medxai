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
