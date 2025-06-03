"""Tests for the logging configuration."""

import logging
import os
from celery_queue_exporter.logging_config import setup_logging, LOGGING_CONFIG


def test_logging_setup(tmp_path):
    """Test that logging is properly configured."""
    # Set up a temporary log file
    log_file = tmp_path / "test.log"
    os.environ["LOG_FILE"] = str(log_file)
    os.environ["LOG_LEVEL"] = "DEBUG"

    # Configure logging
    setup_logging()

    # Get the logger
    logger = logging.getLogger("celery_queue_exporter")

    # Test log message
    test_message = "Test log message"
    logger.info(test_message)

    # Check that the message was written to the file
    assert log_file.exists()
    log_content = log_file.read_text()
    assert test_message in log_content


def test_logging_config_structure():
    """Test that the logging configuration has the expected structure."""
    assert "version" in LOGGING_CONFIG
    assert "formatters" in LOGGING_CONFIG
    assert "handlers" in LOGGING_CONFIG
    assert "loggers" in LOGGING_CONFIG

    # Check formatters
    assert "standard" in LOGGING_CONFIG["formatters"]
    assert "format" in LOGGING_CONFIG["formatters"]["standard"]

    # Check handlers
    assert "console" in LOGGING_CONFIG["handlers"]
    assert "file" in LOGGING_CONFIG["handlers"]

    # Check loggers
    assert "celery_queue_exporter" in LOGGING_CONFIG["loggers"]
    logger_config = LOGGING_CONFIG["loggers"]["celery_queue_exporter"]
    assert "handlers" in logger_config
    assert "level" in logger_config 