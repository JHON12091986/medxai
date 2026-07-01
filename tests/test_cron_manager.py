from unittest.mock import MagicMock
from crons.manager import TaskScheduler
from apscheduler.triggers.interval import IntervalTrigger

def test_cron_manager_duplicate_add_no_error():
    # Instantiate TaskScheduler with a mock nina_os
    mock_nina = MagicMock()
    scheduler = TaskScheduler(mock_nina)
    
    def dummy_func():
        pass
        
    trigger = IntervalTrigger(minutes=5)
    
    # First add
    job1 = scheduler.add(dummy_func, trigger, id="test_duplicate_job")
    assert job1 is not None
    assert scheduler._sched.get_job("test_duplicate_job") is not None
    
    # Second add (should reschedule and not raise ConflictingIdError)
    job2 = scheduler.add(dummy_func, trigger, id="test_duplicate_job")
    assert job2 is not None
    assert scheduler._sched.get_job("test_duplicate_job") is not None
