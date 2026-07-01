# NINA RAID-2 Blueprint — Self-Directed Gap Analysis
**Date:** 25 June 2026  
**Status:** DRAFT — awaiting executor confirmation  
**Evolution Trigger:** Consecutive audit streak > 100  
**Author:** Architect Overwatch (Perplexity)

---

## 1. Executive Summary

RAID-2 graduates NINA from **reactive task execution** (human-authored backlog entries) to **proactive self-diagnosis** (system-authored entries). A lightweight background daemon — the **GapScanner** — runs on a 5-minute cron cadence, scans telemetry, error registers, and repo hygiene signals, then autonomously drafts prioritised tasks into `docs/space/jules_backlog.md`.

This design deliberately fits within the 2 GB VRAM ceiling and the `systemd --user` constraint by keeping the daemon **LLM-free** (Mechanic / INTP tier). LLM inference is invoked only for a single optional step (task title summarisation) and only when a Strategist worker slot is free.

---

## 2. Bedrock Constraints (Non-Negotiables)

| Constraint | Enforcement |
|---|---|
| VRAM ≤ 2 GB | GapScanner is pure Python, zero VRAM; optional LLM step uses existing Strategist pool |
| Mechanic thread < 100 ms | Scan loop is async I/O-bound; no blocking calls in hot path |
| Strategist workers ≤ 2 | LLM summarisation queued, never spawns new threads |
| `systemd --user` only | Service unit uses `[Service] Type=simple`; no `sudo` |
| Guardian pipeline | GapScanner never touches guardian-protected files; writes only to `docs/space/jules_backlog.md` |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  NINA Kernel (core/kernel.py)        │
│                                                      │
│  ┌──────────────┐   scheduler tick (5 min)           │
│  │ Mechanic Bus │──────────────────────────────────┐ │
│  └──────────────┘                                  │ │
│                                              ┌─────▼──────────────┐
│                                              │  GapScanner Daemon  │
│                                              │  (INTP, LLM-free)   │
│                                              │                     │
│   ┌──────────────────────────────────────────┤  1. TelemetryScan   │
│   │                                          │  2. ErrorRegScan    │
│   │  signals: [GapScanResult]               │  3. HygieneScan     │
│   │                                          │  4. BacklogDrafter  │
│   ▼                                          └─────────────────────┘
│  ┌──────────────┐   (optional)                                      
│  │ Strategist   │◄── summarise_task_title(raw_gap) [async queue]    
│  │ Worker Pool  │                                                    
│  └──────────────┘                                                    
└─────────────────────────────────────────────────────┘

   BacklogDrafter writes ──► docs/space/jules_backlog.md
   (append-only, idempotent by gap_id fingerprint)
```

---

## 4. Module Breakdown

### 4.1 `core/gap_scanner/scanner.py`

Entry point for the daemon.  
- `GapScanner` class with `async def run_cycle()` method.  
- Invoked by `core/kernel.py` via the existing scheduler at 5-minute intervals.  
- Returns a `list[GapItem]` dataclass.

```python
@dataclass
class GapItem:
    gap_id: str          # sha256[:12] of (source + raw_text)
    source: str          # 'telemetry' | 'error_register' | 'hygiene'
    priority: str        # 'P1' | 'P2' | 'P3'
    raw_text: str        # human-readable description
    suggested_label: str # e.g. 'feat(telemetry):' | 'fix(core):'
    status: str          # 'READY' | 'BACKLOG'
```

**Idempotency:** Before writing, the drafter reads existing backlog, extracts all `gap_id` fingerprints from task metadata lines (`<!-- gap_id: <id> -->`), and skips duplicates.

---

### 4.2 `core/gap_scanner/telemetry_scan.py`  *(Mechanic / INTP)*

**Input:** `telemetry.jsonl` (tail-read, last 500 lines) + DB sink query via existing telemetry connector.  
**Logic:**
- Count error-class events in the last 60 minutes; if `count > threshold` → generate gap item.
- Detect latency spikes: p95 latency > 3× rolling baseline → P1 gap.
- Detect silent channels: if a registered intent handler has emitted 0 events in 24 h → P3 gap.

**Cost:** Pure file I/O + regex; < 10 ms per cycle.

---

### 4.3 `core/gap_scanner/error_register_scan.py`  *(Mechanic / INTP)*

**Input:** `docs/space/nina_error_register.md`  
**Logic:**
- Parse markdown table rows matching `| OPEN |` status.
- For each open bug, check if a backlog task with matching `gap_id` already exists.
- If not → draft `fix(<module>): <bug_title>` with P1 for CRITICAL, P2 for HIGH, P3 for MEDIUM.

**Regex anchor:**
```python
OPEN_ROW = re.compile(r'\|\s*OPEN\s*\|.*?\|\s*(?P<sev>CRITICAL|HIGH|MEDIUM)\s*\|.*?\|\s*(?P<title>[^|]+)\|')
```

---

### 4.4 `core/gap_scanner/hygiene_scan.py`  *(Mechanic / INTP)*

**Input:** Git working tree (via `subprocess` + `git diff --name-only HEAD`), Python AST parser.  
**Logic:**
- Detect files with syntax errors (compile-check via `py_compile.compile`).
- Flag files modified but not committed for > 72 h.
- Detect obvious duplication: function-name collision across non-`__init__` modules.

**Hard limit:** Scan at most 200 files per cycle to stay < 100 ms. Files sorted by `mtime` descending.

---

### 4.5 `core/gap_scanner/backlog_drafter.py`  *(Mechanic / INTP)*

**Input:** `list[GapItem]`  
**Output:** Atomic append to `docs/space/jules_backlog.md`

**Algorithm:**
1. Read existing backlog into memory; extract all `gap_id` fingerprints.
2. For each new `GapItem` not already present:
   - If `priority == P1` → insert under `## READY` section header.
   - Otherwise → insert under `## BACKLOG` section header.
