#!/usr/bin/env python3
"""
nina_hud.py - NINA Real-Time Heads Up Display
Tails the gemini scratchpad, routing logs, and system health.
Run in a separate terminal during long Gemini CLI or agy sessions.
"""

import time
import json
import os
import sys
from pathlib import Path

def tail_file(filepath, n_lines=10):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            # Read last 8192 bytes or up to file size (sane chunk for 10-15 lines)
            offset = min(size, 8192)
            if offset > 0:
                f.seek(size - offset, os.SEEK_SET)
                data = f.read(offset)
                lines = data.decode('utf-8', errors='replace').splitlines()
                # If we read only part of the file, the first line might be incomplete
                if offset < size and len(lines) > 1:
                    return lines[1:][-n_lines:]
                return lines[-n_lines:]
    except Exception:
        pass
    return []

def parse_scratchpad(line):
    try:
        data = json.loads(line)
        status_icon = "✅" if data.get("status") == "ok" else "❌" if data.get("status") == "fail" else "🔄"
        action = data.get("action", "").upper()
        detail = data.get("detail", "")
        file = data.get("file", "")
        file_str = f" [{file}] " if file else " "
        return f"{status_icon} {action}{file_str}- {detail}"
    except:
        return line.strip()

def parse_router(line):
    try:
        data = json.loads(line)
        provider = data.get("provider", "UNKNOWN")
        task = data.get("task", "")
        cost = data.get("cost", 0)
        return f"⚡ ROUTED: {task} -> {provider} (${cost:.6f})"
    except:
        return ""

def clear_screen():
    print("\033[H\033[J", end="")

def main():
    repo_root = Path(__file__).parent.parent.resolve()
    scratch_log = repo_root / "data" / "gemini_scratch.jsonl"
    router_log = repo_root / "logs" / "router.log"

    print("Starting NINA HUD... (Press Ctrl+C to exit)")
    
    last_scratch_size = 0
    last_router_size = 0

    while True:
        try:
            curr_s_size = os.path.getsize(scratch_log) if scratch_log.exists() else 0
            curr_r_size = os.path.getsize(router_log) if router_log.exists() else 0

            if curr_s_size != last_scratch_size or curr_r_size != last_router_size:
                clear_screen()
                print("="*60)
                print("🚀 NINA OMNIPOTENT HUD - REAL TIME TELEMETRY")
                print("="*60)
                
                print("\n🧠 RECENT AGENT THOUGHTS & ACTIONS (gemini_scratch):")
                scratch_lines = tail_file(scratch_log, 15)
                for line in scratch_lines:
                    print(parse_scratchpad(line))

                print("\n🌐 ROUTING DECISIONS (router.log):")
                router_lines = tail_file(router_log, 5)
                for line in router_lines:
                    parsed = parse_router(line)
                    if parsed: print(parsed)
                
                print("\n" + "="*60)
                
                last_scratch_size = curr_s_size
                last_router_size = curr_r_size
                
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nHUD Terminated.")
            sys.exit(0)
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
