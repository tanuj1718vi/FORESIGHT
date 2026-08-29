"""Structured and configurable logging subsystem for Project FORESIGHT."""

import json
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

from foresight.config.constants import LOGS_DIR, ROOT_DIR


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured log aggregators and production logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt or "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj["extra"] = record.extra
        return json.dumps(log_obj)


def configure_logging(
    level: str = "INFO",
    format_type: str = "standard",
    log_to_file: bool = True,
    log_dir: Path | str = LOGS_DIR,
    log_file_name: str = "foresight.log",
) -> None:
    """Configure the root logging system for FORESIGHT."""
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate logging
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if format_type.lower() == "json":
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler
    if log_to_file:
        target_log_dir = Path(log_dir)
        if not target_log_dir.is_absolute():
            target_log_dir = ROOT_DIR / target_log_dir
        target_log_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_log_dir / log_file_name
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(file_path),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get or create a named logger within the FORESIGHT namespace.

    Args:
        name: Name of the logger, typically __name__ of the calling module.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    # If root logger is unconfigured, apply default configuration
    if not logging.getLogger().handlers:
        configure_logging()
    return logger
