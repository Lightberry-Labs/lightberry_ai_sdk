# Lightberry SDK Examples

This directory contains usage examples for the Lightberry SDK.

## Prerequisites

1. Set up your environment variables in `.env`:
```bash
LIGHTBERRY_API_KEY=lb_your_api_key
DEVICE_ID=your_device_id
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
ROOM_NAME=your_default_room
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Examples

### Basic Audio Streaming (`basic_audio_example.py`)

Audio-only streaming without tool support:

```bash
python examples/basic_audio_example.py
```

This example demonstrates:
- Creating a `LightberryBasicClient` 
- Connecting with API key and device ID
- Starting audio streaming with echo cancellation

### Tool-Enabled Streaming (`tool_client_example.py`)

Audio streaming with tool execution support:

```bash
python examples/tool_client_example.py
```

This example demonstrates:
- Creating a `LightberryToolClient`
- Automatic loading of tools from `local_tool_responses.py`
- Handling remote tool calls via data channels

## Custom Tools

**Important**: The `local_tool_responses.py` file must be in the same directory where you run your script.

To add custom tools, edit `local_tool_responses.py` in your project directory:

```python
@tool(name="my_custom_tool", description="Does something useful")
def my_function(param1: str, param2: int = 42) -> dict:
    print(f"Tool called: my_custom_tool with {param1}, {param2}")
    return {"result": "success", "processed": param1}
```

### Tool Setup
1. Copy `examples/local_tool_responses.py` to your project directory
2. Modify it to add your custom tools
3. Run your script from the same directory

### Available Example Tools
The example `local_tool_responses.py` includes:
- `template` - Demonstration tool that echoes arguments
- Coffee order tools: `add_to_order`, `get_current_order`, `amend_order`, `send_order`
- `end_session` - Gracefully disconnect from the session

Tools are automatically available to `LightberryToolClient` instances.

## Usage Patterns

### Basic Usage
```python
from lightberry_ai import LightberryBasicClient

client = LightberryBasicClient(api_key=api_key, device_id=device_id)
await client.connect()
await client.start_streaming()
```

### Tool-Enabled Usage
```python
from lightberry_ai import LightberryToolClient

client = LightberryToolClient(api_key=api_key, device_id=device_id)
await client.connect()
await client.start_streaming()  # Tools automatically available
```

### Configuration Options
```python
client = LightberryBasicClient(
    api_key=api_key,
    device_id=device_id,
    device_index=1,           # Specific audio device
    enable_aec=False,         # Disable echo cancellation
    log_level="DEBUG"         # Verbose logging
)
```