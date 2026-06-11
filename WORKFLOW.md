# NINA Workflow — Three-Tier Agent Model

## Identity
NINA is a personal AI assistant built by M. Baizid Alam (GitHub: aibony), AGM at BASIC Bank,
Dhaka, Bangladesh. Deployed on ASUS VivoBook X530FN (Ubuntu 26.04) at github.com/aibony/nina.

## The Three-Tier Agent Model

| Agent | Role | Scope |
|------|------|------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Strategic direction, specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| ninaflash (Antigravity CLI) | LOCAL EXECUTOR | Sync local executor — edits, reviews Jules PR diff, merges, deploys |

## 0. Discovery & Governance (New)
**Index-First Workflow:**
1. Check `nf run query-index --path <file>` for the file's entry (path, role, lifecycle, guardrails).
2. **Obey Guardrails:** Strictly adhere to tags like `high_risk_do_not_edit_directly`, `append_only`, and `read_only_for_agents`.
3. **Doc Delta Required:** If code or architecture changes, you MUST update `nina_update_log.md`.
4. If modifying a file within a `duplicate_cluster_id`, edit the `canonical_path` only.
5. If creating, moving, renaming, archiving, or deleting a governed file:
   - Update the file structure.
   - Run `nf run update-index`.
   - Run `nf run validate-index`.
6. Fix validation issues until the validator passes.
7. Run `./nina_audit.sh` to reconcile local drifts and identify stale artifacts.
8. No PR is "Done" and no local task is complete unless `validate_index.py` passes cleanly. The index is the single enforceable contract for inventory.

## 0.6. Capability Crystallization (Self-Upgrading)
NINA is designed to be a self-developing platform. Every session must aim to leave `ninaflash` more capable than it started.
- **Identify:** If a task requires complex cloud reasoning that will likely be repeated, don't just solve it—crystallize it.
- **Register:** Turn the solution into a named command in the **Capability Registry** via `nf register`.
- **Harvest:** Regularly review the "Stray Locals" in the Hygiene Dashboard for potential new tools to be governed and registered.
To prevent governance decay without blocking roadmap progress, NINA uses a dual-track operational model. **Rule of thumb: For every feature PR merged, complete at least one Governance Quest.**

### Lane A: Governance Quests (Continuous)
Small, repeatable tasks driven entirely by `docs/space/nina_governance_dashboard.md`.
1. **Quest: Missing Tests x3**
   - Pick the top 3 files from "Missing-Test Hotspots".
   - Add minimal unit tests (happy path + one failure path) to `tests/`.
   - Run validators and `tools/generate_dashboard.py`. Done when the files disappear from the hotspot list.
2. **Quest: Metadata Polish x3**
   - Pick the 3 lowest-scoring entries from the dashboard.
   - Improve their summary, tags, and retention policy via `tools/update_index.py`.
3. **Quest: Duplicate Cluster Triage x1**
   - Pick the largest duplicate cluster from the dashboard.
   - Confirm the canonical path; adjust retention/lifecycle for non-canonical members (e.g., mark as `purge_candidate`).
4. **Quest: Purge Execution (Dry-Run)**
   - Run `python3 tools/cleanup_by_index.py`, review the commands, and manually execute safe deletions.

### Lane B: Feature Work (Phase 1 Backlog)
Larger, user-facing feature arcs (e.g., Proactive Reminder Engine, Email Triage).
- Always start by querying the index for target files to identify guardrails.
- Implement in small batches.
- At natural stopping points, switch to Lane A for a cool-down quest.

## The Full Parallel Loop (Jules + ninaflash Pipeline)

1. Perplexity diagnoses issue and writes precise spec.
2. Jules receives spec → builds in cloud async. 
   - **MANDATORY:** Jules MUST update `nina_update_log.md` (root) in the same PR.
3. ninaflash (local executor) handles urgent local fixes in parallel on its own worktree.
4. Jules opens PR when feature is complete.
5. ninaflash runs Guardian lint/compile checks on the PR diff.
   - **GOVERNANCE CHECK:** ninaflash verifies `nina_update_log.md` is updated. If missing, PR is rejected.
6. ninaflash merges PR → runs `./nina_sync.sh` → deploys to systemd.
7. Perplexity reviews result in a new thread.


**KEY RULES:**
- ninaflash is NOT just a fixer — it is the local merge and deploy executor.
- Jules does NOT merge its own PRs — ninaflash always performs the merge after review.
- Perplexity is NOT idle during coding — available for unblocking and mid-task review.
- All tools can run IN PARALLEL as the standard operating mode.

## Standard Session Start Checklist (Perplexity Thread)
Before starting any new Perplexity thread:
1. Start from clean `main` in `~/nina`.
2. Run `./nina_sync.sh`.
3. Create branch + worktree for each task.
4. Record claimed files in the centralized `~/nina/juleslock.txt`.
5. Launch local executor and Jules only after territories are confirmed non-overlapping.

## Session Close Checklist (ninaflash)
After every task:
1. The local executor commits only its branch/worktree.
2. Jules opens PR only from its branch/worktree.
3. Review and merge one stream at a time into `main`.
4. Pull updated `main` into remaining worktrees before further edits.
5. Run `./nina_sync.sh` from `main`.
6. Remove finished worktrees.
7. Update task tracker and backlog (see below).

## Post-Task Mandatory Updates
After every successful PR merge, ninaflash must update tracking using **Python only** (never bash echo):
1. Update `docs/space/jules_task_tracker.md` (change IN_PROGRESS to DONE, add PR number/date).
2. Update `docs/space/jules_backlog.md` (set status to DONE, add PR number/date).
3. Run `./nina_sync.sh` again to sync these tracker changes.

## Worktree Branching Strategy
True parallel work is allowed only through separate git branches and separate git worktrees.
- `~/nina` → `main` (production truth, review/merge/sync only)
- `~/nina/.worktrees/local-<task-id>` → `local/<task-id>-<slug>` (local docs, shell, hotfixes)
- `~/nina/.worktrees/jules-<task-id>` → `jules/<task-id>-<slug>` (multi-file features, async PR builds)

Never run parallel agent tasks from the same working directory.

## Quota Cascade Order

| Tool | Model | Daily Quota | Reset |
|------|-------|-------------|-------|
| NinaFlash (Ollama local) | qwen2.5-coder:7b | Unlimited | Never |
| ninaflash (agy) | Gemini Flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Ollama | Local | Unlimited | — |

**Cascade order:** `agy → Qwen Code → Jules (async) → Cursor → Ollama`
