# NINA Workflow — Three-Tier Agent Model

## Identity
NINA is a personal AI assistant built by M. Baizid Alam (GitHub: aibony), AGM at BASIC Bank,
Dhaka, Bangladesh. Deployed on ASUS VivoBook X530FN (Ubuntu 26.04) at github.com/aibony/nina.

## The Three-Tier Agent Model

| Agent | Role | Scope |
|------|------|------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Strategic direction, specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| agynina (Antigravity CLI) | LOCAL EXECUTOR | Sync local executor — edits, reviews Jules PR diff, merges, deploys |

## 0. Discovery & Governance (New)
- **Check the Index:** Before writing any code, creating a new tool, or modifying a document, consult the **Repository Index** (`docs/space/nina_index.md`). This prevents duplication and maintains canonical sources of truth.
- **Update the Index:** If you create, move, rename, archive, or delete a governed artifact, you MUST run `python3 tools/update_index.py` and ensure `python3 tools/validate_index.py` passes.

## The Full Parallel Loop (Jules + agynina Pipeline)

1. Perplexity diagnoses issue and writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. agynina (local executor) handles urgent local fixes in parallel on its own worktree
4. Jules opens PR when feature is complete
5. agynina runs Guardian lint/compile checks on the PR diff
6. agynina merges PR → runs `./nina_sync.sh` → deploys to systemd
7. Perplexity reviews result in a new thread

**KEY RULES:**
- agynina is NOT just a fixer — it is the local merge and deploy executor.
- Jules does NOT merge its own PRs — agynina always performs the merge after review.
- Perplexity is NOT idle during coding — available for unblocking and mid-task review.
- All tools can run IN PARALLEL as the standard operating mode.

## Standard Session Start Checklist (Perplexity Thread)
Before starting any new Perplexity thread:
1. Start from clean `main` in `~/nina`.
2. Run `./nina_sync.sh`.
3. Create branch + worktree for each task.
4. Record claimed files in the centralized `~/nina/jules_lock.txt`.
5. Launch local executor and Jules only after territories are confirmed non-overlapping.

## Session Close Checklist (agynina)
After every task:
1. The local executor commits only its branch/worktree.
2. Jules opens PR only from its branch/worktree.
3. Review and merge one stream at a time into `main`.
4. Pull updated `main` into remaining worktrees before further edits.
5. Run `./nina_sync.sh` from `main`.
6. Remove finished worktrees.
7. Update task tracker and backlog (see below).

## Post-Task Mandatory Updates
After every successful PR merge, agynina must update tracking using **Python only** (never bash echo):
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
| agynina (agy) | Gemini Flash | ~5h rolling | Rolling |
| Qwen Code CLI | Qwen3-Coder-480B | 2,000 req/day | Daily |
| Jules | Gemini 3.1 Pro | 100 tasks/day | Rolling 24h |
| Cursor Hobby | GPT-4o mini | 50 chat/month | Monthly |
| Ollama | Local | Unlimited | — |

**Cascade order:** `agy → Qwen Code → Jules (async) → Cursor → Ollama`