3. Write file atomically via `tmp → rename`.
4. Log drafted count to telemetry.

**Task template:**
```markdown
### <suggested_label> <raw_text>
<!-- gap_id: <gap_id> -->
<!-- auto-drafted: <ISO timestamp> -->
- **Source:** <source>
- **Priority:** <priority>
- **Status:** READY | BACKLOG
- **Acceptance criteria:** Resolve the detected gap; close this task by updating status to DONE.
```

---

### 4.6 Optional LLM Summarisation  *(Strategist / INTJ)*

- When `raw_text` length > 200 chars, queue a Strategist job: `summarise_task_title(raw_text) → short_title`.
- Uses existing Qwen2.5-Coder-3B Q4 (≤ 2 GB VRAM) worker.
- Backlog entry is written with raw text immediately; title is updated in-place when the Strategist job completes.
- If Strategist pool is saturated (both workers busy), skip summarisation; raw text is used as-is.

---

## 5. Kernel Integration

Add to `core/kernel.py` inside the scheduler setup block:

```python
# RAID-2 addition
from core.gap_scanner.scanner import GapScanner

_gap_scanner = GapScanner(
    telemetry_path=config.TELEMETRY_JSONL,
    error_register_path=config.ERROR_REGISTER_MD,
    backlog_path=config.JULES_BACKLOG_MD,
    repo_root=config.REPO_ROOT,
)

# Register with the existing Mechanic scheduler (5-minute cadence)
scheduler.add_job(
    _gap_scanner.run_cycle,
    trigger='interval',
    minutes=5,
    id='gap_scanner',
    replace_existing=True,
    max_instances=1,          # prevent concurrent runs
    misfire_grace_time=60,    # skip if missed by > 60 s
)
```

`max_instances=1` is the primary concurrency guard — APScheduler will skip a new fire if a prior run is still executing.

---

## 6. systemd User Service Unit

> The GapScanner runs inside the NINA kernel process — no separate service needed.
> If you want an isolated scanner process in the future, use the template below.

```ini
# ~/.config/systemd/user/nina-gap-scanner.service
[Unit]
Description=NINA GapScanner Daemon
After=nina-kernel.service

[Service]
Type=simple
WorkingDirectory=%h/nina
ExecStart=%h/nina/venv/bin/python -m core.gap_scanner.scanner --standalone
Restart=on-failure
RestartSec=30
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
```

Enable: `systemctl --user enable --now nina-gap-scanner.service`

---

## 7. Schema Modifications

No new DB tables required for Phase 1. Gap fingerprints are stored inline in the markdown file via HTML comments (`<!-- gap_id: ... -->`). If deduplication needs to scale beyond 10 000 entries, migrate fingerprints to a new SQLite table `gap_fingerprints(gap_id TEXT PRIMARY KEY, drafted_at TEXT)`.

---

## 8. Contingency Matrix

| Failure Mode | Detection | Recovery |
|---|---|---|
| Scanner loop crashes | `on-failure` restart + telemetry log | Restart after 30 s; alert after 3 consecutive failures |
| OOM during scan | `MemoryError` caught in `run_cycle`; logged | Skip cycle; reduce scan window (200→50 files) on next run |
| Backlog file locked (concurrent write) | `FileLock` timeout 5 s | Retry once after 10 s; emit P2 gap for file contention |
| Git subprocess hangs | `subprocess.timeout=10` | Kill subprocess; skip hygiene scan for this cycle |
| Error register not found | `FileNotFoundError` caught | Log warning; skip `error_register_scan` subtask |
| Strategist pool full | `queue.Full` caught in enqueue | Write raw text to backlog immediately; skip LLM summarisation |
| Duplicate gap written | `gap_id` fingerprint check | Idempotent — existing entry is not overwritten |
| Malformed backlog markdown | `re.error` or parse failure | Log error, abort write, preserve existing file unchanged |

---

## 9. Architectural Verdict: Daemon vs. Cron

**Recommendation: Cron-style scheduler inside the kernel (APScheduler `interval` trigger).**

Rationale:
- A separate daemon process would consume an extra ~30 MB RSS and require IPC to share telemetry state already held in the kernel process.
- Running inside the kernel's Mechanic bus costs < 5 MB additional heap and zero VRAM.
- The APScheduler `max_instances=1` guard provides the same single-execution guarantee as a cron job.
- If the kernel is not running, gap scanning is not needed anyway.

The standalone service unit (Section 6) is provided as a fallback only.

---

## 10. Phased Delivery Plan

| Phase | Deliverable | Executor |
|---|---|
---|
| P0 | `core/gap_scanner/__init__.py` scaffold | Jules |
| P1 | `telemetry_scan.py` + unit tests | Jules |
| P2 | `error_register_scan.py` + unit tests | Jules |
| P3 | `hygiene_scan.py` + unit tests | Gemini |
| P4 | `backlog_drafter.py` + idempotency tests | Jules |
| P5 | `scanner.py` orchestrator + kernel wiring | Jules |
| P6 | Optional LLM summarisation hook | Gemini |
| P7 | systemd unit + integration smoke test | Human (M. Baizid) |

---

*End of Blueprint — RAID-2 / 25.06.2026*
