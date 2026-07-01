import os
import re
from datetime import datetime, timezone
from .models import GapItem

def draft_gaps(gaps: list[GapItem], backlog_path: str) -> int:
    if not gaps:
        return 0

    try:
        content = ""
        if os.path.exists(backlog_path):
            with open(backlog_path, 'r', encoding='utf-8') as f:
                content = f.read()

        existing_ids = set(re.findall(r"<!-- gap_id: ([a-f0-9]{12}) -->", content))

        new_blocks = []
        for gap in gaps:
            if gap.gap_id not in existing_ids:
                iso_timestamp = datetime.now(timezone.utc).isoformat()
                block = f"""
---
### [GAP-AUTO] {gap.raw_text}  <!-- gap_id: {gap.gap_id} -->
**Source:** {gap.source} | **Priority:** {gap.priority} | **Status:** {gap.status}
**Auto-drafted:** {iso_timestamp} by GapScanner RAID-2
---
"""
                new_blocks.append(block)
                existing_ids.add(gap.gap_id)

        if not new_blocks:
            return 0

        new_content = content + "".join(new_blocks)
        tmp_path = backlog_path + ".tmp"

        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        os.replace(tmp_path, backlog_path)

        return len(new_blocks)

    except Exception:
        return 0
