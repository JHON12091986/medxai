#!/usr/bin/env python3
import json, time, os
from pathlib import Path
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

SCRATCH = Path.home() / 'nina' / 'data' / 'gemini_scratch.jsonl'
MAX_ROWS = 20
POLL_SEC = 0.4

ACTION_STYLE = {
    'start': 'bold cyan', 'read': 'dim white', 'write': 'bold green',
    'shell': 'yellow', 'think': 'blue', 'error': 'bold red',
    'stuck': 'bold red', 'done': 'bold magenta',
}

def read_tail(n=MAX_ROWS):
    if not SCRATCH.exists():
        return []
    try:
        lines = SCRATCH.read_text().strip().splitlines()
        rows = []
        for line in lines[-n:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
        return rows
    except Exception:
        return []

def build_table(rows):
    t = Table(box=box.SIMPLE_HEAD, expand=True, show_header=True,
              header_style='bold white on grey23')
    t.add_column('#', style='dim', width=4)
    t.add_column('Time', width=8)
    t.add_column('Action', width=8)
    t.add_column('File', style='cyan', overflow='fold', ratio=2)
    t.add_column('Detail', overflow='fold', ratio=4)
    t.add_column('Status', width=6)
    for r in rows:
        ts = r.get('t','')[-8:-3] if r.get('t') else '--:--'
        action = r.get('action','?')
        status = r.get('status','?')
        style = ACTION_STYLE.get(action, 'white')
        status_style = 'green' if status == 'ok' else 'red'
        t.add_row(
            str(r.get('step','')),
            ts,
            Text(action, style=style),
            r.get('file','') or '',
            r.get('detail',''),
            Text(status, style=status_style),
        )
    return t

def main():
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    with Live(refresh_per_second=int(1/POLL_SEC), screen=False) as live:
        while True:
            rows = read_tail()
            last = rows[-1] if rows else {}
            status_line = f'[bold]{last.get("action","waiting")}[/bold] — {last.get("detail","no activity yet")}'
            panel = Panel(
                build_table(rows),
                title=f'[bold cyan]Gemini CLI Live Scratchpad[/bold cyan]  {datetime.now().strftime("%H:%M:%S")}',
                subtitle=status_line,
                border_style='cyan' if last.get('status') != 'fail' else 'red',
            )
            live.update(panel)
            time.sleep(POLL_SEC)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Watcher stopped.')
