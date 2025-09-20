"""Transport layer implementations for knoepfe.

This module provides alternative transport implementations for the StreamDeck library,
including a cython-hidapi based transport that offers better performance and resource
management compared to the default ctypes implementation.
"""

from .cython_hidapi import CythonHIDAPI

__all__ = ["CythonHIDAPI"]
