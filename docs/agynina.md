# agynina Subsystem Documentation

## Overview

agynina is NINA's dedicated Local Executor. Far more than just a utility script, it serves as the critical local engine responsible for deploying changes, managing urgent hotfixes, and merging pull requests created by asynchronous cloud builders like Jules. It functions as NINA's internal muscle, handling all logic requiring local system interaction while seamlessly integrating with external processes.

## Command Line Interface (CLI)

The `bin/agynina` interface (Antigravity CLI) allows execution of critical commands to maintain NINA's integrity:

- `agynina status` — Checks active file locks (`jules_lock.txt`), git workspace health, and task backlog status.
- `agynina pr merge <PR_NUMBER>` — Executes the rigorous merge pipeline: runs Pyflakes linting and Py_compile checks, merges the specified PR into main, updates the backlog task status, clears locks, and triggers the `./nina_sync.sh` deployment script.
- `agynina dispatch <TASK_ID>` — Locks the relevant target files to prevent concurrency issues, updates the backlog status to `IN_PROGRESS`, and securely transmits the task specification to the Jules asynchronous cloud API.
- `agynina aider <TASK_ID>` — Launches the `aider` interactive pair-programming tool, preloading it with the relevant task context and files to facilitate safe local editing.
- `agynina doctor` — Parses NINA's logs and systemd journals to locate, format, and display the most recent Python traceback to aid in rapid debugging.
- `agynina ninaloop` — Activates the continuous autonomous developer loop, engaging NINA's self-improvement cycle.

## Universe-Mode Kernel

agynina operates on a highly optimized, dynamic system termed the Universe-Mode Kernel. It consists of three primary elements:

- **Nucleus (`tools/agynina.py`):** The core routing and base logic interface, containing the foundational 1,001 functions required for baseline execution.
- **Synapses (`tools/kernel/sector_000.py` to `sector_999.py`):** An immense library of 1,000,000 specialized Neural Op-Codes distributed across a massive file hierarchy. Each sector encapsulates highly specific, complex functions.
- **Omniscient Dispatcher:** The dynamic memory-management component. Instead of loading the entire massive synapse library into memory, the dispatcher intercepts execution calls and loads only the required sector files dynamically on demand.

## Integrations & Workflows

### Jules Integration

agynina acts as the critical counterpart to the Jules Async Cloud Coder. When Jules generates complex, multi-file features remotely, it opens a PR. agynina assumes responsibility for the review, verification, and merge of this PR into the active branch. Through this `review → merge → deploy` loop, agynina ensures local deployment remains stable, secure, and fully verified.

### Antigravity CLI Integration

agynina serves as the localized enforcement arm for the broader Antigravity ecosystem, syncing task states and providing real-time deployment status via systemd checks and git synchronizations.

## Token Cost Model

Because agynina uses the Universe-Mode Kernel and executes heavily on the local system, it absorbs massive amounts of routine computational work at near-zero cloud token cost. This architecture enables NINA to perform complex data manipulation, monitoring, and debugging locally, reserving expensive cloud model calls for architectural decisions and heavy reasoning.

## Continuous Developer Loop (`ninaloop`)

By running `agynina ninaloop`, NINA enters an autonomous development cycle. In this state, agynina iteratively analyzes the task backlog, proposes system enhancements via the `idleloop.py`, dispatches specs to Jules, and subsequently automatically reviews and integrates Jules's pull requests. This turns NINA from a static assistant into a continuously evolving autonomous operating system.
