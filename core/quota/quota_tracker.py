"""Real-time quota tracker for all NINA tools and model providers. Persists state to config/quota_state.json. Resets daily at reset_hour_utc."""

import json
import logging
import os
import threading
from datetime import datetime, timezone

QUOTA_STATE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'quota_state.json')

class QuotaTracker:
    """Thread-safe quota tracker. Use QuotaTracker.get_instance() for the singleton."""
    
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'QuotaTracker':
        """Return the singleton QuotaTracker instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Load quota state from disk. Do not call directly — use get_instance()."""
        self._state: dict = {}
        self._file_lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load quota_state.json from disk. Log warning if file missing and use empty state."""
        try:
            with open(QUOTA_STATE_PATH, 'r') as f:
                self._state = json.load(f)
        except FileNotFoundError:
            logging.warning(f"Quota state file missing at {QUOTA_STATE_PATH}. Using empty state.")
            self._state = {'providers': {}}

    def _save(self) -> None:
        """Persist current state to disk atomically via a .tmp file."""
        tmp_path = QUOTA_STATE_PATH + '.tmp'
        with self._file_lock:
            with open(tmp_path, 'w') as f:
                json.dump(self._state, f, indent=2)
            os.replace(tmp_path, QUOTA_STATE_PATH)

    def _maybe_reset(self) -> None:
        """Reset all used counters if current UTC hour matches reset_hour_utc and last reset was not today."""
        with self._file_lock:
            if not self._state or 'providers' not in self._state:
                return
            
            reset_hour = self._state.get('reset_hour_utc', 18)
            now = datetime.now(timezone.utc)
            
            updated_at_str = self._state.get('updated_at', '2026-06-18T00:00:00Z')
            try:
                # Handle 'Z' or other ISO format offsets
                clean_str = updated_at_str.replace('Z', '+00:00')
                last_reset = datetime.fromisoformat(clean_str)
            except Exception:
                last_reset = datetime.fromisoformat('2026-06-18T00:00:00+00:00')

            # Compare today vs last reset date and current hour >= reset_hour
            if now.date() != last_reset.date() and now.hour >= reset_hour:
                for provider_info in self._state.get('providers', {}).values():
                    provider_info['used'] = 0
                self._state['updated_at'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')
                # Save is done outside or inside this lock. Let's write the file atomically now:
                # We can call self._save() but self._save() acquires self._file_lock as well!
                # To prevent deadlock, let's write to tmp_path directly here or use a helper that doesn't acquire the lock, 
                # or just write directly inside _maybe_reset since we already have the file lock.
                tmp_path = QUOTA_STATE_PATH + '.tmp'
                with open(tmp_path, 'w') as f:
                    json.dump(self._state, f, indent=2)
                os.replace(tmp_path, QUOTA_STATE_PATH)

    def consume(self, provider: str, amount: int = 1) -> bool:
        """Decrement quota for provider by amount. Returns True if allowed, False if over limit."""
        self._maybe_reset()
        with self._file_lock:
            providers = self._state.get('providers', {})
            if provider not in providers:
                return True  # unknown provider = unlimited
            
            p = providers[provider]
            if p['used'] + amount > p['daily_limit']:
                logging.warning(f"Quota exceeded for {provider}")
                return False
            
            p['used'] += amount
            
            # Since we already hold self._file_lock, let's write it to disk here directly to avoid deadlock with self._save()
            tmp_path = QUOTA_STATE_PATH + '.tmp'
            with open(tmp_path, 'w') as f:
                json.dump(self._state, f, indent=2)
            os.replace(tmp_path, QUOTA_STATE_PATH)
            return True

    def get_remaining(self, provider: str) -> int:
        """Return remaining quota for provider. Returns -1 if provider unknown."""
        self._maybe_reset()
        with self._file_lock:
            providers = self._state.get('providers', {})
            if provider not in providers:
                return -1
            p = providers[provider]
            return max(0, p['daily_limit'] - p['used'])

    def summary(self) -> dict:
        """Return a dict of {provider: remaining} for all tracked providers."""
        self._maybe_reset()
        with self._file_lock:
            providers = self._state.get('providers', {})
            return {k: max(0, v['daily_limit'] - v['used']) for k, v in providers.items()}
