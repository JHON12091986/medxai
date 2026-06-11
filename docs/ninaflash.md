# ninaflash Subsystem Documentation

## Overview

ninaflash is NINA's dedicated Local Executor. Far more than just a utility script, it serves as the critical local engine responsible for deploying changes, managing urgent hotfixes, and merging pull requests created by asynchronous cloud builders like Jules. It functions as NINA's internal muscle, handling all logic requiring local system interaction while seamlessly integrating with external processes.

## THE PRIME DIRECTIVE: SURGICAL TOOL FIRST (RULE 0)

To maximize token efficiency and minimize latency, all NINA agents must prioritize local surgical tools over direct shell commands. Consult this mandate before every file or git operation:

| WANT TO... | USE THIS INSTEAD |
| :--- | :--- |
| Read part of a file | `nf file read <file> --start N --end N` |
| Find a function/class | `nf code symbol <file> <name>` |
| Search text across files | `nf file grep <pattern> --dir <dir>` |
| See what changed | `nf git changed` |
| Read recent log entries | `nf log tail 5` |
| Find next log ID | `nf log next-id` |
| Get git history | `nf git log --n 10` |
| Search commit messages | `nf git search <keyword>` |
| Get function signatures only | `nf code sigs <dir>` |
| See file diff only | `nf file diff <file>` |
| Edit one string in a file | `nf file patch <file> --find "x" --replace "y"` |
| Get directory structure | `nf code index` (JSON map, no file reads) |

**Mandate:** Only escalate to direct shell `cat`, `read_file`, or `grep` when the `nf` command fails, returns an error, or the operation requires full file context for complex architectural reasoning.

## Surgical Code Intelligence (v14.0)

ninaflash v6.1+ features a "Surgical Code Intelligence" layer designed for extreme token efficiency. It uses local AST (Abstract Syntax Tree) parsing to extract only what is needed:

- `nf code pack <file>` — Distill a large Python file into a token-efficient skeletal summary.
- `nf code symbol --file <f> --name <n>` — Extracts the exact implementation of a specific class or function.
- `nf query "<task>"` — Local capability introspection tool.

### [NEW] File & Git Operations (Zero Cloud Cost)

- `nf file read | grep | patch | insert | diff` — Local file manipulation without cloud escalation.
- `nf git log | changed | search | blame | stash-quick` — Hardened git interface with security blocklist (prevents accidental push/force).

### [NEW] Performance & Metrics (Real Data)

- `nf monitor` — Comprehensive efficiency report parsing real data from:
  - **Gemini CLI Sessions:** Extracts token usage and turn counts from `.jsonl` session files.
  - **NinaGate Logs:** Reports local vs. cloud routing ratios, average latency, and estimated cost savings.
  - **NinaFlash Logs:** Tracks local command execution frequency, timing, and cumulative token savings.
  - Use `nf monitor --full` to parse all historical data instead of just the last 3 sessions.
  - Use `nf monitor --tools` to profile tool usage frequency and estimated token costs per tool.
- `nf batch --cmds "c1|c2"` — Parallel execution of sub-commands using a local thread pool.

### [NEW] High-Velocity Verification (v14.2)

- **`nf bench`** — The "Cloud vs Hybrid" benchmark harness. Runs a standardized reasoning task twice (once pure cloud, once hybrid with local offloading) and reports empirical delta in time, cost, and tokens.
- **`nf test --parallel`** — High-concurrency test runner. Executes the full `pytest` suite using all available CPU cores via `pytest-xdist`, providing real-time resource "bump" metrics (CPU/RAM spikes).
- **`nf query`** — Capability mapping tool. Lists all registered `cmd_` handlers and their documentation to help agents identify local offload opportunities.
- **`nf maintenance pr <pr_id>`** — Surgical PR merging with automated log entry generation and health check verification.

### [NEW] Structured Logging

