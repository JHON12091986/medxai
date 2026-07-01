# NINA HYDRA — Multi-Agent, Multi-Pipeline Ouroboros Blueprint

> *"The Sovereign loop was one head. HYDRA grows many — each independent, each fed by the same body."*
>
> **Status: RESEARCH / PLANNING — 2026-06-25**  
> **Author: M. Baizid Alam / NINA Architect Overwatch**  
> **Supersedes planning section of: `OUROBOROS_BLUEPRINT.md`**

---

## Naming Convention

| Name | Meaning |
|---|---|
| **SOVEREIGN** | The original single-agent Ouroboros loop (`opencode` + ninagate + Ollama). Running live. See `OUROBOROS.md`. |
| **HYDRA** | The planned multi-agent, multi-pipeline extension. This document. |
| **Head** | A single CLI agent slot (OpenCode, Codex, Cursor, Jules, Perplexity, AGY…) |
| **Body** | ninagate — the shared routing, quota, and orchestration layer all heads connect to |
| **Neck** | `AgentQuotaManager` — the per-head budget tracker inside ninagate |
| **Backlog** | `data/ouroboros_backlog.txt` — shared task queue all heads draw from |
| **Genome** | `config/agent_registry.json` — declarative definition of every head's capabilities and limits |

---

## Why HYDRA

SOVEREIGN proved the loop works. It has one structural constraint: **a single agent (opencode) is the only code-execution path.** If opencode is rate-limited, slow, or unsuitable for a task type, the loop stalls or wastes compute.

HYDRA solves this by treating each CLI agent as an interchangeable **head** on the same body:

- Each head has its own free-tier quota (typically ~50 tasks/month)
- ninagate's `AgentQuotaManager` tracks all head budgets simultaneously
- The ouroboros loop routes each task to the **cheapest capable head**
- When a head's quota is exhausted, it goes dormant — the other heads carry the load
- Monthly quota resets bring dormant heads back online automatically
- OpenCode + Ollama (SOVEREIGN head) is always the unlimited fallback — zero cost, offline-capable

**Net effect:** ~100+ free cloud-executed tasks per month stacked on top of unlimited local Ollama execution, all orchestrated by the same loop that's already running.

---

## HYDRA Architecture

```
NINA HYDRA — Full Architecture
══════════════════════════════════════════════════════════════════════

  systemd ouroboros daemon (unchanged)
       │
       ▼
  ouroboros_loop.sh  ──►  get_next_task()  ──►  task + type tag
       │
       ▼
  ┌────────────────────────────────────────────────────────────┐
  │              HYDRA HEAD ROUTER (ninagate)                  │
  │                                                            │
  │  HEAD 1 — SOVEREIGN   opencode   [∞  Ollama / cloud]       │
  │  HEAD 2 — CODEX       codex CLI  [50 free/mo cloud]        │
  │  HEAD 3 — CURSOR      cursor CLI [50 free/mo cloud]        │
  │  HEAD 4 — JULES       jules CLI  [N  free/mo  cloud]  🔜   │
  │  HEAD 5 — PERPLEXITY  pplx API   [N  free/mo  API  ]  🔜   │
  │  HEAD 6 — AGY         agy CLI    [N  free     local ]  🔜   │
  │  HEAD N — …           …          […]                   🔜   │
  │                                                            │
  │  Strategy: cheapest_capable_first (configurable)           │
  │  Fallback: always SOVEREIGN (unlimited Ollama)             │
  └────────────────────────────────────────────────────────────┘
       │
       ▼
  chosen_head runs task (subprocess --non-interactive)
       │
       ▼
  git pre-commit hook → checks/ → [ouroboros] commit lands
       │
       ▼
  AgentQuotaManager.consume(head)  ──►  budget persisted to disk
       │
       ▼
  next cycle
══════════════════════════════════════════════════════════════════════
```

---

## Head Registry — `config/agent_registry.json`

Declarative definition of every head. ninagate reads this at startup. Adding a new head = adding one JSON block + no code changes.

