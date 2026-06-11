# ninaflash Subsystem Documentation

## Overview

ninaflash is NINA's dedicated Local Executor. Far more than just a utility script, it serves as the critical local engine responsible for deploying changes, managing urgent hotfixes, and merging pull requests created by asynchronous cloud builders like Jules. It functions as NINA's internal muscle, handling all logic requiring local system interaction while seamlessly integrating with external processes.

## Surgical Code Intelligence (v14.0)

ninaflash v6.1+ features a "Surgical Code Intelligence" layer designed for extreme token efficiency. It uses local AST (Abstract Syntax Tree) parsing to extract only what is needed:

- `nf code pack <file>` — Distill a large Python file into a token-efficient skeletal summary.
- `nf code symbol --file <f> --name <n>` — Extracts the exact implementation of a specific class or function.
- `nf query "<task>"` — Local capability introspection tool.

### [NEW] File & Git Operations (Zero Cloud Cost)

- `nf file read | grep | patch | insert | diff` — Local file manipulation without cloud escalation.
- `nf git log | changed | search | blame | stash-quick` — Hardened git interface with security blocklist (prevents accidental push/force).

### [NEW] Performance & Parallelism

- `nf monitor` — Parses NinaGate logs to show local vs. cloud routing efficiency, tokens saved, and avg latency.
- `nf batch --cmds "c1|c2"` — Parallel execution of sub-commands using a local thread pool.

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
