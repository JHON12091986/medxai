---
name: nina-testing
description: Guardian pass criteria, verification sequence, and definition of done for NINA. Load this before and after any code change.
---

# NINA Testing & Verification

## Guardian Command
```bash
cd ~/nina && ./guardian
```
Run BEFORE any change to core/, tools/, interfaces/, main.py, .env
Run AFTER every change — no exceptions

## Guardian Pass Criteria (all must pass)
1. venv active, Python 3.14, all required packages present
2. `.env` validation passed (`TELEGRAM_CHAT_ID` warning acceptable)
3. Syntax check all tracked files OK
4. pyflakes — no issues
5. mypy — warnings non-blocking
6. `nina.service` active, no crash pattern
7. Telegram polling confirmed
8. APScheduler started (13 jobs)

## Manual Verification Sequence
```bash
# 1. Syntax check changed file
cd ~/nina && source venv/bin/activate
python3 -m py_compile path/to/changed_file.py

# 2. Restart service
sudo systemctl restart nina.service

# 3. Confirm running
sudo systemctl status nina.service

# 4. Runtime proof — send a message via Telegram and confirm response
```

## Definition of Done
- [ ] Change ID assigned (R/F/S/D-XX)
- [ ] Single purpose only
- [ ] Guardian ran BEFORE change
- [ ] py_compile passed on changed file
- [ ] Guardian ran AFTER change
- [ ] nina.service active and confirmed running
- [ ] Telegram runtime proof obtained
- [ ] Rollback path documented
- [ ] nina_update_log.md updated (Python append only)
- [ ] docs/space/nina_error_register.md updated if bug fixed or new issue found

## Rollback Pattern
```bash
cp ~/nina/upgrades/backups/backup_TIMESTAMP/path/to/file.py ~/nina/path/to/file.py
sudo systemctl restart nina.service
```
