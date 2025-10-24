"""Logging configuration utilities for knoepfe."""

import logging
import sys


def configure_logging(verbose: bool = False) -> None:
    """Configure logging for the application.

    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger with logger name prefix
    logging.basicConfig(
        level=level,
        format="[%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,  # Override any existing configuration
    )
