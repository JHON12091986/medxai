import argparse
import json
import logging
import subprocess
import threading
import time
import os
import fnmatch
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger("nina_sync")


class NINASync:
    def __init__(self, repo_path=".", branch="main",
                 interval=30, protect_main=False, dry_run=False):
        self.repo_path = Path(repo_path).resolve()
        self.branch = branch
        self.interval = interval
        self.protect_main = protect_main
        self.dry_run = dry_run

        self.state_file = self.repo_path / "logs" / ".nina_sync.state"
        self._load_state()

        self._last_commit_time = 0
        self._debounce_timer = None
        self._pending_files = set()
        self._pending_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._ninaignore = self._load_ninaignore()
        self._setup_logging()

    def _load_state(self):
        self.sync_paused = False
        self.stop_requested = False
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                self.sync_paused = state.get("paused", False)
                self.stop_requested = state.get("stop", False)
            except Exception:
                pass

    def _save_state(self):
        try:
            self.state_file.parent.mkdir(exist_ok=True)
            self.state_file.write_text(json.dumps({"paused": self.sync_paused, "stop": self.stop_requested}))
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def pause(self):
        self._load_state()
        self.sync_paused = True
        self._save_state()

    def resume(self):
        self._load_state()
        self.sync_paused = False
        self._save_state()

    def request_stop(self):
        self._load_state()
        self.stop_requested = True
        self._save_state()

    def _setup_logging(self):
        log_dir = self.repo_path / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "nina_sync.log"

        handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(handler)
            logger.addHandler(console)

    def log_event(self, event_type, file=None, commit=None, ts=None, **kwargs):
        ts = ts or time.strftime("%Y-%m-%dT%H:%M:%S%z")
        log_data = {"event": event_type, "ts": ts}
        if file:
            log_data["file"] = str(file)
        if commit:
            log_data["commit"] = commit
        log_data.update(kwargs)

        json_str = json.dumps(log_data)

        for h in logger.handlers:
            if isinstance(h, RotatingFileHandler):
                h.setFormatter(logging.Formatter('%(message)s'))
                logger.info(json_str)

        human_readable = f"[{event_type.upper()}] "
        if file: human_readable += f"file: {file} "
        if commit: human_readable += f"commit: {commit} "
        for k, v in kwargs.items(): human_readable += f"{k}: {v} "

        print(f"{ts} - INFO - {human_readable}")

    def _load_ninaignore(self):
        ignore_path = self.repo_path / ".ninaignore"
        patterns = []
        if ignore_path.exists():
            for line in ignore_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        return patterns

    def _is_ignored(self, filepath):
        rel_path = str(Path(filepath).relative_to(self.repo_path))
        if rel_path.startswith(".git") or "/.git/" in rel_path:
            return True

        for pattern in self._ninaignore:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
            if pattern.endswith("/") and rel_path.startswith(pattern):
                return True
            # Also check if any part of the path matches a pattern with trailing slash
            path_parts = Path(rel_path).parts
            for i in range(1, len(path_parts) + 1):
                sub_path = "/".join(path_parts[:i]) + "/"
                if fnmatch.fnmatch(sub_path, pattern):
                    return True
        return False

    def _run_git(self, args, check=False):
        if self.dry_run and args[0] in ["add", "commit", "push", "stash", "pull", "pop"]:
            self.log_event("dry-run", " ".join(["git"] + args))
            return "dry-run"

        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if not check:
                return e.stdout.strip() or e.stderr.strip()
            raise

    def _check_secrets(self):
        status = self._run_git(["status", "--porcelain"])
        for line in status.splitlines():
            # Catch .env and variants like .env.production
            if ".env" in line:
                return True
        return False

    def _schedule_commit(self, filepath):
        self._load_state()
        if self.sync_paused or self.stop_requested:
            return

        if Path(filepath).name == ".ninaignore":
            self._ninaignore = self._load_ninaignore()

        if self._is_ignored(filepath):
            return

        with self._pending_lock:
            self._pending_files.add(filepath)

        if self._debounce_timer:
            self._debounce_timer.cancel()

        self._debounce_timer = threading.Timer(5.0, self._do_commit_push)
        self._debounce_timer.start()

    def _do_commit_push(self):
        self._load_state()
        with self._pending_lock:
            if self.sync_paused or self.stop_requested or not self._pending_files:
                return

            now = time.time()
            if now - self._last_commit_time < 5.0:
                self._debounce_timer = threading.Timer(5.0, self._do_commit_push)
                self._debounce_timer.start()
                return

            if self._check_secrets():
                self.log_event("error", msg="Untracked secrets (.env) detected. Aborting push.")
                return

            files_to_commit = list(self._pending_files)
            self._pending_files.clear()

        # Filter out files that no longer exist (transient files) for git add
        valid_files = [f for f in files_to_commit if Path(f).exists()]
        # If no valid files but there were pending files, they might have been deleted,
        # which git add --all with pathspec handles if they were tracked.

        rel_files = [str(Path(f).relative_to(self.repo_path)) for f in files_to_commit]

        try:
            target_branch = self.branch

            # For protect main, we push to a different branch. We don't checkout
            # because that causes working tree issues.
            if self.protect_main and self.branch == "main":
                target_branch = f"sync/{int(now)}"

            if not self.dry_run:
                # Add all pending files. Using '--ignore-removal' if we don't want to fail on missing,
                # but 'git add --all <pathspec>' works too if pathspec is valid. To prevent transient file crashes,
                # we do git add on valid files, and for deleted files we do git rm --cached if they were tracked,
                # or just git add --all which handles it if we don't pass specific files but that adds everything.
                # Since we know the files, let's just use `git add` for existing ones, and `git add -u` for tracking removals.
                if valid_files:
                    valid_rel = [str(Path(f).relative_to(self.repo_path)) for f in valid_files]
                    self._run_git(["add"] + valid_rel, check=False) # Ignore errors on add

                # Update index for tracked files (handles deletions)
                self._run_git(["add", "-u"], check=False)

            commit_msg = f"auto: sync {len(rel_files)} files @ {time.strftime('%Y-%m-%dT%H:%M:%S')}"

            if not self.dry_run:
                try:
                    self._run_git(["commit", "-m", commit_msg], check=True)
                except subprocess.CalledProcessError:
                    # Nothing to commit
                    return

                # Push HEAD to the target branch without checking it out
                self._run_git(["push", "origin", f"HEAD:{target_branch}"], check=True)

            self._last_commit_time = time.time()
            self.log_event("push", commit=commit_msg, files=len(rel_files))

            # Save the sync commit hash
            try:
                commit_hash = self._run_git(["rev-parse", "HEAD"]).strip()
                last_commit_file = self.repo_path / "data" / ".last_sync_commit"
                last_commit_file.parent.mkdir(exist_ok=True)
                last_commit_file.write_text(commit_hash)
            except Exception as e:
                self.log_event("incremental_sync_error", msg=f"Failed to record last sync commit: {e}")

            from core.observability import get_hub
            get_hub().set_sync_ts()

        except subprocess.CalledProcessError as e:
            self.log_event("error", msg=f"Git operation failed: {e.stderr}")

    def _poll_remote(self):
        while not self._stop_event.is_set():
            self._load_state()
            if self.stop_requested:
                self.stop()
                break

            if not self.sync_paused:
                try:
                    self._run_git(["fetch", "origin"])

                    # Check if remote is ahead by checking the number of commits remote has that local doesn't
                    behind = self._run_git(["rev-list", "--count", f"HEAD..origin/{self.branch}"])

                    if behind and behind.isdigit() and int(behind) > 0:
                        self._pull_remote()
                except Exception as e:
                    self.log_event("error", msg=f"Remote polling error: {e}")

            for _ in range(self.interval):
                if self._stop_event.is_set() or self.stop_requested:
                    break
                time.sleep(1)

    def _pull_remote(self):
        stashed = False
        try:
            self.log_event("pull_started")
            stash_out = self._run_git(["stash"])
            if "No local changes to save" not in stash_out:
                stashed = True

            # Pull with --no-edit to avoid hanging
            self._run_git(["pull", "--no-edit", "origin", self.branch], check=True)

            if stashed:
                try:
                    self._run_git(["stash", "pop"], check=True)
                except subprocess.CalledProcessError as e:
                    self._handle_conflict(e.stdout + e.stderr)
                    return
            self.log_event("pull_success")
        except subprocess.CalledProcessError as e:
            self.log_event("error", msg=f"Pull failed: {e}")
            if stashed:
                # Attempt to pop if pull failed, or leave it.
                # Actually, if pull fails (e.g. merge conflict in pull itself), we should still restore stash
                # but if we restore stash it might conflict with the partial pull.
                # Let's restore it anyway.
                try:
                    self._run_git(["stash", "pop"], check=False)
                except:
                    pass

    def _handle_conflict(self, output):
        self.pause()
        msg = f"Merge conflict detected during sync:\n{output}\nRun 'python tools/nina_sync.py --resume' after resolving."
        self.log_event("conflict", msg=msg)
        print(f"CONFLICT: {msg}")

        try:
            from core.config import NinaConfig
            # from interfaces.telegram_interface import TelegramInterface
            import asyncio

            config = NinaConfig()

            # Use bot to send directly
            from telegram.ext import ApplicationBuilder

            if config.telegram_bot_token and config.authorized_user_id:
                async def send_alert():
                    app = ApplicationBuilder().token(config.telegram_bot_token).build()
                    await app.bot.send_message(
                        chat_id=config.authorized_user_id,
                        text=f"⚠️ NINA Sync Conflict:\n{msg}"
                    )

                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                if loop.is_running():
                    asyncio.create_task(send_alert())
                else:
                    loop.run_until_complete(send_alert())
        except Exception as e:
            self.log_event("error", msg=f"Failed to send Telegram alert: {e}")

    def start(self):
        self.stop_requested = False

        # Lightning Sync: Incremental backup logic
        try:
            last_commit_file = self.repo_path / "data" / ".last_sync_commit"
            sync_base = "HEAD~1"
            if last_commit_file.exists():
                sync_base = last_commit_file.read_text().strip()

            diff_out = self._run_git(["diff", "--name-only", sync_base, "HEAD"])
            for line in diff_out.splitlines():
                if line.strip():
                    fpath = self.repo_path / line.strip()
                    if fpath.exists():
                        self._schedule_commit(str(fpath))
            self.log_event("incremental_sync", msg=f"Scheduled {len(self._pending_files)} changed files from diff.")
        except Exception as e:
            self.log_event("incremental_sync_error", msg=f"Failed diff: {e}")

        self._save_state()

        self.observer = Observer()
        self.observer.schedule(_LocalChangeHandler(self), str(self.repo_path), recursive=True)
        self.observer.start()

        self.remote_thread = threading.Thread(target=self._poll_remote, daemon=True)
        self.remote_thread.start()

        self.log_event("start", msg="Sync daemon started")

    def stop(self):
        self._stop_event.set()
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        if hasattr(self, 'remote_thread'):
            self.remote_thread.join()
        self.log_event("stop", msg="Sync daemon stopped")

