#!/usr/bin/env python3
import json
import time
import re
import hashlib
from pathlib import Path
from rich.live import Live
from rich.text import Text

SCRATCH = Path.home() / 'nina' / 'data' / 'gemini_scratch.jsonl'
POLL_SEC = 0.4

ACTION_STYLE = {
    'start': 'bold white',
    'read': 'cyan',
    'write': 'green',
    'shell': 'yellow',
    'think': 'blue',
    'error': 'bold red',
    'stuck': 'bold red',
    'done': 'bold magenta',
    'audit': 'grey50'
}

def get_current_run():
    if not SCRATCH.exists():
        return [], None
    try:
        lines = SCRATCH.read_text(errors='replace').strip().splitlines()
        rows = []
        for line in lines:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
        
        # Find the last "start" action
        start_idx = 0
        for i in range(len(rows) - 1, -1, -1):
            if rows[i].get('action') == 'start':
                start_idx = i
                break
        
        current_run = rows[start_idx:]
        start_entry = rows[start_idx] if rows else None
        return current_run, start_entry
    except Exception:
        return [], None

def get_progress_info(current_run):
    if not current_run:
        return 0, 10, 'waiting', 'waiting'
    
    last_entry = current_run[-1]
    last_action = last_entry.get('action', 'think')
    last_detail = last_entry.get('detail', '')
    
    current_step = 0
    total_steps = 10
    found_step = False
    
    for r in reversed(current_run):
        detail = r.get('detail', '')
        m = re.search(r'(?:[Ss]tep\s+)?(\d+)/(\d+)', detail)
        if m:
            current_step = int(m.group(1))
            total_steps = int(m.group(2))
            found_step = True
            break
            
    if not found_step:
        current_step = last_entry.get('step', 0)
        if current_step < 0:
            if last_action == 'done':
                current_step = 10
                total_steps = 10
            else:
                current_step = 0
                total_steps = 10
        else:
            total_steps = max(10, current_step + 3)
            
    if last_action == 'done':
        current_step = total_steps
        
    return current_step, total_steps, last_action, last_detail

def get_main_task_color(start_entry):
    if not start_entry:
        return 'grey50'
    start_detail = start_entry.get('detail', '')
    colors = ['cyan', 'green', 'yellow', 'magenta', 'blue', 'red']
    h = int(hashlib.md5(start_detail.encode('utf-8')).hexdigest(), 16)
    return colors[h % len(colors)]

def main():
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    with Live(refresh_per_second=int(1/POLL_SEC), screen=False) as live:
        while True:
            current_run, start_entry = get_current_run()
            current_step, total_steps, last_action, last_detail = get_progress_info(current_run)
            main_color = get_main_task_color(start_entry)
            sub_color = ACTION_STYLE.get(last_action, 'white')
            
            # Constraints
            total_steps = max(1, total_steps)
            current_step = max(0, min(total_steps, current_step))
            
            # Build bar components
            width = 40
            filled_width = int((current_step / total_steps) * width)
            empty_width = width - filled_width
            
            filled_char = '━'
            empty_char = '─'
            
            bar_text = Text()
            bar_text.append("▕", style=f"bold {main_color}")
            if filled_width > 0:
                bar_text.append(filled_char * filled_width, style=sub_color)
            if empty_width > 0:
                bar_text.append(empty_char * empty_width, style=f"dim {main_color}")
            bar_text.append("▏", style=f"bold {main_color}")
            
            # Simple indicator at the end
            bar_text.append(f"  ● {last_action}", style=sub_color)
            bar_text.append(f" ({current_step}/{total_steps})", style="dim")
            
            live.update(bar_text)
            time.sleep(POLL_SEC)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
