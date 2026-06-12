# Jules Autonomous Pipeline — Documentation

## 1. Overview
The Jules pipeline is NINA's high-capacity autonomous engineering subsystem. It leverages Google's Jules API to perform multi-file code modifications, refactors, and feature implementations asynchronously.

## 2. Core Architecture
The system is designed for **Quota Efficiency**, **Parallelism**, and **Persistence**.

### 2.1 Process Flow
1.  **Intake**: Natural language goals are parsed by `tools/goal_intake.py` and appended to `docs/space/jules_backlog.md` as `READY` tasks.
2.  **Orchestration**: `tools/mega_orchestrator.py` runs every 3 minutes.
    *   It identifies `READY` tasks.
    *   **Mega Batching**: It bundles up to 5 non-overlapping tasks into a single Jules session to conserve the 100-session/day quota.
3.  **Dispatch**: `tools/jules_api.py` sends the bundled prompt to the Jules API.
4.  **Registration**: Upon successful dispatch, `tools/jules_registry.py` logs the Session ID (SID) and associated Task IDs into `data/jules_registry.json`.
5.  **Monitoring**: `tools/jules_watcher.py` tracks state changes. If Jules asks a question, it notifies the user via Telegram.
6.  **Interaction**: User/Agent provides feedback via:
    *   **Telegram**: `/jules feedback <sid> <message>`
    *   **CLI**: `bin/nina jules feedback <sid> <message>`
7.  **Resolution**: Once Jules opens a PR, the Orchestrator verifies the PR and merges it concurrently using `asyncio.gather`.

## 3. File Inventory

| File | Role | Description |
| :--- | :--- | :--- |
| **Engine** | | |
| `tools/jules.py` | Unified Engine | **CONSOLIDATED.** Contains API, Registry, Watcher, and Orchestrator logic. |
| `tools/mega_orchestrator.py`| Legacy Wrapper| Triggers the orchestration cycle in `tools/jules.py`. |
| **Data & State** | | |
| `data/jules_registry.json` | Persistent DB | Tracks SID -> Task ID mappings and timestamps. |
| `docs/space/jules_backlog.md` | Task List | The canonical list of all pending and completed tasks. |
| `juleslock.txt` | Concurrency Lock | Prevents agents from colliding on the same files. |
| `data/jules_seen_activities.json`| Notification Cache | Prevents duplicate Telegram pings. |
| **Interfaces** | | |
| `interfaces/telegram_interface.py`| Telegram Bot | End-user interface for mobile control. |
| `interfaces/cli_interface.py` | CLI Tool | Terminal-based control via `bin/nina jules`. |
| **Legacy/Utilities** | | |
| `tools/jules_api.py` | (Obsolete) | Archived. Logic moved to `tools/jules.py`. |
| `tools/jules_watcher.py` | (Obsolete) | Archived. Logic moved to `tools/jules.py`. |
| `tools/jules_registry.py` | (Obsolete) | Archived. Logic moved to `tools/jules.py`. |
| `fetch_all_questions.py` | Aggregator | Integrated functionality into `tools/jules.py status`. |
| `cancel_jules_sessions.py` | Janitor | Integrated functionality into `tools/jules.py cleanup`. |

## 4. Optimization Strategies
*   **Parallelism**: PR resolution and merging are handled concurrently using `asyncio.gather`.
*   **Quota Management**: The 100/day session limit is preserved via 5-task "Mega Batches."
*   **Zero-Trace State**: The registry ensures that even if the service restarts, NINA knows exactly which Jules sessions are tied to which backlog tasks.

---
_Documented by NINA v14.3 — 2026-06-13_
