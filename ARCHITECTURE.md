# NINA v5.1 Architecture Blueprint

NINA is an autonomous engineering system designed to maintain and evolve its own codebase through a self-healing pipeline.

## 1. The Autonomous Orchestrator & Unified Engine (tools/jules.py)
NINA operates on a continuous 3-minute cron cycle (`crons/manager.py`) governed by the orchestrator cycle in `tools/jules.py`. 
- **Phase 0 (Sense):** Polls Jules cloud sessions for questions/errors via the watcher component.
- **Phase 1 (Resolve):** Uses `asyncio.gather` and the GitHub API to merge Pull Requests concurrently.
- **Phase 2 (Saturate):** Reads `jules_backlog.md` and dispatches new jobs to maintain capacity in the cloud VM queue.

## 2. Jules-Telegram Bridge
When Jules pauses a task to ask a clarifying question, the unified engine in `tools/jules.py` extracts the text and forwards it to the authorized user's Telegram. The user replies via `/jules feedback [SID] [response]`, which NINA relays directly back to the active session via the API client integrated within `tools/jules.py`.

## 3. NinaGate & Smart Routing
NinaGate acts as a reverse proxy intercepting all OpenAI-compatible API calls.
- **Decision Tree:** If a task is "SIMPLE" (formatting, regex, docstrings), NinaGate reroutes it to `NinaFlash` running `qwen2.5-coder` locally via Ollama.
- **Fallbacks:** If a cloud provider rate limits (429) or fails, the router seamlessly cascades to available local or secondary cloud models.

## 4. Guardian AST Engine
Before any code is committed or merged, `guardian_engine.py` builds an Abstract Syntax Tree (AST) of the new code to search for critical violations:
- Execution of `shell=True` without constraints.
- Hardcoded secrets or tokens.
- Unsafe module imports.

## 5. Data Flow & Index Governance
1. **Goal Intake:** Natural language commands are parsed into structured markdown via `tools/jules.py` (goal subcommand).
2. **Spec Generation:** The goal is added to `docs/space/jules_backlog.md`.
3. **Dispatch:** The orchestrator picks up the `READY` task and dispatches it to Jules.
4. **Execution:** Jules opens a Pull Request (`IN_PR`).
5. **Auto-Document:** The orchestrator cycle cross-references the modified files against `docs/space/nina_index.json`. If `"doc_required": true`, it triggers `tools/doc_autogen.py` to write the docs.
6. **Merge & Sync:** The PR is merged, the error register is updated if conflicts occur, and `./nina_sync.sh` backs up the state to Google Drive.
