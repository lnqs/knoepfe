# Transport Patches

Knoepfe applies patches to the upstream `python-elgato-streamdeck` library to fix bugs and improve performance.

## Patches Applied

### 1. Dummy Transport Fix
The Dummy transport's `read()` method returns `bytearray(length)` instead of `None` when no data is available. This causes the StreamDeck polling loop to never sleep, resulting in 100% CPU usage.

**Fix:** Patch the Dummy transport to return `None` when no data is available, matching LibUSBHIDAPI's behavior.

### 2. CythonHIDAPI Transport (Enabled by Default but optional)

Knoepfe includes a Cython-based HID transport implementation for improved performance and reliability when communicating with StreamDeck devices.

## Why CythonHIDAPI?

The Cython implementation provides significant advantages over the ctypes-based approach:

- **Compiled Performance**: Native C code instead of ctypes marshalling overhead
- **True Parallelism**: GIL release during I/O operations for better concurrency
- **Optimized Memory**: Stack allocation for small buffers, efficient dynamic allocation for large ones
- **Proper Resource Management**: Uses `weakref.finalize()` for safe cleanup order
- **Full Compatibility**: Drop-in replacement for LibUSBHIDAPI

## Critical Bug in Upstream LibUSBHIDAPI

The upstream `python-elgato-streamdeck` library's ctypes-based transport has a shutdown race condition that can cause crashes:

**Problem:**
```python
# In Library._load_hidapi_library() (line 143):
atexit.register(self.HIDAPI_INSTANCE.hid_exit)

# In Device.__del__() (line 360):
def __del__(self):
    self.close()  # May access already-cleaned-up library!
```

The `atexit` registration causes `hid_exit()` to be called before device destructors run. When `Device.__del__()` tries to close devices during shutdown, it accesses an already-cleaned-up library, causing crashes.

**Fix for Upstream:**
```python
# Replace atexit with weakref.finalize for proper cleanup order
import weakref
import sys

# In Library._load_hidapi_library(), replace line 143:
# OLD: atexit.register(self.HIDAPI_INSTANCE.hid_exit)
# NEW:
weakref.finalize(sys.modules[__name__], self.HIDAPI_INSTANCE.hid_exit)

# In Device.__del__(), add error handling:
def __del__(self):
    try:
        self.close()
    except:
        # Ignore errors during destruction to avoid shutdown crashes
        pass
```

This ensures devices are closed before the library is cleaned up, preventing shutdown crashes.

## Usage

CythonHIDAPI is enabled by default. To disable it:

```bash
knoepfe --no-cython-hid
```

Or in code:

```python
from knoepfe.transport import apply_transport_patches

# Use CythonHIDAPI (default)
apply_transport_patches(enable_cython_hid=True)

# Use upstream LibUSBHIDAPI
apply_transport_patches(enable_cython_hid=False)
```

## Requirements

- `hidapi` package (installed automatically with knoepfe)
- `StreamDeck` library for base classes