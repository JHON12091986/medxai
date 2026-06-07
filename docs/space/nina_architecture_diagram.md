# NINA Architecture Diagram

This document details the core architecture and operational flow of the NINA system (v12).

## High-Level System Architecture

```ascii
                      +-------------------------------------------------+
                      |                Telegram Interface               |
                      |          (interfaces/telegram_interface.py)     |
                      |  - Receives user input                          |
                      |  - Sends markdown formatted replies             |
                      |  - Handles commands (/ask, /task, /shell, etc)  |
                      +-----------------------+-------------------------+
                                              |
                                              v
                      +-----------------------+-------------------------+
                      |                   NinaOS (Core)                 |
                      |                 (core/nina.py)                  |
                      |  - Orchestrator for all sub-systems             |
                      |  - Manages startup, shutdown, lock              |
                      +---+-------------------+---------------------+---+
                          |                   |                     |
          +---------------+                   |                     +-----------------+
          |                                   |                                       |
+---------v---------+               +---------v---------+                   +---------v---------+
|   MemorySystem    |               |    AgentLoop      |                   |   TaskScheduler   |
| (core/memory.py)  |               |  (core/agent.py)  |                   |  (crons/manager)  |
| - ChromaDB facts  | <-----------> | - THINK/PLAN/ACT  |                   | - APScheduler     |
| - JSON reminders  |               | - Thermal guards  |                   | - Reminder checks |
| - Context builder |               | - Task budget     |                   | - Daily reports   |
+-------------------+               +----+----+----+----+                   +-------------------+
                                         |    |    |
                   +---------------------+    |    +---------------------+
                   |                          |                          |
                   v                          v                          v
         +-------------------+      +-------------------+      +-------------------+
         |    Tools Dict     |      |   HybridRouter    |      |  UpgradePipeline  |
         | (tools/*.py)      |      | (core/router.py)  |      | - Idle updates    |
         | - shell, web,     |      | - Provider health |      | - Self-patching   |
         | - system, browser |      | - Rate limits     |      +-------------------+
         | - jules           |      | - Cost tracking   |
         +-------------------+      +---------+---------+
                                              |
                                              v
                                    +-------------------+
                                    |    Providers      |
                                    | - LOCALFAST       |
                                    | - Cloud (Tier 1-3)|
                                    +-------------------+
```

## The Agent Loop (THINK -> PLAN -> ACT -> OBSERVE)

```ascii
+-----------------------+
|  User Goal Received   |
+-----------+-----------+
            |
            v
+-----------+-----------+       +-------------------+
| System Frame Injected | ----> |   Memory Context  |
| (Goal + Rules)        | <---- |   (ChromaDB)      |
+-----------+-----------+       +-------------------+
            |
            v
+-----------+-----------+
|      Step Loop        | <------------------------------------+
| (Up to task budget)   |                                      |
+-----------+-----------+                                      |
            |                                                  |
            v                                                  |
+-----------+-----------+       +-------------------+          |
|    Hybrid Router      | ----> |   Model Provider  |          |
|   (Route request)     | <---- |   (Response)      |          |
+-----------+-----------+       +-------------------+          |
            |                                                  |
            +------------------------------------+             |
            |                                    |             |
            v                                    v             |
+-----------+-----------+              +---------+---------+   |
|   Response Analysis   |              |  Response Analysis|   |
|   Contains "TOOL:"?   |              | Contains "FINAL:"?|   |
+-----------+-----------+              +---------+---------+   |
            |                                    |             |
            v (Yes)                              v (Yes)       |
+-----------+-----------+              +---------+---------+   |
|    Execute Tool       |              |    Self-Check     |   |
| (shell, web, system)  |              | (Review accuracy) |   |
+-----------+-----------+              +---------+---------+   |
            |                                    |             |
            v                                    v             |
+-----------+-----------+              +---------+---------+   |
|   Append Output to    |              |  Return Final     |   |
|      Scratchpad       | -------------|     Answer        |   |
+-----------------------+              +-------------------+   |
            |                                                  |
            +--------------------------------------------------+
```

## Hybrid Router & Provider Selection

```ascii
+-----------------------+
|     Route Request     |
| (Prompt, Task Type)   |
+-----------+-----------+
            |
            v
+-----------+-----------+       +-------------------+
|       Cache Check     | ----> |    Return Cached  | (If hit)
|  (Prompt + Messages)  |       |      Result       |
+-----------+-----------+       +-------------------+
            | (Miss)
            v
+-----------+-----------+
|    Provider Ordering  |
| - Bangla overrides    |
| - Task sensitivity    |
| - Provider score      |
+-----------+-----------+
            |
            v
+-----------+-----------+
|    Provider Attempt   | <----------------+
| (Wait for rate limit) |                  |
+-----------+-----------+                  |
            |                              |
            +-------------------+          |
            |                   |          |
            v (Success)         v (Fail)   |
+-----------+-----------+   +---+----------+----+
|  Record Metrics &     |   |  Record Failure   |
|       Cost            |   | (Cooldown, error) |
+-----------+-----------+   +---+----------+----+
            |                   |
            v                   v
+-----------+-----------+   +---+-------------------+
|    Return Result      |   | Try Next Provider /   |
+-----------------------+   | Raise Error if Exhausted|
                            +-----------------------+
```

## Data Persistence Strategy

* **Memory (`core/memory.py`):** Uses ChromaDB for factual/historical conversations, stored locally in `data/memory/chromadb`. Reminder engine writes to JSON (`data/reminders.json`).
* **Router Cache (`core/router.py`):** Uses an in-memory dictionary caching mechanism, potentially persisted locally based on configuration.
* **Costs & Metrics:** Stored in local JSON files (e.g. `data/cost.json`, `data/metrics.json`) via explicit persistence calls.
* **Logs (`logs/*.log`):** Application logs separated by module (e.g., `agent.log`, `router.log`, `nina.log`), with daily rotation.
