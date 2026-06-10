
LOCK_FILE = "jules_lock.txt"
FILES_TOUCHED = ["tools/finance.py", "tools/__init__.py", "core/capabilities.py", "tests/test_finance.py", "nina_context.md", "nina_update_log.md"]

def update_lock_file():
    try:
        with open(LOCK_FILE, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("LOCKED_FILES="):
                files = line.strip().split('=')[1].split(',') if line.strip().split('=')[1] else []
                # Only add if not already in the list
                for f_touched in FILES_TOUCHED:
                    if f_touched not in files:
                        files.append(f_touched)
                lines[i] = "LOCKED_FILES=" + ",".join(files) + "\n"
                break

        with open(LOCK_FILE, 'w') as f:
            f.writelines(lines)

        print(f"Updated {LOCK_FILE}")
    except Exception as e:
        print(f"Error updating lock file: {e}")

if __name__ == "__main__":
    update_lock_file()
