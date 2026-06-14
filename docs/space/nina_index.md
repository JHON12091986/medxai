# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview & Scope
This index tracks all governed artifacts in the NINA repository.
- **Governed:** true. Includes docs, tools, scripts, configs, exports, and persistent logs.
- **Unmanaged:** Excludes `__pycache__`, `.venv`, `.git`, transient temp files.

## 2. File Inventory
| Path | Role | Lifecycle | Retention | Summary | Canonical |
|------|------|-----------|-----------|---------|-----------|
| `.aider.chat.history.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.aider.input.history` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.coverage` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.env` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.env.example` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.env.save` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.geminiignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.gitignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.ninaignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `AGENTS.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ARCHITECTURE.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `CHANGELOG.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `CONTRIBUTING.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `EVOLVE_PROPOSAL.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `LICENSE` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `MEMORY.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `Makefile` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `README.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `SECURITY.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `WORKFLOW.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `agent/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `agent/context.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bench_report.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/gemini` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/install_governance.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/nf` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/nina` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/ninaflash` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `bin/ninagate` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `call_graph_test.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/cron_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/env_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/import_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/package_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/router_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/runner.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/security_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/state_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/syntax_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `checks/system_checks.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `commit_message.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/agent.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/agent_loop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/ast_refactor.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/capabilities.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/config.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/hotreload.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/logger.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/memory.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/memory_manager.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/nina.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/observability.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/router.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/task_classifier.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/task_store.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/utils.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `core/verifier.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/backup_jobs.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/evolve_loop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/manager.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/registry.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `crons/runner.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `dashboard/nina-guardian.html` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `dashboard/ninaui.html` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `dashboard/puter_architect.html` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/.guardian_hash` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/capabilities.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/circuit_state.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/deploy.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/discoveredproviders.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/gemini_preamble.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/gemini_scratch.jsonl` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/gpuconfig.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/healthcheck_registry.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/jules_auto_responded.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/jules_registry.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/jules_seen_activities.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/memory/chromadb/chroma.sqlite3` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/memory/facts.json` | system_of_record | active | keep | Governed artifact. | ✅ YES |
| `data/memory/scratchpad.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/memory/session_summaries.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/model_cache.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/modeldiscovery.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/nina.lock` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/nina.pid` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/ninagate_cache.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/ninajulesgithub.lock` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/ninatestrunner_report.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/pipeline.lock` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/plans/templates/README.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/plans/templates/daily_brief.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/plans/templates/expense_log.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/plans/templates/market_check.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/plans/templates/reminder_set.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-05-22_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-05-23_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-05-24_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-01_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-02_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-04_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-05_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-06_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-07_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-08_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-09_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-10_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-11_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-12_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-13_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/proposals/2026-06-14_proposals.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/quota_state.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/router_cache.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/session_ledger.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/session_memory.jsonl` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `data/tasks.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/gemini_perf.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/guardian.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/jules_agent_memory.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/jules_pipeline.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/memory.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/nina_proxy_usage.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/nina_v14_blueprint.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/ninaflash.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/observability.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/roadmap/nina_phase1_roadmap.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/router.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/session_ledger.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/claude_feed.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/conversation_with_nina.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/gemini_shim_spec.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/jules_backlog.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/jules_pipeline_audit.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/jules_queue.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/jules_task_tracker.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_architecture_diagram.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_architecture_spec_v1.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_error_register.md` | system_of_record | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_exporter_contract.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_governance_dashboard.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_index.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_index.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_megatask_index.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_repo_hygiene_dashboard.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/nina_state.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/ninaflash_stub.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `docs/space/ninaflash_task_tracker.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `efficiency_report.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `exports/nina_latest.md` | generated | generated | ephemeral | Governed artifact. | ✅ YES |
| `exports/nina_problem_log_archive.md` | generated | generated | ephemeral | Governed artifact. | ✅ YES |
| `fix_caps_again.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `generate_backups.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `git-hooks/pre-push` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian_engine.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `healthcheck.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `idleloop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `interfaces/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `interfaces/api.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `interfaces/cli_interface.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `interfaces/middleware.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `interfaces/telegram_interface.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `jules_backlog_full.tmp` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `logs/agent.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-05-21` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-05-22` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-05-23` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-05-24` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-06-01` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-06-04` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent.log.2026-06-05` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/agent_actions.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/emailaccess.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/error.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/gemini_wrapper.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/jules_unblock_log.txt` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.jsonl` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-07` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-08` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-09` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-10` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-11` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-12` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina.log.2026-06-13` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina_problem_log.md` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina_sync.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/nina_update_log.md` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninaflash.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninagate.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninagate_init.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninagate_stdout.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninajulesgithub.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/ninajulesgithub.log.2026-06-13` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/pr_audit_log.txt` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/router.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/router.log.2026-05-21` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/router.log.2026-05-22` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/security.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-05-24` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-04` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-05` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-08` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-09` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-12` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/tools.log.2026-06-13` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-06` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-08` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-09` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-10` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-11` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-12` | derived | active | rotate | Governed artifact. | ✅ YES |
| `logs/upgrade.log.2026-06-13` | derived | active | rotate | Governed artifact. | ✅ YES |
| `main.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_agent_final.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_nina_final.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_nina_url_parse.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_ninagate_format.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina-dashboard.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_aider.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_audit.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_cleanup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_codebase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_context.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_docbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_docs_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_logbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_sync.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_update_log.md` | system_of_record | active | keep | Governed artifact. | ✅ YES |
| `ninagate/README.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate/main.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate/ninagate.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate/providers.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate/system_templates.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate_load_test.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninagate_load_test.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninajulesgithub.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninajulesgithub.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pr_desc.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pytest.ini` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `requirements.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `scripts/gemini_monitor.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `system_templates.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `templates/dashboard.html` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `test.lock` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `test_httpx_hook.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `test_router.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/conftest.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_agent_loop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_ast_refactor.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_browser.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_capabilities.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_config.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_cron_registry.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_dispatch.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_doc_audit.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_enforce_type_hints.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_finance.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_finance_market.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_geminiignore.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_guardian.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_hotreload.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_idleloop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_integration.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_logger.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_memory.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_memory_kb.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_memory_manager.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_method_extraction.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_model_discovery.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_nina_proxy.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_nina_sync.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_ninaflash_cycles.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_ninaflash_ext.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_observability.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_router.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_shell.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_smoke.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_surgical.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_task_classifier.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_task_store.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_telegram_interface.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_telegram_interface_errors.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_telegram_interface_status.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_telegram_middleware.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_tools_hardening.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_tools_smoke.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_utils.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tests/test_verifier.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/__init__.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/alert_beep.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/append_log.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/audit_repo_hygiene.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/benchmark_routing.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/browser.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/cleanup_by_index.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/compact_exporter.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/create_pr.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/doc_autogen.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/enforce_type_hints.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/evolve.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/files.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/finance.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/gemini_perf.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/gemini_scoped.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/gemini_watch.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/gemini_wrapper.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/generate_dashboard.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/git_ops.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/jules.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/live_monitor.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/market.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/model_discovery.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/monitor.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/nina_dashboard.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/nina_mcp_server.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/nina_proxy.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/nina_sync.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninacontextpress.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_backlog.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_code.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_context.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_core.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_guard.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninaflash_memory.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/ninatestrunner.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/observable_monitor.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/office_mail.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/pipeline_autopilot.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/providerhunter.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/prune_duplicates.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/query_index.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/retry.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/rule0_audit.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/search.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/session_ledger.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/session_preamble.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/shell.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/system.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/test_gen_autopilot.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/update_index.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/upgradepipeline.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/validate_index.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools/web.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `upgrades/.guardian_handoff.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/.gitkeep` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/NINA Development Policy.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/NINA_CONTEXT.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/NINA_v11_Blueprint.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/NINA_v11_MasterPrompt.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/README old.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/code 1 wop.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/code 2 wp.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina-dev-policy.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina-identity.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina-ops.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina-phase1-roadmap.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina-sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_124135.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_154954.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_184937.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_195029.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_200933.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_210227.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_210636.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_223058.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260522_235818.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_154124.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_213916.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_214933.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_215955.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_220333.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_220925.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_221334.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_221924.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_222422.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260523_230532.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_backup_20260524_003558.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_dev_policy.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_phase1_trajectory.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_problem_log.md.bak.20260524_002746` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_space_instructions.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_update_log.md.bak.20260524_002746` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_v12_CHANGELOG.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_v12_blueprint.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_v12_master_prompt.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_v12_perplexity_prompts.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/nina_vision_manifesto.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/archive/owner-context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_234938/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260606_235836/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_144841/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215041/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_215754/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225141/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260607_225643/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_115158/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_120139/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/.env_flag` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/MANIFEST.txt` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/backup_20260608_155946/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/bugfix_20260522_225926/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/append_lock.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/core/task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/core/verifier.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/create_pr.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/crons/backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/guardian_engine.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/healthcheck.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/interfaces/cli_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/nina_codebase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/nina_docbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/nina_logbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/nina_sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/ninagate/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tests/test_finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tests/test_model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tests/test_task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tests/test_tools_smoke.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/agynina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/compact_exporter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/jules_api.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/market.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/nina_dashboard.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/nina_sync.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/archive/nina-sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/bugfix_20260522_225926/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231025/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231807/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231947/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/officemail_pre_indentfix_20260522202652.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_hotreload.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/crons_backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/interfaces_telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_212539/upgrades/backups/root_bak_cleanup/nina-guardian old.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/append_lock.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/core/task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/core/verifier.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/create_pr.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/crons/backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/guardian_engine.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/healthcheck.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/interfaces/cli_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/nina_codebase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/nina_docbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/nina_logbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/nina_sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/ninagate/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tests/test_finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tests/test_model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tests/test_task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tests/test_tools_smoke.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/agynina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/compact_exporter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/jules_api.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/market.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/nina_dashboard.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/nina_sync.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/archive/nina-sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_234938/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260606_235836/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_144841/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215041/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_215754/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225141/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260607_225643/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_115158/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_120139/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/backup_20260608_155946/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/bugfix_20260522_225926/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/append_lock.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/core/task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/core/verifier.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/create_pr.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/crons/backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/guardian_engine.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/healthcheck.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/interfaces/cli_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/nina_codebase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/nina_docbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/nina_logbase_backup.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/nina_sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/ninagate/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tests/test_finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tests/test_model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tests/test_task_store.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tests/test_tools_smoke.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/agynina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/compact_exporter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/finance.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/jules_api.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/market.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/model_discovery.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/nina_dashboard.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/nina_sync.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/archive/nina-sync.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_234938/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260606_235836/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_144841/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215041/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_215754/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225141/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260607_225643/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_115158/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_120139/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/crons/manager.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/backup_20260608_155946/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/bugfix_20260522_225926/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_012934/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013333/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/guardian_auto_20260523_013508/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231025/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231807/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/healthcheck_20260522_231947/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/officemail_pre_indentfix_20260522202652.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_195855/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_hotreload.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/core_router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/crons_backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/interfaces_telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/prepatch_20260522_202041/tools_upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/codebase_20260609_212539/upgrades/backups/root_bak_cleanup/nina-guardian old.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_012934/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013333/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/guardian_auto_20260523_013508/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/healthcheck_20260522_231025/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/healthcheck_20260522_231807/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/healthcheck_20260522_231947/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/officemail_pre_indentfix_20260522202652.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_195855/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_195855/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_195855/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/core_agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/core_capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/core_hotreload.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/core_nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/core_router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/crons_backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/interfaces_telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/tools_browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/tools_officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/tools_search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/tools_shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/prepatch_20260522_202041/tools_upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/codebase_20260609_214535/upgrades/backups/root_bak_cleanup/nina-guardian old.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.bak.20260523_222148` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.selfcheck.20260524_000742` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.selfcheck2.20260524_000830` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.selfcheck3.20260524_001230` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.selfcheck4.20260524_001324` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/agent.py.selfcheckfull.20260524_000918` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/capabilities.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/config.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/logger.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/memory.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/nina.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/nina.py.bak.20260523_222148` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/nina.py.fix1.20260523_235918` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/router.py.bak.20260523_235643` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/router.py.fix1.20260523_235724` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/core_cleanup/router.py.fix2.20260523_235807` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/logs/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/memory.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/nina_context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/nina_context.md.bak_20260604` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/nina_v12_blueprint.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/space/AGENTS.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/space/nina_context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_212539/space/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/logs/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/memory.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/nina_context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/nina_context.md.bak_20260604` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/nina_v12_blueprint.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/space/AGENTS.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/space/nina_context.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/docbase_20260609_214535/space/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/agent.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/capabilities.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/config.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/logger.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/memory.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/nina.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/browser.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/system.py.save` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/system.py.save.1` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/system.py.save.2` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/upgradepipeline.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_012934/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/agent.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/capabilities.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/config.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/logger.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/memory.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/nina.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/browser.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/system.py.save` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/system.py.save.1` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/system.py.save.2` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/upgradepipeline.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013333/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/agent.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/capabilities.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/config.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/config.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/logger.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/logger.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/memory.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/memory.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/nina.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/__init__.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/browser.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/files.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/gputuner.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/providerhunter.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/searchtool.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/system.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/system.py.save` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/system.py.save.1` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/system.py.save.2` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/upgradepipeline.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/guardian_auto_20260523_013508/tools/web.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/healthcheck_20260522_231025/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/healthcheck_20260522_231807/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/healthcheck_20260522_231947/main.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_212539/nina.log` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_212539/nina.log.2026-06-02` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_212539/nina.log.2026-06-03` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_212539/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_212539/upgrade.log.2026-05-24` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_214535/nina.log` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_214535/nina.log.2026-06-02` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_214535/nina.log.2026-06-03` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_214535/nina_update_log.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/logbase_20260609_214535/upgrade.log.2026-05-24` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory.py.bak.20260604_190900` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260522120550/chromadb/chroma.sqlite3` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260606023000/facts.json` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260609023000/facts.json` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260611023000/chromadb/chroma.sqlite3` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260611023000/facts.json` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260613023000/chromadb/chroma.sqlite3` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/memory20260613023000/facts.json` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_220745.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_222439.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_223046.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_223540.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_232239.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260609_234844.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_002740.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_003649.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_011140.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_161804.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_162243.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_174943.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260610_231951.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_033801.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_034347.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_041209.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_125351.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_133847.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_134500.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_143539.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_144858.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_150003.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_150341.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_155055.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_163138.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_170554.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_191804.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_215702.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_220045.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_222850.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_223004.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_223350.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_223656.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_224040.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_224244.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_224456.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_224947.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_231247.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_232157.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_232821.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_232953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_234033.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_234401.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_234951.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260611_235837.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_000153.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_002503.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_003045.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_003454.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_003859.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_004447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_005250.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_005650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_011338.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_011740.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_012455.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_012751.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_013802.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_015257.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_015804.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_020656.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_020953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_022259.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_023056.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_023658.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_030050.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_103651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_104203.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_112651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_122141.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_202904.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_215350.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_225456.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_232500.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_233156.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260612_233945.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_002141.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_002448.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_002930.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_011744.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_042558.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_043101.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_043343.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_043947.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_044343.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_044651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_044953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_045242.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_103359.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_110949.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_111649.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_115754.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_115944.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_120745.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_121645.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_122850.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_123645.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_123957.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_133651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_145451.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_150506.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_202039.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_202447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_225859.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_230942.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_231103.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_232446.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_232844.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_234451.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260613_235153.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_004146.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_004355.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_015903.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_033653.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_034058.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_034458.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_141147.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_141352.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_150941.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_152201.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_153248.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_154849.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_160048.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_161157.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_codebase_backup_20260614_163601.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_220745.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_222439.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_222930.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_223046.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_223420.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_223540.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_232238.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260609_234843.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_002739.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_003648.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_011139.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_161804.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_162242.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_174943.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260610_231950.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_033801.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_034347.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_041209.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_125350.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_133846.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_134459.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_143538.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_144858.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_150002.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_150341.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_155054.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_163138.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_170554.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_191803.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_215701.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_220045.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_222850.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_223003.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_223349.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_223655.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_224040.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_224243.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_224456.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_224946.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_231246.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_232156.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_232820.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_232953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_234032.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_234401.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_234951.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260611_235837.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_000152.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_002503.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_003045.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_003453.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_003858.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_004447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_005249.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_005650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_011337.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_011739.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_012454.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_012751.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_013801.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_015257.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_015803.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_020656.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_020953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_022259.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_023055.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_023657.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_030050.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_103651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_104202.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_112651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_122141.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_202904.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_215350.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_225455.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_232459.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_233155.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260612_233945.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_002141.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_002447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_002930.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_011744.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_042558.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_043101.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_043343.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_043947.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_044343.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_044651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_044953.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_045242.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_103359.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_110949.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_111649.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_115753.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_115944.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_120744.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_121645.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_122850.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_123644.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_123957.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_133651.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_145451.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_150505.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_202039.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_202447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_225858.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_230942.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_231102.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_232446.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_232844.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_234451.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260613_235153.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_004145.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_004355.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_015903.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_033652.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_034058.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_034458.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_141147.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_141352.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_150941.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_152201.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_153247.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_154848.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_160048.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_161156.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_docbase_backup_20260614_163601.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_220744.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_222438.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_223045.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_223539.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_232238.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260609_234843.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_002739.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_003648.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_011139.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_161803.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_162242.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_174942.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260610_231950.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_033800.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_034346.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_041208.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_125350.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_133846.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_134459.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_143538.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_144857.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_150001.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_150340.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_155054.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_163137.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_170553.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_191803.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_215701.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_220044.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_222849.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_223003.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_223349.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_223654.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_224039.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_224243.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_224455.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_224946.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_231246.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_232155.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_232819.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_232952.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_234032.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_234400.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_234950.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260611_235836.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_000152.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_002502.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_003044.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_003453.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_003858.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_004446.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_005249.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_005649.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_011337.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_011739.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_012454.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_012750.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_013801.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_015256.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_015803.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_020655.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_020952.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_022258.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_023055.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_023657.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_030049.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_103650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_104202.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_112650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_122140.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_202903.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_215349.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_225455.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_232459.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_233155.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260612_233944.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_002140.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_002447.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_002929.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_011743.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_042557.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_043100.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_043342.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_043946.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_044342.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_044650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_044952.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_045241.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_103358.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_110948.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_111648.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_115753.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_115943.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_120744.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_121644.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_122849.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_123644.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_123956.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_133650.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_145450.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_150505.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_202038.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_202446.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_225857.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_230941.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_231101.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_232445.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_232843.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_234450.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260613_235152.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_004145.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_004354.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_015902.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_033652.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_034057.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_034457.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_141146.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_141351.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_150940.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_152200.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_153246.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_154848.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_160047.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_161156.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_logbase_backup_20260614_163600.md` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_update_log.bak.20260606_125916` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/nina_update_log.bak.20260606_201959` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/officemail_pre_indentfix_20260522202652.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_195855/core/nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_195855/core/router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_195855/interfaces/telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/core_agent.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/core_capabilities.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/core_hotreload.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/core_nina.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/core_router.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/crons_backup_jobs.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/idleloop.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/interfaces_telegram_interface.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/tools_browser.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/tools_officemail.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/tools_search.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/tools_shell.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/prepatch_20260522_202041/tools_upgradepipeline.py` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260606030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260609030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260611030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260612030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260613030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_20260614030000.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/py_manual_20260522120938.zip` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/guardian_engine.py.bak.20260523_221712` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/guardian_engine.py.bak.20260523_222148` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/guardian_engine.py.bak.20260523_224145` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/healthcheck.py.bak.20260523_224145` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/idleloop.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/root_bak_cleanup/nina-guardian old.sh` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/browser.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/shell.py.bak.20260523_222148` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/system.py.bak.20260523_224145` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/system.py.save` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/system.py.save.1` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/system.py.save.2` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/upgradepipeline.py.bak` | archive | deprecated | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/backups/tools_cleanup/upgradepipeline.py.bak.20260523_222148` | archive | archived | keep_latest_n: 10 | Governed artifact. | ✅ YES |
| `upgrades/deploy.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `upgrades/guardian_baseline.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214027/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214243/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214311/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214327/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214516/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214556/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_214836/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215024/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215131/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215233/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215629/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_215738/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_220057/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221230/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221450/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221715/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_221936/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_222200/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260523_224157/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184926/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_184942/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260604_190917/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_001811/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191121/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191606/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_191956/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192013/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_192535/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194834/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_194935/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202124/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_202642/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_205227/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215056/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_215854/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220343/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_220731/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_221358/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260605_222008/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_023322/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024118/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024304/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024530/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_024846/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_025635/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_032329/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_033331/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/signature_matches.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_034642/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_035122/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_040127/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_170504/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_212708/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_232820/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_232844/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_233620/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_234134/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_234215/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_234621/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_234944/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260606_235842/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_144848/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/downloads_clues.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/evidence.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/healthcheck.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/journal.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/recent_changes.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/report.json` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/service_status.txt` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215048/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_215800/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_225147/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260607_225648/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260608_115206/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260608_120145/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |
| `upgrades/incidents/guardian_20260608_155952/summary.md` | archive | archived | purge_candidate | Governed artifact. | ✅ YES |

## 3. Core Document Inventory (v14.2)
| Path | Summary | Lifecycle |
|:-----|:--------|:----------|
| `README.md` | Human-facing project overview, agent model, and installation guide. | active |
| `ARCHITECTURE.md` | High-level system design and logic flow map. | active |
| `CHANGELOG.md` | User-friendly summary of major version releases. | active |
| `AGENTS.md` | Agent Operating Law (permissions and scopes for Jules, agy, etc). | active |
| `nina_context.md` | AI session grounding profile & architecture context. Attach to new threads. | active |
| `docs/nina_v14_blueprint.md` | Canonical v14.2 system blueprint and component map. | active |
| `docs/space/nina_state.md` | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | active |
| `docs/space/nina_megatask_index.md` | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | active |

---
_Generated by NINA Indexer on 2026-06-14_
