# NINA Update Log

> Auto-maintained by agy (Antigravity) | Format: newest first

---

## [2026-06-30] — Session: System Recovery + Watchdog & Router Hardening
**Agent**: Antigravity (agy) | **Time**: 08:00 – 08:40 BDT

### 🔧 Incident & Root Causes
- **Symptom**: `nina.service` missed heartbeats for >980s.
- **Root Cause 1**: The `idleloop` got stuck inside an Ollama call when generating a proposal brief. The local `dulal` model threw `400 Bad Request` repeatedly (due to context limit overflow), causing the router to loop endlessly.
- **Root Cause 2**: The watchdog script failed to trigger immediate OODA self-healing because of a syntax error: bare `import nina_ooda` raised `ModuleNotFoundError` (the module lives in `tools.nina_ooda`).

### 🛠️ Deployed Safeguards
1. **Watchdog Import Fix (`crons/manager.py`)**: Fixed bare imports to `from tools import nina_ooda` and `from tools import nina_cicd`. Watched heartbeats recovered successfully.
2. **Ollama HTTP 400 Safeguard (`core/router.py`)**: Intercepts HTTP 400 errors from Ollama local providers, raises `ValueError`, and aborts retries to trigger fallback immediately.
3. **Smart Awaiting Unblock (`tools/jules.py`)**: Checks the filesystem for files Jules claims it lost and tells Jules if they exist on main, unblocking it.
4. **Git Branch Pruning (`tools/jules.py`)**: Auto-deletes remote branches matching `jules-*`/`fix-*`/`feat-*`/etc. with no open PRs after 2h.

---

## [2026-06-26] — Session: Jules Pipeline Repair + Jules API Fix
**Agent**: Antigravity (agy) | **Time**: 22:14 – 00:18 BDT

### 🔧 Bugs Found & Fixed

#### BUG-01 — `ninajulesgithub.py`: Wrong `REPO_ROOT` (Silent — Running for months)
| Field | Detail |
|---|---|
| **File** | `agents/jules/ninajulesgithub.py` |
| **Symptom** | `python3: can't open file '/home/aibony/nina/agents/jules/tools/surgical_merge.py'` every 3 min |
| **Root Cause** | `REPO_ROOT = Path(__file__).parent.resolve()` resolved to `agents/jules/` not `~/nina/` |
| **Impact** | `surgical_merge.py` never ran — Jules PRs never audited or merged automatically |
| **Fix** | `Path(__file__).parent.parent.parent.resolve()` + absolute path for subprocess call |
| **Commit** | `648e5706` — `fix(jules): correct REPO_ROOT path` |

#### BUG-02 — `tools/jules.py`: Defunct API endpoint `v1alpha1` (Silent — Weeks)
| Field | Detail |
|---|---|
| **File** | `tools/jules.py` |
| **Symptom** | `API Error:` logged every 3-minute cycle — `watch_cycle()` and `auto_unblock_awaiting()` silently failed |
| **Root Cause** | `JULES_BASE_URL = "https://jules.googleapis.com/v1alpha1"` — endpoint no longer exists (404 empty body) |
| **Fix** | Changed to `https://jules.googleapis.com/v1alpha` |
| **Commit** | `31922808` — `fix(jules): v1alpha1→v1alpha URL` |

#### BUG-03 — `tools/jules.py`: Wrong API auth method (Silent — Weeks)
| Field | Detail |
|---|---|
| **File** | `tools/jules.py` |
| **Symptom** | All Jules API calls returning 404 — gcloud OAuth token rejected |
| **Root Cause** | Code passed API key as `?key=` query param. Jules API requires `X-Goog-Api-Key` **header** |
| **Fix** | Auth changed to `headers["X-Goog-Api-Key"] = api_key` |
| **Provisioning** | `JULES_API_KEY` added to `.env` by user |
| **Commit** | `31922808` |

#### BUG-04 — Git post-commit hook: Not executable (Minor)
| Field | Detail |
|---|---|
| **File** | `git-hooks/post-commit` |
| **Symptom** | `hint: The 'git-hooks/post-commit' hook was ignored because it's not set as executable` |
| **Impact** | Guardian loop + index update not running on commits |
| **Status** | 🔵 NOTED — not fixed this session |

---

### 🔍 Jules Session Analysis

