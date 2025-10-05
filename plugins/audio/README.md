# Knoepfe Audio Plugin

Audio control widgets for [knoepfe](https://github.com/lnqs/knoepfe) using PulseAudio.

## Installation

```bash
# Install with knoepfe
pip install knoepfe[audio]

# Or install separately
pip install knoepfe-audio-plugin
```

## Plugin Configuration

The audio plugin supports global configuration that applies to all widgets:

```python
plugin.audio(
    default_source='alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone'
)
```

**Parameters:**

- `default_source` (optional): Default PulseAudio source name to use for all audio widgets. Individual widgets can override this with their own `source` parameter.

## Widgets

### MicMute

Controls microphone mute/unmute functionality via PulseAudio.

**Configuration:**

```python
# Use system default microphone with default icons
widget.MicMute()

# Use plugin's default_source (if configured)
plugin.audio(
    default_source='alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone'
)
widget.MicMute()

# Override with widget-specific source
widget.MicMute(
    source='alsa_input.pci-0000_00_1f.3.analog-stereo'
)

# Customize icons and colors with unicode characters
widget.MicMute(
    muted_icon='🔇',
    unmuted_icon='🎤',
    muted_color='gray',
    unmuted_color='green'
)

# Customize icons and colors with codepoints
widget.MicMute(
    muted_icon='\ue02b',
    unmuted_icon='\ue029',
    muted_color='blue',
    unmuted_color='red'
)
```

**Parameters:**

- `source` (optional): PulseAudio source name for this specific widget. If not specified, falls back to the plugin's `default_source`, or the system default source.
- `muted_icon` (optional): Icon to display when muted. Can be a unicode character (e.g., `'🔇'`) or codepoint (e.g., `'\ue02b'`). Default: `'\ue02b'`
- `unmuted_icon` (optional): Icon to display when unmuted. Can be a unicode character (e.g., `'🎤'`) or codepoint (e.g., `'\ue029'`). Default: `'\ue029'`
- `muted_color` (optional): Icon color when muted. Default: `'white'`
- `unmuted_color` (optional): Icon color when unmuted. Default: `'red'`

**Source Selection Priority:**

1. Widget's `source` parameter (highest priority)
2. Plugin's `default_source` configuration
3. System default source from PulseAudio (lowest priority)

**Features:**

- Shows microphone icon with customizable appearance
- Default: red icon when unmuted, white icon when muted
- Click to toggle mute/unmute
- Automatically updates when mute state changes externally
- Works with any PulseAudio-compatible microphone
- Fully customizable icons (unicode or codepoints) and colors

**Finding Your Microphone Source:**

```bash
# List available sources
pactl list sources short

# Example output:
# 0	alsa_input.pci-0000_00_1f.3.analog-stereo	...
# 1	alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone	...
```

## Requirements

- PulseAudio audio system
- `pulsectl-asyncio>=1.2.2` (installed automatically)

## Troubleshooting

**Widget shows as disconnected:**

- Ensure PulseAudio is running: `pulseaudio --check`
- Check if the specified source exists: `pactl list sources short`

**Permission issues:**

- Ensure your user is in the `audio` group: `groups $USER`
- Add to audio group if needed: `sudo usermod -a -G audio $USER`

## Development

```bash
# Install in development mode
uv pip install -e plugins/audio

# Run tests
pytest plugins/audio/tests/
```

