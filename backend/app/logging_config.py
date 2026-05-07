"""Structured logging setup."""

from __future__ import annotations

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Configure root logger from application settings."""
    root = logging.getLogger()
    root.setLevel(settings.logging.level)

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(settings.logging.format))
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
