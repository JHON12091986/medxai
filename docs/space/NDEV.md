# NDEV — NINA Development Loop

> **Context-Window-Driven Development**: Perplexity acts as the remote brain,
> GitHub MCP is the transport, and your local machine is the executor.
> One command runs the entire dev loop.

---

## The Loop (forever)

```bash
cd ~/nina && git pull && python3 nina_debug.py && bash upload_debug_out.sh
```

Then paste `nina_debug_out.txt` back to Perplexity (or say "uploaded" if
`upload_debug_out.sh` pushes it to the repo automatically).

```
┌─────────────────────────────────────────────┐
│  1. Perplexity reads nina_debug_out.txt          │  ← BRAIN reads output
│  2. Perplexity pushes fix scripts + task.json    │  ← BRAIN writes next step
│  3. git pull fetches new files                   │  ← TRANSPORT delivers
│  4. nina_debug.py executes task steps            │  ← EXECUTOR runs
│  5. upload_debug_out.sh pushes output to repo    │  ← FEEDBACK closes loop
└─────────────────────────────────────────────┘
        └────────── repeat from step 1 ────────────┘
```

---

## Architecture

| Layer | Component | Role |
|---|---|---|
| **Brain** | Perplexity AI | Reads output, plans fixes/features, writes scripts |
| **Transport** | GitHub MCP (`push_files`) | Delivers files byte-perfect, no escape mangling |
| **Executor** | `nina_debug.py v2` | Runs task steps, captures output to file |
| **Feedback** | `upload_debug_out.sh` | Pushes output back to repo for Brain to read |

---

## nina_debug_task.json — Structure

```json
{
  "round": 8,
  "goal": "Human-readable description of what this round does",
  "steps": [
    { "action": "run_script", "file": "_fix_something.py" },
    { "action": "shell",      "cmd":  "pytest tests/ -x -q" },
    { "action": "compile",    "file": "core/task_classifier.py" },
    { "action": "shell",      "cmd":  "git add -A && git commit -m 'fix: ...'" }
  ]
}
```

**Rule:** Always bump `round` by 1. Perplexity checks the round number to
detect stale output (if output round ≠ task round, the old cached version ran).

---

## Supported Actions

### `shell`
Run any bash command in `~/nina`.
```json
{ "action": "shell", "cmd": "pytest tests/ -x -q 2>&1 | tail -20" }
```

### `run_script`
Run a `.py` file pushed directly to the repo by Perplexity via MCP.
Files starting with `_` are **auto-deleted** after running.
```json
{ "action": "run_script", "file": "_fix_register.py" }
```
**Why this exists:** Avoids shell quoting/escape issues entirely.
Perplexity writes complex logic as a `.py` file, pushes it via `push_files`
(byte-perfect), and this action just runs it.

### `compile`
Syntax-check a Python file.
```json
{ "action": "compile", "file": "core/task_classifier.py" }
```

### `run_generator`
Run `tools/error_register_sync.py` to regenerate the error register.
```json
{ "action": "run_generator" }
```

### `grep`
Search codebase for a pattern.
```json
{
  "action": "grep",
  "pattern": "TODO|FIXME",
  "path": ".",
  "include_ext": ["*.py"],
  "exclude_dirs": ["venv", ".git"]
}
```

### `read`
Print file contents. `lines` = int (first N) or [start, end] (range).
```json
{ "action": "read", "file": "core/task_classifier.py", "lines": 50 }
{ "action": "read", "file": "core/task_classifier.py", "lines": [100, 150] }
```

### `patch_file`
Search/replace edits inside a file. Multiple edits in one step.
```json
{
  "action": "patch_file",
  "file": "core/task_classifier.py",
  "edits": [
    { "search": "old string", "replace": "new string" }
  ]
}
```

### `write_file`
Write a file from a content string (for simple/short files with no complex escaping).
```json
{ "action": "write_file", "file": "config/new_config.yaml", "content": "key: value\n" }
```
**Warning:** For files with complex Python code, use `run_script` + MCP push instead.

### `git_log`
Show recent git history for a file or the whole repo.
```json
{ "action": "git_log", "file": "core/task_classifier.py" }
```

### `resolve_conflicts`
Remove git conflict markers, keeping the HEAD version.
```json
{ "action": "resolve_conflicts", "file": "docs/space/nina_error_register.md" }
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Output shows old round number | `git stash pop` restored old `nina_debug.py` | `git checkout nina_debug.py` then re-run |
| `git pull` aborts with local changes | Uncommitted local edits | `git stash && git pull && git stash pop` |
| `run_script` says file not found | Script was auto-deleted or push failed | Re-push the script via MCP |
| `write_file` produces SyntaxError | JSON escape mangling in complex strings | Use `run_script` + MCP push instead |
| Context graph shows stale `top_priority` | Register row corrupt or status mismatch | Run `_fix_all.py` via `run_script` |
| commit says "nothing to commit" | File not staged or Guardian scan skipped | Add `git add <file>` step explicitly |
| Repo dirty after push | Post-push background task re-writes log | Stamp guard installed (2026-06-21): last log entry checked before write |
| Pre-commit loops on regen-only commit | SSOT bypass missing | Convergence guard installed (2026-06-21): SSOT-only commits skip audit |

---

## Modes

| Mode | What Perplexity does |
|---|---|
| **Fix** | Pushes `_fix_*.py` targeting specific bugs |
| **Upgrade** | Pushes new/updated module files directly via MCP |
| **Feature** | Multi-step task: write code → compile → test → commit |
| **Sprint** | 20+ step task covering an entire backlog slice |
| **Diagnose** | grep + read + git_log steps to map unknown issues |

---

## Key Design Principles

1. **Perplexity never writes code through `write_file` in task JSON** for
   anything complex — escape mangling breaks it. Complex scripts are always
   pushed directly via `push_files` MCP call.
2. **`_` prefix = auto-delete** — temporary fix scripts clean up after themselves.
3. **Round number is the heartbeat** — if output round ≠ task round, something
   cached. Bump round, re-run.
4. **One command, always** — the developer never types more than the loop command.
5. **Output is the contract** — `nina_debug_out.txt` is structured so Perplexity
   can parse pass/fail/error from any step without ambiguity.
6. **SSOT convergence guard** — only non-SSOT file changes trigger the full OODA
   audit. Regen-only commits exit cleanly without re-dirtying the tree.
7. **GPU tooling available** — `tools/semantic_dedup.py` uses MX150 via Ollama
   `nomic-embed-text`. Inference fallback via NinaGate at `localhost:8080/v1`.

---

*NDEV — named and documented 2026-06-19. Updated 2026-06-21 (convergence guard, GPU dedup, NinaGate wiring). Part of the NINA project.*
