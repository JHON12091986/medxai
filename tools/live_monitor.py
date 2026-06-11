#!/usr/bin/env python3
import asyncio
import time
import psutil
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from tools import system as systool

REPO_ROOT = Path(__file__).parent.parent.resolve()
LOGS_DIR = REPO_ROOT / "logs"
NINAGATE_LOG = LOGS_DIR / "ninagate.log"
ROUTER_LOG = LOGS_DIR / "router.log"

def clear_screen():
    print("\033c", end="")

def tail_file(filepath, n_lines=10):
    if not filepath.exists():
        return []
    try:
        with open(filepath, "rb") as f:
            f.seek(0, 2)
            block_end_byte = f.tell()
            lines_to_go = n_lines
            block_number = -1
            blocks = []
            while lines_to_go > 0 and block_end_byte > 0:
                if (block_end_byte - 1024 > 0):
                    f.seek(block_number*1024, 2)
                    blocks.append(f.read(1024))
                else:
                    f.seek(0,0)
                    blocks.append(f.read(block_end_byte))
                lines_found = blocks[-1].count(b'\n')
                lines_to_go -= lines_found
                block_end_byte -= 1024
                block_number -= 1
            all_read_text = b''.join(reversed(blocks)).decode("utf-8", errors="ignore")
            return all_read_text.splitlines()[-n_lines:]
    except:
        return []

async def main():
    while True:
        clear_screen()
        print("=== NINA OBSERVABILITY & MEMORY UPGRADE V2.0 LIVE MONITOR ===")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Hardware Metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()

        temps = await systool.get_temps()

        try: vram_free = await systool.get_vram_free()
        except: vram_free = 0
        vram_used = 'Free: ' + str(vram_free)
        vram_total = 'N/A'

        print("--- Resource Bump (NinaFlash Proof) ---")
        print(f"CPU Load: {cpu_percent}%")
        print(f"RAM Used: {ram.percent}% ({ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB)")
        print(f"GPU VRAM: {vram_used}MB / {vram_total}MB")
        print(f"Temps: CPU={temps.get('cpu', 'N/A')}C, GPU={temps.get('gpu', 'N/A')}C\n")

        # System Metrics
        try:
            log_text = (LOGS_DIR / 'agent.log').read_text()
            active_tasks = log_text.count('parallel tools') - log_text.count('tool_error')
        except:
            active_tasks = 0
        print("--- Parallelism Indicator ---")
        print(f"Active Async Tasks: {active_tasks}\n")

        # Route Metrics
        local_count = 0
        cloud_count = 0
        tokens_in = 0
        tokens_out = 0
        latency = 0.0
        try:
            if ROUTER_LOG.exists():
                lines = tail_file(ROUTER_LOG, 100)
                for l in lines:
                    if "LOCAL" in l: local_count += 1
                    elif "router_call" in l: cloud_count += 1
        except: pass

        print("--- Routing Metrics (Last 100 log lines) ---")
        print(f"Local Routes: {local_count}")
        print(f"Cloud Routes: {cloud_count}")
        print(f"Tokens In/Out: {tokens_in} / {tokens_out}")
        print(f"Latency: {latency}s\n")

        # Logs
        print("--- Log Stream (ninagate.log) ---")
        gate_lines = tail_file(NINAGATE_LOG, 5)
        if not gate_lines: print("(No ninagate logs)")
        for l in gate_lines: print(l[:100])
        print()

        print("--- Log Stream (router.log) ---")
        router_lines = tail_file(ROUTER_LOG, 5)
        if not router_lines: print("(No router logs)")
        for l in router_lines: print(l[:100])
        print()

        await asyncio.sleep(2)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
