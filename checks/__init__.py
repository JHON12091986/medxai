import sys
from checks.runner import emit_report, METRICS_MODE, JSON_MODE, run_metrics_server

def run_all():
    if METRICS_MODE:
        run_metrics_server()
        return 0
    if not JSON_MODE:
        print("\n  NINA Guardian 2.0 — Startup Safety Assertions")
        print("  " + "─" * 52)

    from checks.system_checks import check_python_version, check_data_dir, check_log_dir, check_ollama
    from checks.env_checks import check_env_file, load_env, check_env_keys
    from checks.package_checks import check_packages
    from checks.syntax_checks import check_syntax
    from checks.import_checks import check_core_imports
    from checks.router_checks import check_router_regressions
    from checks.security_checks import check_shell_allowlist, check_ssrf_guard, check_pipeline_security
    from checks.cron_checks import check_cron_ids
    from checks.state_checks import check_idle_queue_path, check_duplicate_log_handler

    check_python_version()
    check_env_file()
    env_data = load_env()
    check_env_keys(env_data)
    check_packages()
    check_syntax()
    check_core_imports()
    check_router_regressions()
    check_shell_allowlist()
    check_ssrf_guard()
    check_cron_ids()
    check_idle_queue_path()
    check_duplicate_log_handler()
    check_pipeline_security()
    check_data_dir()
    check_log_dir()
    check_ollama()

    return emit_report()

__all__ = ["run_all"]

if __name__ == '__main__':
    sys.exit(run_all())
