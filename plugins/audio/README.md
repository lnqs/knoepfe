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

```toml
# ============================================================================
# Audio Plugin Configuration
# ============================================================================

[plugins.audio]
# Enable/disable the audio plugin
enabled = true

# Default PulseAudio source name for all audio widgets
# Individual widgets can override this with their own 'source' parameter
# Find available sources with: pactl list sources short
default_source = "alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone"
```

**Parameters:**

- `enabled` (optional): Enable the audio plugin. Default: `true`
- `default_source` (optional): Default PulseAudio source name to use for all audio widgets. Individual widgets can override this with their own `source` parameter.

## Widgets

### MicMute

Controls microphone mute/unmute functionality via PulseAudio.

**Configuration:**

```toml
# ----------------------------------------------------------------------------
# Example 1: Use system default microphone
# ----------------------------------------------------------------------------
[[deck.main]]
type = "MicMute"

# ----------------------------------------------------------------------------
# Example 2: Use plugin's default_source (if configured)
# ----------------------------------------------------------------------------
[plugins.audio]
default_source = "alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone"

[[deck.main]]
type = "MicMute"

# ----------------------------------------------------------------------------
# Example 3: Override with widget-specific source
# ----------------------------------------------------------------------------
[[deck.main]]
type = "MicMute"
source = "alsa_input.pci-0000_00_1f.3.analog-stereo"

# ----------------------------------------------------------------------------
# Example 4: Customize icons and colors
# ----------------------------------------------------------------------------
[[deck.main]]
type = "MicMute"
muted_icon = "🔇"
unmuted_icon = "🎤"
muted_color = "gray"
unmuted_color = "green"

# ----------------------------------------------------------------------------
# Example 5: Use Nerd Font codepoints
# ----------------------------------------------------------------------------
[[deck.main]]
type = "MicMute"
muted_icon = "\ue02b"
unmuted_icon = "\ue029"
muted_color = "blue"
unmuted_color = "red"
```

**Parameters:**

- `source` (optional): PulseAudio source name for this specific widget. If not specified, falls back to the plugin's `default_source`, or the system default source.
- `muted_icon` (optional): Icon to display when muted. Can be a unicode character (e.g., `'🔇'`) or codepoint (e.g., `'\uf036d'`). Default: `'\uf036d'` (nf-md-microphone_off)
- `unmuted_icon` (optional): Icon to display when unmuted. Can be a unicode character (e.g., `'🎤'`) or codepoint (e.g., `'\uf036c'`). Default: `'\uf036c'` (nf-md-microphone)
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

