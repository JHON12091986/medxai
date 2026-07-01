#!/usr/bin/env python3
"""NINA Repository Index Generator — Single Source of Truth v15.2

Permanent, idempotent, self-healing. Run: python3 tools/update_index.py
Also invoked by pre-push hook automatically.

Design principles:
  - HARDCODED_METADATA is the canonical reason-for-existence registry
  - GENERATED_AUTO_FILES are pre-seeded BEFORE filesystem walk so symlinks
    and generated files always appear in index even when not on disk
  - AST-extraction fills summaries for any file not in registry
  - Stale index entries (file deleted) are auto-removed
  - New files are auto-discovered and added
  - Symlinks resolved to canonical target — no duplicate entries
  - Generated/volatile files excluded from broken-link errors
  - Idempotent: N runs → identical output

v15.2 fix: REPO_ROOT injected into sys.path so 'import tools.X' always
  resolves regardless of CWD or invocation method (hook, CLI, IDE).
"""

import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# PERMANENT FIX: ensure repo root is on sys.path so 'import tools.X' works
# whether this file is invoked as a script, via hook, or as a module.
_REPO_ROOT_FOR_SYSPATH = Path(__file__).parent.parent.resolve()
if str(_REPO_ROOT_FOR_SYSPATH) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_SYSPATH))

REPO_ROOT = _REPO_ROOT_FOR_SYSPATH
INDEX_JSON = REPO_ROOT / "docs/space/nina_index.json"
INDEX_MD = REPO_ROOT / "docs/space/nina_index.md"

# ---------------------------------------------------------------------------
# FILES THAT ARE AUTO-GENERATED OR SYMLINKS — never cause broken-link errors.
# Pre-seeded into the index before the filesystem walk.
# ---------------------------------------------------------------------------
GENERATED_AUTO_FILES = {
    "data/graphs/nina_context_graph.json",
    "tools/docs/generated/nina_commit_index.md",
    "data/dependency_graph.json",
    "data/symbol_map.json",
    "nina_codemap.json",
    "tools/nina_codemap.json",
    "CODEBASE_MAP.md",
    "REPO_MAP.md",
    # Symlinks — targets may not exist on disk; pre-seed so walk never drops them
    "tools/AGENTS.md",
    "tools/GEMINI.md",
    # New governed files not yet in discovery walk
    "docs/context/NINA_AGENT_PRIMER.md",
    "docs/context/NINA_RULES.md",
    "docs/context/NINA_WORKFLOW.md",
    "docs/context/NINA_OPS.md",
    "bin/nina-universal-wrapper.sh",
}

