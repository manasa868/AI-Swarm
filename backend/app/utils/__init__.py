"""Utility functions and formatting helpers for AI Swarm."""
import logging
import sys
from typing import Dict, Any


def get_logger(name: str) -> logging.Logger:
    """Configures structured console logging for agents and engines."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 1.0:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60.0:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"


def sanitize_filename(name: str) -> str:
    """Remove unsafe characters from filenames."""
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        name = name.replace(char, "_")
    return name.strip()
