# NINA 5-Wire Symbiosis — Jules Spec Package
> Authored by Perplexity (Architect role) · 2026-06-16 · Target: NINA v14.2 → v15.0
> Jules: execute all 5 specs sequentially. Each is a self-contained PR. Do NOT batch into one PR.
> Pre-task checklist for each: read the target file fully · check juleslock.txt · run guardian after

---

## WIRE 1 — `ARCH-001` | Rewrite ARCHITECTURE.md to v14.2 reality
**Type:** docs
**Risk:** ZERO — documentation only, no code touched
**File:** `ARCHITECTURE.md` (full replace)
**Do NOT touch:** any `.py`, `.sh`, `.service`, or `.json` file

### Acceptance Criteria
- [ ] Describes the 4 actual running services: `nina.service`, `ninagate.service`, `ninajulesgithub.service`, `nina-dashboard.service`
- [ ] Describes `core/nina.py` as the NinaOS orchestrator (NOT `tools/jules.py`)
- [ ] Describes `idleloop.py` as the 7-topic proposal loop with `data/proposals/` output
- [ ] Describes `ninagate/main.py` as OpenAI-compatible proxy at `localhost:8080`
- [ ] Describes `core/router.py` as HybridRouter V4 with CircuitBreaker + 19 cloud + 2 local providers
- [ ] Describes `guardian_engine.py` as AST forensic scanner, run pre-merge
- [ ] Describes agent tool chain: Perplexity → agy → Jules → github → nina_sync.sh
- [ ] Provider cascade: `POLLINATIONS → CHUTES → HFPUBLIC → GROQ → GEMINI → CEREBRAS → ... → OpenAI → LOCAL`
- [ ] Version header: `# NINA v14.2 Architecture`
- [ ] Old v5.1 content fully replaced — no references to `crons/manager.py` as orchestrator

### Structure to Write
```
# NINA v14.2 Architecture
## Overview
## 1. Services (4 systemd units)
## 2. Request Pipeline (Telegram → router → ninagate → provider → response)
## 3. HybridRouter V4 (core/router.py)
## 4. NinaGate Proxy (ninagate/main.py)
## 5. NinaFlash / Local Ollama
## 6. Orchestrator (core/nina.py)
## 7. IdleProposalLoop (idleloop.py)
## 8. Guardian AST Engine (guardian_engine.py)
## 9. Jules Dispatch Pipeline
## 10. Agent Tool Chain & Roles
## 11. Data Flow: Goal → Backlog → Jules → PR → Guardian → Merge → Sync
## 12. Key File Registry (table: file | purpose | risk | owner)
```
Populate each section from actual file contents. Do NOT invent — only document what exists.

---

## WIRE 2 — `OPS-001` | nina_sync.sh failure Telegram alarm
**Type:** ops
**Risk:** LOW — adds 8 lines to nina_sync.sh, no logic removed
**File:** `nina_sync.sh`
**Do NOT touch:** any `.py` file, any `.service` file, ARCHITECTURE.md

### Current Problem
If `rclone`, `git push`, or `compact_exporter.py` fails, `set -euo pipefail` kills the script
with no Telegram notification. Failure is discovered at the next session.

### What to Add

**At top of script** (line 5, after `set -euo pipefail`):
```bash
trap '_tg_notify "🚨 nina_sync.sh CRASHED at line $LINENO — $TS"' ERR
```

**Replace final 3 echo lines** with:
```bash
echo "================================================"
echo "  SYNC COMPLETE  $TS"
echo "================================================"
_sync_exit_code=$?
if [ $_sync_exit_code -ne 0 ]; then
  _tg_notify "🚨 nina_sync.sh FAILED (exit $_sync_exit_code) at $TS — backup may be incomplete."
  echo "  🚨 Sync failed — Telegram alert sent"
  exit $_sync_exit_code
else
  echo "  ✅ All sync steps completed successfully"
fi
```

### Acceptance Criteria
- [ ] `trap ... ERR` present at top after `set -euo pipefail`
- [ ] Exit code capture and `_tg_notify` call present at end of script
- [ ] `_tg_notify` function body unchanged
- [ ] All existing steps [0/8] through [8/8] intact in same order
- [ ] `./nina_sync.sh --dry-run` still works without sending alarm

