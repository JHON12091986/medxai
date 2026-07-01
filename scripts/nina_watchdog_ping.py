#!/usr/bin/env python3
"""Call this from main.py's async loop to ping systemd watchdog.
Prevents nina.service from being killed as UNRESPONSIVE.

Usage in main.py:
    from scripts.nina_watchdog_ping import watchdog_ping
    # call every ~60s inside your main loop
    await watchdog_ping()
"""
import os
import asyncio

def _notify(state: str) -> None:
    """Send sd_notify message to systemd."""
    sock_path = os.environ.get("NOTIFY_SOCKET")
    if not sock_path:
        return  # not running under systemd, silently skip
    import socket
    if sock_path.startswith("@"):
        sock_path = "\0" + sock_path[1:]
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
        sock.connect(sock_path)
        sock.sendall(state.encode())

def watchdog_ping() -> None:
    """Synchronous watchdog keepalive ping."""
    _notify("WATCHDOG=1")

async def watchdog_ping_async() -> None:
    """Async watchdog keepalive ping (non-blocking)."""
    await asyncio.get_event_loop().run_in_executor(None, watchdog_ping)

def notify_ready() -> None:
    """Tell systemd nina is fully started (Type=notify)."""
    _notify("READY=1")

def notify_stopping() -> None:
    """Tell systemd nina is shutting down cleanly."""
    _notify("STOPPING=1")

def notify_status(msg: str) -> None:
    """Update systemd status string (visible in systemctl status)."""
    _notify(f"STATUS={msg}")
