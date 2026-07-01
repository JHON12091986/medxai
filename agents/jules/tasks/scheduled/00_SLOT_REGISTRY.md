# NINA Jules Scheduler — Slot Registry
**Version:** 1.0 | **Updated:** 2026-06-18 | **Total Slots:** 24

This is the canonical registry Jules reads to know which task to run per slot.
Slot numbers rotate on a 30-minute interval across 24 slots = 12-hour full cycle.

| Slot | Task ID | Pillar | Task File | Tier | Priority |
|------|---------|--------|-----------|------|----------|
| 01 | VAULT-001 | Credential Vault Proxy | slot-01-vault-001.md | INFRA | P1 |
| 02 | VAULT-002 | Credential Vault Proxy | slot-02-vault-002.md | INFRA | P1 |
| 03 | VAULT-003 | Credential Vault Proxy | slot-03-vault-003.md | INFRA | P1 |
| 04 | SAND-001 | Micro-Sandboxed Subshell | slot-04-sand-001.md | INFRA | P1 |
| 05 | SAND-002 | Micro-Sandboxed Subshell | slot-05-sand-002.md | INFRA | P1 |
| 06 | SAND-003 | Micro-Sandboxed Subshell | slot-06-sand-003.md | INFRA | P1 |
| 07 | OMNI-001 | OmniBridge Adapters | slot-07-omni-001.md | OMNI | P1 |
| 08 | OMNI-002 | OmniBridge Adapters | slot-08-omni-002.md | OMNI | P1 |
| 09 | OMNI-003 | OmniBridge Adapters | slot-09-omni-003.md | OMNI | P1 |
| 10 | OBS-001 | Observability | slot-10-obs-001.md | OBS | P1 |
| 11 | PERF-001 | Compiled Utilities | slot-11-perf-001.md | PERF | P2 |
| 12 | PERF-002 | Compiled Utilities | slot-12-perf-002.md | PERF | P2 |
| 13 | PERF-003 | Compiled Utilities | slot-13-perf-003.md | PERF | P2 |
| 14 | OBS-002 | Governance Validation | slot-14-obs-002.md | OBS | P2 |
| 15 | OBS-003 | Jules Dispatch | slot-15-obs-003.md | OBS | P2 |
| 16 | PROVIDER-REG | Provider Registry | slot-16-provider-registry.md | OBS | P2 |
| 17 | GOVERN-001 | Jules Guard | slot-17-govern-001.md | GOVERN | P2 |
| 18 | GOVERN-002 | Crons Manager | slot-18-govern-002.md | GOVERN | P2 |
| 19 | GOVERN-003 | GitHub Workflows | slot-19-govern-003.md | GOVERN | P2 |
| 20 | SYNC-FIX | nina_sync.sh Dedup | slot-20-sync-fix.md | GOVERN | P1 |
| 21 | SURGICAL-DOCS | P-series Doc Tasks | slot-21-surgical-docs.md | BACKLOG | P3 |
| 22 | IDLE-DEDUP | IdleLoop Dedup | slot-22-idle-dedup.md | BACKLOG | P2 |
| 23 | BACKLOG-AUDIT | Backlog Health Audit | slot-23-backlog-audit.md | BACKLOG | P2 |
| 24 | DEBT-CLEAR | Tech Debt TODOs | slot-24-debt-clear.md | BACKLOG | P3 |

## Lock Protocol

Before any slot executes:
1. Check `juleslock.txt` — if non-empty, ABORT and log skip.
2. Write own slot ID to `juleslock.txt` on start.
3. Clear `juleslock.txt` on exit (success or failure).

This prevents two simultaneous slots from running.
