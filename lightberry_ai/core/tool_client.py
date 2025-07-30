"""
LightberryToolClient - Audio streaming with tool execution support

This client provides audio streaming with tool execution capabilities using LiveKit
data channels for remote tool calls. Tools are defined in local_tool_responses.py.
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Import the SDK's tool streaming functionality
from .tool_streaming import main_with_tools
from ..auth.authenticator import authenticate

load_dotenv()

logger = logging.getLogger(__name__)


class LightberryToolClient:
    """
    Audio streaming client with tool execution support.
    
    Provides audio streaming plus tool execution capabilities via LiveKit data channels.
    Tools are automatically loaded from local_tool_responses.py using the @tool decorator.
    Audio processing uses 48kHz sample rate with mono channel configuration.
    
    Args:
        api_key: Lightberry API key for authentication
        device_id: Device identifier for multi-device client management
        device_index: Audio device index (None for system default)
        enable_aec: Enable acoustic echo cancellation (default: True)
        log_level: Logging verbosity level (DEBUG, INFO, WARNING, ERROR)
    """
    
    def __init__(
        self,
        api_key: str,
        device_id: str,
        device_index: Optional[int] = None,
        enable_aec: bool = True,
        log_level: str = "INFO"
    ):
        self.api_key = api_key
        self.device_id = device_id
        self.device_index = device_index
        self.enable_aec = enable_aec
        self.log_level = log_level
        
        # Internal configuration
        self._data_channel_name = "tool_calls"  # Fixed channel name
        
        # Set by authentication
        self._participant_name: Optional[str] = None
        self._room_name: Optional[str] = None
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        logger.info(f"LightberryToolClient initialized with AEC: {enable_aec}")
        
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
        
    async def connect(self) -> None:
        """
        Connect to LiveKit room using API authentication.
        
        Authenticates using API key and device ID, retrieves room name and
        participant name from the authentication service.
        
        Raises:
            Exception: If quota is exceeded, displays "Quota reached." message
            Exception: If authentication fails for other reasons
        """
        logger.info("Connecting to Lightberry service...")
        
        # Use existing auth function - it will use DEVICE_ID from environment
        # TODO: Pass api_key when server side is ready to accept it
        try:
            # For now, generate a participant name and use fallback room
            fallback_room = os.environ.get("ROOM_NAME", "default-room")
            participant_name = f"sdk-user-{self.device_id}"
            
            token, room_name = await authenticate(participant_name, fallback_room)
            
            self._participant_name = participant_name
            self._room_name = room_name
            
            logger.info(f"Successfully authenticated - Room: {room_name}, Participant: {participant_name}")
            
        except Exception as e:
            # Check for quota exceeded (when server side is implemented)
            if "quota" in str(e).lower():
                raise Exception("Quota reached.")
            else:
                raise e
    
    async def start_streaming(self) -> None:
        """
        Start audio streaming with tool execution support.
        
        Begins audio streaming and enables tool execution via data channels.
        Tools defined in local_tool_responses.py will be automatically available.
        This method will run until manually stopped or interrupted.
        
        Raises:
            RuntimeError: If called before connect()
        """
        if not self._participant_name:
            raise RuntimeError("Must call connect() before start_streaming()")
            
        logger.info("Starting audio streaming with tool support...")
        
        # Call the existing main_with_tools function with our parameters
        await main_with_tools(
            participant_name=self._participant_name,
            device_index=self.device_index,
            enable_aec=self.enable_aec,
            data_channel_name=self._data_channel_name
        )
    
    async def disconnect(self) -> None:
        """
        Disconnect from the LiveKit room.
        
        Performs cleanup and disconnects from the LiveKit room.
        """
        logger.info("Disconnecting from Lightberry service...")
        # The main_with_tools function handles its own cleanup
        self._participant_name = None
        self._room_name = None
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected and ready for streaming."""
        return self._participant_name is not None
    
    @property
    def participant_name(self) -> Optional[str]:
        """Get the participant name assigned by authentication."""
        return self._participant_name
    
    @property
    def room_name(self) -> Optional[str]:
        """Get the room name assigned by authentication."""
        return self._room_name
    
    @property
    def data_channel_name(self) -> str:
        """Get the data channel name used for tool communication."""
        return self._data_channel_name