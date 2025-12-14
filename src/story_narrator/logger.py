"""
Logging configuration for Story Narrator
Provides consistent logging across all modules
"""
import logging
import sys
from pathlib import Path

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger

    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if logger doesn't have any
    if not logger.handlers:
        logger.setLevel(level)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Formatter with timestamp, level, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


def setup_file_logger(name: str, log_file: Path, level: int = logging.DEBUG) -> logging.Logger:
    """
    Create a logger that writes to both console and file

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = setup_logger(name, level)

    # Add file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
