import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = REPO_ROOT / "data"
LEDGER_FILE = DATA_DIR / "session_ledger.json"
PREAMBLE_FILE = DATA_DIR / "gemini_preamble.md"

def generate_preamble(tool: str = 'gemini_cli', max_mistakes: int = 5) -> str:
    try:
        if not LEDGER_FILE.exists():
            return ''

        with open(LEDGER_FILE, 'r') as f:
            ledgers = json.load(f)

        target_session = None
        for ledger in reversed(ledgers):
            if ledger.get('tool') == tool and ledger.get('status') in ('interrupted', 'error', 'active'):
                target_session = ledger
                break

        if not target_session:
            return ''

        task_id = target_session.get('task_id') or 'unknown'
        started_at = target_session.get('started_at', 'unknown')[:16]
        status = target_session.get('status', 'unknown')

        plan = target_session.get('plan', [])
        plan_str = '; '.join(plan[:5])
        if len(plan) > 5:
            plan_str += '...'

        trace = target_session.get('trace', [])
        last_completed = 'none'
        for entry in reversed(trace):
            if entry.get('outcome') == 'success':
                last_completed = entry.get('action', 'none')
                break

        resume_hint = target_session.get('resume_hint', '')
        if not resume_hint:
            if trace:
                resume_hint = trace[-1].get('action', 'unknown')
            else:
                resume_hint = 'unknown'

        mistakes = target_session.get('mistakes', [])
        mistakes.sort(key=lambda x: x.get('seen_count', 0), reverse=True)
        mistake_lines = []
        for mistake in mistakes[:max_mistakes]:
            mistake_lines.append(f"- [{mistake.get('seen_count', 1)}x] {mistake.get('avoid', '')}")

        mistakes_str = '\n'.join(mistake_lines)

        preamble = f"""--- NINA SESSION RECOVERY PREAMBLE ---
PREVIOUS SESSION: {task_id} | started {started_at} | STATUS: {status}
PLAN WAS: {plan_str}
LAST COMPLETED STEP: {last_completed}
INTERRUPTED AT: {resume_hint}
MISTAKES TO AVOID (do not repeat these):
{mistakes_str}
--- RESUME FROM NEXT INCOMPLETE STEP. DO NOT REDO COMPLETED STEPS. ---"""

        # Hard cap at 600 chars, but carefully not to cut in middle if possible, or just slice.
        if len(preamble) > 600:
            preamble = preamble[:597] + "..."

        return preamble
    except Exception:
        return ''

def write_preamble_file(tool: str = 'gemini_cli') -> str:
    try:
        preamble = generate_preamble(tool)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(PREAMBLE_FILE, 'w') as f:
            f.write(preamble)
        return str(PREAMBLE_FILE)
    except Exception:
        return ''

def clear_preamble(tool: str = 'gemini_cli') -> None:
    try:
        if LEDGER_FILE.exists():
            with open(LEDGER_FILE, 'r') as f:
                ledgers = json.load(f)

            for ledger in reversed(ledgers):
                if ledger.get('tool') == tool and ledger.get('status') in ('interrupted', 'error', 'active'):
                    ledger['status'] = 'completed'
                    break

            tmp_file = DATA_DIR / "session_ledger.tmp"
            with open(tmp_file, "w") as f:
                json.dump(ledgers, f, indent=2)
            import os
            os.replace(tmp_file, LEDGER_FILE)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(PREAMBLE_FILE, 'w') as f:
            f.write('')
    except Exception:
        pass
