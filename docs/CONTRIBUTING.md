# Contributing to NINA

## Git Hooks (Mandatory)

Install before any commits:

```bash
cp git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

This hook runs `guardian_engine.py --mode hook` on every staged Python file before committing.
It **blocks commits** with Guardian violations.
Emergency bypass: `git commit --no-verify`
(If you use the bypass, log the reason in `docs/space/nina_error_register.md`.)

## General Rules

- Run `python3 rule0_audit.py` before opening a PR.
- Run `./nina_sync.sh` after every merge to main.
- Do NOT directly edit high-risk files (`core/router.py`, `interfaces/telegram_interface.py`, `.env`) without a Guardian pass.
- All commits must follow the format: `type(scope): description` e.g. `fix(router): handle None provider response`.
