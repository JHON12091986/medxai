"""telemetry — Namespace shim layer for NINA's OpenTelemetry subsystem.
Blueprint: nina_blueprint_23.06.2026.md § II (telemetry/ namespace)
Pass 2 · 25 Jun 2026
"""
from telemetry.tracker import Tracker
from telemetry.emitter import emit

__all__ = ["Tracker", "emit"]