class _LocalChangeHandler(FileSystemEventHandler):
    def __init__(self, sync: NINASync):
        self.sync = sync

    def on_modified(self, event):
        if not event.is_directory:
            self.sync._schedule_commit(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.sync._schedule_commit(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.sync._schedule_commit(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.sync._schedule_commit(event.src_path)
            self.sync._schedule_commit(event.dest_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NINA Bidirectional Git Sync")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--branch", type=str, default="main")
    parser.add_argument("--protect-main", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sync = NINASync(
        branch=args.branch,
        interval=args.interval,
        protect_main=args.protect_main,
        dry_run=args.dry_run
    )

    if args.status:
        sync._load_state()
        print(f"Sync Paused: {sync.sync_paused}")
        print(f"Stop Requested: {sync.stop_requested}")
        print(f"Branch: {sync.branch}")
        print(f"Interval: {sync.interval}s")
        sys.exit(0)

    if args.pause:
        sync.pause()
        print("Sync paused.")
        sys.exit(0)

    if args.resume:
        sync.resume()
        print("Sync resumed.")
        sys.exit(0)

    if args.stop:
        sync.request_stop()
        print("Sync daemon stop requested.")
        sys.exit(0)

    if args.start:
        try:
            sync.start()
            while not sync._stop_event.is_set():
                sync._load_state()
                if sync.stop_requested:
                    sync.stop()
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            sync.stop()
