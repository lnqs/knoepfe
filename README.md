# Knöpfe <sub><sup>[ˈknœpfə]</sub></sup>

Connect and control Elgato Stream Decks from Linux.

## Features

- Several integrated widgets
- OBS integration including
    - Showing and changing if stream is running
    - Showing and changing if recording is running
    - Showing current scene
    - Switching between scenes
- Multiple pages to switch between
- Configuring device's brightness and hardware polling interval
- Automatic sleeping if device isn't used with the possibility for widgets to prevent this (i.e. while OBS is running)

## Installation

### PyPI

```bash
pip install knoepfe
```

For additional functionality, install plugins:

```bash
pip install knoepfe[obs]     # OBS Studio integration
pip install knoepfe[audio]   # Audio control widgets
pip install knoepfe[all]     # All available plugins
```


### Arch Linux AUR

If you're on Arch Linux you can use the [PKGBUILD in the AUR](https://aur.archlinux.org/packages/knoepfe) to install Knöpfe.
Provided you're using `yay`

```bash
yay -S knoepfe
```

should be enough.

### Prerequisites

udev rules are required for Knöpfe to be able to communicate with the device.

Create ` /etc/udev/rules.d/99-streamdeck.rules` with following content:

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0060", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006d", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0080", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0063", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006c", TAG+="uaccess"
    ```

Then, run `sudo udevadm control --reload-rules` and reconnect the device. You should be ready to go then.

## systemd unit

If you want to start Knöpfe automatically on user login, consider creating and enabling a systemd unit in `~/.config/systemd/user/knoepfe.service`:

```
[Unit]
Description=Knoepfe

[Service]
# Set path to where Knoepfe executable was installed to
ExecStart=/usr/local/bin/knoepfe
Restart=always

[Install]
WantedBy=default.target
```

And start and enable it by running:

```bash
systemctl --user enable knoepfe
systemctl --user start knoepfe
```

## Usage

### Starting

Usually just running `knoepfe` should be enough. It reads the configuration from `~/.config/knoepfe/knoepfe.toml` (see below for more information) and connects to the stream deck.

Command line options are available:
```
Usage: knoepfe [OPTIONS] COMMAND [ARGS]...

Connect and control Elgato Stream Decks.

Options:
-v, --verbose    Print debug information.
--config PATH    Config file to use.
--mock-device    Don't connect to a real device. Mainly useful for
                debugging.
--no-cython-hid  Disable experimental CythonHIDAPI transport.
--version        Show the version and exit.
--help           Show this message and exit.

Commands:
list-widgets  List all available widgets.
widget-info   Show detailed information about a widget.
```


### Configuration

Knöpfe uses TOML format for configuration files. Create your configuration at `~/.config/knoepfe/knoepfe.toml`.

Example configurations can be found in the `src/knoepfe/data/` directory:
- `default.toml` - Basic configuration with built-in widgets
- `clocks.toml` - Various clock widget examples
- `streaming.toml` - Configuration with OBS integration

#### Basic Configuration Structure

```toml
# Device settings
[device]
brightness = 100
sleep_timeout = 10.0
device_poll_frequency = 5

# Plugin configurations (optional)
[plugins.obs]
enabled = true
host = "localhost"
port = 4455
password = "${OBS_PASSWORD}"  # Load from environment variable

# Decks - at least one deck named "main" is required
# Widgets in the main deck - properties can be specified directly
[[deck.main]]
type = "Clock"
[[deck.main.segments]]
format = "%H:%M"
x = 0
y = 0
width = 96
height = 96

[[deck.main]]
type = "Text"
text = "Hello\nWorld"

# Widgets can be assigned to specific positions using the 'index' parameter
# Without index, widgets are placed in order of appearance
[[deck.main]]
type = "Timer"
index = 5  # Place this widget at position 5 (0-based)

