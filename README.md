# Lightberry AI SDK

A Python SDK for real-time audio streaming with AI tool execution capabilities using LiveKit infrastructure.

## Features

- **Real-time audio streaming** at 48kHz with configurable echo cancellation
- **AI tool execution** via LiveKit data channels for remote function calls
- **Two client types**: Basic audio-only streaming and tool-enabled streaming
- **Terminal audio meters** with logging-friendly alternatives
- **Standalone SDK** with no dependencies on external script files

## Installation

Install the SDK from the project directory:

```bash
cd lightberry_ai_sdk
pip install -e .
```

## Quick Start

### Basic Audio Streaming

```python
import asyncio
from lightberry_ai import LBBasicClient

async def main():
    client = LBBasicClient(
        api_key="your_api_key",
        device_id="your_device_id",
        enable_aec=True
    )
    
    await client.connect()
    await client.enable_audio()

asyncio.run(main())
```

### Tool-Enabled Streaming

```python
import asyncio
from lightberry_ai import LBToolClient

async def main():
    client = LBToolClient(
        api_key="your_api_key", 
        device_id="your_device_id"
    )
    
    await client.connect()
    await client.enable_audio()  # Tools automatically available

asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file in your project:

```bash
LIGHTBERRY_API_KEY=your_api_key
DEVICE_ID=your_device_id
```

### Client Parameters

Both client classes support these parameters:

- `api_key` (str): Lightberry API key for authentication
- `device_id` (str): Device identifier for multi-device management
- `device_index` (int, optional): Audio device index (None for default)
- `enable_aec` (bool): Enable acoustic echo cancellation (default: True)
- `log_level` (str): Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `assistant_name` (str, optional): Override configured assistant (⚠️  testing only!) - If multiple assistants with the same name exist, the first one found will be used

## Custom Tools

### Tool Architecture

Tools in Lightberry AI follow a two-part architecture:

1. **Server-side Definition**: Tools are defined and configured on the **Lightberry Dashboard** where you specify:
   - Tool names and descriptions
   - Parameter schemas and types
   - When the AI agent should call each tool
   
2. **Client-side Implementation**: The `local_tool_responses.py` file defines **how** each tool executes on your device:

```python
from local_tool_responses import tool

@tool(name="move_robot_arm", description="Moves robot arm to position")
def handle_arm_movement(x: float, y: float, z: float) -> dict:
    # Your implementation here - integrate with existing robot control
    robot_controller.move_arm_to(x, y, z)
    return {"result": "success", "position": [x, y, z]}

@tool(name="add_to_order", description="Add item to coffee order")
def add_coffee_item(coffee_type: str, milk_type: str, size: str = "medium") -> dict:
    # Integration with coffee machine API
    coffee_machine.add_order_item(coffee_type, milk_type, size)
    print(f"☕ Added {size} {coffee_type} with {milk_type} milk to order")
    return {"result": "success", "item_added": True}
```

### Workflow

1. **Configure on Dashboard**: Define tools, parameters, and AI behavior on the Lightberry Dashboard
2. **Implement Locally**: Create `local_tool_responses.py` with functions that handle the actual execution
3. **Tool Matching**: When the AI calls a tool, it's routed to your local implementation by name

This separation allows you to:
- Configure AI behavior centrally via the dashboard
- Implement tool execution using your existing codebase and hardware integrations
- Update tool logic locally without changing server configuration

### Current Limitations

**⚠️ Tool Response Feedback**: The AI agent currently does not receive feedback from locally executed tool calls. While your tools execute successfully and can return data, this information is not sent back to the AI agent for follow-up conversations.

**🚀 Coming Soon**: Tool response feedback functionality is in development and will allow the AI agent to:
- Receive and process tool execution results
- Make follow-up decisions based on tool outcomes
- Provide more contextual responses about completed actions

**Important**: The `local_tool_responses.py` file must be in the same directory where you run your script.

## Examples

Complete working examples are available in the [`examples/`](examples/) directory:

- **[`basic_audio_example.py`](examples/basic_audio_example.py)** - Audio-only streaming
- **[`tool_client_example.py`](examples/tool_client_example.py)** - Tool-enabled streaming
- **[`assistant_override_example.py`](examples/assistant_override_example.py)** - Testing with different assistants
- **[`local_tool_responses.py`](examples/local_tool_responses.py)** - Example tool definitions

### Running Examples

```bash
# Copy the tool definitions to your working directory
cp examples/local_tool_responses.py .

# Run basic audio streaming
python examples/basic_audio_example.py

# Run tool-enabled streaming  
python examples/tool_client_example.py
```

See the [examples README](examples/README.md) for detailed usage instructions.

## API Reference

### LightberryBasicClient

Audio-only streaming client.

**Methods:**
- `await connect()` - Authenticate and connect to LiveKit room
- `await enable_audio()` - Enable bidirectional audio streaming (blocks until stopped)
- `await disconnect()` - Disconnect and cleanup

**Properties:**
- `is_connected` - Connection status
- `participant_name` - Assigned participant name
- `room_name` - Assigned room name

### LightberryToolClient

Audio streaming with tool execution support. Inherits all `LightberryBasicClient` functionality.

**Additional Properties:**
- `data_channel_name` - Data channel used for tool communication

**Tool System:**
- Automatically loads tools from `local_tool_responses.py`
- Supports both sync and async tool functions
- Tools receive JSON parameters as keyword arguments
- Tools can control application lifecycle (e.g., `end_session`)

## Audio Configuration

- **Sample Rate**: 48kHz
- **Channels**: Mono
- **Frame Size**: 10ms (480 samples)
- **Echo Cancellation**: Configurable AEC with AudioProcessingModule
- **Audio Meters**: Adaptive display (terminal or logging-based)

## Requirements

- Python 3.8+
- LiveKit Python SDK
- SoundDevice for audio I/O
- NumPy for audio processing
- aiohttp for API communication
- python-dotenv for environment variables

## Troubleshooting

### Tool Import Issues
```
WARNING: local_tool_responses.py not found - no tools will be available
```
**Solution**: Copy `examples/local_tool_responses.py` to your project directory.

### Audio Device Issues
Use `list_devices.py` from the original project to find the correct `device_index`.

### Connection Issues
Verify your `.env` file contains valid `LIGHTBERRY_API_KEY` and `DEVICE_ID`.

## License

See [LICENSE](LICENSE) file for details.