# ---------------------------------------------------------------------------
# CANONICAL METADATA — reason for existence, role, and owner for every key file
# ---------------------------------------------------------------------------
HARDCODED_METADATA: dict[str, dict] = {
    # ── Root docs ────────────────────────────────────────────────────────────────────────
    "README.md":                    {"role": "source_of_truth", "origin": "manual",  "summary": "Human-facing project overview, agent model, installation guide."},
    "ARCHITECTURE.md":              {"role": "source_of_truth", "origin": "manual",  "summary": "High-level system design and OODA/Guardian logic flow map."},
    "CHANGELOG.md":                 {"role": "source_of_truth", "origin": "manual",  "summary": "User-friendly summary of major version releases."},
    "AGENTS.md":                    {"role": "source_of_truth", "origin": "manual",  "summary": "Agent Operating Law — permissions and scopes for Jules, agy, Gemini."},
    "GEMINI.md":                    {"role": "source_of_truth", "origin": "manual",  "summary": "Gemini agent instructions and context injection profile."},
    "nina_context.md":              {"role": "system_of_record","origin": "manual",  "summary": "AI session grounding profile; attach to every new thread."},
    "nina_update_log.md":           {"role": "system_of_record","origin": "manual",  "summary": "Human-maintained changelog of architectural decisions and fixes."},
    "jules_lock.txt":               {"role": "system_of_record","origin": "guardian","summary": "Jules scope lock — prevents concurrent task collisions."},
    "opencode.json":                {"role": "config",           "origin": "manual",  "summary": "OpenCode IDE configuration for NINA workspace."},
    "telemetry.jsonl":              {"role": "derived",          "origin": "runtime", "summary": "Runtime telemetry stream; ephemeral, not committed.", "lifecycle": "generated"},
    # ── Symlinks (targets may be missing on disk — pre-seeded) ───────────────────
    "tools/AGENTS.md":              {"role": "source_of_truth", "origin": "manual",  "summary": "Symlink → root AGENTS.md — agent scope law for tools context."},
    "tools/GEMINI.md":              {"role": "source_of_truth", "origin": "manual",  "summary": "Symlink → root GEMINI.md — Gemini agent context for tools dir."},
    # ── docs/context/ ───────────────────────────────────────────────────────────────────
    "docs/context/NINA_AGENT_PRIMER.md": {"role": "source_of_truth", "origin": "manual", "summary": "Agent primer — onboarding context for new AI agent sessions."},
    "docs/context/NINA_RULES.md":        {"role": "source_of_truth", "origin": "manual", "summary": "NINA operating rules — immutable constraints for all agents."},
    "docs/context/NINA_WORKFLOW.md":     {"role": "source_of_truth", "origin": "manual", "summary": "NINA workflow guide — task lifecycle from intake to completion."},
    "docs/context/NINA_OPS.md":          {"role": "source_of_truth", "origin": "manual", "summary": "NINA ops manual — service management, restart, and recovery."},
    # ── bin/ ──────────────────────────────────────────────────────────────────────────────
    "bin/nina-universal-wrapper.sh":     {"role": "source_of_truth", "origin": "manual", "summary": "Universal CLI wrapper — routes nina commands to correct venv/service."},
    # ── docs/space ──────────────────────────────────────────────────────────────────────
    "docs/space/nina_index.json":   {"role": "system_of_record","origin": "script:update_index", "summary": "Machine-readable governance index — SSoT for all files."},
    "docs/space/nina_index.md":     {"role": "system_of_record","origin": "script:update_index", "summary": "Human-readable governance index generated from nina_index.json."},
    "docs/space/nina_state.md":     {"role": "source_of_truth", "origin": "manual",  "summary": "Subsystem deep-dives: Guardian, Memory, Router, ninaflash."},
    "docs/space/nina_error_register.md": {"role": "system_of_record", "origin": "manual", "summary": "Canonical error register — every known error with diagnosis and resolution."},
    "docs/space/jules_backlog.md":  {"role": "system_of_record","origin": "manual",  "summary": "Jules task backlog — pending implementation work items."},
    "docs/space/nina_megatask_index.md": {"role": "source_of_truth","origin": "manual", "summary": "Indexed list of all NINA megatasks with status."},
    "docs/nina_v14_blueprint.md":   {"role": "source_of_truth", "origin": "manual",  "summary": "Canonical v14 system blueprint and component map."},
    # ── CODEBASE_MAP (generated) ────────────────────────────────────────────────────────
    "CODEBASE_MAP.md":              {"role": "generated",        "origin": "script:generate_codemap", "summary": "Auto-generated codebase map with SSoT status and duplicate detection.", "lifecycle": "generated"},
    "REPO_MAP.md":                  {"role": "generated",        "origin": "script:generate_codemap", "summary": "Legacy alias — superseded by CODEBASE_MAP.md.", "lifecycle": "deprecated"},
    # ── core/ ────────────────────────────────────────────────────────────────────────────
    "core/router.py":               {"role": "source_of_truth", "origin": "manual",  "summary": "Central intent router — maps incoming requests to correct tool/agent."},
    "core/dispatcher.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "Task dispatcher — queues and routes tasks to executor workers."},
    "core/executor.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "Async task executor — runs tool calls and manages timeouts."},
    "core/memory.py":               {"role": "source_of_truth", "origin": "manual",  "summary": "Memory subsystem — read/write to NINA facts and context store."},
    "core/context_gate.py":         {"role": "source_of_truth", "origin": "manual",  "summary": "Context gate — validates context budget before expensive tool calls."},
    "core/task_lock.py":            {"role": "source_of_truth", "origin": "manual",  "summary": "Task lock manager — prevents duplicate concurrent task execution."},
    "core/task_spec.py":            {"role": "source_of_truth", "origin": "manual",  "summary": "Task specification dataclass — canonical schema for all tasks."},
    "core/task_dag.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "DAG-based task graph — manages dependencies between tasks."},
    "core/quota_tracker.py":        {"role": "source_of_truth", "origin": "manual",  "summary": "API quota tracker — enforces per-provider rate limits."},
    "core/output_validator.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "Output validator — schema-checks tool outputs before commit."},
    "core/prompt_compressor.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Prompt compressor — reduces token usage via semantic summarization."},
    "core/watcher.py":              {"role": "source_of_truth", "origin": "manual",  "summary": "File watcher — triggers OODA observe phase on repo changes."},
    "core/per_loop.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "PER learning loop — Post-Event Review accumulates lessons."},
    # ── tools/ ───────────────────────────────────────────────────────────────────────────
    "tools/guardian_engine.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "Guardian Engine — OODA health monitor, circuit breaker, self-repair core."},
    "tools/nina_ooda.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "OODA loop driver — Observe/Orient/Decide/Act cycle orchestration."},
    "tools/nina_sync.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "Sync orchestrator — coordinates git pull/push and service restarts."},
    "tools/merge_resolver.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Merge conflict resolver — auto-resolves known conflict patterns."},
    "tools/jules.py":               {"role": "source_of_truth", "origin": "manual",  "summary": "Jules integration — task spec to Jules API bridge and response parser."},
    "tools/ninaflash.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash entry point — dispatches flash-mode LLM tasks."},
    "tools/ninaflash_core.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash core — streaming response handler and token accounting."},
    "tools/ninaflash_code.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash code mode — code generation and edit application."},
    "tools/ninaflash_context.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash context builder — injects repo context into flash prompts."},
    "tools/ninaflash_guard.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash guard — validates outputs before applying code changes."},
    "tools/ninaflash_backlog.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash backlog — queues deferred flash tasks for later execution."},
    "tools/ninaflash_bench.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash benchmark harness — measures latency and quality."},
    "tools/ninaflash_memory.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "ninaflash memory accessor — reads/writes session facts during flash."},
    "tools/update_index.py":        {"role": "source_of_truth", "origin": "manual",  "summary": "THIS FILE — idempotent index generator v15.2, SSoT for all file metadata."},
    "tools/validate_index.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Governance validator v16 — checks index integrity before git push."},
    "tools/generate_codemap.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Generates CODEBASE_MAP.md with AST-based status and duplicate detection."},
    "tools/generate_dashboard.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Generates HTML dashboard for NINA system health overview."},
    "tools/nina_context_graph.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Builds the context graph: nodes=files, edges=imports/calls."},
    "tools/nina_commit_index.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Generates nina_commit_index.md from git log for agent context."},
    "tools/nina_wiring_audit.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Wiring audit — checks all service/import references resolve correctly."},
    "tools/nina_token_guard.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Token guard — enforces per-call and daily token budgets."},
    "tools/nina_debug.py":          {"role": "source_of_truth", "origin": "manual",  "summary": "Debug utility — traces OODA decisions and logs diagnostic snapshots."},
    "tools/nina_dashboard.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Live dashboard renderer — terminal UI for NINA subsystem status."},
    "tools/nina_hud.py":            {"role": "source_of_truth", "origin": "manual",  "summary": "HUD overlay — compact status line for tmux/terminal integration."},
    "tools/nina_env_sync.py":       {"role": "source_of_truth", "origin": "manual",  "summary": "Environment sync — validates .env keys against required config schema."},
    "tools/nina_proxy.py":          {"role": "source_of_truth", "origin": "manual",  "summary": "Proxy layer — routes external API calls through rate-limit middleware."},
    "tools/nina_mcp_server.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "MCP server entry point — exposes NINA tools via Model Context Protocol."},
    "tools/nina_cicd.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "CI/CD integration — triggers and monitors GitHub Actions workflows."},
    "tools/gemini_perf.py":         {"role": "source_of_truth", "origin": "manual",  "summary": "Gemini performance profiler — benchmarks Flash/Pro latency and quality."},
    "tools/gemini_watch.py":        {"role": "source_of_truth", "origin": "manual",  "summary": "Gemini file watcher — re-runs Gemini analysis on changed files."},
    "tools/gen_claude_feed.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "Generates Claude context feed from repo state for session priming."},
    "tools/audit_repo_hygiene.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Repo hygiene auditor — finds dead code, orphan files, naming violations."},
    "tools/ast_cache.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "AST cache — memoizes parsed ASTs to speed up multi-pass analysis."},
    "tools/compact_exporter.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Compact exporter — serializes NINA state to minimal JSON for agents."},
    "tools/ninacontextpress.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Context compressor — removes redundant context before LLM submission."},
    "tools/dependency_mapper.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Dependency mapper — builds import graph for all Python modules."},
    "tools/error_register_sync.py": {"role": "source_of_truth", "origin": "manual",  "summary": "Syncs nina_error_register.md entries with context graph error nodes."},
    "tools/evolve.py":              {"role": "source_of_truth", "origin": "manual",  "summary": "Evolutionary optimizer — A/B tests prompt variants and tracks wins."},
    "tools/cleanup_by_index.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Index-driven cleanup — removes files marked deprecated in the index."},
    "tools/doc_autogen.py":         {"role": "source_of_truth", "origin": "manual",  "summary": "Auto-generates docstrings for undocumented functions via LLM."},
    "tools/debug_utility.py":       {"role": "source_of_truth", "origin": "manual",  "summary": "General debug utility — pretty-prints NINA data structures."},
    "tools/enforce_type_hints.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Enforces type hints across codebase; flags untyped function signatures."},
    "tools/context_pruner.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Context pruner — removes low-relevance entries from agent context."},
    "tools/benchmark_routing.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Benchmarks router decision latency across intent categories."},
    "tools/model_discovery.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "Discovers available models across providers and updates config."},
    "tools/market.py":              {"role": "source_of_truth", "origin": "manual",  "summary": "Market data tool — fetches price/news for NINA finance commands."},
    "tools/finance.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "Finance tool — portfolio tracking and bank statement parsing."},
    "tools/monitor.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "System monitor — CPU/RAM/disk metrics for health check."},
    "tools/live_monitor.py":        {"role": "source_of_truth", "origin": "manual",  "summary": "Live system monitor — real-time terminal display of resource usage."},
    "tools/hardware_check.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Hardware checker — validates GPU/CPU/disk for NINA workload requirements."},
    "tools/heartbeat.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "Heartbeat emitter — pings Telegram when NINA services are alive."},
    "tools/alert_beep.py":          {"role": "source_of_truth", "origin": "manual",  "summary": "Alert beeper — plays audio notification on critical events."},
    "tools/append_log.py":          {"role": "source_of_truth", "origin": "manual",  "summary": "Append-only log writer — thread-safe structured log helper."},
    "tools/browser.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "Browser tool — fetches and extracts text from URLs for research."},
    "tools/files.py":               {"role": "source_of_truth", "origin": "manual",  "summary": "File operations tool — read/write/list with path safety checks."},
    "tools/git_ops.py":             {"role": "source_of_truth", "origin": "manual",  "summary": "Git operations helper — commit, push, branch, diff wrappers."},
    "tools/create_pr.py":           {"role": "source_of_truth", "origin": "manual",  "summary": "PR creator — opens GitHub PRs from task specs via API."},
    "tools/compile_extensions.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Compiles C extension modules for performance-critical NINA components."},
    "tools/_fix_all.py":            {"role": "source_of_truth", "origin": "manual",  "summary": "Batch fixer — runs all lint/type/format corrections in one pass."},
    "tools/agy_quota_monitor.sh":   {"role": "source_of_truth", "origin": "manual",  "summary": "Shell monitor for agy API quota — alerts on threshold breach."},
    "tools/gemini_scoped.sh":       {"role": "source_of_truth", "origin": "manual",  "summary": "Scoped Gemini runner — executes Gemini with repo file scope limit."},
    "tools/gemini_wrapper.sh":      {"role": "source_of_truth", "origin": "manual",  "summary": "Gemini CLI wrapper — normalizes flags and injects NINA context."},
    # ── scripts/ ─────────────────────────────────────────────────────────────────────────
    "scripts/nina_sync.sh":         {"role": "source_of_truth", "origin": "manual",  "summary": "Master sync script — git pull/rebase, service restart, index regen."},
    "scripts/gen_codemap.sh":       {"role": "source_of_truth", "origin": "manual",  "summary": "Shell wrapper to regenerate CODEBASE_MAP.md."},
    "scripts/deploy_services.sh":   {"role": "source_of_truth", "origin": "manual",  "summary": "Deploys systemd --user services for nina.service and ninajulesgithub.service."},
    # ── tests/ ─────────────────────────────────────────────────────────────────────────
    "tests/test_task_lock.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Tests TaskLock — concurrent lock/release and timeout behaviour."},
    "tests/test_task_spec.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Tests TaskSpec schema validation and serialization."},
    "tests/test_cli.py":            {"role": "source_of_truth", "origin": "manual",  "summary": "Tests NINA CLI entry point commands."},
    "tests/test_async_shell.py":    {"role": "source_of_truth", "origin": "manual",  "summary": "Tests async shell executor — timeout, stderr capture."},
    "tests/test_context_gate.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Tests ContextGate token budget enforcement."},
    "tests/test_nina_ooda.py":      {"role": "source_of_truth", "origin": "manual",  "summary": "Tests OODA loop observe/orient/decide/act phases."},
    "tests/test_queue.py":          {"role": "source_of_truth", "origin": "manual",  "summary": "Tests task queue ordering, priority, and dequeue."},
    "tests/test_output_validator.py":{"role": "source_of_truth","origin": "manual",  "summary": "Tests OutputValidator schema checks and rejection paths."},
    "tests/test_agy_briefing.py":   {"role": "source_of_truth", "origin": "manual",  "summary": "Tests agy briefing generator output format."},
    "tests/test_seed_from_slots.py":{"role": "source_of_truth", "origin": "manual",  "summary": "Tests slot-seeding for context graph initialization."},
    "tests/test_per_loop.py":       {"role": "source_of_truth", "origin": "manual",  "summary": "Tests PER (Post-Event Review) lesson accumulation."},
    "tests/test_watcher.py":        {"role": "source_of_truth", "origin": "manual",  "summary": "Tests file watcher event detection and debouncing."},
    "tests/test_dispatcher.py":     {"role": "source_of_truth", "origin": "manual",  "summary": "Tests dispatcher task routing and worker assignment."},
    "tests/test_guardian_engine.py":{"role": "source_of_truth", "origin": "manual",  "summary": "Tests GuardianEngine health checks and self-repair triggers."},
    "tests/test_quota_tracker.py":  {"role": "source_of_truth", "origin": "manual",  "summary": "Tests QuotaTracker rate limit enforcement and reset."},
    "tests/test_task_dag.py":       {"role": "source_of_truth", "origin": "manual",  "summary": "Tests TaskDAG dependency resolution and cycle detection."},
    "tests/test_prompt_compressor.py":{"role":"source_of_truth","origin": "manual",  "summary": "Tests PromptCompressor reduction ratio and semantic fidelity."},
    # ── data/ ─────────────────────────────────────────────────────────────────────────────
    "data/graphs/nina_context_graph.json": {"role": "generated", "origin": "script:nina_context_graph", "summary": "Auto-generated context graph — nodes mapping file relationships.", "lifecycle": "generated"},
    "data/memory/facts.json":       {"role": "system_of_record","origin": "runtime", "summary": "Persistent facts store — long-term memory for NINA session continuity."},
    "data/dependency_graph.json":   {"role": "generated",        "origin": "script:dependency_mapper", "summary": "Import dependency graph for all Python modules.", "lifecycle": "generated"},
    "data/symbol_map.json":         {"role": "generated",        "origin": "script:symbol_mapper",    "summary": "Symbol map — all exported functions/classes per module.", "lifecycle": "generated"},
    # ── perplexity/ ──────────────────────────────────────────────────────────────────────
    "perplexity/tasks/PRX-TEST-001.json": {"role": "config", "origin": "manual", "summary": "Perplexity task spec — test task for PRX integration."},
    "perplexity/tasks/test_output.txt":   {"role": "generated", "origin": "runtime", "summary": "Test output from Perplexity task run.", "lifecycle": "generated"},
}

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".agent", ".jules", "node_modules", ".aider",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".egg-info", ".so", ".DS_Store"}
EXCLUDE_NAMES = {"thumbs.db", ".gitkeep"}