```json
{
  "heads": {
    "sovereign": {
      "display_name": "SOVEREIGN (OpenCode + Ollama)",
      "cli_command": "opencode --non-interactive --message",
      "type": "unlimited",
      "backend": "ollama",
      "quota_limit": null,
      "quota_reset": null,
      "task_types": ["architectural", "refactor", "docs", "test", "config", "small_fix"],
      "priority": 99,
      "status": "live",
      "offline_capable": true,
      "deny_list": "opencode.json"
    },
    "codex": {
      "display_name": "CODEX CLI",
      "cli_command": "codex --quiet",
      "type": "free_tier",
      "backend": "openai",
      "quota_limit": 50,
      "quota_reset": "monthly",
      "task_types": ["test", "small_fix", "docstring", "refactor"],
      "priority": 2,
      "status": "planned",
      "offline_capable": false,
      "deny_list": null
    },
    "cursor": {
      "display_name": "CURSOR CLI (headless)",
      "cli_command": "cursor --headless --task",
      "type": "free_tier",
      "backend": "anthropic",
      "quota_limit": 50,
      "quota_reset": "monthly",
      "task_types": ["config", "small_fix", "rename", "formatting"],
      "priority": 3,
      "status": "planned",
      "offline_capable": false,
      "deny_list": null
    },
    "jules": {
      "display_name": "JULES (Google)",
      "cli_command": "jules --task",
      "type": "free_tier",
      "backend": "google",
      "quota_limit": null,
      "quota_reset": "unknown",
      "task_types": ["test", "refactor", "docs"],
      "priority": 4,
      "status": "research",
      "offline_capable": false,
      "deny_list": null,
      "notes": "Jules operates async via GitHub issues — integration model differs. See HYDRA_JULES_INTEGRATION note below."
    },
    "perplexity": {
      "display_name": "PERPLEXITY API",
      "cli_command": "pplx --query",
      "type": "free_tier",
      "backend": "perplexity",
      "quota_limit": null,
      "quota_reset": "unknown",
      "task_types": ["research", "docs", "web_context"],
      "priority": 5,
      "status": "research",
      "offline_capable": false,
      "deny_list": null,
      "notes": "Not a code-execution head. Used for research tasks that feed context into code-execution heads."
    },
    "agy": {
      "display_name": "AGY (local agent)",
      "cli_command": "agy run",
      "type": "unlimited",
      "backend": "local",
      "quota_limit": null,
      "quota_reset": null,
      "task_types": ["shell", "file_ops", "orchestration"],
      "priority": 6,
      "status": "research",
      "offline_capable": true,
      "deny_list": null
    }
  },
  "default_strategy": "cheapest_capable_first",
  "fallback_head": "sovereign",
  "strategies": [
    "cheapest_capable_first",
    "round_robin",
    "quota_spread",
    "task_type_match"
  ]
}
```

---

## Routing Strategies

### `cheapest_capable_first` (default)

For each task, filter heads by `task_types` match, then sort by cost:
`unlimited offline` → `unlimited online` → `free_tier with quota remaining` → skip (exhausted).
Sovereign always wins ties — it's the spine.

### `quota_spread`

Distributes tasks evenly across all capable heads to preserve each head's budget longer.
Good for burst periods where many tasks arrive at once.

### `round_robin`

Ignores task type — cycles through available heads in order. Useful for testing that all heads are functional.

### `task_type_match`

Strict: a head only runs tasks explicitly in its `task_types` list. Sovereign handles overflow.
Good for maximizing each head's specialization.

---

## Contingency Matrix — HYDRA-Specific Failures

The SOVEREIGN contingency matrix (see `OUROBOROS.md`) covers daemon-level failures.
This matrix covers HYDRA-specific multi-head failure modes.

