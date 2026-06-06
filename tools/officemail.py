# Wrapper to maintain backwards compatibility while introducing the new office_mail.py

from .office_mail import (
    EWSConnection,
    EmailItem,
    fetch_messages,
    triage_messages,
    fetch,
)

__all__ = [
    "EWSConnection",
    "EmailItem",
    "fetch_messages",
    "triage_messages",
    "fetch",
]
