import json
import os
import re

def parse_logs():
    data = {
        "local_requests": 0,
        "cloud_requests": 0,
        "latency_spikes": 0,
        "offload_opportunities": 0
    }

    if os.path.exists("logs/router.log"):
        with open("logs/router.log", "r") as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    if log_entry.get("provider", "").startswith("LOCAL"):
                        data["local_requests"] += 1
                    else:
                        data["cloud_requests"] += 1
                    if log_entry.get("latency", 0) > 5.0:
                        data["latency_spikes"] += 1
                except json.JSONDecodeError:
                    pass

    if os.path.exists("logs/ninagate.log"):
        with open("logs/ninagate.log", "r") as f:
            for line in f:
                if "OFFLOAD_OPPORTUNITY" in line:
                    data["offload_opportunities"] += 1

    return data

def update_dashboard(score_pct):
    if os.path.exists('dashboard/nina-guardian.html'):
        with open('dashboard/nina-guardian.html', 'r') as f:
            content = f.read()

        content = re.sub(r'id="evolution-score"[^>]*>.*?</span>', f'id="evolution-score" style="color:var(--color-primary)">{score_pct:.1f}%</span>', content)

        with open('dashboard/nina-guardian.html', 'w') as f:
            f.write(content)

def generate_efficiency_report():
    data = parse_logs()

    # Calculate simple token savings baseline vs actual
    # Assuming baseline = all cloud
    total_reqs = data["local_requests"] + data["cloud_requests"]
    data["baseline_cloud_reqs"] = total_reqs
    data["token_savings_pct"] = (data["local_requests"] / total_reqs) * 100 if total_reqs > 0 else 0

    with open('efficiency_report.json', 'w') as f:
        json.dump(data, f, indent=4)

    update_dashboard(data["token_savings_pct"])

    return data
