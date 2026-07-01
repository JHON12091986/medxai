#!/usr/bin/env python3
"""
nina_debug.py v2 — Robust NINA development pipeline agent.

Usage (forever):
    cd ~/nina && git pull && python3 nina_debug.py && bash upload_debug_out.sh

Perplexity pushes nina_debug_task.json each round.
Fix scripts are pushed directly as .py files by Perplexity via MCP.
This script executes them via run_script — no escape mangling.

Actions: shell, run_script, compile, run_generator, grep, read,
         write_file, patch_file, git_log, resolve_conflicts
"""
import json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

REPO      = Path('/home/aibony/nina')
TASK_FILE = REPO / 'nina_debug_task.json'
OUT_FILE  = Path.home() / 'nina_debug_out.txt'
VENV_PY   = REPO / 'venv/bin/python3'
PYTHON    = str(VENV_PY) if VENV_PY.exists() else sys.executable

lines_out = []

def emit(s=''):  lines_out.append(str(s))
def section(t):  emit(); emit('='*60); emit(f' {t}'); emit('='*60)

# ── ACTIONS ──────────────────────────────────────────────────

def action_shell(spec):
    cmd = spec['cmd']
    section(f'SHELL: {cmd[:80]}')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO))
    if r.stdout.strip(): emit(r.stdout.rstrip())
    if r.stderr.strip(): emit(f'STDERR: {r.stderr.rstrip()}')
    emit(f'  → exit code {r.returncode}')
    return r.returncode

def action_run_script(spec):
    """Run a .py file pushed directly to the repo by Perplexity via MCP."""
    script = REPO / spec['file']
    section(f'RUN SCRIPT: {spec["file"]}')
    if not script.exists():
        emit(f'  ❌ NOT FOUND: {script}'); return 1
    r = subprocess.run([PYTHON, str(script)], capture_output=True, text=True, cwd=str(REPO))
    if r.stdout.strip(): emit(r.stdout.rstrip())
    if r.stderr.strip(): emit(f'STDERR: {r.stderr.rstrip()}')
    emit(f'  → exit code {r.returncode}')
    if spec['file'].startswith('_'):
        script.unlink(missing_ok=True)
        emit(f'  🗑  auto-deleted {spec["file"]}')
    return r.returncode

def action_compile(spec):
    section(f'COMPILE: {spec["file"]}')
    path = REPO / spec['file']
    if not path.exists(): emit('  ❌ NOT FOUND'); return 1
    r = subprocess.run([PYTHON, '-m', 'py_compile', str(path)], capture_output=True, text=True)
    emit('  ✅ OK') if r.returncode == 0 else emit(f'  ❌ COMPILE ERROR:\n{r.stderr}')
    return r.returncode

def action_run_generator(spec):
    section('RUN GENERATOR: error_register_sync.py')
    r = subprocess.run([PYTHON, 'tools/error_register_sync.py'], capture_output=True, text=True, cwd=str(REPO))
    if r.stdout.strip(): emit(r.stdout.rstrip())
    if r.stderr.strip(): emit(f'STDERR: {r.stderr.rstrip()}')
    emit(f'  → exit code {r.returncode}')

