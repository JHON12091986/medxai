# agy Anti-Patterns — What NOT To Do

This file is a negative example bank. Every entry is a real failure mode.
Read before starting any task. If your plan matches a pattern here, STOP and redesign.

---

## P001 — Blind Append to Config or List
**Pattern:** Adding a new entry to a list/dict/config without checking if it already exists.
**Consequence:** Duplicate entries, double-loaded providers, infinite loops in routers.
**Fix:** Always guard with `if X not in collection` before appending.
```python
# BAD
PROVIDERS.append("groq")  # might already be there

# GOOD
if "groq" not in PROVIDERS:
    PROVIDERS.append("groq")
```

---

## P002 — Touching Protected Files Without Explicit Instruction
**Pattern:** Editing `telegram_interface.py`, `.env`, `core/router.py`, `main.py`, `guardian_engine.py`, `tools/shell.py`, or `ninagate/main.py` as a side-effect of another task.
**Consequence:** Service outage, broken routing, lost Telegram connection.
**Fix:** These files require explicit instruction + explicit `Do NOT touch` exemption. If a task naturally reaches into them, STOP and report.

---

## P003 — Committing Without Running py_compile
**Pattern:** Editing a `.py` file and committing without running `python3 -m py_compile <file>`.
**Consequence:** Syntax errors go to production, services crash on restart.
**Fix:** `py_compile` + `pyflakes` are mandatory before every commit. No exceptions.

---

## P004 — Bundling Unrelated Edits in One Commit
**Pattern:** Fixing a bug AND adding a new feature in the same commit.
**Consequence:** Rollback of the bug fix also removes the feature. Blame is ambiguous.
**Fix:** One logical change = one commit. Split unrelated edits into sequential tasks.

---

## P005 — Renaming Without Grep-Verifying All Callers
**Pattern:** Renaming a function or variable in one file without checking all files that call it.
**Consequence:** `NameError` or `AttributeError` at runtime in a different module.
**Fix:** Use `agy_impact_check.py` before renaming. Verify all callers are updated.

---

## P006 — Editing Deep Dependencies Last
**Pattern:** In a multi-file task, editing the top-level orchestrator first, then the module it depends on.
**Consequence:** Intermediate commits break the service because the dependency isn't updated yet.
**Fix:** Always edit in dependency order — deepest (fewest callers) first, top-level last.

---

## P007 — Heredoc / Bash Echo for Python Log Appends
**Pattern:** Using `echo "..." >> logfile.txt` or `cat <<EOF >> file.py` to append Python code.
**Consequence:** Indentation corruption, encoding issues, partial writes on interrupt.
**Fix:** All log appends and file writes must go through Python. Bash echo is for shell scripts only.

---

## P008 — Skipping Session Journal Entry
**Pattern:** Completing a task and committing without appending to `agy_session.md`.
**Consequence:** The next task has no context. agy re-discovers what was already done, risks double-changes.
**Fix:** Append the mandatory session journal block after every successful commit. It is non-negotiable.

---

## P009 — Resolving Merge Conflicts Blindly
**Pattern:** Encountering a git merge conflict and resolving it by picking one side without understanding both.
**Consequence:** Silent data loss — a valid change from one branch disappears.
**Fix:** STOP immediately. Report the conflict to Perplexity. Never resolve blind.

---

## P010 — Using Fixed Line Numbers for Edits
**Pattern:** Targeting `line 247` for a change instead of targeting the function or symbol name.
**Consequence:** Line numbers drift with every commit. The edit lands in the wrong place.
**Fix:** Always target by function name, class name, or unique string pattern — never by line number.

---

## P011 — Ignoring juleslock.txt
**Pattern:** Editing a file that appears in `juleslock.txt` because the task "needs" it.
**Consequence:** Collision with an in-flight Jules task. Merge conflict guaranteed.
**Fix:** Pre-flight step 2 is mandatory. If the file is locked, STOP. Wait for Jules to open a PR, then agy merges it first.

---

## P012 — AST-Context Fallback Treated as Ground Truth
**Pattern:** Using the `--inject-context` grep-fallback window as definitive proof that a function exists at those lines.
**Consequence:** Context window shows partial code; agy edits the wrong block or misses the real function.
**Fix:** AST extraction names the function explicitly (`AST-extracted: func_name() lines N-M`). If the header says "fallback", treat context as orientation only — read the full function before editing.

---

*Last updated: nina-20260616-008 | Add entries here whenever a new failure mode is discovered.*