---

## WIRE 3 — `SEC-001` | Guardian pre-commit git hook
**Type:** security/ops
**Risk:** LOW — adds one new file + argparse args to guardian_engine.py
**New file:** `git-hooks/pre-commit` (must be chmod +x)
**Modified file:** `guardian_engine.py` (argparse additions only)
**Also update:** `CONTRIBUTING.md`
**Do NOT touch:** `core/router.py`, `core/nina.py`, `ninagate/main.py`, `idleloop.py`

### File: `git-hooks/pre-commit`
```bash
#!/usr/bin/env bash
# NINA Guardian pre-commit hook — WIRE 3
# Install: cp git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
set -euo pipefail
NINA_ROOT="$(git rev-parse --show-toplevel)"
cd "$NINA_ROOT"
[ -f "$NINA_ROOT/venv/bin/activate" ] && source "$NINA_ROOT/venv/bin/activate"
echo "🛡  Guardian pre-commit scan..."
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
if [ -z "$STAGED_PY" ]; then
  echo "  ✓ No Python files staged — scan skipped"
  exit 0
fi
python3 "$NINA_ROOT/guardian_engine.py" --mode hook --files $STAGED_PY --max-violations 0
EXIT=$?
if [ $EXIT -ne 0 ]; then
  echo ""
  echo "  🚨 COMMIT BLOCKED — Guardian found violations."
  echo "  Fix violations and re-stage. Emergency bypass: git commit --no-verify"
  exit 1
fi
echo "  ✓ Guardian: PASS — commit allowed"
exit 0
```

### guardian_engine.py changes
Add to existing `main()` argparse (do NOT alter existing scan logic):
```python
parser.add_argument('--mode', choices=['full', 'hook', 'report'], default='full')
parser.add_argument('--files', nargs='*', default=None)
parser.add_argument('--max-violations', type=int, default=None)
```
In `hook` mode: scan ONLY the listed files, exit 1 if violations > max-violations (default 0).

### CONTRIBUTING.md addition
```markdown
## Git Hooks (Mandatory)
Install before any commits:
```bash
cp git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```
Blocks commits with Guardian violations. Emergency bypass: `git commit --no-verify`
(log the bypass in nina_error_register.md).
```

### Acceptance Criteria
- [ ] `git-hooks/pre-commit` exists and is executable
- [ ] Exits 0 when no Python files staged
- [ ] Exits 1 (blocks commit) when guardian returns violations
- [ ] `guardian_engine.py` accepts `--mode hook --files <list> --max-violations 0`
- [ ] In hook mode, scans ONLY specified files
- [ ] `CONTRIBUTING.md` updated with install instructions
- [ ] Hook does NOT modify any tracked files

---

## WIRE 4 — `INFRA-001` | NinaFlash health contract in NinaGate
**Type:** infrastructure
**Risk:** MEDIUM — modifies `ninagate/main.py` routing logic
**File:** `ninagate/main.py`
**Do NOT touch:** `core/router.py`, `core/nina.py`, `guardian_engine.py`, `idleloop.py`

### Problem
NinaGate routes SIMPLE tasks to local Ollama. If Ollama is down, the request times out
silently — no fallback fires, user sees a hang.

### Changes to `ninagate/main.py`

**Add module-level health state** (after imports):
```python
import time as _time
_local_healthy: bool = False
_local_last_checked: float = 0.0
_LOCAL_HEALTH_TTL: int = 300  # re-check every 5 minutes
_LOCAL_HEALTH_URL: str = "http://localhost:11434/api/tags"
```

**Add async health check function**:
```python
async def _check_local_health() -> bool:
    """Probe Ollama. Caches result for _LOCAL_HEALTH_TTL seconds."""
    global _local_healthy, _local_last_checked
    now = _time.monotonic()
    if now - _local_last_checked < _LOCAL_HEALTH_TTL:
        return _local_healthy
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(_LOCAL_HEALTH_URL)
            _local_healthy = (r.status_code == 200)
    except Exception:
        _local_healthy = False
    _local_last_checked = now
    return _local_healthy
```