def _file_hash(path: Path) -> str | None:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _ast_summary(path: Path) -> str:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
        if (isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, (ast.Constant, ast.Str))):
            doc = tree.body[0].value.s if hasattr(tree.body[0].value, 's') else tree.body[0].value.value
            return str(doc).strip().splitlines()[0][:120]
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                return f"Contains: {node.name}() — auto-discovered."
    except Exception:
        pass
    return "Auto-discovered file."


def _resolve_symlink_target(path: Path) -> str | None:
    try:
        if path.is_symlink():
            target = (path.parent / os.readlink(path)).resolve()
            return str(target.relative_to(REPO_ROOT))
    except Exception:
        pass
    return None


def _classify(rel: str) -> tuple[str, str, str, str]:
    suffix = Path(rel).suffix
    name = Path(rel).name
    if suffix == ".md":        category = "doc"
    elif suffix == ".py":      category = "code"
    elif suffix == ".sh":      category = "script"
    elif suffix == ".json":    category = "config"
    elif suffix == ".txt":     category = "config"
    elif suffix == ".toml":    category = "config"
    elif suffix in (".yaml", ".yml"): category = "config"
    else:                      category = "other"
    if rel.startswith("logs/"):              category = "log"
    elif rel.startswith("exports/"):         category = "export"
    elif rel.startswith("upgrades/backups"): category = "backup"
    elif rel.startswith("upgrades/incidents"): category = "incident"
    lifecycle = "active"
    if category in ("backup", "incident"):    lifecycle = "archived"
    elif category == "export":               lifecycle = "generated"
    elif name.endswith(".bak") or ".bak_" in name: lifecycle = "deprecated"
    elif rel in GENERATED_AUTO_FILES:        lifecycle = "generated"
    role = "source_of_truth"
    if rel in ("nina_update_log.md", "docs/space/nina_error_register.md",
               "data/memory/facts.json", "jules_lock.txt"):
        role = "system_of_record"
    elif lifecycle in ("archived", "deprecated"): role = "archive"
    elif lifecycle == "generated" or category == "export": role = "generated"
    elif category == "log":    role = "derived"
    elif category == "backup": role = "backup"
    if category == "log":      retention = "rotate"
    elif category == "backup": retention = "keep_latest_n: 10"
    elif category == "incident": retention = "purge_candidate"
    elif category == "export":   retention = "ephemeral"
    elif lifecycle == "generated": retention = "ephemeral"
    else:                        retention = "keep"
    return category, lifecycle, role, retention


