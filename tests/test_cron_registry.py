import json
import os
import sys
import pytest
from unittest.mock import patch, mock_open

from crons.registry import CronJob, CronRegistry
from crons.runner import CronRunner

def test_registry_registers_job():
    registry = CronRegistry()
    job = CronJob(
        id='test_job_1',
        name='Test Job 1',
        schedule='0 * * * *',
        module='tests.test_job_1',
        description='Test Job'
    )
    if registry.get('test_job_1'):
        registry._jobs.pop('test_job_1') # cleanup from prior runs
    registry.register(job)
    retrieved = registry.get('test_job_1')
    assert retrieved is not None
    assert retrieved.id == 'test_job_1'

def test_registry_duplicate_raises():
    registry = CronRegistry()
    job = CronJob(
        id='test_job_2',
        name='Test Job 2',
        schedule='0 * * * *',
        module='tests.test_job_2',
        description='Test Job'
    )
    if registry.get('test_job_2'):
        registry._jobs.pop('test_job_2')
    registry.register(job)
    with pytest.raises(ValueError, match="Duplicate cron ID: test_job_2"):
        registry.register(job)

def test_registry_disable_enable():
    registry = CronRegistry()
    job = CronJob(
        id='test_job_3',
        name='Test Job 3',
        schedule='0 * * * *',
        module='tests.test_job_3',
        description='Test Job'
    )
    if registry.get('test_job_3'):
        registry._jobs.pop('test_job_3')
    registry.register(job)

    assert any(j.id == 'test_job_3' for j in registry.get_enabled())
    registry.disable('test_job_3')
    assert not any(j.id == 'test_job_3' for j in registry.get_enabled())
    registry.enable('test_job_3')
    assert any(j.id == 'test_job_3' for j in registry.get_enabled())

def test_runner_run_job_success(tmp_path):
    # Create a dummy module with a run() function
    dummy_module_path = tmp_path / "dummy_cron_success.py"
    dummy_module_path.write_text("def run():\n    pass\n")

    sys.path.insert(0, str(tmp_path))

    try:
        job = CronJob(id='dummy_success', name='Dummy', schedule='* * * * *', module='dummy_cron_success')
        runner = CronRunner()
        result = runner.run_job(job)
        assert result.ok is True
        assert result.id == 'dummy_success'
        assert result.error is None
    finally:
        sys.path.remove(str(tmp_path))

def test_runner_run_job_failure(tmp_path):
    # Create a dummy module with a run() function that raises an exception
    dummy_module_path = tmp_path / "dummy_cron_failure.py"
    dummy_module_path.write_text("def run():\n    raise ValueError('Simulated failure')\n")

    sys.path.insert(0, str(tmp_path))

    try:
        job = CronJob(id='dummy_failure', name='Dummy', schedule='* * * * *', module='dummy_cron_failure')
        runner = CronRunner()
        result = runner.run_job(job)
        assert result.ok is False
        assert result.id == 'dummy_failure'
        assert "Simulated failure" in result.error
    finally:
        sys.path.remove(str(tmp_path))

def test_runner_logs_to_file(tmp_path):
    dummy_module_path = tmp_path / "dummy_cron_log.py"
    dummy_module_path.write_text("def run():\n    pass\n")
    sys.path.insert(0, str(tmp_path))

    runner = CronRunner()
    results_file = str(tmp_path / "cron_results.json")
    runner.results_file = results_file

    job = CronJob(id='dummy_log', name='Dummy Log', schedule='* * * * *', module='dummy_cron_log')
    # Use a fresh registry to avoid running other jobs
    runner.registry._jobs = {}
    runner.registry.register(job)

    try:
        runner.run_all_enabled()

        assert os.path.exists(results_file)
        with open(results_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["id"] == "dummy_log"
            assert data["ok"] is True
    finally:
        sys.path.remove(str(tmp_path))
