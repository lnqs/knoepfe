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

    pip install knoepfe

should do the trick :)

### Prerequisites

udev rules are required for Knöpfe to be able to communicate with the device.

Create ` /etc/udev/rules.d/99-streamdeck.rules` with following content:

    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0060", TAG+="uaccess"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006d", TAG+="uaccess"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0080", TAG+="uaccess"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="0063", TAG+="uaccess"
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", ATTRS{idProduct}=="006c", TAG+="uaccess"

Then, run `sudo udevadm control --reload-rules` and reconnect the device. You should be ready to go then.

## systemd unit

If you want to start Knöpfe automatically on user login, consider creating and enabling a systemd unit in `~/.config/systemd/user/knoepfe.service`:

    [Unit]
    Description=Knoepfe

    [Service]
    # Set path to where Knoepfe executable was installed to
    ExecStart=/usr/local/bin/knoepfe
    Restart=always

    [Install]
    WantedBy=default.target

And start and enable it by running:

    systemd --user enable knoepfe
    systemd --user start knoepfe

## Usage

### Starting

Usually just running `knoepfe` should be enough. It reads the configuration from `~/.config/knoepfe/knoepfe.cfg` (see below for more information) and connects to the stream deck.

Anyway, some command line options are available:

    knopfe
    Connect and control Elgato Stream Decks

    Usage:
      knoepfe [(-v | --verbose)] [--config=<path>]
      knoepfe (-h | --help)
      knoepfe --version

    Options:
      -h --help       Show this screen.
      -v --verbose    Print debug information.
      --config=<path> Config file to use.


### Configuration

Unless overwritten on command line, Knöpfe loads its configuration from `~/.config/knoepfe/knoepfe.cfg`. So you should create that file if you don't want to stick to the example config used as fallback.

Anyway, the example is a great way to start. It can be found as `knoepfe/default.cfg` in this repository and the installation target directory.

The configuration is parsed as Python code. So every valid Python statement can be used, allowing to dynamically create and reuse parts of it.
The default configuration is heavily commented, hopefully explaining how to use it clear enough.

## Widgets

Following widgets are included:

### Text

Simple widget just displaying a text.

Can be instantiated as:

    widget({'type': 'knoepfe.widgets.Text', 'text': 'My great text!'})

Does nothing but showing the text specified with `text` on the key.

### Clock

Widget displaying the current time. Instantiated as:

    widget({'type': 'knoepfe.widgets.Clock', 'format': '%H:%M'})

`format` expects a [strftime() format code](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) to define the formatting.

### Timer

Stop watch widget.

Instantiated as:

    widget({'type': 'knoepfe.widgets.Timer'})

When pressed it counts the seconds until it is pressed again. It then shows the time elapsed between both presses until pressed again to reset.

This widget acquires the wake lock while the time is running, preventing the device from going to sleep.

### Mic Mute

Mute/unmute PulseAudio source, i.e. microphone.

Instantiated with:

    widget({'type': 'knoepfe.widgets.MicMute'})

Accepts `device` as optional argument with the name of source the operate with. If not set, the default source is used.
This widget shows if the source is muted and toggles the state on pressing it.

### OBS Streaming and Recording

Show and toggle OBS streaming/recording.

These widgets can be instantiated with

    widget({'type': 'knoepfe.widgets.obs.Recording'})

and

    widget({'type': 'knoepfe.widgets.obs.Streaming'})

They connect to OBS (if running, they're quite gray if not) and show if the stream or recording is running. On a long press the state is toggled.

As long as the connection to OBS is established these widgest hold the wake lock.

### OBS Current Scene and Scene Switch

Show and switch active OBS scene.

These widgets are instantiated with

    widget({'type': 'knoepfe.widgets.obs.CurrentScene'})

and

    widget({'type': 'knoepfe.widgets.obs.SwitchScene', 'scene': 'Scene'})

The current scene widget just displays the active OBS scene.

The scene switch widget indicates if the scene set with the `scene` key is currently active. If not and the widget is pressed it switches to the scene.

As long as the connection to OBS is established these widgets hold the wake lock.

## Development

Please feel free to open an [issue](https://github.com/lnqs/knoepfe/issues) if you encounter any bugs.

Pull requests are also very welcome :)

As widgets are loaded by their module path it should also be possible to add new functionality in a plugin-ish way by just creating independent python modules defining their behaviour. But, well, I haven't tested that yet.

## Mentions

This project relies on [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) to communicate with the devices and is heavily inspired by [Dev Deck](https://github.com/jamesridgway/devdeck) and [deckmaster](https://github.com/muesli/deckmaster/).
