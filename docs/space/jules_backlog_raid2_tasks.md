# RAID-2 Backlog Tasks — Self-Directed Gap Analysis
**Auto-drafted:** 25 June 2026  
**Blueprint ref:** `docs/blueprints/nina_blueprint_25.06.2026.md`

> Copy these tasks into `jules_backlog.md` under the appropriate READY/BACKLOG headers.
> Each task is atomic and independently executable by Jules or Gemini.

---

## READY (P1 — unblock RAID-2 evolution)

### feat(gap_scanner): scaffold `core/gap_scanner/` package
<!-- gap_id: raid2-p0-scaffold -->
- **Source:** Blueprint §10 Phase P0
- **Priority:** P1
- **Status:** READY
- **Files:** `core/gap_scanner/__init__.py`, `core/gap_scanner/models.py`
- **Acceptance criteria:**
  - `GapItem` dataclass defined in `models.py` with fields: `gap_id`, `source`, `priority`, `raw_text`, `suggested_label`, `status`.
  - Package importable from `core.gap_scanner`.
  - `gap_id` generation helper: `sha256(source + raw_text)[:12]`.
  - Zero external dependencies beyond stdlib.

---

### feat(telemetry): implement `TelemetryScan` class
<!-- gap_id: raid2-p1-telemetry-scan -->
- **Source:** Blueprint §4.2
- **Priority:** P1
- **Status:** READY
- **Files:** `core/gap_scanner/telemetry_scan.py`, `tests/gap_scanner/test_telemetry_scan.py`
- **Acceptance criteria:**
  - Reads last 500 lines of `telemetry.jsonl` (path from config).
  - Detects error-class event bursts (count > configurable threshold in 60 min window) → P1 GapItem.
  - Detects p95 latency spike > 3× rolling baseline → P1 GapItem.
  - Detects silent intent handlers (0 events in 24 h) → P3 GapItem.
  - Pure I/O + regex; completes in < 50 ms on 500-line file.
  - Unit tests cover: normal data, empty file, malformed JSON lines (must skip gracefully).

---

### feat(error_register): implement `ErrorRegisterScan` class
<!-- gap_id: raid2-p2-error-register-scan -->
- **Source:** Blueprint §4.3
- **Priority:** P1
- **Status:** READY
- **Files:** `core/gap_scanner/error_register_scan.py`, `tests/gap_scanner/test_error_register_scan.py`
- **Acceptance criteria:**
  - Parses `docs/space/nina_error_register.md` markdown table.
  - Extracts all rows with `| OPEN |` status.
  - Maps severity: CRITICAL→P1, HIGH→P2, MEDIUM→P3.
  - Returns list of `GapItem` with `suggested_label = 'fix(<module>):'`.
  - Handles file-not-found gracefully (log warning, return empty list).
  - Unit tests cover: open bugs, resolved bugs (must be excluded), missing file.

---

## BACKLOG (P2/P3 — sequential after READY tasks)

### feat(hygiene): implement `HygieneScan` class
<!-- gap_id: raid2-p3-hygiene-scan -->
- **Source:** Blueprint §4.4
- **Priority:** P2
- **Status:** BACKLOG
- **Files:** `core/gap_scanner/hygiene_scan.py`, `tests/gap_scanner/test_hygiene_scan.py`
- **Acceptance criteria:**
  - Uses `git diff --name-only HEAD` (subprocess, timeout=10 s) to find modified files.
  - Runs `py_compile.compile` on modified `.py` files; flags syntax errors.
  - Flags files modified but uncommitted > 72 h.
  - Scans at most 200 files per cycle (sorted by mtime desc).
  - Returns list of `GapItem` with `suggested_label = 'fix(hygiene):'`.
  - Subprocess timeout handled: on timeout, skip hygiene scan, log warning.

---

### feat(backlog): implement `BacklogDrafter` with idempotency
<!-- gap_id: raid2-p4-backlog-drafter -->
- **Source:** Blueprint §4.5
- **Priority:** P2
- **Status:** BACKLOG
- **Files:** `core/gap_scanner/backlog_drafter.py`, `tests/gap_scanner/test_backlog_drafter.py`
- **Acceptance criteria:**
  - Reads `docs/space/jules_backlog.md`; extracts all `<!-- gap_id: ... -->` fingerprints.
  - Skips any `GapItem` whose `gap_id` already exists in the file.
  - P1 items appended under `## READY` section; others under `## BACKLOG`.
  - Writes atomically: write to `.jules_backlog.md.tmp` then `os.replace()`.
  - `FileLock` with 5 s timeout; on timeout, retry once after 10 s, then abort with log.
  - Unit tests: duplicate suppression, section routing, atomic write, file-lock contention.

---

### feat(gap_scanner): implement `GapScanner` orchestrator + kernel wiring
<!-- gap_id: raid2-p5-scanner-orchestrator -->
- **Source:** Blueprint §4.1, §5
- **Priority:** P2
- **Status:** BACKLOG
- **Files:** `core/gap_scanner/scanner.py` (update), `core/kernel.py` (update)
- **Acceptance criteria:**
  - `GapScanner.run_cycle()` calls all three scan sub-tasks sequentially; collects results.
  - Passes combined `list[GapItem]` to `BacklogDrafter`.
  - Registered in `core/kernel.py` APScheduler with `interval=5 min`, `max_instances=1`, `misfire_grace_time=60`.
  - On any scan sub-task exception: log error, skip that sub-task, continue with others.
  - Telemetry event emitted at end of each cycle: `{event: 'gap_scan_complete', gaps_drafted: N, duration_ms: X}`.

---

### feat(gap_scanner): optional LLM summarisation hook
<!-- gap_id: raid2-p6-llm-summary-hook -->
- **Source:** Blueprint §4.6
- **Priority:** P3
- **Status:** BACKLOG
- **Files:** `core/gap_scanner/llm_summariser.py`
- **Acceptance criteria:**
  - Enqueues Strategist job only when `len(raw_text) > 200`.
  - Uses existing Qwen2.5-Coder-3B Q4 worker (≤ 2 GB VRAM).
  - If Strategist pool full (`queue.Full`): log info, skip, return `raw_text[:80]` as fallback title.
  - Backlog entry is written immediately with raw text; title updated in-place on completion.
  - No new LLM workers spawned; re-uses existing Strategist thread pool.

---

### chore(systemd): add `nina-gap-scanner.service` unit (standalone fallback)
<!-- gap_id: raid2-p7-systemd-unit -->
- **Source:** Blueprint §6
- **Priority:** P3
- **Status:** BACKLOG
- **Files:** `deploy/nina-gap-scanner.service`
- **Acceptance criteria:**
  - Unit file uses `systemctl --user` convention; no `sudo`.
  - `Type=simple`, `Restart=on-failure`, `RestartSec=30`.
  - `ExecStart` uses venv Python path.
  - Install instructions added to `docs/space/nina_runbook.md`.

---

*End of RAID-2 task batch — 25.06.2026*
