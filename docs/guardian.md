# Guardian Gate Subsystem

## Purpose

The Guardian Gate provides a crucial forensic safety layer for autonomous self-patching. Because NINA operates as a self-developing autonomous system—meaning AI agents are writing and deploying actual code updates locally—there is an inherent risk of syntax errors, broken logic, or catastrophic failures. The Guardian Gate acts as a mandatory filter ensuring that patches applied by ninaflash and Jules meet strict safety thresholds before they are deployed to the local system service.

## Components

The Guardian Gate is composed of two primary elements:
- **`guardian` (watchdog script):** A system-level bash script responsible for continuously monitoring the NINA service and triggering immediate rollbacks or restarts if a fatal crash occurs during runtime.
- **`guardian_engine.py`:** A massive 73KB forensic Python engine that performs deep Abstract Syntax Tree (AST) scanning on all incoming code modifications before they are permitted to execute.

## Verification Pipeline

Whenever a change is proposed (such as through a pull request merge or automated local patch), the Guardian Gate enforces the following strict pipeline:
1. **AST Scan:** Analyzes the Abstract Syntax Tree of the modified code to check for prohibited behaviors.
2. **Baseline Drift Check:** Compares the structural and logical footprint against `upgrades/guardian_baseline.json`.
3. **`py_compile` + `pyflakes`:** Performs immediate syntax and linting verification.
4. **[NEW] Autonomous Self-Fix Loop:** If a syntax error is detected during verification, the Guardian autonomously re-routes the error back to the agent in `core/agent.py`. The agent is given up to 2 attempts to surgically fix the error (e.g., using `sed` or a Python script) and re-verify the patch.
5. **Log:** Records successful verifications or fatal rejections in `docs/logs/nina_update_log.md`.
6. **Sync:** After successful validation, triggers `nina_sync.sh` to apply the changes and restart the systemd service.

## Guardian Baseline

The file `upgrades/guardian_baseline.json` serves as the immutable structural map of NINA's intended state. The Guardian engine utilizes this JSON map to identify unexpected drift in critical runtime files or configurations, preventing agents from "hallucinating" destructive architectural changes.

## Log and Sync Operations

- **Log location:** `docs/logs/nina_update_log.md` tracks all operations.
- **Sync script:** `nina_sync.sh` handles the actual system reboot process, acting only when explicitly permitted by the Guardian pipeline.

## High-Risk Files

Several critical files within NINA are flagged as "high-risk" by Guardian. These files always invoke the strictest analysis and are generally restricted from being edited by async tools (like Jules) without local human or ninaflash intervention:
- `interfaces/telegram_interface.py`
- `.env`
- `core/router.py`
- `main.py`
- `guardian_engine.py`
- `tools/shell.py`
- `data/memory/facts.json`

## Recommended Enhancement

*Auto-Rollback on Drift Detection:* It is highly recommended to implement an automatic rollback mechanism via `git reset --hard HEAD` and `git clean -fd` if `guardian_engine.py` detects a baseline drift violation, ensuring the system instantaneously reverts to a known safe state without human intervention.