| Scenario | Detection | Response |
|---|---|---|
| **Head quota exhausted mid-cycle** | `AgentQuotaManager.can_use()` returns False | Immediately reroute task to next capable head. Log `[hydra] quota exhausted: <head>`. Sovereign is always the final fallback. |
| **Head CLI not installed** | `preflight_check_head()` runs `which <cmd>` on startup | Mark head `status=unavailable` in runtime registry. Loop skips it silently. Alert logged. |
| **Head CLI crashes / non-zero exit** | `run_task()` exit code check (existing) | Retry up to 3× on same head. On 3rd failure, blacklist head for this cycle, reroute to next. SOVEREIGN retried unlimited. |
| **Head produces no git diff** | `git diff --cached --stat` after head exits | Task marked `no_op`. Head not penalized on quota. Task re-queued with different head on next cycle. |
| **Head writes to deny-list file** | `git pre-commit hook` (existing) | Commit blocked. Head retries same task. If 3 blocked commits from one head → head suspended for current cycle. |
| **All free-tier heads exhausted simultaneously** | `AgentQuotaManager.all_exhausted()` | Loop falls back to SOVEREIGN-only mode. Flag written to `data/hydra_cloud_exhausted.flag`. Human notified via Telegram. |
| **Monthly reset not detected** | Cron `scripts/hydra_quota_reset.sh` runs on 1st of month | Reads `agent_registry.json` reset dates, zeroes counters in `data/hydra_quotas.json`, removes `hydra_cloud_exhausted.flag`. |
| **Two heads attempt same file simultaneously** | File-level lock in `ouroboros_loop.sh` | Only one head runs at a time (sequential loop). HYDRA is serial by default. Parallel mode (future) requires file-lock manager. |
| **Head returns hallucinated code** | `checks/` gate (SSOT + vulture + pytest) | Pre-commit blocks bad commit. Same retry + blacklist logic as crash failure. |
| **Head modifies ninagate itself** | `deny_list` in `agent_registry.json` per head | Heads without a deny_list configured default to no write restrictions on ninagate — **MUST be configured per head before activation.** |
| **Jules async lag (tasks not completed in cycle)** | Jules integration returns task_id, not result | Loop marks task as `pending_jules:<task_id>`. Separate `jules_poller.sh` checks GitHub issue status every 5 min. On completion, loop resumes. |
| **Perplexity used for code execution** | Task type check in router | Perplexity head is `research` only — router blocks code-execution tasks from routing to it. Hard-typed in `AgentQuotaManager`. |
| **New head added without deny-list** | `preflight_check_head()` startup validation | Warns loudly in log: `[hydra] WARNING: head <name> has no deny_list configured. Running in unrestricted mode.` Loop still runs but human must audit. |
| **Strategy misconfigured** | `agent_registry.json` schema validation on startup | If strategy not in `strategies[]`, default to `cheapest_capable_first`. Log warning. |

---

## Multi-Pipeline Architecture — The Six Pipelines

Beyond code-execution heads, HYDRA envisions **distinct pipelines** for different task categories. Each pipeline is an orchestration pattern — not just a CLI agent, but a full observe→act→verify flow.

```
NINA HYDRA — Six Pipelines
══════════════════════════════════════════════════════════════════════

  PIPELINE 1 — SOVEREIGN   (Code Execution)     ← LIVE
  ┌─────────────────────────────────────────────────────┐
  │  opencode → ninagate → Ollama/cloud → git commit    │
  │  Task types: architectural, refactor, test, docs    │
  │  Loop: ouroboros_loop.sh (existing daemon)          │
  └─────────────────────────────────────────────────────┘

  PIPELINE 2 — JULES        (Async GitHub Tasks)        🔜
  ┌─────────────────────────────────────────────────────┐
  │  nina injects task → Jules picks up GitHub issue    │
  │  Jules writes PR → nina merges on verify           │
  │  Task types: large refactors, cross-file changes    │
  │  Loop: event-driven (GitHub webhook or poller)     │
  └─────────────────────────────────────────────────────┘

  PIPELINE 3 — PERPLEXITY   (Research + Context)        🔜
  ┌─────────────────────────────────────────────────────┐
  │  nina injects research query → pplx returns context │
  │  Context written to data/research_cache/            │
  │  Context injected into SOVEREIGN/CODEX next task    │
  │  Task types: "research before code" pattern        │
  └─────────────────────────────────────────────────────┘

  PIPELINE 4 — AGY           (Local Orchestration)      🔜
  ┌─────────────────────────────────────────────────────┐
  │  agy handles shell, file ops, system tasks          │
  │  Bridges NINA to OS-level automation               │
  │  Task types: cron setup, file cleanup, monitoring   │
  └─────────────────────────────────────────────────────┘

  PIPELINE 5 — CODEX/CURSOR  (Free Cloud Execution)     🔜
  ┌─────────────────────────────────────────────────────┐
  │  codex / cursor run tasks during SOVEREIGN's rest   │
  │  Quota: ~50 tasks/mo each, resets monthly          │
  │  Task types: tests, small fixes, docstrings        │
  └─────────────────────────────────────────────────────┘

  PIPELINE 6 — HYBRID        (Research → Code)          🔜
  ┌─────────────────────────────────────────────────────┐
  │  Perplexity fetches context → SOVEREIGN/CODEX codes │
  │  Two-step task: research_task + code_task chained   │
  │  Task types: tasks requiring web knowledge         │
  └─────────────────────────────────────────────────────┘
══════════════════════════════════════════════════════════════════════
```

---

## Jules Integration — Special Case

