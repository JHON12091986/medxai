## 2026-06-13 - [Security Rules Tightening]
**Vulnerability:** Weak security scanning pattern in `upgradepipeline.py` allowed missing coverage for risky system functions.
**Learning:** Hardcoded tools allowed `subprocess.check_output`, `subprocess.Popen`, `subprocess.call` and `os.system` missing proper constraints, risking remote execution. `shutil.rmtree` was also not blocked.
**Prevention:** Extend regex list of `DANGEROUS_PATTERNS` to uniformly cover shell risk aliases and explicit file deletion risk functions.

## 2026-06-13 - [Command Injection via os.system in ninaflash_core]
**Vulnerability:** A CRITICAL command injection vulnerability existed in `tools/ninaflash_core.py` within the `cmd_batch` function where `os.system` was used to execute a string containing unsanitized user input (`args.cmds`).
**Learning:** Hardcoding `os.system` along with string interpolation or concatenation opens up significant vectors for shell command injection, allowing an attacker to execute arbitrary commands.
**Prevention:** Always use `subprocess.run` (or similar `subprocess` methods) with `shell=False` and properly tokenized arguments using `shlex.split` or passing arguments as a list.