# Additional decks can be defined similarly
[[deck.utilities]]
type = "Text"
text = "Back"
switch_deck = "main"
```

#### Widget Positioning

By default, widgets are placed on the Stream Deck in the order they appear in the configuration file. However, you can explicitly control widget positions using the `index` parameter:

```toml
# Without index - widgets placed in order (0, 1, 2, ...)
[[deck.main]]
type = "Clock"

[[deck.main]]
type = "Text"
text = "Button 1"

# With explicit index - can be out of order
[[deck.main]]
type = "Timer"
index = 5  # This will be at position 5

[[deck.main]]
type = "Text"
text = "Button 3"
index = 3  # This will be at position 3

# Mixing indexed and unindexed widgets
# Unindexed widgets fill remaining positions in order
[[deck.main]]
type = "Text"
text = "Auto"  # Will fill next available position
```

**Note:** Index is 0-based, so `index = 0` is the first button, `index = 1` is the second, etc.

#### Environment Variables

Configuration values can reference environment variables using `${VAR_NAME}` syntax. This is particularly useful for sensitive data like passwords:

```toml
[plugins.obs]
password = "${OBS_PASSWORD}"
```

You can also use the `KNOEPFE_` prefix to override any configuration value via environment variables:
```bash
export KNOEPFE_DEVICE__BRIGHTNESS=50
export KNOEPFE_PLUGINS__OBS__PASSWORD=mysecret
```

## Widgets

Following widgets are included:

### Text

Simple widget displaying text.

```toml
[[deck.main]]
type = "Text"
text = "My great text!"
```

### Clock

Widget displaying the current time with customizable segments.

```toml
[[deck.main]]
type = "Clock"
interval = 1.0  # Update interval in seconds
[[deck.main.segments]]
format = "%H:%M"  # strftime format code
x = 0
y = 0
width = 96
height = 96
```

The `format` field expects a [strftime() format code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

### Timer

Stop watch widget.

```toml
[[deck.main]]
type = "Timer"
```

When pressed it counts the seconds until pressed again. It then shows the elapsed time until pressed again to reset.

This widget acquires the wake lock while running, preventing the device from going to sleep.

### Mic Mute

Mute/unmute PulseAudio source (microphone). **Requires the audio plugin** (`pip install knoepfe[audio]`).

```toml
[[deck.main]]
type = "MicMute"
# device = "alsa_input.usb-..."  # Optional: specific device name
```

If no device is specified, the default source is used. Shows mute state and toggles on press.

### OBS Streaming and Recording

Show and toggle OBS streaming/recording. **Requires the OBS plugin** (`pip install knoepfe[obs]`).

```toml
[[deck.main]]
type = "OBSRecording"

[[deck.main]]
type = "OBSStreaming"
```

These widgets connect to OBS and show if streaming/recording is active. Long press toggles the state.

As long as the connection to OBS is established, these widgets hold the wake lock.

### OBS Current Scene and Scene Switch

Show and switch active OBS scene. **Requires the OBS plugin** (`pip install knoepfe[obs]`).

```toml
[[deck.main]]
type = "OBSCurrentScene"

[[deck.scenes]]
type = "OBSSwitchScene"
scene = "Scene Name"
```

The current scene widget displays the active OBS scene. The scene switch widget indicates if the specified scene is active and switches to it when pressed.

As long as the connection to OBS is established, these widgets hold the wake lock.

## Development

Please feel free to open an [issue](https://github.com/lnqs/knoepfe/issues) if you encounter any bugs.

Pull requests are also very welcome :)

Knoepfe supports a plugin system for extending functionality. Plugins can be installed as separate packages and will be automatically discovered and loaded. See the existing plugins (obs, audio, example) as examples for creating new plugins.

## Mentions

This project relies on [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) to communicate with the devices and is heavily inspired by [Dev Deck](https://github.com/jamesridgway/devdeck) and [deckmaster](https://github.com/muesli/deckmaster/).
