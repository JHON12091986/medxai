--- CONTEXT PACK: ninaflash.py ---
Path: tools/ninaflash.py
Size: 103615 bytes | 2620 lines

def run_cmd(cmd, cwd=str(REPO_ROOT), timeout=60): """[001] Base execution primitive...."""
def safe_run_cmd(cmd: str, timeout=60): """[NEW] Hardened execution with blocklist for git push/force...."""
def _safe_run(cmd: str, timeout=60): """[002] Hardened execution with NINA security policy enforcement...."""
def _path_resolve(rel_path: str): """[003] Absolute path resolution from repo root...."""
def cmd_find(args): ...
def cmd_edit(args): ...
def cmd_git(args): ...
def cmd_status(args): """[004] Unified system health snapshot...."""
def _append_update_log(task_id: str, title: str, summary: str): """[007] Appends a standardized entry to nina_update_log.md...."""
def _print_pulse(): """Generate high-density 10-line pulse...."""
def _get_locks(): """[005] Internal: Get list of locked files...."""
def get_backlog_tasks(): """[006] Parse all tasks from jules_backlog.md with mtime caching...."""
def write_nf_log(command: str, subcommand: str='', duration_ms: float=0, tokens_saved: int=0, outcome: str='OK'): """Structured JSON log entry for every nf command execution...."""
def _load_geminiignore(): ...
def _is_ignored(path_str: str, patterns: List[str]): ...
def _find_py_files(): """[008] Find all .py files excluding standard ignore dirs and .geminiignore with depth cap...."""
def _find_md_files(): """[009] Find all .md files excluding standard ignore dirs and .geminiignore...."""
def _resolve_v13_docs(): """[010] Surgically resolve v13 doc conflicts locally...."""
def cmd_maintain_pr(args): """[011] Atomic 'Rebase -> Resolve -> Merge -> Log -> Close' workflow...."""
def cmd_pr_reconcile(args): """[012] Prune stale remote refs...."""
def cmd_code_outline(args): """[012] Extract signatures/docstrings only using AST...."""
def cmd_code_dep_map(args): """[013] Map project dependencies excluding venv...."""
def cmd_code_index(args): """[037] Global Symbol Indexer: Generate JSON map of all classes/functions...."""
def cmd_code_call_graph(args): """[038] Local Call Graph Generator: Trace function calls locally without LLM...."""
def cmd_code_call_stack(args): """[040] Symbol-Based Context Injector: Read only the call stack of a function...."""
def cmd_context_mini_gen(args): """[014] Generate high-density 2KB pulse-JSON...."""
def _compress_diff(diff_text: str): """[015] Strip metadata from diffs to save tokens...."""
def cmd_log_find_id(args): """[037] Zero-token log parsing for specific task ID...."""
def _save_task_status(task_id: str, new_status: str): """[016] Update task status in jules_backlog.md...."""
def _find_blockers(task_id: str): """[017] Parse dependencies for a task...."""
def cmd_backlog_summary(args): """[100] Print a 5-line summary of the backlog...."""
def cmd_task_active(args): """[101] List active tasks and their locked files...."""
def _get_log_entries(): ...
def cmd_log_tail(args): """[102] Print the last <n> entries of the log...."""
def cmd_log_next_id(args): """[103] Print the next available entry ID...."""
def cmd_backlog_triage(args): """[018] Promote BLOCKED tasks to READY if deps are DONE...."""
def cmd_backlog_dag(args): """[019] ASCII DAG: Visualize dependencies with circularity guard...."""
def cmd_backlog_add(args): """[020] Add new task using CLI arguments...."""
def cmd_backlog_archive(args): """[021] Move DONE items to archived status (simplified)...."""
def cmd_memory_stash(args): """[037] Save a snippet of working memory...."""
def cmd_session_checkpoint(args): """[022] Save session state...."""
def cmd_session_resume(args): """[023] Resume session state...."""
def cmd_verify_all(args): """[024] Atomic verification suite...."""
def cmd_check_code(args): """[033] Quality gate: run py_compile + pyflakes + ruff on target file...."""
def cmd_check_ignore(args): """[045] Show which files are currently being hidden from the agent...."""
def cmd_check_doc(args): """[034] Doc quality gate: validate required sections and stale references...."""
def cmd_install_hooks(args): """[037] Install pre-commit hook to prevent syntax errors...."""
def cmd_doc_consolidate(args): """[038] Consolidate old entries from nina_update_log.md to archive...."""
def cmd_gen_tool(args): """[025] Generate NINA tool boilerplate...."""
def cmd_gen_test(args): """[026] Generate pytest boilerplate...."""
def cmd_ops_thermal(args): """[027] Safety monitor...."""
def cmd_ops_vram(args): """[028] VRAM monitor...."""
def cmd_ops_compress_logs(args): """[036] Compress repetitive log lines using a sliding window...."""
def cmd_hw_gate(args): """[033] Hardware Gate: Check sensors and return GO/HOLD/DEFER...."""
def _get_hw_status(): """[034] Logic for hardware gate GO/HOLD/DEFER...."""
def cmd_register_capability(args): """[035] Dynamically register a new capability...."""
def cmd_run_capability(args): """[036] Execute a registered capability by name...."""
def cmd_help_ai(args): """[029] Optimized briefing for new agents...."""
def cmd_capability_map(args): """[030] Discoverability map...."""
def cmd_stats(args): """[031] Show ninaflash file stats and function count, plus efficiency metrics...."""
def cmd_kernel_upgrade(args): """[032] Self-evolution command...."""
def cmd_context_pack(args): """[041] Context Pack: Distill a file into a token-efficient skeletal summary...."""
def cmd_query(args): """[044] Query capabilities mapping of NinaFlash local handlers...."""
def cmd_query_capability(args): """[042] Query: Check if a task type can be handled locally by NinaFlash...."""
def cmd_log_summarize(args): """[037] Sliding window summarizer for nina_update_log.md...."""
def cmd_file_read(args): """[043] Read file lines N to M...."""
def cmd_file_grep(args): """[044] Regex search across files...."""
def cmd_file_patch(args): """[045] Replace first occurrence of exact string...."""
def cmd_file_insert(args): """[046] Insert line after anchor...."""
def cmd_file_diff(args): """[047] Show git diff for file...."""
def cmd_git_log(args): """[048] git log --oneline -N...."""
def cmd_git_changed(args): """[049] git diff --name-only HEAD...."""
def cmd_git_search(args): """[050] git log --oneline --grep=<keyword>...."""
def cmd_git_blame(args): """[051] git blame -L N,M <file>...."""
def cmd_git_stash_quick(args): """[052] git stash push -m LABEL...."""
def cmd_monitor_tools(sessions_dir, limit): """Parse Gemini CLI sessions: tool call frequency + token cost per tool...."""
def cmd_monitor(args): """Parse real Gemini CLI session data + NinaGate logs for savings report...."""
def cmd_batch(args): """[054] Parallel execution of multiple nf commands...."""
def cmd_memory_session_save(args): """[055] Save current session summary...."""
def cmd_memory_session_recall(args): """[056] Recall last N session entries...."""
def cmd_memory_inject(args): """[057] Inject session context for Gemini CLI bootstrap...."""
def cmd_ops_rotate_logs(args): """[038] Compress and rotate tool logs...."""
def cmd_session_start(args): ...
def cmd_session_log(args): ...
def cmd_session_preamble(args): ...
def cmd_session_done(args): ...
def cmd_code_symbol(args): """[037] Extract source code of a specified class or function using AST...."""
def cmd_find_symbol(args): """[038] Recursively search the repository for a specified class or function definition...."""
def cmd_code_sigs(args): """[039] Generate a high-density map of all function and class signatures in a directory...."""
def cmd_bench(args): """[043] Benchmark: Compare Cloud vs Hybrid execution stats...."""
def cmd_code_doc(args): """[040] Search for keywords only within docstrings...."""
def cmd_code_dead_code(args): """[065] Identify unused functions/imports using vulture...."""
def cmd_test(args): """[043] Test Runner: Execute pytest suite...."""
def cmd_gemini_context(args): ...
def cmd_gemini_prompt(args): ...
def cmd_gemini_status(args): ...
def cmd_gemini_run(args): ...
def main(): ...

--- END PACK ---
