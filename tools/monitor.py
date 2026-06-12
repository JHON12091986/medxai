import json
import os
import re
import glob
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

def parse_iso_ts(ts_str):
    """Parses ISO 8601 timestamps, handling common variations."""
    try:
        if re.search(r'\+\d{4}$', ts_str):
            ts_str = ts_str[:-2] + ":" + ts_str[-2:]
        ts_str = ts_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts_str).timestamp()
    except Exception:
        try:
            base = re.split(r'[\+\Z]', ts_str)[0]
            if len(base) > 19: base = base[:19]
            return datetime.strptime(base, "%Y-%m-%dT%H:%M:%S").timestamp()
        except Exception:
            return 0

def get_hw_metrics():
    """Collects CPU, RAM, and VRAM metrics."""
    metrics = {
        "cpu_load_pct": 0,
        "ram_available_mb": 0,
        "vram_used_mb": 0,
        "vram_total_mb": 0
    }
    
    if psutil:
        metrics["cpu_load_pct"] = psutil.cpu_percent(interval=0.1)
        metrics["ram_available_mb"] = int(psutil.virtual_memory().available / 1024 / 1024)
    
    try:
        # Check dGPU (NVIDIA)
        res = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"], 
                            capture_output=True, text=True)
        if res.returncode == 0:
            parts = res.stdout.strip().split(',')
            metrics["vram_used_mb"] = int(parts[0])
            metrics["vram_total_mb"] = int(parts[1])
    except Exception:
        pass
        
    return metrics

def parse_logs():
    data = {
        "local_requests": 0,
        "cloud_requests": 0,
        "cached_requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "tokens_saved": 0,
        "total_latency_ms": 0,
        "start_ts": float('inf'),
        "end_ts": 0,
        "offload_opportunities": 0,
        "parallel_count": 0
    }

    def process_entry(entry):
        nonlocal data
        prov = str(entry.get("provider", "")).upper()
        is_local = any(x in prov for x in ("OLLAMA", "NINAFLASH", "LOCAL", "QWEN"))
        is_cached = bool(entry.get("cached", False)) or prov == "CACHE"
        
        in_t = int(entry.get("input_tokens", 0))
        out_t = int(entry.get("output_tokens", 0))
        total_t = in_t + out_t
        
        if is_local:
            data["local_requests"] += 1
            data["tokens_saved"] += total_t
        elif is_cached:
            data["cached_requests"] += 1
            data["tokens_saved"] += total_t
        else:
            data["cloud_requests"] += 1
            
        data["total_input_tokens"] += in_t
        data["total_output_tokens"] += out_t
        
        latency = float(entry.get("total_ms", entry.get("latency_ms", 0)))
        data["total_latency_ms"] += latency
        
        if entry.get("parallel"):
            data["parallel_count"] += 1
            
        ts_str = entry.get("ts")
        if ts_str:
            try:
                end_t = parse_iso_ts(ts_str)
                start_t = end_t - (latency / 1000.0)
                if end_t > 0:
                    data["start_ts"] = min(data["start_ts"], start_t)
                    data["end_ts"] = max(data["end_ts"], end_t)
            except Exception: pass

    # 1. Parse router.log
    router_log = "logs/router.log"
    if os.path.exists(router_log):
        with open(router_log, "r") as f:
            for line in f:
                if "{" in line and "}" in line:
                    try:
                        match = re.search(r'(\{.*\})', line)
                        if match:
                            process_entry(json.loads(match.group(1)))
                    except Exception: pass

    # 2. Parse ninagate.log
    ninagate_log = "logs/ninagate.log"
    if os.path.exists(ninagate_log):
        with open(ninagate_log, "r") as f:
            for line in f:
                if "OFFLOAD_OPPORTUNITY" in line:
                    data["offload_opportunities"] += 1
                if "{" in line and "}" in line:
                    try:
                        match = re.search(r'(\{.*\})', line)
                        if match:
                            process_entry(json.loads(match.group(1)))
                    except Exception: pass

    return data

def update_dashboard(score_pct):
    dashboard_path = 'dashboard/nina-guardian.html'
    if os.path.exists(dashboard_path):
        try:
            with open(dashboard_path, 'r') as f:
                content = f.read()
            content = re.sub(r'id="evolution-score"[^>]*>.*?</span>', 
                            f'id="evolution-score" style="color:var(--color-primary)">{score_pct:.1f}%</span>', content)
            with open(dashboard_path, 'w') as f:
                f.write(content)
        except Exception: pass

def generate_efficiency_report():
    data = parse_logs()
    data["hw"] = get_hw_metrics()
    
    total_reqs = data["local_requests"] + data["cloud_requests"] + data["cached_requests"]
    
    if data["start_ts"] == float('inf'):
        data["start_ts"] = 0
        
    wall_time_s = data["end_ts"] - data["start_ts"] if data["end_ts"] > data["start_ts"] else 0
    data["wall_time_s"] = round(wall_time_s, 2)
    data["rpm"] = round((total_reqs / (wall_time_s / 60.0)), 2) if wall_time_s > 60 else total_reqs
    
    data["sequential_time_s"] = round(data["total_latency_ms"] / 1000.0, 2)
    data["time_efficiency_s"] = round(data["sequential_time_s"] - wall_time_s, 2)
    
    total_tokens = data["total_input_tokens"] + data["total_output_tokens"]
    data["token_savings_pct"] = round((data["tokens_saved"] / total_tokens) * 100, 2) if total_tokens > 0 else 0

    with open('efficiency_report.json', 'w') as f:
        json.dump(data, f, indent=4)
        
    update_dashboard(data["token_savings_pct"])
    return data

if __name__ == "__main__":
    report = generate_efficiency_report()
    print("========================================")
    print("  NINA DEEP METRICS ENGINE v5.0")
    print("========================================")
    print(f"  Token Savings:    {report['token_savings_pct']}% ({report['tokens_saved']} tokens)")
    print(f"  Time Efficiency:  {report['time_efficiency_s']}s")
    print(f"  Throughput Rank:  {report['rpm']} RPM")
    print(f"  Hardware Load:    CPU {report['hw']['cpu_load_pct']}% | VRAM {report['hw']['vram_used_mb']}MB")
    print("----------------------------------------")
    print(f"  Local Requests:   {report['local_requests']}")
    print(f"  Cloud Requests:   {report['cloud_requests']}")
    print("========================================")
