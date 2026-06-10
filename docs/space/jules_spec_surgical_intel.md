🛠️ MEGA-TASK: NF-EXT Surgical Code Intelligence (AG-M-03)
Assignee: Jules (Async Cloud Coder)
Objective: Implement local code research tools in ninaflash to eliminate the need for full-file reads in the cloud.

🏗️ Domain 1: Symbol Extraction
- nf code symbol <file> <name>: Use Python's `ast` module to parse the file and return only the source code for the specified class or function.
- nf find-symbol <name>: Recursively search the repository for where the specified class or function is defined and return its file path and line number.

🧠 Domain 2: Symbol Mapping
- nf code sigs <dir>: Generate a high-density map of all function and class signatures in a directory. Output should include docstrings but skip method bodies.

📉 Domain 3: Docstring Search
- nf code doc <keyword>: Search for keywords only within docstrings to help find relevant tools and logic without full-text grep.

📝 Acceptance Criteria:
- All commands must be implemented as named functions in `ninaflash.py`.
- No new dependencies; use standard library `ast` and `pathlib`.
- Provide unit tests in `tests/test_ninaflash_ext.py`.
