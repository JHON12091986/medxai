#!/usr/bin/env python3
import json, time, os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

NINA_ROOT = Path.home() / 'nina'
NINAGATE_LOG = NINA_ROOT / 'logs' / 'ninagate.log'

def get_rule0_score(hours=8):
    """Compute local routing % from ninagate.log for the last N hours."""
    if not NINAGATE_LOG.exists():
        return None, 0, 0, 0
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    total = local = cloud_violations = 0
    try:
        for raw in NINAGATE_LOG.read_text(errors='replace').splitlines():
            try:
                e = json.loads(raw.strip())
                ts_str = e.get('ts', '')
                if not ts_str:
                    continue
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < cutoff:
                    continue
                total += 1
                if e.get('provider') == 'ollama':
                    local += 1
                elif e.get('task_type') == 'SIMPLE':
                    cloud_violations += 1
            except Exception:
                pass
    except Exception:
        pass
    pct = (local / total * 100) if total else 0.0
    return pct, local, total, cloud_violations

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

def build_rule0_bar(pct, local, total, violations):
    """Build a compact RULE 0 status string for the panel title."""
    if total == 0:
        return '[dim]RULE0: no data[/dim]'
    icon = '✅' if pct >= 66 else '❌'
    color = 'green' if pct >= 66 else 'red'
    viol = f'  [yellow]⚠ {violations} SIMPLE→cloud[/yellow]' if violations else ''
    return (f'[{color}]{icon} RULE0: {local}/{total} local ({pct:.1f}%)[/{color}]{viol}')

def main():
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    with Live(refresh_per_second=int(1/POLL_SEC), screen=False) as live:
        while True:
            rows = read_tail()
            last = rows[-1] if rows else {}
            status_line = f'[bold]{last.get("action","waiting")}[/bold] — {last.get("detail","no activity yet")}'
            pct, local_n, total_n, viols = get_rule0_score()
            rule0_bar = build_rule0_bar(pct or 0.0, local_n, total_n, viols)
            panel = Panel(
                build_table(rows),
                title=(
                    f'[bold cyan]Gemini CLI Live Scratchpad[/bold cyan]  '
                    f'{datetime.now().strftime("%H:%M:%S")}  │  {rule0_bar}'
                ),
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
