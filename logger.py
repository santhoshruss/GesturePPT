"""
logger.py
---------
Application-wide logging setup. Produces both console and rotating file
output, including timestamp, gesture, confidence, action, and errors.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config import CONFIG


def get_logger(name: str = "GesturePPT") -> logging.Logger:
    """
    Create (or retrieve) a configured logger instance.

    Args:
        name: Logger name, typically the module's __name__.

    Returns:
        A configured logging.Logger instance with console + rotating file handlers.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured (avoids duplicate handlers on repeated calls).
        return logger

    level = getattr(logging, CONFIG.logging.level.upper(), logging.INFO)
    logger.setLevel(level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    # Rotating file handler
    try:
        os.makedirs(CONFIG.logging.log_dir, exist_ok=True)
        log_path = os.path.join(CONFIG.logging.log_dir, CONFIG.logging.log_file)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=CONFIG.logging.max_bytes,
            backupCount=CONFIG.logging.backup_count,
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("Could not create log file handler: %s", exc)

    return logger


def log_gesture_event(
    logger: logging.Logger,
    gesture: str,
    confidence: float,
    action: str,
) -> None:
    """Log a structured gesture-detection + action-execution event."""
    logger.info(
        "Gesture=%s | Confidence=%.2f | Action=%s",
        gesture, confidence, action,
    )