def _make_entry(rel: str, full: Path | None = None) -> dict:
    """Build a single index entry from path + optional real file."""
    category, lifecycle, role, retention = _classify(rel)
    meta      = HARDCODED_METADATA.get(rel, {})
    summary   = meta.get("summary", "")
    role      = meta.get("role", role)
    origin    = meta.get("origin", "manual")
    lifecycle = meta.get("lifecycle", lifecycle)
    retention = meta.get("retention_policy", retention)
    if not summary and full and full.suffix == ".py" and full.exists() and not full.is_symlink():
        summary = _ast_summary(full)
    if not summary:
        summary = "Governed artifact."
    requires_tests = False
    if (category == "code" and lifecycle == "active" and
            full and not rel.startswith("tests/") and not rel.endswith("__init__.py")):
        if any(rel.startswith(d + "/") for d in ("core/", "tools/", "crons/", "interfaces/")):
            requires_tests = True
    return {
        "path":             rel,
        "category":         category,
        "role":             role,
        "governed":         True,
        "lifecycle":        lifecycle,
        "origin":           origin,
        "retention_policy": retention,
        "series_id":        None,
        "series_type":      None,
        "requires_tests":   requires_tests,
        "doc_required":     category == "code" and lifecycle == "active",
        "guardrails":       ["high_risk_review"] if rel in (
            "core/router.py", "tools/guardian_engine.py",
            "tools/merge_resolver.py", "tools/jules.py"
        ) else [],
        "summary":          summary,
        "hash":             _file_hash(full) if full and full.exists() and not full.is_symlink() else None,
        "tags":             list({category, lifecycle, role}),
    }


