import os
import re
from .models import GapItem

def scan_error_register(register_path: str) -> list[GapItem]:
    if not os.path.exists(register_path):
        return []

    gaps = []
    open_row_pattern = re.compile(r'\|\s*OPEN\s*\|\s*(CRITICAL|HIGH|MEDIUM|LOW)\s*\|.*?\|\s*([^|]+)\s*\|', re.IGNORECASE)

    try:
        with open(register_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = open_row_pattern.search(line)
                if match:
                    severity = match.group(1).upper()
                    title = match.group(2).strip()

                    priority = "P3"
                    if severity == "CRITICAL":
                        priority = "P1"
                    elif severity == "HIGH":
                        priority = "P2"

                    gaps.append(GapItem(
                        source="error_register",
                        raw_text=f"Fix {severity} bug: {title}",
                        priority=priority
                    ))
    except Exception:
        pass

    return gaps