Jules is not a CLI agent in the traditional sense — it operates **asynchronously via GitHub issues and PRs**. The integration model is fundamentally different from OpenCode/Codex/Cursor:

```
NINA → creates GitHub issue with task description
         │
         ▼
      Jules picks up issue autonomously
         │
         ▼
      Jules opens PR with code changes
         │
         ▼
      nina_jules_poller.sh detects new PR
         │
         ▼
      checks/ gate runs on PR diff
         │
      PASS ──► nina auto-merges PR → [ouroboros] commit
      FAIL ──► nina comments on PR with failure reason
                  │
                  ▼
               Jules retries (if configured)
```

**Key files needed (planned):**
- `scripts/nina_jules_task.sh` — creates GitHub issue in correct format for Jules
- `scripts/nina_jules_poller.sh` — polls for Jules PRs every 5 min via GitHub API
- `config/jules_task_templates/` — task prompt templates Jules responds to well

**Contingency:** Jules has an SLA of ~minutes to ~hours. Tasks routed to Jules must be flagged `async=true` in the backlog. The ouroboros loop does not wait — it moves to the next synchronous task immediately.

---

## Perplexity Integration — Research Pipeline

Perplexity is a **context enrichment head**, not a code executor. It feeds the `HYBRID` pipeline:

```python
# Pseudocode — Pipeline 6 HYBRID flow
def hybrid_task(task: dict) -> None:
    # Step 1: Perplexity researches the problem
    research_context = perplexity_head.query(
        f"Best practices for: {task['description']}"
    )
    # Step 2: Write context to cache
    write_to("data/research_cache/", research_context)
    # Step 3: Inject context into SOVEREIGN task
    enriched_task = task.copy()
    enriched_task["context"] = research_context
    sovereign_head.run(enriched_task)
```

This is particularly powerful for NINA's Wave 2 observability tasks (tasks 11-14) — Perplexity can fetch the latest best practices for circuit breakers, structured logging, and caching patterns before SOVEREIGN writes the code.

---

## AGY Integration — Local Orchestration

AGY serves a different role: **OS-level tasks** that neither OpenCode, Codex, nor Cursor should touch. Shell operations, file system management, cron setup, process monitoring:

```
Task: "clean up logs older than 7 days"
  → router: task_type=shell → AGY head
  → agy run "find ~/nina/logs -mtime +7 -delete"
  → no git commit (shell ops don't produce code changes)
  → ouroboros loop continues
```

AGY tasks bypass the git commit flow — they produce **state changes, not code changes**. The loop handles this via a `commit_required: false` flag in the task schema.

---

## Task Schema — Extended for HYDRA

The existing backlog is a plain text file. HYDRA needs structured tasks to enable routing:

```jsonc
// data/ouroboros_backlog.jsonl — one JSON object per line
{
  "id": "task_20260625_001",
  "description": "Add pytest for QuotaManager thread-safety",
  "type": "test",
  "pipeline": "auto",        // auto = let router decide | sovereign | codex | jules | ...
  "async": false,
  "commit_required": true,
  "priority": 1,             // 1=highest, 10=lowest
  "context_required": false, // true = run Perplexity first (HYBRID pipeline)
  "injected_by": "human",   // human | ouroboros | jules | perplexity
  "created_at": "2026-06-25T17:50:00Z"
}
```

The plain text backlog (`data/ouroboros_backlog.txt`) remains supported for human-injected quick tasks. HYDRA's router detects format automatically.

---

## Quota Multiplication — Monthly Budget

| Head | Tasks/Month | Cost | Status |
|---|---|---|---|
| SOVEREIGN (Ollama) | Unlimited | $0 | Live |
| SOVEREIGN (cloud fallback) | Quota-managed | Existing budget | Live |
| Codex CLI | ~50 | $0 | Planned |
| Cursor CLI | ~50 | $0 | Planned |
| Jules | TBD | $0 | Research |
| Perplexity | TBD (research only) | Free tier | Research |
| AGY | Unlimited (local) | $0 | Research |
| **TOTAL free cloud tasks** | **~100+/mo** | **$0** | — |

Monthly quota resets replenish all free-tier heads. SOVEREIGN's Ollama backend ensures the loop **never stops** regardless of cloud quota state.

---

## Implementation Phases

### Phase 0 — Rename (Now)
- [x] SOVEREIGN name established for the existing loop
- [x] HYDRA blueprint documented (this file)
- [ ] Add `SOVEREIGN` label to `OUROBOROS.md` header