Every `nf` command execution is now recorded in `logs/ninaflash.log` in a machine-readable JSON format. This log captures:
- **Command/Subcommand:** Precisely what was executed.
- **Duration:** Execution time in milliseconds (monotonic timing).
- **Outcome:** Success state or specific error messages.
- **Tokens Saved:** Estimated cloud tokens avoided by using the local executor.

| Command Type | Est. Tokens Saved |
| :--- | :--- |
| `file` | 2000 |
| `code` | 1500 |
| `git` | 800 |
| `find-symbol` | 1000 |
| `batch` | 1200 |

### [NEW] Session & Memory Management

- `nf memory session-save --summary "TEXT"` — Standardized end-of-session learning capture.
- `nf memory inject` — Bootstrap command to load last session context into active reasoning.

## Atomic Maintenance (Maintainer Mode)

The `maintain` module handles the high-turn "Daily Maintenance" loop automatically:

- `nf maintain pr <id> --task <id> --title <t> --summary <s>` — Atomically rebases a PR, surgically resolves documentation regressions (preserving v13+ headers locally), marks the backlog task as DONE, and appends the update log.
- **Improved Verification:** All code checks now use `python3 -m pyflakes` for reliable venv-isolated validation, regardless of system PATH.

## Telemetry & User Visibility (v14.0)

ninaflash and all NINA agents adhere to a strict **"Glass Box"** reasoning protocol:
- **Topic Heartbeats:** Granular updates via `update_topic` for every sub-goal.
- **Thought Streaming:** High-level reasoning intent is mirrored to `logs/agent_thoughts.log`.
- **Diagnostic Transparency:** Explicit reporting of tool stalls or hardware constraints.

## Universe-Mode Kernel

ninaflash operates on a highly optimized, dynamic system termed the Universe-Mode Kernel. It consists of three primary elements:

- **Nucleus (`tools/ninaflash.py`):** The core routing and base logic interface, containing the foundational 1,001 functions required for baseline execution.
- **Synapses (`tools/kernel/sector_000.py` to `sector_999.py`):** An immense library of 1,000,000 specialized Neural Op-Codes distributed across a massive file hierarchy. Each sector encapsulates highly specific, complex functions.
- **Omniscient Dispatcher:** The dynamic memory-management component. Instead of loading the entire massive synapse library into memory, the dispatcher intercepts execution calls and loads only the required sector files dynamically on demand.

## Integrations & Workflows

### Jules Integration

ninaflash acts as the critical counterpart to the Jules Async Cloud Coder. When Jules generates complex, multi-file features remotely, it opens a PR. ninaflash assumes responsibility for the review, verification, and merge of this PR into the active branch. Through this `review → merge → deploy` loop, ninaflash ensures local deployment remains stable, secure, and fully verified.

### Antigravity CLI Integration

ninaflash serves as the localized enforcement arm for the broader Antigravity ecosystem, syncing task states and providing real-time deployment status via systemd checks and git synchronizations.

## Token Cost Model

Because ninaflash uses the Universe-Mode Kernel and executes heavily on the local system, it absorbs massive amounts of routine computational work at near-zero cloud token cost. This architecture enables NINA to perform complex data manipulation, monitoring, and debugging locally, reserving expensive cloud model calls for architectural decisions and heavy reasoning.

Additional token savings are achieved through:
- **Persistent Response Caching:** The HybridRouter caches identical prompts to disk, ensuring that repeated local tasks or duplicate instructions consume zero external tokens.
- **Local Model Routing:** Sensitive or routine tasks are routed to local Ollama instances, bypassing paid cloud APIs entirely.

## Continuous Developer Loop (`ninaloop`)

By running `ninaflash ninaloop`, NINA enters an autonomous development cycle. In this state, ninaflash iteratively analyzes the task backlog, proposes system enhancements via the `idleloop.py`, dispatches specs to Jules, and subsequently automatically reviews and integrates Jules's pull requests. This turns NINA from a static assistant into a continuously evolving autonomous operating system.