def action_grep(spec):
    section(f'GREP: {spec["pattern"]} in {spec.get("path",".")}')
    target = REPO / spec.get('path', '.')
    pattern = spec['pattern']
    excl = spec.get('exclude_dirs', ['.venv','venv','env','__pycache__','.git','node_modules','upgrades','dist','build'])
    exts = spec.get('include_ext', ['*.py'])
    count = 0
    for ext in exts:
        for p in sorted(target.rglob(ext)):
            if any(ex in p.relative_to(REPO).parts for ex in excl): continue
            try: text = p.read_text(encoding='utf-8', errors='replace')
            except: continue
            for i, line in enumerate(text.splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    emit(f'  {p.relative_to(REPO)}:{i}: {line.rstrip()}')
                    count += 1
    emit(f'  → {count} match(es)')

def action_read(spec):
    section(f'READ: {spec["file"]}')
    path = REPO / spec['file']
    if not path.exists(): emit('  ❌ NOT FOUND'); return
    raw = spec.get('lines')
    text_lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    if isinstance(raw, list):
        start, end = int(raw[0])-1, int(raw[1])
        text_lines = text_lines[start:end]
        emit(f'  (lines {raw[0]}-{raw[1]})')
    elif isinstance(raw, int):
        text_lines = text_lines[:raw]
        emit(f'  (first {raw} lines)')
    emit('\n'.join(text_lines))

def action_write_file(spec):
    section(f'WRITE: {spec["file"]}')
    path = REPO / spec['file']
    path.parent.mkdir(parents=True, exist_ok=True)
    content = spec['content']
    path.write_text(content, encoding='utf-8')
    emit(f'  ✅ written ({len(content)} bytes)')

def action_patch_file(spec):
    section(f'PATCH: {spec["file"]}')
    path = REPO / spec['file']
    if not path.exists(): emit('  ❌ NOT FOUND'); return
    src = path.read_text(encoding='utf-8')
    applied = 0
    for edit in spec.get('edits', []):
        if edit['search'] in src:
            src = src.replace(edit['search'], edit['replace'], 1)
            emit(f'  ✅ applied: {repr(edit["search"][:60])}...')
            applied += 1
        else:
            emit(f'  ⚠️  NOT FOUND: {repr(edit["search"][:60])}...')
    path.write_text(src, encoding='utf-8')
    emit(f'  → {applied}/{len(spec.get("edits",[]))} edits applied')

def action_git_log(spec):
    section(f'GIT LOG: {spec.get("file","")}')
    cmd = f'git log --oneline -20 -- {spec["file"]}' if 'file' in spec else 'git log --oneline -20'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(REPO))
    emit(r.stdout.rstrip())

def action_resolve_conflicts(spec):
    section(f'RESOLVE CONFLICTS: {spec["file"]}')
    path = REPO / spec['file']
    if not path.exists(): emit('  ❌ NOT FOUND'); return
    text = path.read_text(encoding='utf-8')
    if '<<<<<<<' not in text: emit('  ℹ️  no conflict markers found'); return
    lines, skip, count = [], False, 0
    for line in text.splitlines():
        if line.startswith('<<<<<<<'):   skip = False; count += 1
        elif line.startswith('======='): skip = True
        elif line.startswith('>>>>>>>'): skip = False
        elif not skip:                   lines.append(line)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    emit(f'  ✅ resolved {count} conflict(s) (kept HEAD)')

ACTION_MAP = {
    'shell': action_shell, 'run_script': action_run_script,
    'compile': action_compile, 'run_generator': action_run_generator,
    'grep': action_grep, 'read': action_read,
    'write_file': action_write_file, 'patch_file': action_patch_file,
    'git_log': action_git_log, 'resolve_conflicts': action_resolve_conflicts,
}

# ── MAIN ─────────────────────────────────────────────────────

def main():
    emit(f'NINA DEBUG AGENT v2 — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    if not TASK_FILE.exists():
        emit('ERROR: nina_debug_task.json not found.'); return
    task = json.loads(TASK_FILE.read_text(encoding='utf-8'))
    emit(f'Repo       : {REPO}')
    emit(f'Task round : {task.get("round","?")}')
    emit(f'Goal       : {task.get("goal","?")}')
    steps = task.get('steps', [])
    emit(f'Steps      : {len(steps)}')
    for i, step in enumerate(steps, 1):
        action = step.get('action', '')
        emit(f'\n[Step {i}/{len(steps)}] action={action}')
        fn = ACTION_MAP.get(action)
        if fn:
            try: fn(step)
            except Exception as e: emit(f'  ❌ EXCEPTION: {e}')
        else:
            emit(f'  ❌ UNKNOWN ACTION: {action}')
    emit(); emit('='*60); emit(' SUMMARY'); emit('='*60)
    emit(f'Completed {len(steps)} step(s).')
    emit('Run: bash upload_debug_out.sh — then say "uploaded" to Perplexity.')

if __name__ == '__main__':
    main()
    OUT_FILE.write_text('\n'.join(lines_out) + '\n', encoding='utf-8')
    print(f'Output → {OUT_FILE}')
