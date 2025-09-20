# CythonHIDAPI Transport

An alternative transport implementation for StreamDeck devices using the cython-hidapi library.

## Features

- **Compiled Performance**: Uses Cython-compiled code for HID operations
- **Resource Management**: Automatic cleanup with weakref finalizers
- **Thread Safety**: All operations are properly synchronized with threading locks
- **Platform Support**: Includes macOS HIDAPI 0.9.0 bug workaround for compatibility
- **Drop-in Replacement**: Implements the exact same interface as LibUSBHIDAPI

## Issues with LibUSBHIDAPI (ctypes Implementation)

### Shutdown Race Conditions
- **atexit registration**: `atexit.register(hid_exit)` calls library cleanup before devices are closed
- **Unsafe destructors**: Device `__del__` methods call `hid_close()` on potentially unloaded library
- **No dependency tracking**: No guarantee that HIDAPI library stays alive until all devices are closed
- **Result**: Potential crashes during program shutdown when device destructors access unloaded library

### Performance Characteristics
- **ctypes overhead**: Every HID call has Python-to-C marshalling overhead
- **No GIL release**: All operations hold the Python GIL, limiting concurrency
- **Manual buffer management**: Uses `ctypes.create_string_buffer()` for every operation
- **Threading bottlenecks**: Python threading locks with GIL contention

### API Coverage
- **Manual bindings**: ctypes function signatures must be manually maintained for new HIDAPI features
- **Platform-specific code**: Custom library loading logic for each platform
- **Missing features**: Incomplete API coverage (missing `hid_open()`, timeout reads, error reporting, etc.)
- **Missing fields**: `hid_device_info` structure lacks `bus_type` field from newer HIDAPI versions

## Unique Features in LibUSBHIDAPI

### macOS Homebrew Support
- **Homebrew path detection**: Automatically finds HIDAPI library in Homebrew installation paths
- **Environment variable support**: Respects `HOMEBREW_PREFIX` environment variable
- **Fallback logic**: Sophisticated library search with multiple fallback paths

### macOS HIDAPI 0.9.0 Bug Workaround
- **Read length adjustment**: `read_length = (length + 1) if platform == 'Darwin' else length`
- **Result length handling**: Special logic to handle the off-by-one bug in feature report reads
- **Platform-specific**: Only applied on macOS to avoid issues on other platforms

### Library Singleton Pattern
- **Instance caching**: `HIDAPI_INSTANCE` class variable prevents multiple library loads
- **Performance optimization**: Avoids slow library loading on subsequent uses

## CythonHIDAPI Implementation

### Shutdown Issues - Addressed
- **Safe resource management**: cython-hidapi uses `weakref.finalize()` for proper cleanup order
- **No atexit problems**: Library cleanup tied to module lifecycle, not arbitrary atexit timing
- **Exception handling**: All destructors wrapped in try/except to prevent shutdown crashes

### Performance - Improved
- **Compiled performance**: Cython compiles to native C code, eliminating ctypes overhead
- **GIL release**: cython-hidapi uses `with nogil:` for true parallelism in I/O operations
- **Optimized memory**: Stack allocation for small buffers, efficient dynamic allocation for large ones

### API Completeness - Enhanced
- **Complete API**: cython-hidapi exposes full HIDAPI functionality including missing features
- **Better error handling**: Proper error reporting with `hid_error()` function
- **Timeout support**: `hid_read_timeout()` for non-blocking operations with timeouts

### macOS HIDAPI 0.9.0 Bug - Preserved
- **Workaround preserved**: Exact same logic implemented in `read_feature()` method
- **Platform detection**: Uses `platform.system()` to apply workaround only on macOS
- **Compatibility maintained**: Ensures existing StreamDeck code continues to work

### Homebrew Support - Alternative Approach
- **Not needed**: cython-hidapi can be installed via pip with embedded HIDAPI
- **System integration**: Uses system package manager integration instead of manual path detection
- **Alternative approach**: More reliable than manual path searching

### Library Management - Simplified
- **Automatic management**: cython-hidapi handles library lifecycle automatically
- **No singleton needed**: Each device instance manages its own resources properly
- **Cleaner architecture**: No global state or class variables required

## Usage

```python
from knoepfe.transport import CythonHIDAPI

# Use as a drop-in replacement for LibUSBHIDAPI
transport = CythonHIDAPI()
devices = transport.enumerate(vendor_id, product_id)

# Or use with StreamDeck library by monkey-patching
import StreamDeck.Transport.LibUSBHIDAPI
StreamDeck.Transport.LibUSBHIDAPI.LibUSBHIDAPI = CythonHIDAPI
```

