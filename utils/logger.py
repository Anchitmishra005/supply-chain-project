"""
=============================================================================
 Project Logger
=============================================================================
 Provides a pre-configured logger for the entire project.
 Logs are written to both the console and a rotating log file.
=============================================================================
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Log directory
# ---------------------------------------------------------------------------
LOG_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str = "supply_chain") -> logging.Logger:
    """
    Return a configured logger instance.

    Parameters
    ----------
    name : str
        Logger name (typically __name__ of the calling module).

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler (INFO and above)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # File handler (DEBUG and above, rotates at 5 MB)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
