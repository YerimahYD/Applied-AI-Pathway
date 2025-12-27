import logging
from typing import Optional


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Create a consistent logger for the project.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if re-imported in notebooks/tests
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level.upper())
    logger.propagate = False
    return logger
