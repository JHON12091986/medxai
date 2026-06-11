import datetime
import subprocess
from pathlib import Path

BOLT_MD = Path(".jules/bolt.md")
AGENTS_MD = Path("AGENTS.md")


def extract_insights_and_append(summary_dict):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    title = summary_dict.get("title", "Session Complete")
    learning = summary_dict.get("learning", "No major learnings recorded.")
    action = summary_dict.get("action", "Continue standard operating procedure.")

    BOLT_MD.parent.mkdir(parents=True, exist_ok=True)

    entry = (
        f"\n## {date_str} - [{title}]\n**Learning:** {learning}\n**Action:** {action}\n"
    )

    if BOLT_MD.exists():
        with open(BOLT_MD, "a") as f:
            f.write(entry)
    else:
        with open(BOLT_MD, "w") as f:
            f.write(entry)


def append_routing_history(history_summary):
    if AGENTS_MD.exists():
        with open(AGENTS_MD, "a") as f:
            f.write(f"\n<!-- NinaGate Routing History: {history_summary} -->\n")


def run_sync():
    print("Running nina_sync.sh...")
    subprocess.run(["bash", "./nina_sync.sh"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Session End Protocol")
    parser.add_argument("--title", type=str, default="Session End")
    parser.add_argument("--learning", type=str, default="Default learning")
    parser.add_argument("--action", type=str, default="Default action")
    parser.add_argument("--history", type=str, default="No routing history provided")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    extract_insights_and_append(
        {"title": args.title, "learning": args.learning, "action": args.action}
    )
    append_routing_history(args.history)

    if not args.dry_run:
        run_sync()
    else:
        print("Dry run complete. Insights and history appended.")
