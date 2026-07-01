import json
import time
import asyncio
from pathlib import Path

class SupplyLedger:
    def __init__(self, health_tracker: dict):
        self.health_tracker = health_tracker
        self.snapshot_file = Path("data/supply_snapshot.json")

    async def run_loop(self):
        while True:
            try:
                total = len(self.health_tracker)
                if total > 0:
                    degraded = sum(1 for h in self.health_tracker.values() if h.cb.state != "CLOSED")
                    pressure = degraded / total
                else:
                    pressure = 1.0

                snapshot = {
                    "ts": time.time(),
                    "pressure": pressure
                }

                self.snapshot_file.parent.mkdir(parents=True, exist_ok=True)
                self.snapshot_file.write_text(json.dumps(snapshot, indent=2))
            except Exception:
                pass

            await asyncio.sleep(30)
