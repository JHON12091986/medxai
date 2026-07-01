# NINA vs. Hermes Agent & Multi-Level SLA Watchdog Blueprint
## Date: 2026-06-16 | Role: ARCHITECT & EXECUTOR

This blueprint reviews how NINA aligns with the key architectural principles of the **Hermes Agent** (by Nous Research) and outlines how we can adopt these techniques to enhance her capabilities. Additionally, it details a robust design for a system-wide, multi-level **Time-Bound SLA and Alerting Framework** to inject deep "time-awareness" into all tasks, subtasks, and background daemons.

---

## 1. NINA vs. Hermes Agent Alignment

| Hermes Key Advantage | NINA Alignment Status | How NINA Implements It | Future Adoption/Enhancement |
| :--- | :--- | :--- | :--- |
| **Self-Evolving Skills** | 🟡 **PARTIAL / DEBT** | Has an `/evolve` concept and capability registration (`core/capabilities.py`), but currently operates on static, pre-defined tool interfaces without an automatic self-compilation storage. | **Adopt Hermes Skill Cache:** Automatically compile optimized task execution scripts and store them in a persistent folder `tools/skills/`, dynamically registering them as tools. |
| **Persistent Memory & Curation** | 🟢 **ROBUST** | Handled via the `/remember` and `/recall` layer (`core/memory.py`). We use strict token-budget limits (3-layer context conservation) to prevent memory bloating. | **Context Distillation:** Implement a bottom-up memory pruner to routinely synthesize old conversation fragments into semantic key-value preference trees. |
| **Model Flexibility** | 🟢 **COMPLETE** | Managed by `core/router.py` (HybridRouter v4, QuotaRouter, RPMScheduler, keyless public fallbacks, and local fallback to Ollama with 0 latency). | **Tiered Routing Optimization:** No additional action needed; NINA is already highly optimized in this dimension. |
| **Long-Horizon Autonomy** | 🟢 **ROBUST** | 4 continuous systemd background services, state persistence checkpoints (`tools/session_ledger.py`), and cron-based pipeline watchdogs. | **Agent Flow Checkpoint & Resume:** Implement a checkpoint serializer in the `AgentLoop` state machine to resume execution on service restarts. |
| **Data Sovereignty** | 🟢 **COMPLETE** | Fully self-hosted on your local ASUS VivoBook (Ubuntu 26.04 LTS), running completely in your environment with local routing capability. | **Zero-Cloud Sandbox:** Standard practice already in place; secure local data storage. |

---

## 2. Adoption Proposal: Dynamic Skill Evolution

To bring NINA on par with Hermes' **Self-Evolving Skills**, we can design a **Dynamic Skill compilation loop**:

### Skill Generation Protocol
1. **Detection:** When a multi-step task achieves a near-perfect feedback score (e.g., `feedback_score >= 0.90`), the agent isolates the precise terminal sequence of commands or Python statements.
2. **Refinement:** The agent triggers an internal `synthesis` pass to compile these instructions into a single clean Python file with standard arguments.
3. **Storage:** The file is persisted in a new directory: `tools/skills/` (e.g., `tools/skills/extract_financial_ratios.py`).
4. **Registration:** The skill is written to `core/capabilities.json`. During next runs, `AgentLoop` dynamically imports and lists this skill in its available toolset, avoiding complex replanning and running significantly faster.

---

## 3. Multi-Level SLA & Time-Bound Alerting Framework

### Layer 1: Subtask/Tool-Run SLA (Micro-level)
* **Goal:** Prevent an individual sub-agent or tool from hanging indefinitely during planning or execution.
* **Target files:** `core/task_planner.py` (TaskNode), `core/swarm_engine.py` (SwarmEngine._run_node)
* **Mechanism:**
  1. Extend `TaskNode` to include `sla_seconds` attribute (default: `60`).
  2. Wrap `SwarmEngine._run_node` execution in `asyncio.wait_for(timeout=node.sla_seconds)`.
  3. On `asyncio.TimeoutError`: call `node.mark_failed(f"Subtask SLA Exceeded ({sla_seconds}s)")` and emit telemetry.

### Layer 2: Task Backlog SLA (Macro-level)
* **Goal:** Ensure dispatched backlog tasks do not stall or get forgotten.
* **Target files:** `tools/jules.py` (`check_pipeline_watchdog`), `docs/space/jules_backlog.md`
* **Mechanism:**
  1. Read task-specific deadlines from backlog table if defined (e.g., `| TASK-ID | status | SLA | ... |`).
  2. Default SLA: `120` minutes for standard tasks, `15` minutes for `TODO-P1` tasks.
  3. On violation: trigger Telegram alert immediately.

### Layer 3: Service/Daemon Heartbeat Watchdog (System-level)
* **Goal:** Inject system-wide service liveness tracking.
* **Target files:** `data/heartbeats.json` (new), `crons/manager.py` (new watchdog function), all 4 service entry points
* **Mechanism:**
  1. Each service writes its ISO timestamp to `data/heartbeats.json` every `60s`.
  2. `crons/manager.py` reads the file every `5` minutes.
  3. If any heartbeat age > `300s`: send urgent Telegram alert with service name and staleness duration.

---

## 4. Implementation Phases

| Phase | Task | Target File(s) | Priority |
|---|---|---|---|
| P1-A | Service heartbeat writer + `crons/manager.py` liveness checker | all 4 service entry points, `crons/manager.py`, `data/heartbeats.json` | HIGH |
| P1-B | `TaskNode.sla_seconds` + `SwarmEngine._run_node` asyncio timeout | `core/task_planner.py`, `core/swarm_engine.py` | HIGH |
| P2-A | `tools/skills/` evolution compiler + `core/capabilities.json` registration | `tools/skills/` (new dir), `core/capabilities.py`, `core/capabilities.json` | MEDIUM |

---
*Blueprint approved by Bostami. Jules specs generated by Perplexity ARCHITECT session 2026-06-16.*
