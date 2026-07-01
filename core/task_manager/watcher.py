import time
import threading
import logging
from core.task_manager.queue import TaskQueue

logger = logging.getLogger("nina.task_manager.watcher")

class QueueWatcher:
    """
    Watches data/task_queue.json for new PENDING tasks.
    Uses polling (no inotify dependency) — checks every `interval` seconds.
    On new task detected: calls callback(task_spec).
    Runs in a daemon thread — safe to start from crons/manager.py.
    """

    def __init__(self, queue: TaskQueue, callback, interval: int = 30):
        self.queue = queue
        self.callback = callback
        self.interval = interval
        self.seen_task_ids = set()
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Start the watcher daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            return

        # Populate seen tasks from what is already in the queue to only trigger for NEW tasks
        try:
            for task in self.queue.list_all():
                self.seen_task_ids.add(task.task_id)
        except Exception as e:
            logger.error(f"QueueWatcher failed to populate initial tasks: {e}")

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="NINATaskQueueWatcher")
        self._thread.start()
        logger.info("QueueWatcher started.")

    def stop(self):
        """Stop the watcher thread gracefully."""
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=5)
        self._thread = None
        logger.info("QueueWatcher stopped.")

    def _run(self):
        while not self._stop_event.is_set():
            try:
                pending = self.queue.list_pending()
                for task in pending:
                    if task.task_id not in self.seen_task_ids:
                        self.seen_task_ids.add(task.task_id)
                        try:
                            self.callback(task)
                        except Exception as e:
                            logger.error(f"Error in QueueWatcher callback: {e}")
            except Exception as e:
                logger.error(f"Error in QueueWatcher loop: {e}")

            # Sleep in small increments to respond quickly to stop event
            for _ in range(self.interval):
                if self._stop_event.is_set():
                    break
                time.sleep(1)
