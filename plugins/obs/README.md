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
widget({'type': 'OBSRecording'})
```

**Features:**
- Shows recording status with red indicator when active
- Displays recording timecode
- Long press to start/stop recording
- Short press shows help text

### OBSStreaming
Controls OBS streaming functionality.

**Configuration:**
```python
widget({'type': 'OBSStreaming'})
```

**Features:**
- Shows streaming status with red indicator when active
- Displays streaming timecode
- Long press to start/stop streaming
- Short press shows help text

### OBSCurrentScene
Displays the currently active OBS scene.

**Configuration:**
```python
widget({'type': 'OBSCurrentScene'})
```

**Features:**
- Shows current scene name
- Updates automatically when scene changes
- Grayed out when OBS is disconnected

### OBSSwitchScene
Switch to a specific OBS scene.

**Configuration:**
```python
widget({
    'type': 'OBSSwitchScene',
    'scene': 'Gaming'
})
```

**Parameters:**
- `scene` (required): Name of the OBS scene to switch to

**Features:**
- Shows scene name on button
- Red highlight when scene is active
- Click to switch to the scene
- Grayed out when OBS is disconnected

## OBS Configuration

Configure OBS connection in your knoepfe config:

```python
config({
    'knoepfe_obs_plugin.config': {
        'host': 'localhost',      # OBS WebSocket host
        'port': 4444,             # OBS WebSocket port
        'password': 'your-pass'   # OBS WebSocket password (optional)
    }
})
```

## Requirements

- OBS Studio with WebSocket plugin enabled
- `simpleobsws>=1.4.0` (installed automatically)

## Development

```bash
# Install in development mode
uv pip install -e plugins/obs

# Run tests
pytest plugins/obs/tests/