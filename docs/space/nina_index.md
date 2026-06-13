# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview & Scope
This index tracks all governed artifacts in the NINA repository.
- **Governed:** true. Includes docs, tools, scripts, configs, exports, and persistent logs.
- **Unmanaged:** Excludes `__pycache__`, `.venv`, `.git`, transient temp files.

## 2. File Inventory
| Path | Role | Lifecycle | Retention | Summary | Canonical |
|------|------|-----------|-----------|---------|-----------|
| `.coverage` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.env.example` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.geminiignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.gitignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `.ninaignore` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `AGENTS.md` | source_of_truth | active | keep | Agent Operating Law (permissions and scopes for Jules, agy, etc). | ✅ YES |
| `ARCHITECTURE.md` | source_of_truth | active | keep | High-level system design and logic flow map. | ✅ YES |
| `CHANGELOG.md` | source_of_truth | active | keep | User-friendly summary of major version releases. | ✅ YES |
| `CONTRIBUTING.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `EVOLVE_PROPOSAL.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `LICENSE` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `MEMORY.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `Makefile` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `README.md` | source_of_truth | active | keep | Human-facing project overview, agent model, and installation guide. | ✅ YES |
| `SECURITY.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `WORKFLOW.md` | source_of_truth | active | keep | Repository rules of engagement and development lifecycle. | ✅ YES |
| `bench_report.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `call_graph_test.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `commit_message.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `efficiency_report.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `fix_caps_again.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `generate_backups.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `guardian_engine.py` | source_of_truth | active | keep | Forensic AST scanner and baseline drift analyzer (73KB). | ✅ YES |
| `healthcheck.py` | source_of_truth | active | keep | Pre-deployment health and dependency verification suite. | ✅ YES |
| `idleloop.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `main.py` | source_of_truth | active | keep | Primary entry point for the NINA systemd service. | ✅ YES |
| `modify_agent_final.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_nina_final.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_nina_url_parse.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `modify_ninagate_format.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina-dashboard.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_aider.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_audit.sh` | source_of_truth | active | keep | Permanent wrapper script for the repository hygiene audit. | ✅ YES |
| `nina_cleanup.sh` | source_of_truth | active | keep | Permanent wrapper script for safe redundancy cleanup execution. | ✅ YES |
| `nina_codebase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_context.md` | source_of_truth | active | keep | AI session grounding profile & architecture context. Attach to new threads. | ✅ YES |
| `nina_docbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_docs_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_export.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_logbase_backup.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `nina_sync.sh` | source_of_truth | active | keep | Post-session synchronization and deployment script. | ✅ YES |
| `nina_update_log.md` | system_of_record | active | keep | Canonical live activity log (Entry 001-167). Newest entries at top. | ✅ YES |
| `ninagate_load_test.sh` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninajulesgithub.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `ninajulesgithub.service` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `plan.md` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pr_desc.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `pytest.ini` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `requirements.txt` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `system_templates.json` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `test_httpx_hook.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `test_router.py` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `tools.log` | source_of_truth | active | keep | Governed artifact. | ✅ YES |
| `agent/` | subsystem | active | keep | Subsystem directory containing agent logic/docs. | ✅ YES |
| `bin/` | subsystem | active | keep | Subsystem directory containing bin logic/docs. | ✅ YES |
| `checks/` | subsystem | active | keep | Subsystem directory containing checks logic/docs. | ✅ YES |
| `core/` | subsystem | active | keep | System orchestrator, router, memory, and config modules. | ✅ YES |
| `crons/` | subsystem | active | keep | Subsystem directory containing crons logic/docs. | ✅ YES |
| `dashboard/` | subsystem | active | keep | Subsystem directory containing dashboard logic/docs. | ✅ YES |
| `data/` | subsystem | active | keep | Subsystem directory containing data logic/docs. | ✅ YES |
| `docs/` | subsystem | active | keep | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | ✅ YES |
| `exports/` | subsystem | active | keep | Subsystem directory containing exports logic/docs. | ✅ YES |
| `git-hooks/` | subsystem | active | keep | Subsystem directory containing git-hooks logic/docs. | ✅ YES |
| `interfaces/` | subsystem | active | keep | Telegram and REST API communication layers. | ✅ YES |
| `logs/` | subsystem | active | keep | Subsystem directory containing logs logic/docs. | ✅ YES |
| `ninagate/` | subsystem | active | keep | Subsystem directory containing ninagate logic/docs. | ✅ YES |
| `scripts/` | subsystem | active | keep | Subsystem directory containing scripts logic/docs. | ✅ YES |
| `templates/` | subsystem | active | keep | Subsystem directory containing templates logic/docs. | ✅ YES |
| `tests/` | subsystem | active | keep | Subsystem directory containing tests logic/docs. | ✅ YES |
| `tools/` | subsystem | active | keep | Capability kernel and domain-specific action modules (ninaflash nucleus). | ✅ YES |
| `upgrades/` | subsystem | active | keep | Subsystem directory containing upgrades logic/docs. | ✅ YES |

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

## 4. Redundancy & Conflicts
The following clusters contain identical content. Consolidate to the canonical source where possible.

- **Cluster `dup-0001`**: Canonical is `tools.log`. Members: `tools.log`, `data/gemini_preamble.md`, `interfaces/api.py`, `interfaces/__init__.py`, `tests/__init__.py`, `crons/__init__.py`, `agent/__init__.py`, `agent/context.py`
- **Cluster `dup-0002`**: Canonical is `data/tasks.json`. Members: `data/tasks.json`, `data/circuit_state.json`
- **Cluster `dup-0003`**: Canonical is `data/gpuconfig.json`. Members: `data/modeldiscovery.json`, `data/gpuconfig.json`
- **Cluster `dup-0004`**: Canonical is `bin/nf`. Members: `bin/nf`, `bin/ninaflash`

## 5. Governance Rules & Index-First Workflow
1. **Check the Index:** `python3 tools/query_index.py --path <file>`
2. **Duplicate Clusters:** When writing to a path that belongs to a duplicate cluster, you MUST only write to the `canonical_path`.
3. **Index Modification:** If creating/moving a governed file:
   - Run `python3 tools/update_index.py`.
   - Run `python3 tools/validate_index.py`.
4. **Validation:** No PR touching governed paths is "Done" unless `validate_index.py` passes.
5. **Contract:** The index is the single enforceable contract for doc/log/code inventory.

---
_Generated by NINA Indexer on 2026-06-12_
