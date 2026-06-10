🚀 MEGA-TASK: NINA Throughput Maximizer (v2.0 Architecture) Assignee: Jules (Async Cloud Coder)
Objective: Transform ninaflash and NinaGate into a high-velocity, low-cost autonomous control plane that reduces cloud token usage by 90% and accelerates feature delivery by 10x.

🏗️ Domain 1: NinaGate "Fast-Path" & Local Drafting Engine Leverage NinaGate to move boilerplate and scaffolding from Cloud to Local AI.

    Local Fast-Path Routing: Add a local_fast model category to NinaGate. Route specifically to qwen2.5-coder:1.5b or deepseek-coder:1.3b on Ollama for instant local inference.
    Boilerplate Scaffolding: Implement nf draft. Use local Jinja2 templates + Local Fast-Path AI to generate NINA-style tool stubs and class structures for free.
    Local Syntax Fixer: Create a local hook that catches common Python syntax errors (missing imports, indentations) and uses the Local Fast-Path AI to fix them locally before a cloud turn is wasted.
    Commit Message Autogen: Add nf gen-commit. Analyzes git diff via NinaGate to generate structured, professional commit messages.
    Docstring Engine: Automatically populate missing docstrings in newly created files using local tiny-models.

🧠 Domain 2: Autonomous Governance & Self-Healing Move repository maintenance from "Manual Quests" to "Autonomous Tasks."

    Governance Task Feed: Update tools/generate_dashboard.py to output data/governance_tasks.json. Every "Missing Test" or "Low Metadata" entry is now an executable task object.
    IdleLoop Integration: Configure idleloop.py to consume the Task Feed. NINA now heals her own metadata and writes missing tests when idle.
    Repro Script Factory: When pytest fails, nf uses NinaGate to write a standalone bin/repro_fail_X.py script. The cloud agent's goal shifts from "fix bug" to "fix script."
    Dependency Self-Healer: Catch ModuleNotFoundError during local runs; nf automatically cross-references requirements.txt and runs pip install in the venv.
    Auto-Archiver: Automatically move files flagged as purge_candidate by the index into exports/archive/ after a 30-day window.

📉 Domain 3: Context Engineering & Token Compression Stop sending "Noise" to the cloud. Send only the "Signal."

    Context Distillation: Create nf distill
    The Bitmask Index: Generate a tiny, token-optimized version of nina_index.json containing only governed files and their guardrails.
    Task Sandboxing (Workbench): nf workbench --task F-06. Creates a transient directory of symlinks to ONLY the files relevant to the task (via dependency mapping).
    Virtual Governance Headers: Modify tools/files.py (read tool). When an agent reads a file, prepend a virtual header: # GOVERNANCE: ROLE=SOT, GUARDRAILS=APPEND_ONLY.
    Incremental Log Summarizer: Instead of full logs, nf provides a 10-line summary of the last 100 log entries using NinaGate.

🛡️ Domain 4: Decision Engine & Safety Rails Turn the index from a list of files into a "Rules of Engagement" enforcement engine.

    Workflow Compression (nf wrap): Consolidate update_index, validate, cleanup, dashboard, and sync into one high-level command.
    Semantic Relationship Mapping: Enhance query_index.py to show dependencies (e.g., "File X is used by Tool Y").
    Policy-Based Blocking: If a cloud agent attempts to write to a read_only_for_agents file, nf kills the task locally and immediately.
    Metadata Quality Scoring (Target: 95%): Add stricter scoring in validate_index.py that fails the build if new files lack summaries.
    Security Sandbox: nf runs bandit security scans automatically on every local modification.

📡 Domain 5: Visibility & Performance Watchdog Make NINA proactive in reporting her own health and speed.

    Proactive Telegram Governance Bot: NINA pings the user if hygiene metrics drop or if an autonomous task fails local validation.
    Performance Regression Watcher: Benchmark core functions (Router latency, Memory fetch time) after every merge. Flag regressions.
    Log Memory (ChromaDB): Index nina_update_log.md into NINA's vector memory so agents can "recall" previous fixes.
    Throughput Dashboard: Add a "Throughput" section to the Governance Dashboard tracking "Tasks Closed per Week" and "Tokens Saved via Local Drafting."
    Weekly Hygiene Report: Automated Sunday summary of repo drift and stale files sent via Telegram.

📝 Acceptance Criteria for Jules:

    Local Execution: All generation must use http://localhost:8765 (NinaGate).
    Governance: Every new tool/script must be indexed and have a doc_delta_required: true flag.
    Tests: Provide unit tests for each new nf command.
    Documentation: Update nina_update_log.md with an entry for every module completed.

Jules, you are cleared to proceed. This is a multi-file, multi-subsystem feature. Begin with Domain 1 (Fast-Path & Drafting) to establish the infrastructure for the rest of the work.
