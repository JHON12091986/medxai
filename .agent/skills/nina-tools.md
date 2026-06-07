---
name: nina-tools
description: NINA tools layer — shell allowlist rules, security constraints, and Stage C tools being built. Load this for any work in tools/ or when suggesting shell commands.
---

# NINA Tools Layer

## High-Risk Rules (Non-Negotiable)
- `tools/shell.py` — DO NOT weaken the shell allowlist, ever
- `cat` is BANNED from the allowlist — confirmed removed by R-48 ✅ (O-06 closed 2026-06-06)
- `.env` and API keys — never read, log, or expose via any tool
- `tools/browser.py` — SSRF protection must stay intact; `_is_internal()` must resolve hostnames before allowing requests

## Shell Allowlist Policy
- Only explicitly whitelisted commands are permitted
- When suggesting shell operations, check allowlist first
- Never suggest adding new commands to allowlist without a security review ID (S-XX)

## Existing Tools
| File | Purpose |
|------|---------|
| `tools/browser.py` | Web browsing with SSRF protection |
| `tools/shell.py` | Shell execution with strict allowlist |
| `tools/officemail.py` | EWS email — BASIC Bank mailboxes (wrapper handles NTLM logic safely) |
| `tools/finance.py` | SQLite expense ledger — NLP entry, weekly summary, threshold alerts |
| `tools/market.py` | DSE/CSE monitor — mock price alerts (real DSE/CSE API pending) |
| `core/memory.py` | Memory & Knowledge Base core primitives via ChromaDB (`kb_add_entry` / `kb_search`) |
| `tools/compact_exporter.py` | Context compact snapshot generator for Perplexity Space |
| `tools/upgradepipeline.py` | Self-upgrade system — high risk, handle carefully |

## Local Models for Sensitive Tasks
Sensitive data (banking, personal) → local model only:
- `qwen2.5:1.5b` → LOCALFAST
- `qwen2.5:7b` → LOCALHEAVY
Never route sensitive tasks to cloud providers.
