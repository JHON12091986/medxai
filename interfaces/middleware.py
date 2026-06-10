import time
from collections import defaultdict
from typing import List, Dict

class RateLimiter:
    def __init__(self, max_calls: int = 10, period_seconds: int = 60):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.users: Dict[int, List[float]] = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        now = time.time()
        # Clean up old timestamps
        self.users[user_id] = [t for t in self.users[user_id] if now - t <= self.period_seconds]

        if len(self.users[user_id]) >= self.max_calls:
            return False

        self.users[user_id].append(now)
        return True

class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Dict[str, str]] = {}

    def register(self, command: str, handler_name: str, description: str):
        self.commands[command] = {
            "command": command,
            "handler_name": handler_name,
            "description": description
        }

    def get_all(self) -> List[Dict[str, str]]:
        return list(self.commands.values())

    def is_registered(self, command: str) -> bool:
        return command in self.commands
