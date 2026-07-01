# NINA Task Routing Policy — agy vs. Jules Auto-Decision
## Phase I | Risk: LOW | Version: 1.0.0 | Date: 2026-06-18

This document outlines the self-routing policy matrix utilized by NINA agents (`agy` and `Jules`) to distribute, coordinate, and execute backlog tasks. Routing is optimized to prioritize safety, local resource preservation, parallel throughput, and strict repository compliance.

---

## 📋 1. Routing Policy Decision Matrix

### 💻 ROUTE TO agy (Local Execution) IF:
- The task creates **new files only** (no edits to existing core logic files).
- The scope is very small and contained (**1–3 files maximum**).
- The risk profile is **LOW**.
- No protected files listed in `AGENTS.md` are involved.
- The task covers pure documentation, configuration, standard testing setup, or new adapter definitions.

### 🤖 ROUTE TO JULES (Google Cloud VM Execution) IF:
- The task edits or extends **existing modules with >200 lines**.
- The risk profile is **MEDIUM or HIGH**.
- The task modifies existing files inside `core/` or `tools/`.
- The task requires executing the **full test suite** for rigorous PR validation before integration.
- The task belongs to the `SAND` (subshell/UNIX resource limiters) or `PERF` (programmatic compiler helpers) pillars where sandbox and compiler isolation are required.

### 🧑‍💻 ESCALATE TO HUMAN (Faridpur/Dhaka Operations Control) IF:
- The task touches any protected file specified in `AGENTS.md` (`.env`, `core/router.py`, `core/nina.py`, `tools/shell.py`, `main.py`, `guardian_engine.py`, `interfaces/telegram_interface.py`, `ninagate/main.py`).
- The risk level is explicitly flagged as `ESCALATE_REQUIRED` or logically contradictory.
- The task requires provisioning private API tokens, authentication codes, or destructive operations.

---

## ⛓️ 2. Routing Decisions for the 10 Remaining Phase I Backlog Tasks

Based on the criteria above, the remaining 10 tasks in the Phase I backlog have been evaluated and routed:

| Task ID | Task Title | Routed To | Decision Rationale |
| :--- | :--- | :---: | :--- |
| **`OBS-001`** | Implement Standalone Provider Health Observability Tracker | **`agy`** | New file only; no modifications to existing modules. Low risk. |
| **`VAULT-002`** | Secure Getter Integration and Env Masking | **`Jules`** | Edits existing `core/vault.py` module; requires isolated validation. |
| **`VAULT-003`** | Wire Scoped Vault Loader to Config Registry | **`Jules`** | Chained dependency risk. Modifies config/binding behaviors. |
| **`OMNI-002`** | Build Standalone TUI Channel Mock Adapter | **`Jules`** | Extends base adapter classes; edits existing adapter systems. |
| **`OMNI-003`** | Standardize Message Parser and Dispatcher Adapter | **`Jules`** | Downstream dependency on TUI Mock; requires integration PR gates. |
| **`PERF-002`** | Develop Speed-Optimized Regex Matching Registry | **`agy`** | Creates new helper caching utilities without touching existing core logic. |
| **`PERF-003`** | Optimise AST Token count Parser with Caching | **`Jules`** | Edits compiled hotpaths; requires VM sandbox test runs. |
| **`SAND-001`** | Implement Safe Subshell Subprocess Resource Guard | **`Jules`** | Subshell sandboxing and UNIX resource limitation; high execution risk. |
| **`SAND-002`** | Build Environment Variable Stripper and Guard | **`Jules`** | Extends complex subshell modules; high-dependency. |
| **`SAND-003`** | Create Sandboxed Exec Wrapper for Command Runs | **`Jules`** | Final sandbox orchestrator integration; highest execution risk. |

---

## ⚙️ 3. Execution Directives
- **`agy`** shall execute `OBS-001` and `PERF-002` immediately.
- **`Jules`** shall receive parallel dispatch prompts for `VAULT-002` and `SAND-001` through the cloud VM API to initiate automated PR reviews.
