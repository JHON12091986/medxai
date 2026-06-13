## 2026-06-13 - [Security Rules Tightening]
**Vulnerability:** Weak security scanning pattern in `upgradepipeline.py` allowed missing coverage for risky system functions.
**Learning:** Hardcoded tools allowed `subprocess.check_output`, `subprocess.Popen`, `subprocess.call` and `os.system` missing proper constraints, risking remote execution. `shutil.rmtree` was also not blocked.
**Prevention:** Extend regex list of `DANGEROUS_PATTERNS` to uniformly cover shell risk aliases and explicit file deletion risk functions.
