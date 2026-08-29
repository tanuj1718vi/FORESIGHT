"""Unit tests for the structured logging subsystem."""

import json
import logging
from pathlib import Path

import pytest

from foresight.utils.logger import JSONFormatter, configure_logging, get_logger


@pytest.mark.unit
def test_get_logger_creation() -> None:
    """Verify get_logger returns a Logger instance with the expected name."""
    logger = get_logger("foresight.test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "foresight.test_module"


@pytest.mark.unit
def test_json_formatter_structure() -> None:
    """Verify JSONFormatter outputs valid JSON containing standard fields."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=42,
        msg="Test log message with value: %d",
        args=(100,),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert data["line"] == 42
    assert data["message"] == "Test log message with value: 100"
    assert "timestamp" in data


@pytest.mark.unit
def test_file_logging(tmp_path: Path) -> None:
    """Verify file logging creates log file and writes structured entries."""
    log_dir = tmp_path / "test_logs"
    log_file = "test_run.log"

    configure_logging(
        level="DEBUG",
        format_type="standard",
        log_to_file=True,
        log_dir=log_dir,
        log_file_name=log_file,
    )

    logger = get_logger("test.file.logger")
    test_msg = "Logging to file test message"
    logger.info(test_msg)

    # Flush handlers
    for handler in logging.getLogger().handlers:
        handler.flush()

    target_file = log_dir / log_file
    assert target_file.exists()

    content = target_file.read_text(encoding="utf-8")
    assert test_msg in content
    # Parse json line
    lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
    last_entry = json.loads(lines[-1])
    assert last_entry["message"] == test_msg
    assert last_entry["level"] == "INFO"