def discover_files() -> list[dict]:
    """Walk the repo and return a list of index entries.

    KEY CHANGE v15.1: GENERATED_AUTO_FILES are pre-seeded FIRST so that
    symlinks (tools/AGENTS.md, tools/GEMINI.md) and generated files always
    appear in the index even when their targets don't exist on disk.
    The filesystem walk then adds all real files, skipping any already seeded.
    """
    seen_paths: set[str] = set()
    entries: list[dict] = []

    # ─── Phase 1: Pre-seed GENERATED_AUTO_FILES (symlinks + volatile) ───────────
    for rel in sorted(GENERATED_AUTO_FILES):
        if rel in seen_paths:
            continue
        seen_paths.add(rel)
        full = REPO_ROOT / rel
        entries.append(_make_entry(rel, full if full.exists() else None))

    # ─── Phase 2: Filesystem walk for everything else ──────────────────────────
    symlink_targets: dict[str, str] = {}
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fname in files:
            full = Path(root) / fname
            rel = str(full.relative_to(REPO_ROOT))
            if full.is_symlink():
                target = _resolve_symlink_target(full)
                if target:
                    symlink_targets[rel] = target

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fname in files:
            full = Path(root) / fname
            rel = str(full.relative_to(REPO_ROOT))
            if full.suffix in EXCLUDE_SUFFIXES or full.name in EXCLUDE_NAMES:
                continue
            if rel in symlink_targets.values():
                for sl, tgt in symlink_targets.items():
                    if tgt == rel:
                        rel = sl
                        break
            if rel in seen_paths:
                continue
            seen_paths.add(rel)
            entries.append(_make_entry(rel, full))

    entries.sort(key=lambda x: x["path"])
    return entries


