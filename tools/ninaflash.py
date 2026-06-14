#!/usr/bin/env python3
"""ninaflash — Thin CLI dispatcher. All logic lives in ninaflash_* submodules."""
import argparse
import sys
import os
from pathlib import Path

_REPO_ROOT = str(Path(__file__).parent.parent.resolve())
if _REPO_ROOT not in sys.path: sys.path.insert(0, _REPO_ROOT)

from tools.ninaflash_core import (
    cmd_find, cmd_edit, cmd_git, cmd_list, cmd_status, cmd_check_ignore,
    cmd_file_read, cmd_file_grep, cmd_file_patch, cmd_file_insert, cmd_file_diff,
    cmd_git_log, cmd_git_changed, cmd_git_search, cmd_git_blame, cmd_git_stash_quick,
    cmd_monitor, cmd_batch, cmd_hw_gate, cmd_gen_tool, cmd_gen_test, cmd_install_hooks,
    write_nf_log, NF_TOKEN_SAVINGS
)
from tools.ninaflash_code import (
    cmd_code_outline, cmd_code_cycles, cmd_code_dep_map,
    cmd_code_index, cmd_code_call_graph, cmd_code_call_stack,
    cmd_code_symbol, cmd_code_migrate, cmd_find_symbol,
    cmd_code_sigs, cmd_code_doc, cmd_code_dead_code, cmd_code_extract_method
)
from tools.ninaflash_context import (
    cmd_context_mini_gen, cmd_log_find_id, cmd_log_tail, cmd_log_next_id,
    cmd_query, cmd_query_capability, cmd_context_pack, cmd_capability_map,
    cmd_stats, cmd_help_ai, cmd_log_summarize,
    cmd_context_compress, cmd_context_stall
)
from tools.ninaflash_backlog import (
    cmd_backlog_summary, cmd_task_active, cmd_backlog_triage,
    cmd_backlog_dag, cmd_backlog_add, cmd_backlog_archive
)
from tools.ninaflash_memory import (
    cmd_memory_stash, cmd_session_checkpoint, cmd_session_resume,
    cmd_memory_session_save, cmd_memory_session_recall, cmd_memory_inject,
    cmd_session_start, cmd_session_log, cmd_session_preamble, cmd_session_done
)
from tools.ninaflash_guard import (
    cmd_verify_all, cmd_check_code, cmd_check_complexity,
    cmd_check_doc, cmd_maintain_pr, cmd_pr_reconcile,
    cmd_test_run, cmd_bench, cmd_code_audit_doc,
    cmd_gemini_context, cmd_gemini_prompt, cmd_gemini_status, cmd_gemini_run
)

