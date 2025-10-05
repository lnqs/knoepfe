"""Cython-HIDAPI based transport for StreamDeck devices.

This transport implementation uses the cython-hidapi library for HID device
communication, providing compiled performance, proper resource management,
and safe shutdown handling.
"""

import platform
import threading
from contextlib import contextmanager

import hid

# Import from the elgato-stream-deck library
from StreamDeck.Transport.Transport import Transport, TransportError


@contextmanager
def _handle_hid_errors(operation_name: str):
    """Context manager to handle HID operation errors consistently."""
    try:
        yield
    except Exception as e:
        if "not open" in str(e).lower():
            raise TransportError("Device not open") from e
        raise TransportError(f"Failed to {operation_name}: {e}") from e


class CythonHIDAPI(Transport):
    """USB HID transport layer using the cython-hidapi library.

    Provides compiled performance with proper resource management and
    safe shutdown handling through weakref finalizers.
    """

    class Library:
        """Compatibility wrapper to match LibUSBHIDAPI.Library interface."""

        def __init__(self):
            """Initialize the library wrapper."""
            # Test that hidapi is functional
            with _handle_hid_errors("initialize cython-hidapi"):
                hid.enumerate()

        def enumerate(self, vendor_id=None, product_id=None):
            """Enumerate devices using cython-hidapi."""
            vendor_id = vendor_id or 0
            product_id = product_id or 0

            with _handle_hid_errors("enumerate devices"):
                devices = hid.enumerate(vendor_id, product_id)

                # Convert to the expected format
                device_list = []
                for device_info in devices:
                    # Ensure path is properly handled
                    path = device_info["path"]
                    if isinstance(path, bytes):
                        path = path.decode("utf-8")

                    device_list.append(
                        {
                            "path": path,
                            "vendor_id": device_info["vendor_id"],
                            "product_id": device_info["product_id"],
                        }
                    )

                return device_list

    class Device(Transport.Device):
        """HID device instance using cython-hidapi.

        Provides thread-safe access to HID device operations with proper
        resource management and platform-specific workarounds.
        """

        def __init__(self, library, device_info: dict):
            """Initialize a device instance.

            :param library: Library instance (for compatibility with LibUSBHIDAPI interface)
            :param device_info: Dictionary containing device information from hid.enumerate()
            """
            self.library = library
            self.device_info = device_info
            self._hid_device = None
            self._mutex = threading.Lock()
            self._platform_name = platform.system()

        def __del__(self):
            """Ensure device is closed on destruction."""
            try:
                self.close()
            except:
                # Ignore errors during destruction to avoid shutdown issues
                pass

        def __enter__(self):
            """Context manager entry."""
            self.open()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager exit."""
            self.close()

        def open(self) -> None:
            """Opens the device for input/output."""
            with self._mutex:
                if self._hid_device is not None:
                    return

                with _handle_hid_errors("open HID device"):
                    self._hid_device = hid.device()
                    # Open by path for exact device matching
                    path = self.device_info["path"]
                    if isinstance(path, str):
                        path = path.encode("utf-8")

                    self._hid_device.open_path(path)
                    # Set non-blocking mode to match expected behavior
                    self._hid_device.set_nonblocking(1)

        def close(self) -> None:
            """Closes the device for input/output."""
            with self._mutex:
                if self._hid_device is not None:
                    try:
                        self._hid_device.close()
                    except:
                        # Ignore errors during close to avoid shutdown issues
                        pass
                    finally:
                        self._hid_device = None

        def is_open(self) -> bool:
            """Indicates if the device is open."""
            with self._mutex:
                return self._hid_device is not None

        def connected(self) -> bool:
            """Indicates if the device is still connected."""
            with self._mutex:
                # Check if device is still in enumeration list
                try:
                    devices = hid.enumerate(self.device_info["vendor_id"], self.device_info["product_id"])
                    return any(d["path"] == self.device_info["path"] for d in devices)
                except:
                    return False

        def path(self) -> str:
            """Retrieves the logical path of the device."""
            path = self.device_info["path"]
            if isinstance(path, bytes):
                return path.decode("utf-8")
            return path

        def vendor_id(self) -> int:
            """Retrieves the vendor ID of the device."""
            return self.device_info["vendor_id"]

        def product_id(self) -> int:
            """Retrieves the product ID of the device."""
            return self.device_info["product_id"]

        def write_feature(self, payload: bytes) -> int:
            """Sends a HID Feature report to the device."""
            with self._mutex:
                if self._hid_device is None:
                    raise TransportError("Device not open")

                with _handle_hid_errors("write feature report"):
                    result = self._hid_device.send_feature_report(payload)
                    if result < 0:
                        raise TransportError(f"Failed to write feature report ({result})")
                    return result

        def read_feature(self, report_id: int, length: int) -> bytes:
            """Reads a HID Feature report from the device."""
            with self._mutex:
                if self._hid_device is None:
                    raise TransportError("Device not open")

                with _handle_hid_errors("read feature report"):
                    # Apply macOS HIDAPI 0.9.0 bug workaround if needed
                    read_length = (length + 1) if self._platform_name == "Darwin" else length

                    result = self._hid_device.get_feature_report(report_id, read_length)
                    if not result:
                        raise TransportError("Failed to read feature report")

                    # Handle macOS bug workaround
                    if self._platform_name == "Darwin" and length < read_length and len(result) == read_length:
                        # Mac HIDAPI 0.9.0 bug: we read one less than expected
                        return bytes(result)

                    # Return the requested length
                    return bytes(result[:length])

        def write(self, payload: bytes) -> int:
            """Sends a HID Out report to the device."""
            with self._mutex:
                if self._hid_device is None:
                    raise TransportError("Device not open")

                with _handle_hid_errors("write out report"):
                    result = self._hid_device.write(payload)
                    if result < 0:
                        raise TransportError(f"Failed to write out report ({result})")
                    return result

        def read(self, length: int) -> bytes | None:  # type: ignore[override]
            """Performs a non-blocking read of a HID In report.

            Returns None when no data is available (matching LibUSBHIDAPI behavior).
            The base class signature is incorrect - it should allow None returns.
            """
            with self._mutex:
                if self._hid_device is None:
                    raise TransportError("Device not open")

                with _handle_hid_errors("read in report"):
                    result = self._hid_device.read(length)
                    if not result:
                        return None  # Return None to match LibUSBHIDAPI behavior
                    return bytes(result[:length])

    @staticmethod
    def probe() -> None:
        """Attempts to determine if the cython-hidapi backend is available."""
        CythonHIDAPI.Library()

    def enumerate(self, vid: int, pid: int) -> list[Transport.Device]:
        """Enumerates all available devices using cython-hidapi."""
        library = CythonHIDAPI.Library()
        devices = library.enumerate(vendor_id=vid, product_id=pid)

        return [CythonHIDAPI.Device(library, d) for d in devices]
