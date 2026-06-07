# NINA Workflow — Three-Tool Parallel Model

## Identity
NINA is a personal AI assistant built by M. Baizid Alam (GitHub: aibony), AGM at BASIC Bank,
Dhaka, Bangladesh. Deployed on ASUS VivoBook X530FN (Ubuntu 24.04) at github.com/aibony/nina.

## The Three Tools

| Tool | Role | Mode |
|------|------|------|
| Perplexity Enterprise Pro | ARCHITECT + OVERWATCH | Active throughout — specs before, reviews after, unblocks during |
| Google Jules | ASYNC CLOUD CODER | Fire-and-forget cloud VM — builds multi-file features via PRs |
| Antigravity CLI (agy) | LOCAL MUSCLE | Sync local executor — edits, merges Jules PRs, deploys to service |

## The Full Parallel Loop

1. Perplexity diagnoses issue and writes precise spec
2. Jules receives spec → builds in cloud async (no interaction after submit)
3. agy handles urgent local fixes in parallel on its own worktree
4. Jules opens PR when done
5. agy reviews Jules PR diff, runs lint/compile checks, merges to main
6. agy runs ./nina_sync.sh to deploy and export
7. Perplexity reviews result (attach nina_latest.md to new thread)

**KEY RULES:**
- agy is NOT just a fixer — it is the local merge and deploy executor
- Jules does NOT merge its own PRs — agy always performs the merge after review
- Perplexity is NOT idle during coding — available for unblocking and mid-task review
- All three can run IN PARALLEL as the standard operating mode

## Session Start Checklist (Perplexity Thread)
Before starting any new Perplexity thread:
- [ ] Run: cd ~/nina && ./nina_sync.sh
- [ ] Attach: exports/nina_latest.md to the Perplexity thread
- [ ] Attach: the specific source file(s) being discussed (never rely on snapshot alone for code edits)
- [ ] State: the task type (bug / feature / doc / security / review)
- [ ] Check: juleslock.txt — is any target file currently locked by Jules?

## Session Close Checklist (agy)
After every agy task:
1. python3 -m py_compile <changed_file> && pyflakes <changed_file>
2. Append entry to nina_update_log.md using Python (never heredoc/echo)
3. Update juleslock.txt LOCKED_FILES with any .py files you changed
4. cd ~/nina && ./nina_sync.sh

## agy as Merge Executor
- agy is responsible for ALL Jules PR merges — never auto-merge via GitHub UI
- Before merging: run py_compile + pyflakes on changed files, check juleslock.txt
- After merging: run ./nina_sync.sh — no exceptions
- If merge conflict: stop, report to Perplexity for re-spec

## Branch Lanes
- main — production truth, review/merge/sync only
- agy-{task-id-slug} — local docs, shell, single-file hotfixes
- jules-{task-id-slug} — multi-file features, refactors, async PR builds

## Territory Rules
- agy default: docs/space/*.md, AGENTS.md, *.sh, single-file hotfixes
- Jules default: core/*.py, tools/*.py, interfaces/*.py, tests/*.py
- Shared (sequential only): requirements.txt, data/*.json
- Forbidden parallel: .env, secrets, lock-sensitive runtime files

## High-Risk Files (agy/manual only — never Jules)
interfaces/telegram_interface.py | .env | core/router.py | main.py | guardian_engine.py | tools/shell.py

## Key Paths
- Repo: ~/nina
- venv: source ~/nina/venv/bin/activate
- agy binary: ~/.local/bin/agy
- Service: sudo systemctl restart nina.service
- Snapshot export: ~/nina/exports/nina_latest.md
- Lock file: ~/nina/juleslock.txt

## Quota Reference
| Tool | Model | Reset |
|------|-------|-------|
| agy | Gemini 3.5 Flash Medium (default) | ~5h rolling |
| agy | Gemini 3.5 Flash High | ~5h rolling |
| agy | Gemini 3.1 Pro High | ~5h rolling |
| agy | Claude Sonnet 4.6 Thinking | Weekly ~7 days — reserve |
| agy | Claude Opus 4.6 Thinking | Weekly ~7 days — last resort |
| Jules | Gemini 3.1 Pro (built-in) | Rolling 24h, 100 tasks/day |
