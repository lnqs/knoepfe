# Knoepfe Example Plugin

A minimal example plugin demonstrating how to create custom widgets for [knoepfe](https://github.com/lnqs/knoepfe).

This plugin serves as a template and learning resource for developers who want to create their own knoepfe widgets.

## Installation

This example plugin is not published to PyPI. To install it for development:

```bash
# Install in development mode from the knoepfe monorepo
uv pip install -e plugins/example

# Or if you're working outside the monorepo
pip install -e /path/to/knoepfe/plugins/example
```

## Widget: ExampleWidget

A simple interactive widget that demonstrates the basic structure and functionality of a knoepfe widget.

### Configuration

```python
# Basic usage with defaults
widget("ExampleWidget")

# Customized configuration
widget("ExampleWidget", {
    'message': 'Hello World'
})
```

### Parameters

- `message` (optional, default: 'Example'): The text message to display on the widget

### Features

- **Interactive Display**: Shows a customizable message with click counter
- **Click Tracking**: Counts and displays the number of times the widget has been clicked
- **State Management**: Demonstrates how to maintain widget state between updates

### Behavior

1. **Initial State**: Shows the configured message with "Click me!" text
2. **After Clicking**: Displays click count

## Development Guide

This example demonstrates the essential components of a knoepfe widget:

### 1. Widget Class Structure

```python
class ExampleWidget(Widget[ExamplePluginState]):
    def __init__(self, widget_config: Dict[str, Any], global_config: Dict[str, Any], plugin_state: ExamplePluginState) -> None:
        # Initialize widget with configuration and plugin state
        
    async def activate(self) -> None:
        # Called when widget becomes active
        
    async def deactivate(self) -> None:
        # Called when widget becomes inactive
        
    async def update(self, key: Key) -> None:
        # Render the widget display
        
    async def on_key_down(self) -> None:
        # Handle key press events
        
    async def on_key_up(self) -> None:
        # Handle key release events
        
    @classmethod
    def get_config_schema(cls) -> Schema:
        # Define configuration parameters
```

### 2. Entry Point Registration

In `pyproject.toml`:

```toml
[project.entry-points."knoepfe.widgets"]
ExampleWidget = "knoepfe_example_plugin.example_widget:ExampleWidget"
```

### 3. Configuration Schema

Use the `schema` library to define and validate configuration parameters:

```python
@classmethod
def get_config_schema(cls) -> Schema:
    schema = Schema({
        Optional('message', default='Example'): str,
    })
    return cls.add_defaults(schema)
```

### 4. Rendering with Key Renderer

Use the key renderer context manager to draw the widget:

```python
async def update(self, key: Key) -> None:
    with key.renderer() as renderer:
        renderer.text('Hello World')
```

### 5. State Management

Widgets can maintain both internal state and shared plugin state:

```python
def __init__(self, widget_config, global_config, plugin_state):
    super().__init__(widget_config, global_config, plugin_state)
    self._click_count = 0  # Internal widget state
    
    # Access shared plugin state
    self.plugin_state.register_widget(f"ExampleWidget-{id(self)}")
    shared_count = self.plugin_state.increment_counter()
```

#### Plugin State vs Widget State

- **Widget State**: Private to each widget instance (e.g., `self._click_count`)
- **Plugin State**: Shared between all widgets of the same plugin (e.g., `self.plugin_state.shared_counter`)

Plugin state is useful for:
- Sharing connections (like OBS WebSocket)
- Coordinating between multiple widget instances
- Maintaining plugin-wide configuration
- Tracking global plugin statistics

### 6. Event Handling

Handle user interactions:

```python
async def on_key_down(self) -> None:
    self._click_count += 1
    self.request_update()  # Trigger re-render
```

## Plugin Structure

```
plugins/example/
├── README.md                          # This file
├── pyproject.toml                     # Package configuration
├── src/
│   └── knoepfe_example_plugin/
│       ├── __init__.py               # Package initialization & plugin descriptor
│       ├── plugin.py                 # Plugin instance with state management
│       └── example_widget.py        # Widget implementation
└── tests/
    └── test_example_widget.py       # Unit tests (optional)
```

### Creating Custom Plugin State

For plugins that need to share data between widgets, create a custom plugin state:

```python
# plugin_state.py
from knoepfe.plugin_state import PluginState

class ExamplePluginState(PluginState):
    def __init__(self, plugin_config):
        super().__init__(plugin_config)
        self.shared_counter = 0
        self.widget_instances = []
    
    def increment_counter(self):
        self.shared_counter += 1
        return self.shared_counter
```

Then implement the `plugin_state` property in your plugin:

```python
# plugin.py
class ExamplePlugin(Plugin):
    def __init__(self, config):
        super().__init__(config)
        self._plugin_state = ExamplePluginState(config)
    
    @property
    def plugin_state(self):
        return self._plugin_state
```

For simple plugins that don't need shared state, use `NullPluginState`:

```python
from knoepfe.plugin_state import NullPluginState

class SimplePlugin(Plugin):
    @property
    def plugin_state(self):
        return NullPluginState()
```

## Key Concepts

### Widget Lifecycle

1. **Initialization**: `__init__()` - Set up initial state and configuration
2. **Activation**: `activate()` - Start background tasks, initialize resources
3. **Updates**: `update()` - Render the widget display (called frequently)
4. **Events**: `on_key_down()`, `on_key_up()` - Handle user interactions
5. **Deactivation**: `deactivate()` - Clean up resources, stop tasks

### Configuration Management

- Use `self.config` to access widget-specific configuration
- Use `self.global_config` to access global knoepfe settings
- Define schema with `get_config_schema()` for validation
- Use `Optional()` with defaults for optional parameters

### Rendering

- Use `key.renderer()` context manager for drawing
- Use `renderer.text()` for text display
- Call `self.request_update()` to trigger re-rendering

## Testing

```bash
# Run tests (if implemented)
pytest plugins/example/tests/

# Test widget discovery
uv run python -m knoepfe list-widgets

# Test widget info
uv run python -m knoepfe widget-info ExampleWidget
```

## Next Steps

To create your own widget:

1. Copy this example plugin structure
2. Rename the package and widget class
3. Implement your custom logic in the widget methods
4. Update the configuration schema for your parameters
5. Add your widget to the entry points in `pyproject.toml`
6. Install and test your plugin

## Resources

- [Knoepfe Documentation](https://github.com/lnqs/knoepfe)
- [Schema Library Documentation](https://github.com/keleshev/schema)
- [Stream Deck SDK](https://developer.elgato.com/documentation/stream-deck/)

## License

GPL-3.0-or-later