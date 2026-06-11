import asyncio
import json
import psutil
from pathlib import Path
from tools.system import get_vram_used_mb

LOG_FILE = Path("logs/nina.jsonl")


async def parse_logs():
    if not LOG_FILE.exists():
        return "No logs found."

    total_latency = 0
    total_tokens_in = 0
    total_tokens_out = 0
    ttft_total = 0
    ttft_count = 0
    req_count = 0
    routing_stats = {}

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                record = entry.get("record", {})
                extra = record.get("extra", {})
                msg = record.get("message", "")

                if msg == "router_success" and extra.get("log") == "router.log":
                    req_count += 1
                    total_latency += extra.get("ms", 0)

                    provider = extra.get("provider", "unknown")
                    routing_stats[provider] = routing_stats.get(provider, 0) + 1

                    total_tokens_in += extra.get("tokens_in", 0)
                    total_tokens_out += extra.get("tokens_out", 0)

                    if "ttft" in extra:
                        ttft_total += extra["ttft"]
                        ttft_count += 1
            except Exception:
                continue

    avg_latency = total_latency / req_count if req_count > 0 else 0
    avg_ttft = ttft_total / ttft_count if ttft_count > 0 else 0
    cpu_percent = psutil.cpu_percent(interval=1)
    vram_mb = await get_vram_used_mb()

    routing_str = "\n".join(
        [f"  - {k}: {v} requests" for k, v in routing_stats.items()]
    )

    dashboard = f"""
=== NinaGate Performance Monitor ===
Total Requests: {req_count}
Avg Latency: {avg_latency:.2f} ms
Avg TTFT: {avg_ttft:.2f} ms
Tokens In: {total_tokens_in}
Tokens Out: {total_tokens_out}

Routing Decisions:
{routing_str}

System Status:
CPU Load: {cpu_percent}%
GPU VRAM Used: {vram_mb} MB
====================================
"""
    return dashboard


if __name__ == "__main__":
    print(asyncio.run(parse_logs()))
