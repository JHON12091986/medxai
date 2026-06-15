#!/usr/bin/env python3
"""tests/test_merge_resolver.py — Unit tests for NINA MergeResolver"""
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Stub out heavyweight imports before loading the module
sys.modules.setdefault("core.logger", types.ModuleType("core.logger"))
sys.modules["core.logger"].get_logger = lambda name: MagicMock()
sys.modules.setdefault("tools.telegram_notify", types.ModuleType("tools.telegram_notify"))
sys.modules["tools.telegram_notify"].send = lambda msg: None

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.merge_resolver import (
    ConflictBlock,
    ConflictVerdict,
    _is_downgrade,
    _is_false_conflict,
    _is_net_new,
    _normalize,
    parse_conflict_blocks,
    evaluate_conflict,
    build_report,
    ResolutionReport,
)


# ── _normalize ────────────────────────────────────────────────────────────────

def test_normalize_strips_comments():
    lines = ["# this is a comment", "def foo():", "    pass"]
    result = _normalize(lines)
    assert "# this is a comment" not in result
    assert "def foo():" in result


def test_normalize_strips_whitespace():
    a = ["  x = 1  ", "  y = 2  "]
    b = ["x = 1", "y = 2"]
    assert _normalize(a) == _normalize(b)


# ── _is_false_conflict ────────────────────────────────────────────────────────

def test_false_conflict_identical_content():
    lines = ["x = 1", "y = 2"]
    is_false, reason = _is_false_conflict(lines, lines)
    assert is_false
    assert "false conflict" in reason.lower() or "identical" in reason.lower()


def test_false_conflict_whitespace_diff():
    main  = ["x = 1", "y = 2"]
    jules = ["x = 1  ", "y = 2"]
    is_false, _ = _is_false_conflict(jules, main)
    assert is_false


def test_not_false_conflict_different_logic():
    main  = ["def route(self):", "    return GEMINI"]
    jules = ["def route(self):", "    return OLLAMA"]
    is_false, _ = _is_false_conflict(jules, main)
    assert not is_false


# ── _is_downgrade ─────────────────────────────────────────────────────────────

def test_downgrade_detected_old_casing_bug():
    jules = ['if provider == "ollama":']
    main  = ['if provider.lower() == "ollama":']
    is_dg, reason = _is_downgrade(jules, main)
    assert is_dg
    assert "downgrade" in reason.lower() or "pattern" in reason.lower()


def test_downgrade_detected_get_secret_bug():
    jules = ["key = self.config.get_secret('groq_api_key')"]
    main  = ["key = getattr(self.config, 'groq_api_key', None)"]
    is_dg, reason = _is_downgrade(jules, main)
    assert is_dg


def test_no_downgrade_when_both_same():
    lines = ["key = getattr(self.config, 'groq_api_key', None)"]
    is_dg, _ = _is_downgrade(lines, lines)
    assert not is_dg


# ── _is_net_new ───────────────────────────────────────────────────────────────

def test_net_new_new_function():
    jules = ["async def batch_route(self, prompts):", "    pass"]
    main  = ["def route(self):", "    return 'x'"]
    is_new, reason = _is_net_new(jules, main)
    assert is_new
    assert "batch_route" in reason or "net-new" in reason.lower()


def test_net_new_empty_main():
    jules = ["def validate_response(content):", "    return True"]
    main  = []
    is_new, reason = _is_net_new(jules, main)
    assert is_new
    assert "additive" in reason.lower() or "empty" in reason.lower()


def test_not_net_new_same_function():
    lines = ["def route(self):", "    return 'x'"]
    is_new, _ = _is_net_new(lines, lines)
    assert not is_new


# ── evaluate_conflict ─────────────────────────────────────────────────────────

def test_evaluate_false_conflict():
    block = ConflictBlock(
        file="core/router.py",
        start_line=10,
        end_line=14,
        main_content=["x = 1", "y = 2"],
        jules_content=["x = 1", "y = 2"],
    )
    with patch("tools.merge_resolver.get_file_commit_time", return_value=0.0):
        result = evaluate_conflict(block, jules_branch="jules/task-1")
    assert result.verdict == ConflictVerdict.FALSE_CONFLICT
    assert result.resolved_content == ["x = 1", "y = 2"]


def test_evaluate_downgrade_kept_main():
    block = ConflictBlock(
        file="core/router.py",
        start_line=20,
        end_line=24,
        main_content=["key = getattr(self.config, 'x', None)"],
        jules_content=["key = self.config.get_secret('x')"],
    )
    with patch("tools.merge_resolver.get_file_commit_time", return_value=0.0):
        result = evaluate_conflict(block, jules_branch="jules/task-1")
    assert result.verdict == ConflictVerdict.KEEP_MAIN
    assert result.resolved_content == block.main_content


def test_evaluate_net_new_cherry_pick():
    block = ConflictBlock(
        file="core/router.py",
        start_line=30,
        end_line=36,
        main_content=["def route(self):", "    return 'x'"],
        jules_content=["async def batch_route(self, prompts):", "    pass"],
    )
    with patch("tools.merge_resolver.get_file_commit_time", return_value=0.0):
        result = evaluate_conflict(block, jules_branch="jules/task-1")
    assert result.verdict == ConflictVerdict.CHERRY_PICK
    combined = "\n".join(result.resolved_content)
    assert "route" in combined
    assert "batch_route" in combined


def test_evaluate_main_newer_wins():
    block = ConflictBlock(
        file="core/router.py",
        start_line=40,
        end_line=44,
        main_content=["x = 'updated'"],
        jules_content=["x = 'old_value'"],
    )
    def mock_commit_time(filepath, ref="HEAD"):
        return 1_700_000_000.0 if ref == "HEAD" else 1_600_000_000.0

    with patch("tools.merge_resolver.get_file_commit_time", side_effect=mock_commit_time):
        result = evaluate_conflict(block, jules_branch="jules/task-1")
    assert result.verdict == ConflictVerdict.KEEP_MAIN


# ── build_report ──────────────────────────────────────────────────────────────

def test_build_report_contains_summary():
    report = ResolutionReport(
        pr_number=42,
        branch="jules/task-42",
        base_commit="abc1234",
        head_commit="def5678",
        conflicts_total=3,
        auto_resolved=1,
        cherry_picked=1,
        kept_main=1,
    )
    output = build_report(report)
    assert "jules/task-42" in output
    assert "3" in output
    assert "Auto-resolved" in output or "auto_resolved" in output.lower()


def test_build_report_includes_blocks():
    block = ConflictBlock(
        file="core/router.py",
        start_line=10,
        end_line=14,
        main_content=["x = 1"],
        jules_content=["x = 1"],
        verdict=ConflictVerdict.FALSE_CONFLICT,
        reason="Semantically identical",
        resolved_content=["x = 1"],
    )
    report = ResolutionReport(
        pr_number=None,
        branch="jules/task-1",
        base_commit="aaa",
        head_commit="bbb",
        conflicts_total=1,
        auto_resolved=1,
        blocks=[block],
    )
    output = build_report(report)
    assert "core/router.py" in output
    assert "false_conflict" in output or "✅" in output
