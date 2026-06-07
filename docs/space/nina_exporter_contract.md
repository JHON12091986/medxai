# nina_latest.md — Exporter Contract

## Purpose
This contract defines the mandatory sections that tools/compact_exporter.py
MUST include in every nina_latest.md export. If any section is missing or
shows "not parsed", the exporter is broken and must be fixed before the
next session.

## Mandatory Sections (in order)

### 1. Header
- Generated timestamp
- Repo, branch, Python version
- Purpose line: "AI context snapshot for Perplexity Space"

### 2. Executive Snapshot
Must contain ALL of the following subsections:
- Identity & Deployment Summary (project name, owner, machine, service)
- Core Architecture Summary (provider tiers, routing score algorithm)
- NINA Tool Routing Policy v2 Summary (3-row tool table: Perplexity / Jules / agynina)
- Three-Tool Parallel Model (the 7-step parallel loop)
- agynina as Merge Executor — Mandatory (4-rule block)
- Key Rules (high-risk file list, juleslock check, sensitive paths)
- High-Risk Files
- Latest Verified Runtime Status (guardian health score, BLOCKER/WARN counts)

### 3. Current Action Board
- Summary counts (BLOCKER, WARN, DEBT, FEATURE_PENDING)
- All OPEN issues with ID, severity, component, assignee

### 4. Current Phase Roadmap
- Current stage and next task
- Open milestones

### 5. Recent Meaningful Changes
- Last 5 meaningful update log entries (skip D-sync spam)

### 6. Key Rules (agynina + Jules)
- agynina mandatory rules after every code change
- agynina mandatory rules after every task close
- Jules rules
- Guardian gate
- Never-do list

### 7. Targeted Code Context
- compact signatures for: core/router.py, core/agent.py, core/nina.py,
  interfaces/telegram_interface.py, core/memory.py
- full source for: tools/shell.py, tools/browser.py

## Validation Test
After every exporter run, confirm these strings appear in nina_latest.md:
- "ARCHITECT" (routing policy table)
- "ASYNC CLOUD CODER" (routing policy table)
- "LOCAL MUSCLE" (routing policy table)
- "agynina as Merge Executor" (executive snapshot section)
- "The Full Parallel Loop" (executive snapshot section)
- "BLOCKER" (action board)
- "Guardian Gate" (key rules)

If any string is missing, the exporter has a parse failure. Fix compact_exporter.py
before uploading nina_latest.md to Perplexity Space.

## Parse Failure History
- 2026-06-07: "NINA Tool Routing Policy v2 Summary" section was not parsed due to
  heading mismatch between nina_state.md and compact_exporter.py section matcher.
  Fixed by aligning the section header string in compact_exporter.py.