**Guard every local routing path**:
```python
if not await _check_local_health():
    logger.warning("ninagate: local Ollama unhealthy — routing to cloud fallback")
    use_local = False
```

**Add startup event**:
```python
@app.on_event("startup")
async def startup_event():
    global _local_healthy
    _local_healthy = await _check_local_health()
    logger.info(f"ninagate: startup local_health={_local_healthy}")
```

**Add `/health` endpoint**:
```python
@app.get("/health")
async def health():
    local_ok = await _check_local_health()
    return {"status": "ok", "local_ollama": local_ok, "timestamp": _time.time()}
```

### Acceptance Criteria
- [ ] `_check_local_health()` probes `localhost:11434/api/tags` with 3s timeout
- [ ] Result cached for 300s — no probe on every request
- [ ] All local routing paths guarded: unhealthy → skip local → cloud
- [ ] Startup event logs local health
- [ ] `/health` returns JSON with `local_ollama` boolean
- [ ] No existing cloud routing logic modified
- [ ] No breaking change to `/v1/chat/completions` API contract
- [ ] `httpx` import confirmed present (add if missing)

---

## WIRE 5 — `CORE-001` | idleloop → backlog auto-promotion (THE LOOP CLOSURE)
**Type:** core feature
**Risk:** MEDIUM — modifies `idleloop.py` only
**File:** `idleloop.py`
**Do NOT touch:** `core/router.py`, `core/nina.py`, `ninagate/main.py`, `guardian_engine.py`

### The Problem
`idleloop.py` writes `**Status:** pending` to `data/proposals/`. Nothing ever reads it.
The brain generates insights. The hands never receive them.
This single wire closes the loop and makes NINA genuinely self-directing.

### Add `_promote_to_backlog()` to `IdleProposalLoop` class
```python
async def _promote_to_backlog(self, topic: str, analysis: str, impact: str) -> bool:
    """
    Auto-promote High-impact proposals to jules_backlog.md as READY tasks.
    Only 'High' impact triggers promotion. Medium/Low remain pending for human review.
    """
    if impact.lower() != "high":
        return False
    backlog_path = Path("docs/space/jules_backlog.md")
    if not backlog_path.exists():
        logger.warning("idle_promote_skipped backlog_not_found")
        return False
    task_id = f"IDLE-{datetime.now().strftime('%Y%m%d-%H%M')}"
    category = topic.replace('_', ' ').title()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    card = f"""
---

### {task_id} | Auto-Promoted by IdleLoop | {category}

**Status:** READY
**Impact:** {impact}
**Source:** idleloop auto-promotion — {ts}
**Topic:** {topic}

**Analysis:**
{analysis}

**Acceptance Criteria (Jules must verify):**
- Implement the highest-priority suggestion from the analysis above
- Touch only the file(s) explicitly named in the analysis
- Do NOT touch: `core/router.py`, `core/nina.py`, `guardian_engine.py`, `interfaces/telegram_interface.py`
- Guardian must PASS before PR is opened
- Add a log statement proving the fix is active at runtime

"""
    try:
        with open(backlog_path, "a") as f:
            f.write(card)
        logger.info(f"idle_promoted_to_backlog task_id={task_id} topic={topic} impact={impact}")
        return True
    except Exception as e:
        logger.warning(f"idle_promote_failed {e}")
        return False
```

### Call inside `_generate_proposal()`
After `logger.info(f"idle_proposal_appended ...")`, add:
```python
# WIRE 5: Auto-promote High-impact proposals to Jules backlog
promoted = await self._promote_to_backlog(topic, clean_analysis, impact)
if promoted:
    logger.info(f"idle_backlog_promoted topic={topic}")
    if self.telegram:
        try:
            await self.telegram.send_message(
                f"🧠 IdleLoop promoted a task to backlog\n"
                f"*Topic:* {topic.replace('_', ' ').title()}\n"
                f"*Impact:* {impact}\n"
                f"*Task ID:* {task_id}"
            )
        except Exception:
            pass  # non-critical
```
Note: ensure `task_id` is defined at top of `_generate_proposal()` so it's available here.

