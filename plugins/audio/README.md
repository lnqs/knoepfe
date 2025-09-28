# Knoepfe Audio Plugin

Audio control widgets for [knoepfe](https://github.com/lnqs/knoepfe) using PulseAudio.

## Installation

```bash
# Install with knoepfe
pip install knoepfe[audio]

# Or install separately
pip install knoepfe-audio-plugin
```

## Widgets

### MicMute

Controls microphone mute/unmute functionality via PulseAudio.

**Configuration:**

```python
# Use default microphone
widget("MicMute")

# Specify specific microphone source
widget("MicMute", {
    'source': 'alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone'
})
```

**Parameters:**

- `source` (optional): PulseAudio source name. If not specified, uses the default source.

**Features:**

- Shows microphone icon (red when unmuted, gray when muted)
- Click to toggle mute/unmute
- Automatically updates when mute state changes externally
- Works with any PulseAudio-compatible microphone

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

