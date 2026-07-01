"""Stub tests for core/planner/task_dag.py"""
import pytest


def test_task_dag_importable():
    import importlib
    mod = importlib.import_module("core.planner.task_dag")
    assert mod is not None


@pytest.mark.skip(reason="stub — implement when TaskDAG API is stable")
def test_add_node_increments_count():
    pass


@pytest.mark.skip(reason="stub — implement when TaskDAG API is stable")
def test_topological_sort_linear_chain():
    pass


@pytest.mark.skip(reason="stub — implement when TaskDAG API is stable")
def test_cycle_detection_raises():
    pass
