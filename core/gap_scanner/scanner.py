class GapScanner:
    def __init__(self, telemetry_path: str, register_path: str, backlog_path: str, repo_root: str = "."):
        self.telemetry_path = telemetry_path
        self.register_path  = register_path
        self.backlog_path   = backlog_path
        self.repo_root      = repo_root

    def run_cycle(self):
        from .telemetry_scan      import scan_telemetry
        from .error_register_scan import scan_error_register
        from .hygiene_scan        import scan_hygiene
        from .backlog_drafter     import draft_gaps
        import logging
        log = logging.getLogger("gap_scanner")

        try:
            gaps = (
                scan_telemetry(self.telemetry_path) +
                scan_error_register(self.register_path) +
                scan_hygiene(self.repo_root)
            )
            drafted = draft_gaps(gaps, self.backlog_path)
            if drafted:
                log.info(f"GapScanner: drafted {drafted} new gap(s) into backlog")
        except MemoryError:
            log.error("GapScanner: MemoryError — skipping cycle")
        except Exception as exc:
            log.error(f"GapScanner: cycle error: {exc}")
