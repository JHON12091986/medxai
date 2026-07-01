from checks.runner import record, ENV_FILE
def check_env_file():
    if ENV_FILE.exists():
        record("PASS", "env.file_present", ".env file present")
    else:
        record(
            "BLOCKER", "env.file_missing",
            ".env file missing",
            detail=f"Expected at: {ENV_FILE}",
            fix="Create ~/nina/.env with required keys. See nina_problem_log.md §R-10.",
        )

def load_env():
    env = {}
    if not ENV_FILE.exists():
        return env
    for line in ENV_FILE.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env

def check_env_keys(env):
    BLOCKER_KEYS = [
        ("TELEGRAM_BOT_TOKEN",  "config.missing_env.telegrambottoken"),
        ("TELEGRAM_CHAT_ID",     "config.missing_env.telegramchatid"),
        ("API_SECRET_KEY",        "config.missing_env.apisecretkey"),
    ]
    ADVISORY_KEYS = [
        ("TELEGRAMCHATID",    "config.missing_env.telegramchatid"),
    ]

    for key, sig_id in BLOCKER_KEYS:
        val = env.get(key, "").strip()
        if val:
            record("PASS", f"env.{key.lower()}", f"Env key present: {key}")
        else:
            record(
                "BLOCKER", sig_id,
                f"Env key MISSING or EMPTY: {key}",
                detail=f"Key '{key}' is required for NINA to start.",
                fix=f"Add {key}=<value> to ~/nina/.env and re-run guardian.",
            )

    for key, sig_id in ADVISORY_KEYS:
        val = env.get(key, "").strip()
        if val:
            record("PASS", f"env.{key.lower()}", f"Env key present: {key}")
        else:
            record(
                "INFO", sig_id,
                f"Env key missing (non-blocking): {key}",
                detail="TELEGRAMCHATID enables proactive notifications. Not required for startup.",
                fix=f"Optionally add {key}=<your_chat_id> to ~/nina/.env.",
            )
