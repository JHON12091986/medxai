#!/usr/bin/env python3
# _fix_all.py — register repair, auto-deleted after run
from pathlib import Path

REPO = Path('/home/aibony/nina')
reg  = REPO / 'docs/space/nina_error_register.md'
lines = reg.read_text(encoding='utf-8').splitlines()

# Pass 1: fix corrupt merge_resolver row
out = []
for line in lines:
    if 'merge_resolver' in line and ('OPEN/PENDING' in line or '.*remove' in line):
        line = ('| todo.tools_merge_resolver_py_184 | \U0001f7e1 DEBT | tools |'
                ' [TODO] remove stale branch logic | \u2705 FIXED | unassigned |'
                ' R-debug-03 | tools/merge_resolver.py | 1 | 2026-06-19 | CLOSED |')
        print('[FIX1] Repaired corrupt merge_resolver row')
    out.append(line)

# Pass 2: flip every FIXED row that still ends with | OPEN |
flipped = 0
out2 = []
for line in out:
    if line.startswith('|') and '\u2705 FIXED' in line and line.rstrip().endswith('| OPEN |'):
        line = line.rstrip()[:-len('| OPEN |')] + '| CLOSED |'
        flipped += 1
    out2.append(line)

reg.write_text('\n'.join(out2) + '\n', encoding='utf-8')
print(f'[FIX2] Flipped {flipped} FIXED->CLOSED')
print(f'[FIX2] Total CLOSED rows: {sum(1 for l in out2 if "| CLOSED |" in l)}')
print('=== _fix_all.py DONE ===')