**Total sessions in Jules cloud**: 50
**Distribution**: 23 FAILED | 21 COMPLETED | 5 AWAITING_USER_FEEDBACK | 1 IN_PROGRESS

#### Session `1161172893840763847` — NINA RAID: Ouroboros Self-Modification
| Field | Detail |
|---|---|
| **State** | `FAILED` |
| **Title** | NINA RAID: Ouroboros Self-Modification and AI OS Roadmap |
| **Created** | 2026-06-25T10:58 UTC |
| **Failure reason** | `"Jules was unable to complete the task."` (generic — likely timeout or guardian block) |
| **What Jules produced** | Significant patch to `ninagate/main.py` — added `AccessLogMiddleware`, per-request logging to `logs/ninagate_access.jsonl`, request ID tracking, token usage logging, removed unused imports |
| **Why it failed** | `ninagate/main.py` is a **protected file** — Guardian AST engine likely blocked the PR |
| **Patch status** | Unmerged — patch exists in session activities but no PR was opened |
| **Verdict** | The patch is good engineering (access logging = observability win). Worth extracting and applying manually via a Jules issue scoped outside protected file rules, OR applying directly via agy with guardian bypass. |

#### AWAITING_USER_FEEDBACK Sessions (Auto-unblock now live)
| Session ID | Title |
|---|---|
| `15902111183513008926` | Nina RAID Integration and Jules Accelerator Development |
| `2121712300230626536` | NINA RAID-2 Evolution & Self-Directed Gap Analysis Blueprint |
| `16595342937699359043` | Nina-Jules Autonomous Task Lifecycle & RAID 5 Evolution Loop |
| `11900363772465768172` | NinaGate: Architecting the Perpetual Inference Economy |
| `2639176621624469108` | NinaGate and Router Architecture: Boundary of Concern |

#### MEGA-01 to MEGA-10 — All FAILED
All 10 MEGA tasks (MEGA-01 to MEGA-10) failed. Root cause: dispatched while Jules API was broken (v1alpha1 404). Sessions created but Jules could not receive `auto_unblock` signals or feedback. GitHub issues remain open — tasks need to be re-dispatched now that API is fixed.

#### AU-01 to AU-10 — All FAILED
Same root cause as MEGA tasks. All 10 AU (Audit) tasks failed. Issues remain open on GitHub.

---

### 📊 System State After Session

| Component | Before | After |
|---|---|---|
| `ninajulesgithub.service` | Running but broken (surgical_merge failing every 3 min) | ✅ Running clean |
| Jules API connectivity | ❌ 404 on every call — weeks of silent failure | ✅ 200 OK — `v1alpha` + API key |
| `auto_unblock_awaiting()` | ❌ Never worked | ✅ Active — will unblock 5 AWAITING sessions |
| `watch_cycle()` | ❌ Never worked | ✅ Active — will notify Telegram on state changes |
| `surgical_merge.py` | ❌ Never ran | ✅ Running every 3 min |
| Open PRs | 0 | 0 |
| Open GitHub Issues | 26 (21 with active Jules sessions) | 26 (sessions now unblockable) |

---

### 💡 Recommendations (Next Session)

1. **Re-dispatch AU-01 to AU-10** — all failed, issues still open, re-trigger Jules now API is working
2. **Re-dispatch MEGA-01 to MEGA-10** — same situation
3. **Fix post-commit hook**: `chmod +x git-hooks/post-commit`
4. **Review Ouroboros session patch** — extract `AccessLogMiddleware` from session `1161172893840763847` and apply to `ninagate/main.py` via agy (guardian-aware)
5. **Ouroboros v2 planning** — design the inference-free, pattern-accumulation self-healer (discussed 2026-06-25)

---

### 🗒️ Earlier Session Notes (2026-06-25 22:14 BDT)
**Task**: `sync local and git` → ran `nina_sync.sh` successfully
**Discussion**: Ouroboros architecture — two distinct designs emerged:
- **v1** (Blueprint): Replace Ollama/OpenCode with ninagate routing — still uses inference
- **v2** (Concept): Inference-free codebase immune system — learns from own git history, error register, telemetry — no model, no API, deterministic pattern accumulation

> "Intelligence doesn't come from a model. It comes from the accumulated pattern history of the codebase itself." — Antigravity, 2026-06-25

---