## Requirements

- `hidapi` package (install with `pip install hidapi`)
- `StreamDeck` library for base classes

## Potential Upstream Patches for LibUSBHIDAPI

If improving the existing ctypes implementation is preferred, here are patches that would address the identified issues:

### 1. Fix Shutdown Race Condition (CRITICAL)
```python
# Replace dangerous atexit registration
# OLD: atexit.register(self.HIDAPI_INSTANCE.hid_exit)
# NEW: Use weakref.finalize for proper cleanup order
import weakref
import sys

# In Library.__init__():
weakref.finalize(sys.modules[__name__], self.HIDAPI_INSTANCE.hid_exit)

# In Device.__del__():
def __del__(self):
    try:
        self.close()
    except:
        # Ignore errors during destruction to avoid shutdown crashes
        pass
```

### 2. Add Missing bus_type Field
```python
# Update hid_device_info structure to include missing field
hid_device_info._fields_ = [
    ('path', ctypes.c_char_p),
    ('vendor_id', ctypes.c_ushort),
    ('product_id', ctypes.c_ushort),
    ('serial_number', ctypes.c_wchar_p),
    ('release_number', ctypes.c_ushort),
    ('manufacturer_string', ctypes.c_wchar_p),
    ('product_string', ctypes.c_wchar_p),
    ('usage_page', ctypes.c_ushort),
    ('usage', ctypes.c_ushort),
    ('interface_number', ctypes.c_int),
    ('next', ctypes.POINTER(hid_device_info)),
    ('bus_type', ctypes.c_int)  # ADD THIS LINE
]
```

### 3. Add Missing API Functions
```python
# Add missing HIDAPI functions for complete API coverage
self.HIDAPI_INSTANCE.hid_open.argtypes = [ctypes.c_ushort, ctypes.c_ushort, ctypes.c_wchar_p]
self.HIDAPI_INSTANCE.hid_open.restype = ctypes.c_void_p

self.HIDAPI_INSTANCE.hid_read_timeout.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t, ctypes.c_int]
self.HIDAPI_INSTANCE.hid_read_timeout.restype = ctypes.c_int

self.HIDAPI_INSTANCE.hid_get_manufacturer_string.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_size_t]
self.HIDAPI_INSTANCE.hid_get_manufacturer_string.restype = ctypes.c_int

self.HIDAPI_INSTANCE.hid_error.argtypes = [ctypes.c_void_p]
self.HIDAPI_INSTANCE.hid_error.restype = ctypes.c_wchar_p
```

### 4. Improve Error Handling
```python
# Add consistent error handling context manager
@contextmanager
def _handle_hid_errors(operation_name: str):
    try:
        yield
    except Exception as e:
        if "not open" in str(e).lower():
            raise TransportError("Device not open") from e
        raise TransportError(f"Failed to {operation_name}: {e}") from e

# Use in all HID operations:
def send_feature_report(self, handle, data):
    with _handle_hid_errors("write feature report"):
        # existing code here
```

### 5. Add Context Manager Support
```python
# Add context manager support to Device class
def __enter__(self):
    self.open()
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
```

### 6. Improve Thread Safety
```python
# Use threading.RLock instead of Lock for reentrant operations
import threading

def __init__(self):
    # OLD: self.mutex = threading.Lock()
    self.mutex = threading.RLock()  # Allow reentrant locking
```

### 7. Add Proper Resource Cleanup
```python
# Ensure devices are closed before library cleanup
class Library:
    def __init__(self):
        self._open_devices = weakref.WeakSet()
        # ... existing code ...
    
    def open_device(self, path):
        # ... existing code ...
        self._open_devices.add(device_handle)
        return device_handle
    
    def close_device(self, handle):
        # ... existing code ...
        self._open_devices.discard(handle)
    
    def cleanup(self):
        # Close all open devices before library cleanup
        for device in list(self._open_devices):
            try:
                self.close_device(device)
            except:
                pass
        self.hid_exit()
```

### Patch Priority
1. **CRITICAL**: Shutdown race condition fix (prevents crashes)
2. **HIGH**: Missing bus_type field (compatibility with newer HIDAPI)
3. **MEDIUM**: Error handling improvements (better debugging)
4. **LOW**: Missing API functions (feature completeness)

These patches would address the identified issues while maintaining the ctypes approach.

## Implementation Notes

- Uses `contextmanager` for consistent error handling across all HID operations
- Maintains compatibility with existing StreamDeck library code
- Includes platform-specific workarounds (e.g., macOS HIDAPI 0.9.0 bug)
- Thread-safe device operations with proper mutex locking