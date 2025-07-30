# Installation Guide

## Development Installation (Editable)

For development and testing, install the package in editable mode:

```bash
# From the project directory
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Testing the Installation

```bash
# Test the SDK
python test_sdk.py

# Test basic audio streaming
python examples/basic_audio_example.py

# Test tool-enabled streaming  
python examples/tool_client_example.py
```

## Package Installation (Future)

Once published to PyPI:

```bash
pip install lightberry-ai
```

## Usage After Installation

```python
from lightberry_ai import LightberryBasicClient, LightberryToolClient

# Basic client
client = LightberryBasicClient(api_key="your_key", device_id="your_device")
await client.connect()
await client.start_streaming()

# Tool client
tool_client = LightberryToolClient(api_key="your_key", device_id="your_device")
await tool_client.connect() 
await tool_client.start_streaming()
```

## Requirements

- Python 3.8+
- LiveKit Python SDK
- Audio device access
- Environment variables set in `.env`

## Environment Setup

Create `.env` file with your Lightberry credentials:
```bash
LIGHTBERRY_API_KEY=your_api_key
DEVICE_ID=your_device_id
```

Note: LiveKit connection details are provided by the Lightberry authentication service.