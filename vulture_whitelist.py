# =============================================================================
# vulture_whitelist.py  —  Nina dead-code false-positive suppressions
#
# HOW VULTURE WHITELISTS WORK:
#   Vulture scans this file for "used" names. The correct pattern is to access
#   each suppressed name as an attribute of a dummy class — vulture sees the
#   attribute access and marks the name as "used" in its analysis.
#
#   WRONG:  frame = None          ← vulture ignores this
#   RIGHT:  _.frame               ← vulture sees "frame" as used
#
# Usage: vulture ~/nina vulture_whitelist.py --min-confidence 80
# =============================================================================

class _:  # noqa: N801 — dummy whitelist class, never instantiated

    # signal handler args — required by Python signal.signal() API signature
    # tools/compact_exporter.py:238
    frame
    signum

    # Rich / Progress imports — used conditionally in observability
    # core/observability.py:105-108
    Table
    BarColumn
    Progress
    TextColumn
    TimeElapsedColumn
    Layout

    # requests.structures import — type hint in ninagate
    # ninagate/main.py:789
    Headers

    # guardian_engine — called externally via importlib / ssot_registry
    # tools/guardian_engine.py:22
    baseline_needs_refresh
    changed_py_files
    stamp_run

    # Variables assigned for side-effects / broader scope / logging
    # core/autogen.py:37
    initial_prompt
    # archive/orphan_cognitive/cognitive/base.py:33
    execution_trace
    # interfaces/base_adapter.py:8  +  tests/test_base_adapter.py:11
    parse_mode
    # tests/test_memory_kb.py:18,36
    include
    # tools/merge_resolver.py:274
    run_test_check
    # tools/pipeline_autopilot.py:364
    merged_prs
