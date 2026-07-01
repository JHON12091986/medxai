# runtime/

> **Ephemeral live state only.** Nothing in this folder is source code or configuration.
> All files here are written and read at runtime — they are intentionally excluded from git tracking (see `.gitignore`).

---

## Structure

```
runtime/
├── state/          ← Live JSON state files (circuit breaker, cron health, quota)
├── cache/          ← NinaGate response cache and provider caches
├── db/             ← SQLite runtime databases (provider metrics)
├── logs/           ← Live log files: telemetry, OpenCode run logs
│   └── opencode/   ← Per-run OpenCode output logs
└── locks/          ← Lock files (juleslock mirror, service locks)
```

---

## Files

| File | Owner | Description |
|---|---|---|
| `state/circuit_state.json` | `core/router.py` | CircuitBreaker trip state per provider |
| `state/cron_health.json` | `crons/` | Last cron execution timestamps + health |
| `state/quota_state.json` | `core/quota_router.py` | Daily/weekly token usage counters per provider |
| `cache/ninagate_cache.json` | `ninagate/main.py` | Payload-keyed LLM response cache |
| `db/provider_metrics.db` | `ninagate/main.py` | SQLite: per-provider latency, success rate, cost |
| `logs/telemetry.jsonl` | `core/nina.py` | Full request telemetry stream |
| `logs/opencode/` | `opencode/tools/opencode_tool.py` | OpenCode autonomous run logs |
| `locks/juleslock.txt` | `ninajulesgithub.service` | Files Jules must not touch (runtime mirror) |

---

## Rules

1. **Never commit live state.** All `runtime/` content is gitignored except `.gitkeep` anchors.
2. **Safe to wipe.** If Nina behaves strangely, `rm -rf runtime/state/* runtime/cache/*` is a valid reset.
3. **Do not put config here.** Config lives in `config/`. This folder is for ephemeral data only.
4. **OpenCode logs land in `logs/opencode/`.** Each run writes `last_run.log` — older runs are rotated.

---

*Consolidated from `data/` and repo root on 2026-06-22 — NINA v14.4+*
