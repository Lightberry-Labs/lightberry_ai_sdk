"""
LightberryToolClient - Audio streaming with tool execution support

This client provides audio streaming with tool execution capabilities using LiveKit
data channels for remote tool calls. Tools are defined in local_tool_responses.py.
"""

import logging
from typing import Optional

# Import the SDK's tool streaming functionality
from .tool_streaming import main_with_tools
from .basic_client import LBBasicClient

logger = logging.getLogger(__name__)


class LBToolClient(LBBasicClient):
    """
    Audio streaming client with tool execution support.
    
    Provides audio streaming plus tool execution capabilities via LiveKit data channels.
    Tools are automatically loaded from local_tool_responses.py using the @tool decorator.
    Audio processing uses 48kHz sample rate with mono channel configuration.
    
    Args:
        api_key: Lightberry API key for authentication (optional for local mode)
        device_id: Device identifier for multi-device client management (optional for local mode)
        use_local: Use local LiveKit server instead of cloud (default: False)
        device_index: Audio device index (None for system default)
        enable_aec: Enable acoustic echo cancellation (default: True)
        log_level: Logging verbosity level (DEBUG, INFO, WARNING, ERROR)
        assistant_name: Optional assistant name to override configured assistant (testing only)
        initial_transcripts: Optional list of transcript dictionaries to initialize conversation history
        session_instructions: Optional instructions to append to the system prompt for this session only
        livekit_url_override: Optional custom LiveKit server URL (e.g., "ws://192.168.1.100:7880")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        device_id: Optional[str] = None,
        use_local: bool = False,
        device_index: Optional[int] = None,
        enable_aec: bool = True,
        log_level: str = "INFO",
        assistant_name: Optional[str] = None,
        initial_transcripts: Optional[list] = None,
        session_instructions: Optional[str] = None,
        livekit_url_override: Optional[str] = None
    ):
        # Call parent constructor with all parameters
        super().__init__(
            api_key=api_key,
            device_id=device_id,
            use_local=use_local,
            device_index=device_index,
            enable_aec=enable_aec,
            log_level=log_level,
            assistant_name=assistant_name,
            initial_transcripts=initial_transcripts,
            session_instructions=session_instructions,
            livekit_url_override=livekit_url_override
        )
        
        # Tool-specific configuration
        self._data_channel_name = "tool_calls"  # Fixed channel name
        
        # Load tools from local_tool_responses.py
        self._load_tools()
        
    def _load_tools(self):
        """Load tools from local_tool_responses.py automatically."""
        try:
            import local_tool_responses
            from local_tool_responses import get_available_tools
            
            tools = get_available_tools()
            logger.info(f"Loaded {len(tools)} tools: {list(tools.keys())}")
            
        except ImportError:
            logger.warning("local_tool_responses.py not found - no tools will be available")
        except Exception as e:
            logger.error(f"Error loading tools: {e}")
    
    async def enable_audio(self) -> None:
        """
        Enable bidirectional audio streaming with tool execution support.
        
        Begins audio streaming, sets up the hardware output device, and enables
        tool execution via data channels. Tools defined in local_tool_responses.py
        will be automatically available. This method will run until manually
        stopped or interrupted.
        
        Raises:
            RuntimeError: If called before connect()
        """
        if not self._participant_name:
            raise RuntimeError("Must call connect() before enable_audio()")
            
        logger.info("Starting audio streaming with tool support...")
        
        # Call the tool streaming function instead of basic audio streaming
        await main_with_tools(
            participant_name=self._participant_name,
            device_index=self.device_index,
            enable_aec=self.enable_aec,
            data_channel_name=self._data_channel_name,
            initial_transcripts=self.initial_transcripts,
            token=self._token,
            livekit_url=self._livekit_url
        )
    
    @property
    def data_channel_name(self) -> str:
        """Get the data channel name used for tool communication."""
        return self._data_channel_name