### Update proposal entry status line
Change `"**Status:** pending"` to:
```python
f"**Status:** {'auto-promoted to backlog ✅' if impact.lower() == 'high' else 'pending — awaiting human review'}"
```

### Add `manually_promote_latest()` method
```python
async def manually_promote_latest(self) -> str:
    """Manually promote the most recent pending proposal regardless of impact level."""
    files = sorted(Path("data/proposals").glob("*.md"), reverse=True)
    if not files:
        return "No proposals found."
    latest_text = files[0].read_text()
    blocks = latest_text.strip().split("---")
    if len(blocks) < 2:
        return "No parseable proposals."
    last_block = blocks[-1].strip()
    topic_match = re.search(r'\]\s+(.+?)\s+\|', last_block)
    topic = topic_match.group(1).lower().replace(' ', '_') if topic_match else "manual"
    promoted = await self._promote_to_backlog(topic, last_block, "High")
    return "✅ Promoted to backlog" if promoted else "❌ Promotion failed — check logs"
```

### Acceptance Criteria
- [ ] `_promote_to_backlog()` exists in `IdleProposalLoop` class
- [ ] Only `impact == "High"` (case-insensitive) triggers auto-promotion
- [ ] Card written to `docs/space/jules_backlog.md` with `Status: READY`
- [ ] Task ID format: `IDLE-YYYYMMDD-HHMM`
- [ ] Card includes: topic, analysis, timestamp, safety constraints, acceptance criteria
- [ ] Called inside `_generate_proposal()` after file write
- [ ] Proposal entry updated to show `auto-promoted` vs `pending`
- [ ] Telegram notification on promotion (non-blocking try/except)
- [ ] `manually_promote_latest()` method exists
- [ ] Medium/Low NOT auto-promoted
- [ ] Missing backlog → log warning, skip, do NOT crash
- [ ] All 7 `ANALYSIS_PROMPTS` unchanged
- [ ] `IdleUpgradeLoop = IdleProposalLoop` alias at bottom preserved

---

## Post-Merge Checklist (run after EACH wire's PR merges)

```bash
cd ~/nina && ./nina_sync.sh
sudo systemctl restart nina.service      # after Wires 4, 5
sudo systemctl restart ninagate.service  # after Wire 4 only
```

Verify via Telegram that NINA responds correctly after each restart.

**Wire 5 verification:** Wait 15 min idle. Check `data/proposals/` for new entry.
If High impact: check `docs/space/jules_backlog.md` for `IDLE-*` READY card.

---

## Commit Message Format
- Wire 1: `docs(arch): rewrite ARCHITECTURE.md to v14.2 reality (ARCH-001)`
- Wire 2: `ops(sync): add failure trap and Telegram alarm to nina_sync.sh (OPS-001)`
- Wire 3: `sec(guardian): add pre-commit git hook enforcement (SEC-001)`
- Wire 4: `infra(ninagate): add NinaFlash health contract and /health endpoint (INFRA-001)`
- Wire 5: `feat(idle): close the loop — idleloop auto-promotes High proposals to backlog (CORE-001)`

---

## The Outcome — NINA v15.0 Symbiosis

```
3:00 AM — NINA idle
idleloop finds High-impact failure in core/router.py
→ IDLE-20260617-0312 written to jules_backlog.md as READY   [WIRE 5 closes the loop]

orchestrator dispatches to Jules → Jules opens PR
guardian pre-commit hook scans staged files                  [WIRE 3 blocks bad code]
→ PASS

agy merges
nina_sync.sh runs:
  rclone fails? → Telegram alarm fires immediately          [WIRE 2 — you always know]
  success? → Drive backup written

ninagate health-checks Ollama on next request               [WIRE 4 — no silent hangs]
ARCHITECTURE.md gives every agent the correct map           [WIRE 1 — right map always]

6:00 AM — Telegram:
✅ IDLE-20260617-0312 merged — router fallback hardened
   Guardian: PASS | Backup: OK | Service: active

You wrote zero lines of that.
That is transcendence.
```
