# Knoepfe OBS Plugin

OBS Studio integration widgets for [knoepfe](https://github.com/lnqs/knoepfe).

## Installation

```bash
# Install with knoepfe
pip install knoepfe[obs]

# Or install separately
pip install knoepfe-obs-plugin
```

## Widgets

### OBSRecording
Controls OBS recording functionality.

**Configuration:**
```python
# Use default icons and colors
widget.OBSRecording()

# Customize icons and colors
widget.OBSRecording(
    recording_icon='🔴',
    stopped_icon='⏹️',
    loading_icon='⏳',
    recording_color='green',
    stopped_color='blue'
)
```

**Parameters:**
- `recording_icon` (optional): Icon when recording. Can be unicode character or codepoint. Default: `'\ue04b'`
- `stopped_icon` (optional): Icon when stopped. Can be unicode character or codepoint. Default: `'\ue04c'`
- `loading_icon` (optional): Icon when loading. Can be unicode character or codepoint. Default: `'\ue5d3'`
- `recording_color` (optional): Icon/text color when recording. Default: `'red'`
- `stopped_color` (optional): Icon color when stopped. Default: `'white'`

**Features:**
- Shows recording status with customizable colors
- Displays recording timecode
- Long press to start/stop recording
- Short press shows help text
- Fully customizable icons and colors

### OBSStreaming
Controls OBS streaming functionality.

**Configuration:**
```python
# Use default icons and colors
widget.OBSStreaming()

# Customize icons and colors
widget.OBSStreaming(
    streaming_icon='📡',
    stopped_icon='🚫',
    loading_icon='⏳',
    streaming_color='green',
    stopped_color='blue'
)
```

**Parameters:**
- `streaming_icon` (optional): Icon when streaming. Can be unicode character or codepoint. Default: `'\ue0e2'`
- `stopped_icon` (optional): Icon when stopped. Can be unicode character or codepoint. Default: `'\ue0e3'`
- `loading_icon` (optional): Icon when loading. Can be unicode character or codepoint. Default: `'\ue5d3'`
- `streaming_color` (optional): Icon/text color when streaming. Default: `'red'`
- `stopped_color` (optional): Icon color when stopped. Default: `'white'`

**Features:**
- Shows streaming status with customizable colors
- Displays streaming timecode
- Long press to start/stop streaming
- Short press shows help text
- Fully customizable icons and colors

### OBSCurrentScene
Displays the currently active OBS scene.

**Configuration:**
```python
# Use default icon and color
widget.OBSCurrentScene()

# Customize icon and color
widget.OBSCurrentScene(
    icon='🎬',
    connected_color='cyan'
)
```

**Parameters:**
- `icon` (optional): Scene icon. Can be unicode character or codepoint. Default: `'\ue40b'`
- `connected_color` (optional): Icon/text color when connected. Default: `'white'`

**Features:**
- Shows current scene name
- Updates automatically when scene changes
- Grayed out when OBS is disconnected
- Customizable icon and color

### OBSSwitchScene
Switch to a specific OBS scene.

**Configuration:**
```python
# Basic usage
widget.OBSSwitchScene(scene='Gaming')

# Customize icon and colors
widget.OBSSwitchScene(
    scene='Gaming',
    icon='🎮',
    active_color='green',
    inactive_color='gray'
)
```

**Parameters:**
- `scene` (required): Name of the OBS scene to switch to
- `icon` (optional): Scene icon. Can be unicode character or codepoint. Default: `'\ue40b'`
- `active_color` (optional): Icon/text color when scene is active. Default: `'red'`
- `inactive_color` (optional): Icon/text color when scene is inactive. Default: `'white'`

**Features:**
- Shows scene name on button
- Customizable highlight when scene is active
- Click to switch to the scene
- Grayed out when OBS is disconnected
- Fully customizable icon and colors

## Plugin Configuration

Configure OBS connection and global settings in your knoepfe config:

```python
plugin.obs(
    # Host OBS is running. Probably `localhost`.
    host='localhost',
    # Port to obs-websocket is listening on. Defaults to 4455.
    port=4455,
    # Password to use when authenticating with obs-websocket.
    password='supersecret',
    # Icon color when OBS is disconnected (applies to all widgets)
    disconnected_color='#202020'
)
```

**Parameters:**
- `host` (optional): OBS WebSocket host. Default: `'localhost'`
- `port` (optional): OBS WebSocket port. Default: `4455`
- `password` (optional): OBS WebSocket password. Default: `None`
- `disconnected_color` (optional): Icon color when OBS is disconnected. Default: `'#202020'`

## Requirements

- OBS Studio with WebSocket plugin enabled
- `simpleobsws>=1.4.0` (installed automatically)

## Development

```bash
# Install in development mode
uv pip install -e plugins/obs

# Run tests
pytest plugins/obs/tests/