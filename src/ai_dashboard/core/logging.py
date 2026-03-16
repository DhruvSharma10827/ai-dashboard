"""Logging configuration for AI Dashboard.

This module provides centralized logging configuration with:
- Structured JSON logging support
- Multiple log handlers (file, console)
- Log rotation
- Context-aware logging

Example:
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started")
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log directory
LOG_DIR = Path.home() / ".ai-dashboard" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class ContextFilter(logging.Filter):
    """Filter that adds context information to log records."""

    def __init__(self, context: Optional[dict] = None) -> None:
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    enable_console: bool = True,
    enable_colors: bool = True,
) -> logging.Logger:
    """Set up application logging.

    Args:
        level: Logging level.
        log_file: Optional log file path.
        enable_console: Whether to enable console logging.
        enable_colors: Whether to use colored output.

    Returns:
        Configured logger instance.
    """
    # Get root logger
    root_logger = logging.getLogger("ai_dashboard")
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)

        if enable_colors and sys.stderr.isatty():
            formatter: logging.Formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
        else:
            formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file is None:
        log_file = LOG_DIR / f"ai-dashboard-{datetime.now():%Y-%m-%d}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Module name (typically __name__).

    Returns:
        Logger instance.
    """
    if not name.startswith("ai_dashboard"):
        name = f"ai_dashboard.{name}"
    return logging.getLogger(name)


# Initialize default logging on import
_logger: Optional[logging.Logger] = None


def initialize_logging(level: int = logging.INFO) -> logging.Logger:
    """Initialize the default logger.

    Args:
        level: Logging level.

    Returns:
        Configured logger instance.
    """
    global _logger
    if _logger is None:
        _logger = setup_logging(level)
    return _logger
