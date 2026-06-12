# TASK: NINA Observability & Memory Upgrade v4.0 (The NINA-Evolve Protocol)

## 0. OBJECTIVE: AUTONOMOUS SELF-OPTIMIZATION
*Goal: Create a self-reinforcing "Vicious Cycle" where NINA monitors its performance, identifies bottlenecks, proposes upgrades, and autonomously implements them.*

## 1. PHASE 1: THE PERFORMANCE ANALYTIC LAYER (SENSE)
- **Deep Metrics Engine:** Enhance `tools/monitor.py` to calculate:
  - **Token Savings:** (Estimated Baseline Cloud Tokens) - (Actual Cloud Tokens Used).
  - **Time Efficiency:** (Sequential Execution Time) - (Parallel Execution Time).
  - **Throughput Rank:** Requests per minute handled locally vs. cloud.
- **Efficiency Baseline:** Establish a "Plain Gemini CLI" baseline to measure improvement.

## 2. PHASE 2: THE AUTONOMOUS FEEDBACK LOOP (THINK)
- **Bottleneck Identifier:** Create `tools/evolve.py` to analyze `logs/ninagate.log` and `logs/router.log` for:
  - Frequent cloud escalations that *could* have been local (OFFLOAD_OPPORTUNITY).
  - High-latency tool calls.
  - Repetitive mechanical tasks.
- **Improvement Proposals:** Every 10 tasks, the engine must generate an `EVOLVE_PROPOSAL.md` with specific code or configuration upgrades.

## 3. PHASE 3: AUTONOMOUS IMPLEMENTATION (ACT)
- **Self-Upgrade Pipeline:** When an `EVOLVE_PROPOSAL.md` is generated, NINA must:
  - Create a temporary branch.
  - Apply the proposed optimization (e.g., refactoring a tool for better parallelism).
  - Run the `test/smoke.py` and `test/performance.py` suites.
  - If tests pass and metrics improve, merge the upgrade.
- **Incremental Documentation:** For every upgrade, autonomously update `ARCHITECTURE.md` and `CHANGELOG.md` to reflect the new system state.

## 4. PHASE 4: THE VICIOUS CYCLE (EVOLVE)
- **Recursive Learning:** The system must treat its own code as a subject for continuous "Surgical Surgery."
- **Fact Persistence:** The learnings from each optimization cycle must be appended to `AGENTS.md` and the `MEMORY.md` index to prevent regressing on efficiency.

## 5. ARCHITECTURAL MANDATES
- **Closed-Loop:** The cycle must run without user intervention (Sense -> Think -> Act -> Document -> Repeat).
- **Safety First:** Self-upgrades MUST be validated by the `Verifier` and never bypass the `pyflakes`/`py_compile` gates.
- **Metrics-Driven:** No upgrade is merged unless it proves a >5% improvement in time or token efficiency.

## 6. ACCEPTANCE CRITERIA
1. NINA generates an `efficiency_report.json` after every session.
2. The system autonomously identifies and fixes at least one latency bottleneck per cycle.
3. `ARCHITECTURE.md` is updated incrementally with every self-implemented feature.
4. The dashboard shows a "System Evolution" score (cumulative efficiency gains).
