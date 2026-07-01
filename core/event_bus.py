#!/usr/bin/env python3
"""
NINA Event Bus Module
Provides an asynchronous, non-blocking Event Pub/Sub system
enabling decoupled service-to-service communication.
"""

import asyncio
import logging
import time
import json
import pathlib
from typing import Callable, Awaitable, Dict, List, Any, Union

logger = logging.getLogger("nina.event_bus")

class Event:
    def __init__(self, topic: str, data: Any = None, sender: str = "system"):
        self.topic = topic
        self.data = data
        self.sender = sender
        self.timestamp = time.time()

    def to_json(self) -> str:
        return json.dumps({
            "topic": self.topic,
            "data": self.data,
            "sender": self.sender,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        parsed = json.loads(json_str)
        obj = cls(parsed["topic"], parsed["data"], parsed["sender"])
        obj.timestamp = parsed["timestamp"]
        return obj

class EventBus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_file: str = "logs/event_bus.jsonl"):
        if getattr(self, "_initialized", False):
            return
        self._subscribers: Dict[str, List[Callable[[Event], Union[None, Awaitable[None]]]]] = {}
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._log_path = pathlib.Path(log_file)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._loop_task: Union[asyncio.Task, None] = None
        self._initialized = True

    def start(self):
        """Starts the event loop process task if not already running."""
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_loop_task = asyncio.create_task(self._process_queue())
            logger.info("EventBus loop started.")

    async def shutdown(self):
        """Gracefully shuts down the event bus queue processing."""
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            logger.info("EventBus loop stopped.")

    def subscribe(self, topic: str, callback: Callable[[Event], Union[None, Awaitable[None]]]):
        """Subscribes a callable handler to a given topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        if callback not in self._subscribers[topic]:
            self._subscribers[topic].append(callback)
            logger.debug(f"Subscribed callback to topic: {topic}")

    def unsubscribe(self, topic: str, callback: Callable[[Event], Union[None, Awaitable[None]]]):
        """Unsubscribes a callback handler from a topic."""
        if topic in self._subscribers and callback in self._subscribers[topic]:
            self._subscribers[topic].remove(callback)
            logger.debug(f"Unsubscribed callback from topic: {topic}")

    async def publish(self, topic: str, data: Any = None, sender: str = "system"):
        """Publishes an event to the queue asynchronously."""
        event = Event(topic, data, sender)
        await self._queue.put(event)
        self._log_event(event)

    def publish_sync(self, topic: str, data: Any = None, sender: str = "system"):
        """Synchronous publisher helper (thread-safe queue insert)."""
        event = Event(topic, data, sender)
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self._queue.put_nowait, event)
        except RuntimeError:
            # Fallback when no running loop is present in the current thread
            pass
        self._log_event(event)

    def _log_event(self, event: Event):
        """Appends events to a localized audit JSONL log file."""
        try:
            with open(self._log_path, "a") as f:
                f.write(event.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to log event in event bus: {e}")

    async def _process_queue(self):
        """Processes the internal queue and routes to matching subscribers."""
        while True:
            try:
                event = await self._queue.get()
                callbacks = self._subscribers.get(event.topic, [])
                # Also support wildcard topic subscriptions
                callbacks = callbacks + self._subscribers.get("*", [])

                for callback in callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(event))
                        else:
                            callback(event)
                    except Exception as handler_err:
                        logger.error(f"Error executing callback for topic {event.topic}: {handler_err}")
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as queue_err:
                logger.error(f"Error in EventBus processing: {queue_err}")
                await asyncio.sleep(1)
