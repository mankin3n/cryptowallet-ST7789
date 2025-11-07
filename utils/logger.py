"""
Logging Configuration.

Sets up logging for the application with file and console handlers.
Supports rotation and different log levels.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
import config


def setup_logging() -> None:
    """
    Configure logging for the application.

    Creates console and file handlers with rotation.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if not config.DEBUG_MODE else logging.DEBUG)

    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler with rotation
    log_file = Path(config.LOG_FILE)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))

    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logging configured")
    logger.info(f"Log level: {config.LOG_LEVEL}")
    logger.info(f"Mock hardware: {config.MOCK_HARDWARE}")
    logger.info(f"Debug mode: {config.DEBUG_MODE}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
