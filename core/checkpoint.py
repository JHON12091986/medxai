"""
NINA LangGraph-style SQLite-Backed State Checkpoint & Resume Pattern
Saves execution graph step-states, enabling complete recovery and step resumption.
"""
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

class SqliteCheckpointManager:
    def __init__(self, db_path: str = "data/checkpoints.db") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    session_id TEXT,
                    step_id INTEGER,
                    state_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, step_id)
                )
            """)
            conn.commit()

    def save_checkpoint(self, session_id: str, step_id: int, state: Dict[str, Any]) -> None:
        """
        Saves a dictionary representing the agent state at a specific graph step.
        """
        state_json = json.dumps(state)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints (session_id, step_id, state_json) VALUES (?, ?, ?)",
                (session_id, step_id, state_json)
            )
            conn.commit()

    def load_latest_checkpoint(self, session_id: str) -> Optional[Tuple[int, Dict[str, Any]]]:
        """
        Loads the latest (highest step_id) checkpoint state for a given session.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT step_id, state_json FROM checkpoints WHERE session_id = ? ORDER BY step_id DESC LIMIT 1",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                step_id, state_json = row
                return step_id, json.loads(state_json)
        return None

    def clear_checkpoints(self, session_id: str) -> None:
        """
        Clears all checkpoints associated with a session.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM checkpoints WHERE session_id = ?", (session_id,))
            conn.commit()