def main():
    parser = argparse.ArgumentParser(description="ninaflash AI Agent Kernel v6.1")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Primitives
    p_find = subparsers.add_parser("find"); p_find.add_argument("query"); p_find.add_argument("--regex", action="store_true"); p_find_sym = subparsers.add_parser("find-symbol"); p_find_sym.add_argument("name")
    p_edit = subparsers.add_parser("edit"); p_edit.add_argument("file"); p_edit.add_argument("edits")
    subparsers.add_parser("list"); subparsers.add_parser("status").add_argument("--pulse", action="store_true")
    subparsers.add_parser("monitor"); subparsers.add_parser("batch").add_argument("--cmds", required=True)
    
    # File & Git
    p_file = subparsers.add_parser("file"); p_fs_f = p_file.add_subparsers(dest="sub")
    p_fr = p_fs_f.add_parser("read"); p_fr.add_argument("file"); p_fr.add_argument("--start", type=int); p_fr.add_argument("--end", type=int)
    p_fg = p_fs_f.add_parser("grep"); p_fg.add_argument("pattern"); p_fg.add_argument("--dir"); p_fg.add_argument("--ext")
    p_fp = p_fs_f.add_parser("patch"); p_fp.add_argument("file"); p_fp.add_argument("--find", required=True); p_fp.add_argument("--replace", required=True)
    p_fi = p_fs_f.add_parser("insert"); p_fi.add_argument("file"); p_fi.add_argument("--after", required=True); p_fi.add_argument("--text", required=True)
    p_fd = p_fs_f.add_parser("diff"); p_fd.add_argument("file")
    
    p_git = subparsers.add_parser("git"); p_gs_g = p_git.add_subparsers(dest="sub")
    p_gl = p_gs_g.add_parser("log"); p_gl.add_argument("--n", type=int)
    p_gs_g.add_parser("changed"); p_gs_g.add_parser("search").add_argument("keyword")
    p_gb = p_gs_g.add_parser("blame"); p_gb.add_argument("file"); p_gb.add_argument("--start", type=int); p_gb.add_argument("--end", type=int)
    p_gs_g.add_parser("stash-quick").add_argument("--label")

    # Code & Docs
    p_code = subparsers.add_parser("code"); p_cs = p_code.add_subparsers(dest="sub")
    p_cs.add_parser("outline").add_argument("file"); p_cs.add_parser("dep-map"); p_cs.add_parser("index")
    p_cs.add_parser("call-graph").add_argument("file", nargs="?"); p_cs.add_parser("cycles"); p_cs.add_parser("sigs").add_argument("dir"); p_cs.add_parser("doc").add_argument("keyword"); p_cs.add_parser("call-stack").add_argument("file"); p_cs.choices["call-stack"].add_argument("name")
    p_cs.add_parser("migrate").add_argument("old_name"); p_cs.choices["migrate"].add_argument("new_name"); p_cs.choices["migrate"].add_argument("--dir", default=".")
    p_sym = p_cs.add_parser("symbol"); p_sym.add_argument("file"); p_sym.add_argument("name")
    p_ext = p_cs.add_parser("extract-method"); p_ext.add_argument("file"); p_ext.add_argument("func_name")
    p_ext.add_argument("start_line"); p_ext.add_argument("end_line"); p_ext.add_argument("new_name")
    
    # Backlog & Session
    p_bl = subparsers.add_parser("backlog"); p_bs = p_bl.add_subparsers(dest="sub")
    p_bs.add_parser("summary"); p_bs.add_parser("triage"); p_bs.add_parser("dag").add_argument("task_id", nargs="?")
    p_ba = p_bs.add_parser("add"); p_ba.add_argument("--title"); p_ba.add_argument("--priority"); p_ba.add_argument("--component")
    
    p_session = subparsers.add_parser("session"); p_ss = p_session.add_subparsers(dest="sub")
    p_ss.add_parser("checkpoint").add_argument("--goal"); p_ss.add_parser("resume"); p_ss.add_parser("inject")
    p_sstart = p_ss.add_parser("start"); p_sstart.add_argument("--tool"); p_sstart.add_argument("--task", dest="task_id")
    p_slog = p_ss.add_parser("log"); p_slog.add_argument("--tool"); p_slog.add_argument("--step", type=int); p_slog.add_argument("--action")
    p_slog.add_argument("--outcome"); p_slog.add_argument("--detail")
    p_ss.add_parser("preamble").add_argument("--tool"); p_ss.add_parser("done").add_argument("--tool")

    p_memory = subparsers.add_parser("memory"); p_ms = p_memory.add_subparsers(dest="sub")
    p_ms.add_parser("stash").add_argument("text"); p_ms.add_parser("inject")
    p_ms.add_parser("session-save").add_argument("--summary"); p_ms.add_parser("session-recall").add_argument("--n", type=int)
    
    # Context
    p_ctx = subparsers.add_parser("context"); p_ctxs = p_ctx.add_subparsers(dest="sub")
    p_ccp = p_ctxs.add_parser("compress"); p_ccp.add_argument("--task"); p_ccp.add_argument("--cp", type=int, default=0)
    p_ctxs.add_parser("stall")
    p_cpk = p_ctxs.add_parser("pack"); p_cpk.add_argument("--file", required=True)



    # Guard & Triage
    p_check = subparsers.add_parser("check"); p_cks = p_check.add_subparsers(dest="sub")
    p_cc = p_cks.add_parser("code"); p_cc.add_argument("file"); p_cc.add_argument("--strict", action="store_true"); p_cx = p_cks.add_parser("complexity"); p_cx.add_argument("file")
    p_cd = p_cks.add_parser("doc"); p_cd.add_argument("file"); p_cd.add_argument("--agents", action="store_true")
    
    p_test = subparsers.add_parser("test"); p_ts = p_test.add_subparsers(dest="sub")
    p_tr = p_ts.add_parser("run"); p_tr.add_argument("--file"); p_tr.add_argument("--suite", choices=["sync", "full", "fast"]); p_tr.add_argument("--json", action="store_true"); p_tr.add_argument("--strict", action="store_true")

    p_maintain = subparsers.add_parser("maintain"); p_mts = p_maintain.add_subparsers(dest="sub")
    p_mpr = p_mts.add_parser("pr"); p_mpr.add_argument("pr_id"); p_mpr.add_argument("--task", dest="task_id")
    p_mpr.add_argument("--title"); p_mpr.add_argument("--summary")

    # Dispatch
    args = parser.parse_args()
    import time as _time
    t0 = _time.monotonic()
    try:
        cmd, sub = args.command, getattr(args, 'sub', None)
        cmd_norm = cmd.replace("-", "_")
        sub_norm = sub.replace("-", "_") if sub else None
        func = globals().get(f"cmd_{cmd_norm}_{sub_norm}") if sub_norm else globals().get(f"cmd_{cmd_norm}")
        if func: func(args)
        else: print(f"Unknown command: {cmd} {sub}")
        
        dur = (_time.monotonic() - t0) * 1000
        write_nf_log(cmd, sub or "", dur, tokens_saved=NF_TOKEN_SAVINGS.get(cmd, 0))
    except Exception as e:
        print(f"❌ Error: {e}")
        write_nf_log(args.command, getattr(args, 'sub', '') or "", 0, outcome=f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
