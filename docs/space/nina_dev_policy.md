---
name: nina_dev_policy
description: NINA's strict development policy and workflow rules. Load when helping with any code changes, patches, commits, or deployments to NINA. Every rule here is mandatory.
version: 1.4
updated: 2026-06-05
---

# NINA Dev Policy v1.3

## Dev Environment Stack
- **AI Tooling:** Perplexity Enterprise Pro with Claude Sonnet 4.6
- **Developer CLI + Local Build Agent (Claude Sonnet 4.6 Thinking — interactive, filesystem access, real-time debugging):** Antigravity CLI agy v1.0.5
- **Primary Developer Agent:** Jules at jules.google
- **Reference & Search:** NotebookLM
- **Note:** Gemini CLI was removed on June 5, 2026.

## The 12 Rules (Non-Negotiable)
1. Every change has an ID — no anonymous fixes
2. One purpose per patch — never bundle unrelated changes
3. Guardian runs **before AND after** every change to `core/`, `tools/`, `interfaces/`, `main.py`, `.env`, or service files
4. Every risky change must be recoverable — guardian snapshot, git commit, or manual backup first
5. Runtime proof required — `nina.service` active, Telegram responding, target behavior confirmed
6. Logs updated same day — `nina_update_log.md` + `nina_problem_log.md`
7. Production fixes beat cleanup — priority: security → startup failure → service crash → broken user path
8. No blind AI patching — read target files, confirm paths are real, confirm names match current code
9. Protect interfaces and secrets — `interfaces/telegraminterface.py`, `.env`, `core/router.py` are high-risk
10. Warnings must be managed — ACCEPTED NOW / FIX NEXT / BLOCK RELEASE
11. Small changes win — prefer one-line fixes over rewrites
12. **Done = ID + one purpose + guardian ran + runtime verified + rollback exists + logs updated**
13. **Run `./nina_sync.sh` at the end of every session** — commits space files, updates log, pushes to GitHub, notifies Telegram

## Session Workflow

    # Start of session
    cd ~/nina && ./guardian          # Health check before any work

    # End of session (mandatory)
    cd ~/nina && ./nina_sync.sh      # Sync everything, commit, push, notify

    # Dry-run preview (optional)
    cd ~/nina && ./nina_sync.sh --dry-run

    # LOCAL-BUILD path (scoped single-module tasks)
    # Use agy directly instead of filing a Jules issue

## Change ID System
- `R-XX` — bug fix / reliability
- `F-XX` — new feature
- `S-XX` — security improvement
- `D-XX` — debt cleanup

## High-Risk Files (extra caution required)
- `interfaces/telegraminterface.py`
- `.env` / any API keys
- `core/router.py`
- deploy/restart logic
- `tools/upgradepipeline.py`

## Log Append Rule (Non-Negotiable)
- **NEVER** use heredoc `cat >> file << 'EOF'` for log appends — backticks inside break Perplexity UI renderer
- **ALWAYS** use Python for all log appends
- Use PYEOF as heredoc terminator — never use EOF in Perplexity
- When entry content contains code fences, build the entry as a list of strings joined with newlines
- Never embed raw backtick blocks inside Python string literals
- Same rule applies to `nina_problem_log.md` and any other markdown file append

## Python Log Append Pattern

    python3 - << 'PYEOF'
    lines = [
        "",
        "## Entry XXX — YYYY-MM-DD · ID Short Title",
        "",
        "**Triggered by:** reason",
        "",
        "**Files changed:**",
        "- path/to/file.py",
        "",
        "**Verification:** py_compile OK, service restarted, runtime test passed",
        "",
        "**Rollback:** cp path/to/backup path/to/file",
        "",
    ]
    entry = chr(10).join(lines)
    for path in ["/home/aibony/nina/nina_update_log.md", "/home/aibony/nina/logs/nina_update_log.md"]:
        with open(path, "a") as f:
            f.write(entry)
    print("Done")
    PYEOF

## Git Commit Style

    fix: wrap tool grammar in fallback guard (R-78)
    feat: add expenditure tracker tool (F-04)
    security: remove .env from tracking

Format: `type: short description (ID)`
Types: fix | feat | security | refactor | docs | chore

## Log Entry Format

    ## Entry XXX — YYYY-MM-DD · ID Short Title
    **Triggered by:** reason
    **Files changed:**
    - path/to/file.py — what changed
    **Verification:**
    - py_compile OK
    - service restarted, PID XXXXX
    - runtime test passed
    **Rollback:** cp path/to/backup path/to/file

## Rollback Commands

    cp ~/nina/upgrades/backups/backup_TIMESTAMP/core/memory.py ~/nina/core/memory.py
    sudo systemctl restart nina

## Definition of Done Checklist
- [ ] Change ID assigned (R/F/S/D-XX)
- [ ] Single purpose only
- [ ] Guardian ran BEFORE change
- [ ] `python3 -m py_compile` passed on changed file
- [ ] Guardian ran AFTER change
- [ ] `nina.service` active and confirmed running
- [ ] Telegram runtime proof obtained
- [ ] Rollback path documented
- [ ] `nina_update_log.md` updated (Python append, not heredoc)
- [ ] `nina_problem_log.md` updated if bug fixed or new issue found
- [ ] `./nina_sync.sh` run at session end
