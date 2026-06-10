import re

LOG_FILE = "nina_update_log.md"

def append_to_log():
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()

        # Find the last entry number
        matches = re.findall(r'### Entry (\d+)', content)
        if matches:
            next_num = int(matches[-1]) + 1
        else:
            next_num = 1

        new_entry = f"""
### Entry {next_num:03d} - 2026-06-06
**Title:** Implement F-04 Expenditure Tracker
**Changes:**
- Added `tools/finance.py` with `run_expenditure_report` to process CSV/text expenses.
- Registered finance tool in `tools/__init__.py` and `core/capabilities.py`.
- Added unit tests in `tests/test_finance.py`.
- Updated `nina_context.md` status.
**Verification:**
- Ran `python3 -m py_compile` and `pyflakes` on all changed files successfully.
- Ran tests in `tests/test_finance.py`.
**Rollback:** git checkout previous commit
"""
        with open(LOG_FILE, 'a') as f:
            f.write(new_entry)

        print(f"Appended Entry {next_num:03d} to {LOG_FILE}")
    except Exception as e:
        print(f"Error appending to log: {e}")

if __name__ == "__main__":
    append_to_log()
