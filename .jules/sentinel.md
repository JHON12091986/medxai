## 2026-06-08 - [CRITICAL] Command Injection Risk with shell=True in tools/agynina.py
**Vulnerability:** Found `subprocess.run` calls in `tools/agynina.py` that utilized `shell=True` without tokenizing input variables via `shlex.split`, presenting a risk of command injection, especially where `run_cmd` can accept untrusted input or when arguments are concatenated in `f"{AIDER_PATH} {files_str}"`.
**Learning:** Even though `upgradepipeline.py` explicitly bans `subprocess.*shell\s*=\s*True`, some administrative tooling (like `agynina.py`) used it out of convenience without proper injection safeguards. Python's `shlex.split()` combined with `shell=False` is a secure and simple solution for most commands.
**Prevention:** Always use `shell=False` combined with a tokenized argument list (e.g. `shlex.split()`) instead of string formatting with `shell=True`, unless relying heavily on bash pipelines (`|`) or logical operators (`&&`), which should themselves be heavily scrutinized.
## 2026-06-08 - [CRITICAL] Fix command injection risk in guardian_engine.py
**Vulnerability:** Found `subprocess.run` being called with `use_shell=True` and un-tokenized string commands in `guardian_engine.py` when invoking `healthcheck.py`.
**Learning:** Even internal tool invocations that appear safe because they use local variables (like NINA_DIR) are flagged by our security scanners (tools/agynina.py and healthcheck.py) and represent a bad practice. The parameter `use_shell=True` allows shell operators and requires the command to be passed as a single string.
**Prevention:** Always use `use_shell=False` (or `shell=False`) in `subprocess.run` and pass the command and its arguments as a list of strings (`[str(python_bin), str(healthcheck_path), "--json"]`). This explicitly prevents shell interpretation of any variable content.

## 2026-06-10 - [CRITICAL] Exception Handlers and Mocking
**Vulnerability:** Found generic `except Exception as e:` blocks in multiple tool files (`jules_api.py`, `model_discovery.py`, etc.).
**Learning:** Using generic exceptions hides logic bugs (like `KeyError` in JSON structures) and makes debugging difficult. Furthermore, when mocking `httpx.RequestError` in tests, it requires a mandatory `request` keyword argument, else the mock itself throws a `TypeError`.
**Prevention:** Always replace bare `except:` or `except Exception:` with explicit exception types (`OSError`, `ValueError`, `httpx.RequestError`, etc.) and ensure `logger.error` or `logger.warning` captures the failure. In tests, explicitly provide `request=MagicMock()` to `httpx.RequestError`.
