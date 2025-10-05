"""Monkey patches for StreamDeck library transports.

This module contains fixes for bugs in the upstream StreamDeck library's
transport implementations that cause performance issues, and provides
optional performance enhancements.
"""

import logging


def apply_transport_patches(enable_cython_hid: bool = True) -> None:
    """Apply all transport monkey patches and optional enhancements.

    This function:
    1. Patches bugs in the upstream StreamDeck library transports:
       - Dummy transport: Fix read() to return None instead of bytearray
    2. Optionally replaces LibUSBHIDAPI with CythonHIDAPI for better performance

    Args:
        enable_cython_hid: If True, replace LibUSBHIDAPI with CythonHIDAPI
                          for compiled performance and better resource management.
                          Default is True.

    These patches prevent 100% CPU usage in the device polling loop.
    """
    _patch_dummy_transport()

    if enable_cython_hid:
        _enable_cython_hidapi()


def _patch_dummy_transport() -> None:
    """Fix Dummy transport to return None when no data available.

    The Dummy transport's read() method returns bytearray(length) instead of None
    when no data is available. This causes the StreamDeck polling loop to never
    sleep, resulting in 100% CPU usage.

    This patch fixes the return value to match LibUSBHIDAPI's behavior.
    """
    import StreamDeck.Transport.Dummy as Dummy_module
    from StreamDeck.Transport.Transport import TransportError

    def fixed_dummy_read(self, length: int):
        """Fixed read that returns None instead of empty bytearray."""
        if not self.is_open:
            raise TransportError("Deck read while deck not open.")

        logging.info("Deck report read (length %s)", length)
        return None  # Return None instead of bytearray(length)

    Dummy_module.Dummy.Device.read = fixed_dummy_read  # type: ignore[assignment]


def _enable_cython_hidapi() -> None:
    """Replace LibUSBHIDAPI with CythonHIDAPI for better performance.

    CythonHIDAPI provides:
    - Compiled performance using cython-hidapi instead of ctypes
    - Proper resource management with weakref finalizers
    - Safe shutdown handling without race conditions
    - GIL release for true parallelism in I/O operations

    This is a drop-in replacement that maintains full compatibility with
    the StreamDeck library's expected interface.
    """
    import StreamDeck.Transport.LibUSBHIDAPI as LibUSBHIDAPI_module

    from .cython_hidapi import CythonHIDAPI

    LibUSBHIDAPI_module.LibUSBHIDAPI = CythonHIDAPI
