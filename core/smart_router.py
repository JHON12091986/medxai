import sqlite3
import time
from pathlib import Path
from typing import Any

class ProviderMetrics:
    def __init__(self, db_path: str = "data/router/provider_metrics.db") -> None:
        self.db_path = db_path
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    provider TEXT,
                    latency REAL,
                    success INTEGER,
                    query_type TEXT,
                    ts REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_query_type ON metrics(query_type)")
            conn.commit()

    def record_execution(self, provider: str, latency: float, success: bool, query_type: Any) -> None:
        provider_str = str(provider) if provider is not None else ""
        query_type_str = str(query_type) if query_type is not None else ""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO metrics (provider, latency, success, query_type, ts) VALUES (?, ?, ?, ?, ?)",
                (provider_str.lower(), latency, 1 if success else 0, query_type_str.lower(), time.time())
            )
            conn.commit()

    def select_best_provider(self, query_type: Any) -> str | None:
        query_type_str = str(query_type) if query_type is not None else ""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Select provider with lowest average latency and highest success rate in the last 100 runs for this query_type
            cursor.execute("""
                SELECT provider, AVG(latency) as avg_lat, AVG(success) as success_rate
                FROM metrics
                WHERE query_type = ?
                GROUP BY provider
                HAVING success_rate >= 0.8
                ORDER BY avg_lat ASC
                LIMIT 1
            """, (query_type_str.lower(),))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None


class SmartRouter(ProviderMetrics):
    def __init__(self, db_path: str = "data/router/provider_metrics.db", w1: float = 1000.0, w2: float = 1.0) -> None:
        super().__init__(db_path=db_path)
        self.w1 = w1
        self.w2 = w2

    def record_invocation(self, provider: str, task_type: str, latency: float, success: bool) -> None:
        self.record_execution(provider, latency, success, task_type)

    def get_best_provider(self, task_type: str) -> str | None:
        task_type_str = str(task_type) if task_type is not None else ""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT provider, AVG(latency) as avg_lat, AVG(success) as success_rate
                FROM metrics
                WHERE query_type = ?
                GROUP BY provider
            """, (task_type_str.lower(),))
            rows = cursor.fetchall()
            if not rows:
                return None
            best_provider = None
            best_score = -float('inf')
            for row in rows:
                provider, avg_lat, success_rate = row
                # Score = (Success Rate * w1) - (Average Latency * w2)
                score = (success_rate * self.w1) - (avg_lat * self.w2)
                if score > best_score:
                    best_score = score
                    best_provider = provider
            return best_provider

