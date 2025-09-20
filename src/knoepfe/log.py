"""Logging configuration for knoepfe."""

import logging
import sys


def configure_logging(verbose: bool = False) -> None:
    """Configure logging for the application.

    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,  # Override any existing configuration
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name, typically __name__ from calling module.
              If None, returns the root logger.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
