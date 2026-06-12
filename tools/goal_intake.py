import sys
import asyncio
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"

async def parse_goal(goal_text: str):
    """Converts plain English goal into a structured Jules Spec."""
    print(f"Parsing goal: {goal_text}")
    
    # Placeholder: In a real v5.1 scenario, this would call NinaGate/NinaFlash
    # to perform the NLP translation. For the scaffold, we generate a valid row.
    
    backlog_text = BACKLOG_PATH.read_text() if BACKLOG_PATH.exists() else ""
    existing_ids = re.findall(r'^\|\s*(B-\d+)\s*\|', backlog_text, re.M)
    next_num = 1
    if existing_ids:
        nums = [int(i.split('-')[1]) for i in existing_ids]
        next_num = max(nums) + 1
        
    new_id = f"B-{next_num:03d}"
    new_row = f"| {new_id} | {goal_text[:50]} | `READY` | TBD | — | Auto-ingested via Goal Intake |"
    
    return new_row

def append_to_backlog(row: str):
    if not BACKLOG_PATH.exists():
        print("Backlog not found.")
        return
    
    content = BACKLOG_PATH.read_text()
    # Insert at the top of the P1 section for immediate attention
    marker = "## ██ P1 — HIGH"
    if marker in content:
        parts = content.split(marker)
        new_content = parts[0] + marker + "\n\n" + row + "\n" + parts[1]
        BACKLOG_PATH.write_text(new_content)
        print(f"Added to backlog: {row}")

async def run(goal: str):
    row = await parse_goal(goal)
    append_to_backlog(row)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/goal_intake.py 'your goal here'")
    else:
        asyncio.run(run(" ".join(sys.argv[1:])))
