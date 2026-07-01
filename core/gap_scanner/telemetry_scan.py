import json
import os
from .models import GapItem

def scan_telemetry(telemetry_path: str, tail_lines: int = 500) -> list[GapItem]:
    if not os.path.exists(telemetry_path):
        return []

    gaps = []

    try:
        with open(telemetry_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = lines[-tail_lines:]

            provider_counts = {}

            for line in lines:
                try:
                    data = json.loads(line)

                    if data.get('level') == 'ERROR':
                        err_msg = data.get('message', 'Unknown error')
                        gaps.append(GapItem(
                            source="telemetry",
                            raw_text=f"ERROR level detected: {err_msg}",
                            priority="P1"
                        ))

                    if 'latency_ms' in data and data['latency_ms'] > 5000:
                        gaps.append(GapItem(
                            source="telemetry",
                            raw_text=f"High latency detected: {data['latency_ms']}ms",
                            priority="P2"
                        ))

                    provider = data.get('provider')
                    if provider:
                        provider_counts[provider] = provider_counts.get(provider, 0) + 1

                except json.JSONDecodeError:
                    continue

    except Exception:
        pass

    return gaps
