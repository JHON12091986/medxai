---
name: nina-dev-policy
description: NINA's strict development policy and workflow rules. Load when helping with any code changes, patches, commits, or deployments to NINA. Every rule here is mandatory.
---

# NINA Dev Policy v1.1

## The 12 Rules (Non-Negotiable)

1. Every change has an ID — no anonymous fixes
2. One purpose per patch — never bundle unrelated changes
3. Guardian runs before AND after every change to core/, tools/, interfaces/, main.py, .env, or service files
4. Every risky change must be recoverable — guardian snapshot, git commit, or manual backup first
5. Runtime proof required — nina.service active, Telegram responding, target behavior confirmed
6. Logs updated same day — nina_update_log.md + docs/space/nina_error_register.md
7. Production fixes beat cleanup — priority: security > startup failure > service crash > broken user path
8. No blind AI patching — read target files, confirm paths are real, confirm names match current code
9. Protect interfaces and secrets — interfaces/telegram_interface.py, .env, router are high-risk
10. Warnings must be managed — ACCEPTED NOW / FIX NEXT / BLOCK RELEASE
11. Small changes win — prefer one-line fixes over rewrites
12. Done = ID + one purpose + guardian ran + runtime verified + rollback exists + logs updated

---

## Change ID System

- R-XX  bug fix / reliability
- F-XX  new feature
- S-XX  security improvement
- D-XX  debt cleanup

---

## High-Risk Files (extra caution required)

- interfaces/telegram_interface.py
- .env / any API keys
- core/router.py
- deploy/restart logic
- tools/upgradepipeline.py

---

## Log Append Rule (Non-Negotiable)

- NEVER use heredoc `cat >> file << EOF` for log appends
  Reason: backticks inside content break Perplexity UI renderer

- ALWAYS use Python for all log appends:

```
python3 - << 'PYEOF'
entry = "your log entry text here"
with open("/home/aibony/nina/nina_update_log.md", "a") as f:
    f.write(entry)
with open("/home/aibony/nina/logs/nina_update_log.md", "a") as f:
    f.write(entry)
print("Done")
PYEOF
```

- Same rule applies to docs/space/nina_error_register.md and any other markdown file append
- PYEOF is the safe heredoc terminator — never use EOF as terminator in Perplexity
- When entry content contains code fences, build the entry as a list of strings
  joined with newlines — never embed raw backtick blocks inside Python string literals

---

## Git Commit Style

```
fix(tool): wrap tool grammar in fallback guard (R-78)
feat(finance): add expenditure tracker tool (F-04)
security(config): remove .env from tracking
```

Format: `type(scope): description (ID)`
Types: fix / feat / security / refactor / docs / chore

---

## Session Workflow

1. Attach exports/nina_latest.md to every new thread
2. Check nina_update_log.md for last entry and current version
3. Check docs/space/nina_error_register.md for any BLOCKING open issues
4. State today's goal before starting
5. Run ./guardian before touching any code
6. Make one change, verify, log it
7. Run ./guardian after the change
8. Update nina_update_log.md + docs/space/nina_error_register.md same session (Python append only)
9. Upload fresh exports/nina_latest.md to Space before closing

---

## Log Entry Format

```
## Entry XXX — YYYY-MM-DD · [ID] Short Title

**Triggered by:** reason

**Files changed:**
- path/to/file.py

**[ID] · file — what changed**
- bullet describing the change

**Verification:**
- py_compile OK
- service restarted, PID XXXXX
- runtime test passed

**Rollback:** cp path/to/backup path/to/file
```

---

## Rollback Commands

```
cp ~/nina/upgrades/backups/backup_TIMESTAMP/core/memory.py ~/nina/core/memory.py
sudo systemctl restart nina

cp ~/nina/upgrades/backups/core_cleanup/memory.py.bak ~/nina/core/memory.py
```

---

## Definition of Done Checklist

- [ ] Change ID assigned (R/F/S/D-XX)
- [ ] Single purpose only
- [ ] Guardian ran BEFORE change
- [ ] python3 -m py_compile passed on changed file
- [ ] Guardian ran AFTER change
- [ ] nina.service active and confirmed running
- [ ] Telegram runtime proof obtained
- [ ] Rollback path documented
- [ ] nina_update_log.md updated (Python append, not heredoc)
- [ ] docs/space/nina_error_register.md updated if bug fixed or new issue found
