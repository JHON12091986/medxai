# config/

Nina shell configuration. Everything in this directory is version-controlled and synced via git.

---

## Files

| File | Purpose |
|---|---|
| `.bashrc_nina` | Nina CLI aliases — sourced by `~/.bashrc` |

---

## Setup (one-time, per machine)

```bash
# 1. Add to ~/.bashrc
echo 'source ~/nina/config/.bashrc_nina' >> ~/.bashrc

# 2. Set git autostash (prevents pull failures on dirty working tree)
git -C ~/nina config pull.autostash true

# 3. Reload
source ~/.bashrc

# 4. Verify
ngit --help 2>/dev/null || echo "alias: ngit ready"
```

---

## Alias Reference

### Git

| Alias | Command | When to use |
|---|---|---|
| `ngit "msg"` | `bash ~/nina/scripts/ngit.sh` | You made changes — ships them to remote |
| `sync` | `bash ~/nina/scripts/nina_sync.sh all` | Manual OODA health check |
| `npush "msg"` | same as `ngit` | Legacy muscle memory |

**Flow:**
```
ngit → stage → commit → pull → push --no-verify
              └── post-push hook fires sync in background automatically
```

### Navigation

| Alias | Does |
|---|---|
| `nina` | `cd ~/nina && source venv/bin/activate` |

### Service (systemctl --user, never sudo)

| Alias | Does |
|---|---|
| `nstart` | Start nina.service |
| `nstop` | Stop nina.service |
| `nrestart` | Restart nina.service |
| `nstatus` | Status of nina.service |
| `nlog` | Live journal logs (`journalctl --user -u nina -f`) |

### Log tails

| Alias | Does |
|---|---|
| `ngit-log` | `tail -f ~/nina/runtime/logs/ngit.log` |
| `sync-log` | `tail -f ~/nina/runtime/logs/nina_sync.log` |

---

## P0 MCP Aliases

The P0 relay bus aliases (`nina_exec`, `nina_tail`, `nina_diff`, `nina_search`, `nina_status`) live separately in `mcp/aliases.sh`.
See `mcp/README.md` for setup.

---

## Why config/ and not ~/.bashrc directly?

- Nina's aliases live **inside the Nina repo** — version controlled, backed up, auto-synced via `ngit`
- `~/.bashrc` is a system file — not in git, lost on reinstall
- On a new machine: one line restores everything:
  ```bash
  echo 'source ~/nina/config/.bashrc_nina' >> ~/.bashrc
  ```