### Phase 1 — HYDRA Core (Next)
- [ ] `config/agent_registry.json` — head definitions
- [ ] `AgentQuotaManager` in ninagate — extends existing `QuotaManager`
- [ ] `/v1/quota/agents` endpoint in ninagate
- [ ] `select_head()` function in `ouroboros_loop.sh`
- [ ] `scripts/hydra_quota_reset.sh` — monthly cron
- [ ] `data/hydra_quotas.json` — persisted quota state

### Phase 2 — Codex + Cursor Heads
- [ ] Install and test Codex CLI headless mode
- [ ] Install and test Cursor CLI headless mode
- [ ] Configure deny-lists for both heads
- [ ] `preflight_check_head()` validates both CLIs on daemon start
- [ ] Run 5 test tasks through each head manually before enabling in loop

### Phase 3 — Jules Pipeline
- [ ] `scripts/nina_jules_task.sh`
- [ ] `scripts/nina_jules_poller.sh`
- [ ] `config/jules_task_templates/`
- [ ] async task handling in `ouroboros_loop.sh`

### Phase 4 — Perplexity + HYBRID Pipeline
- [ ] Perplexity API integration in ninagate
- [ ] `data/research_cache/` directory and TTL management
- [ ] HYBRID pipeline task chaining logic

### Phase 5 — AGY Pipeline
- [ ] AGY local agent integration
- [ ] Shell task type handling (no git commit flow)
- [ ] AGY deny-list / safety scope definition

---

## Immune System — Extended for HYDRA

The SOVEREIGN immune system (4 layers) is inherited by all heads. HYDRA adds two new layers:

### Layer 6 — Per-Head Deny Lists

Every head that performs code execution **must** have a deny-list configured before activation. The deny-list format is head-specific (opencode uses `opencode.json`, cursor uses `.cursorignore`-style, etc.) but the semantic content mirrors the SOVEREIGN deny-list: no core, no immune system, no ouroboros scripts, no secrets.

### Layer 7 — Cross-Head Convergence Monitor

Extends the existing `check_convergence()` to detect when **multiple heads are reverting each other's work** — a multi-head divergence pattern unique to HYDRA:

```bash
# If head A commits X, then head B reverts X in the next cycle,
# and this pattern repeats 3 times → cross-head conflict detected
# → suspend HYDRA, fall back to SOVEREIGN-only, alert human
check_cross_head_divergence() {
    local revert_pattern=$(git log --oneline -20 | \
        grep -c 'revert.*ouroboros\|ouroboros.*revert')
    if [[ $revert_pattern -ge 3 ]]; then
        echo 'HYDRA_CONFLICT' > "$DATA_DIR/ouroboros_suspended.flag"
        notify_telegram "[HYDRA] Cross-head conflict detected. SOVEREIGN-only mode activated."
    fi
}
```

---

## What HYDRA Does NOT Change

- `OUROBOROS.md` (root) — SOVEREIGN spec, human-maintained, deny-listed
- `scripts/ouroboros_loop.sh` — core daemon, deny-listed
- `scripts/ouroboros_watchdog.sh` — watchdog, deny-listed
- `checks/` — immune system gates, deny-listed
- `git-hooks/pre-commit` — deny-listed
- `core/` — spine, deny-listed
- `tools/ninagate/main.py` — the body, deny-listed

HYDRA extends the loop — it does not replace the snake. SOVEREIGN remains live and running during all HYDRA phases.

---

## Open Questions (Research Needed)

| Question | Impact | Priority |
|---|---|---|
| Does Codex CLI support `--non-interactive` / `--quiet` headless mode? | Phase 2 blocker | HIGH |
| Does Cursor CLI have a true headless task mode? | Phase 2 blocker | HIGH |
| What is Jules' actual free-tier task limit? | Phase 3 scoping | MEDIUM |
| Can Jules be triggered via API/CLI or only via GitHub UI? | Phase 3 architecture | HIGH |
| Does Perplexity API have a free tier suitable for research queries? | Phase 4 scoping | MEDIUM |
| What is AGY's task interface / invocation syntax? | Phase 5 architecture | HIGH |
| Should HYDRA run heads in parallel (file-lock needed) or stay serial? | Performance vs complexity | LOW |

---

*Blueprint version: 1.0 — 2026-06-25*  
*Location: `docs/research/HYDRA_BLUEPRINT.md` — ALLOW (research docs)*  
*Next: implement Phase 1 — `config/agent_registry.json` + `AgentQuotaManager`*