def generate_index():
    print("🔍 Scanning repository...")
    files = discover_files()
    print(f"✅ Discovered {len(files)} governed files.")

    index_data = {
        "version": "15.2",
        "generated_at": datetime.now().isoformat(),
        "repo": "NINA",
        "generated_by": "tools/update_index.py — permanent SSoT, idempotent v15.2",
        "files": files,
    }

    try:
        try:
            from tools.validate_index import reconcile_tests
        except ImportError:
            from validate_index import reconcile_tests
        reconcile_tests(index_data, REPO_ROOT)
    except Exception as e:
        print(f"⚠️  Test reconciliation skipped: {e}")

    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print(f"💾 Written: {INDEX_JSON.relative_to(REPO_ROOT)}")

    md_lines = [
        "# NINA Repository Index",
        "_SSoT — auto-generated by `tools/update_index.py` v15.2. Do not edit manually._",
        "",
        f"**Version:** {index_data['version']}  ",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Total files:** {len(files)}  ",
        "",
        "## File Inventory",
        "| Path | Role | Lifecycle | Summary |",
        "|------|------|-----------|---------|",
    ]
    for f in files:
        md_lines.append(
            f"| `{f['path']}` | {f['role']} | {f['lifecycle']} | {f['summary'][:80]} |"
        )
    md_lines += [
        "",
        "---",
        f"_Generated by `tools/update_index.py` v15.2 on {datetime.now().strftime('%Y-%m-%d')}_",
    ]
    INDEX_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"💾 Written: {INDEX_MD.relative_to(REPO_ROOT)}")

    for module_name, func_name, output_path, label in [
        ("tools.dependency_mapper", "generate_dependency_graph", REPO_ROOT / "data/dependency_graph.json", "Dependency graph"),
        ("tools.symbol_mapper",     "generate_symbol_map",       REPO_ROOT / "data/symbol_map.json",       "Symbol map"),
    ]:
        try:
            mod = __import__(module_name, fromlist=[func_name])
            result = getattr(mod, func_name)(REPO_ROOT)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"✅ {label} updated: {output_path.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"⚠️  {label} skipped: {e}")

    print("\n✅ Index generation complete (idempotent, SSoT v15.2).")
    return index_data


if __name__ == "__main__":
    generate_index()
