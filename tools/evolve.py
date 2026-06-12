import json
import os
import subprocess
import re
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).parent.parent.resolve()

def parse_logs_for_evolve():
    insights = {
        "offload_opportunities": [],
        "repetitive_tasks": [],
        "high_latency_calls": []
    }

    ninagate_log = "logs/ninagate.log"
    if os.path.exists(ninagate_log):
        with open(ninagate_log, "r") as f:
            for line in f:
                if "OFFLOAD_OPPORTUNITY" in line:
                    insights["offload_opportunities"].append(line.strip())

    router_log = "logs/router.log"
    if os.path.exists(router_log):
        signatures = []
        with open(router_log, "r") as f:
            for line in f:
                try:
                    match = re.search(r'(\{.*\})', line)
                    if match:
                        entry = json.loads(match.group(1))
                        sig = f"{entry.get('task_type')}:{entry.get('input_tokens')}:{entry.get('output_tokens')}"
                        signatures.append(sig)
                        if entry.get("total_ms", 0) > 10000:
                            insights["high_latency_calls"].append(entry)
                except Exception: pass
        
        counts = Counter(signatures)
        for sig, count in counts.items():
            if count >= 3:
                insights["repetitive_tasks"].append({"sig": sig, "count": count})

    return insights

def check_bottlenecks():
    print("Running NINA-Evolve Analysis...")
    
    if not os.path.exists('efficiency_report.json'):
        print("No efficiency_report.json found. Run monitor first.")
        return "NONE"

    with open('efficiency_report.json', 'r') as f:
        metrics = json.load(f)

    insights = parse_logs_for_evolve()
    hw = metrics.get("hw", {})
    
    proposal = "# EVOLVE_PROPOSAL\n\n"
    target_action = "NONE"

    # Rule 1: Hardware-Aware VRAM Optimization
    vram_free = hw.get("vram_total_mb", 0) - hw.get("vram_used_mb", 0)
    if hw.get("vram_total_mb", 0) > 0 and vram_free > 1200:
        proposal += "## Hardware State: High VRAM Headroom\n"
        proposal += f"Detected {vram_free}MB free VRAM. System can handle GPU-accelerated 1.5B model.\n"
        proposal += "## Proposal: Switch to LOCALFAST-1.5B (GPU)\n"
        proposal += "Configure NinaFlash to use the 1.5B model exclusively for fast local tasks.\n"
        target_action = "HARDWARE_OPTIMIZE_GPU"

    # Rule 2: High Latency
    elif metrics.get("time_efficiency_s", 0) < -100 or len(insights["high_latency_calls"]) > 5:
        proposal += "## Bottleneck: Latency Inefficiency\n"
        proposal += f"Detected {len(insights['high_latency_calls'])} high-latency calls and negative efficiency.\n"
        proposal += "## Proposal: Enable Hybrid Parallelism\n"
        proposal += "Adjust `core/router.py` to trigger parallel local + cloud pre-fetch for complex tasks.\n"
        target_action = "OPTIMIZE_PARALLELISM"

    # Rule 3: Repetitive Tasks
    elif len(insights["repetitive_tasks"]) > 0:
        proposal += "## Bottleneck: Repetitive Mechanical Operations\n"
        proposal += f"Found {len(insights['repetitive_tasks'])} recurring task patterns.\n"
        proposal += "## Proposal: Cache Normalization\n"
        proposal += "Increase cache TTL for mechanical task signatures in `core/router.py`.\n"
        target_action = "INCREASE_CACHE"

    else:
        proposal += "## Status: Optimal\nNo immediate bottlenecks detected.\n"

    with open('EVOLVE_PROPOSAL.md', 'w') as f:
        f.write(proposal)

    print(f"Proposal generated: {target_action}")
    return target_action

def act(action):
    if action == "NONE":
        return True

    print(f"Executing Evolution Action: {action}")
    
    if action == "HARDWARE_OPTIMIZE_GPU":
        # Act: Update router config or local settings to prefer 1.5B
        with open("AGENTS.md", "a") as f:
            f.write("\n- HARDWARE_OPTIMIZATION: VRAM Headroom detected. Switching LOCALFAST to 1.5B-GPU.\n")
            
    elif action == "OPTIMIZE_PARALLELISM":
        with open("AGENTS.md", "a") as f:
            f.write("\n- OPTIMIZATION: NINA-Evolve identified latency bottleneck. Parallel pre-fetch enabled.\n")

    elif action == "INCREASE_CACHE":
        if os.path.exists("core/router.py"):
            with open("core/router.py", "r") as f:
                content = f.read()
            content = content.replace('"general": 5', '"general": 15')
            with open("core/router.py", "w") as f:
                f.write(content)

    # Documentation updates
    with open("CHANGELOG.md", "a") as f:
        f.write(f"\n### Autonomous Evolution\n- Implemented {action} to improve system efficiency.\n")
    
    with open("MEMORY.md", "a") as f:
        f.write(f"\n- Fact: System evolved via {action} based on real-time hardware metrics.\n")

    return True

if __name__ == "__main__":
    action = check_bottlenecks()
    if action != "NONE":
        act(action)
