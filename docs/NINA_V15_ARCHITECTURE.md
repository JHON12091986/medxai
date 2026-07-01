# NINA v15 Architecture — Guardian Loop & Permanence Engine

> **Status**: Implemented — commit `feat(v15): implement Guardian Loop`  
> **Owner**: M. Baizid Alam, AGM, BASIC Bank PLC

## The Five New Modules

| Module | Role | Replaces |
|---|---|---|
| `core/indexer.py` | AST semantic symbol index (SQLite, 5ms lookup) | `CODEBASE_MAP.md` reads |
| `core/canonicalization.py` | Alias cluster detection + SSOT rename proposals | `patch_authorized_user_id.sh` |
| `core/file_registry.py` | FILE_PURPOSE parser, dependency graph, orphan detection | Manual architecture docs |
| `core/guardian_loop.py` | The Snake Loop — runs on every commit | `nina_fix.sh`, `nina_cleanup_sprint.sh` |
| `git-hooks/post-commit` | Wires Guardian Loop to every git commit | Cron-based polling |

---

## The Guardian Loop (Snake Loop)

Every Python file change in a commit triggers:

```
Commit
  ↓
[1] AST Scan       — syntax validation of changed files
  ↓
[2] Index Update   — incremental SQLite symbol index update
  ↓
[3] Doc Update     — flags stale documentation candidates
  ↓
[4] Registry Update — refreshes file dependency + orphan graph
  ↓
[5] Redundancy Scan — runs canonicalization, reports alias clusters
  ↓
[6] Memory Update  — signals memory consolidator
  ↓
[7] Health Check   — import validation of changed modules
  ↓
Done → logs/guardian_loop.jsonl
```

Runs **in background** (non-blocking). Critical step (AST) can abort the loop.

---

## Activating the Hook

```bash
# Option A — symlink (recommended, auto-updates with repo)
git config core.hooksPath git-hooks

# Option B — copy
cp git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

---

## Semantic Index Usage

```bash
# Index the full repo (incremental — skips unchanged files)
python -m core.indexer

# Search for any symbol
python -m core.indexer search auth_user
python -m core.indexer search telegram_chat function

# Stats
python -m core.indexer stats
```

---

## Canonicalization Usage

```bash
# Detect alias clusters
python -m core.canonicalization

# JSON output for Jules/Gemini prompt injection
python -m core.canonicalization --json
```

---

## File Registry Usage

```bash
# Full registry report (orphans + missing FILE_PURPOSE)
python -m core.file_registry

# JSON stats
python -m core.file_registry --json
```

---

## FILE_PURPOSE Convention

Every new file in `core/`, `agents/`, `tools/` **must** include:

```python
FILE_PURPOSE = {
    "why": "one sentence reason for existence",
    "owner": "component or person",
    "breaks_if_removed": ["list of dependent features"],
    "dependencies": ["module1", "module2"],
    "replaces": "what this supersedes (optional)",
}
```

The file registry scans for this and reports coverage `%`.

---

## Layer Stack Summary

```
Layer 1 — Permanence Engine     ← guardian_loop.py + post-commit hook
Layer 2 — Semantic Brain        ← indexer.py (AST → SQLite)
Layer 3 — Token Killer          ← indexer replaces 317KB CODEBASE_MAP reads
Layer 4 — Autonomous Intelligence ← guardian_loop reflection + health steps  
Layer 5 — Architecture Guardian ← canonicalization.py + file_registry.py
```
