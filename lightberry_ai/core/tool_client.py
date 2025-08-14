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
from ..auth import authenticate, authenticate_local

load_dotenv()

logger = logging.getLogger(__name__)


class LBToolClient:
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
        session_instructions: Optional[str] = None
    ):
        # Validate required parameters based on mode
        if not use_local and (not api_key or not device_id):
            raise ValueError("api_key and device_id are required for remote mode")
        
        self.api_key = api_key
        self.device_id = device_id if device_id else "local-device"
        self.use_local = use_local
        self.device_index = device_index
        self.enable_aec = enable_aec
        self.log_level = log_level
        self.assistant_name = assistant_name
        self.initial_transcripts = initial_transcripts
        self.session_instructions = session_instructions
        
        # Internal configuration
        self._data_channel_name = "tool_calls"  # Fixed channel name
        
        # Set by authentication
        self._participant_name: Optional[str] = None
        self._room_name: Optional[str] = None
        self._token: Optional[str] = None
        self._livekit_url: Optional[str] = None
        
        # Configure logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        logger.info(f"LBToolClient initialized with AEC: {enable_aec}")
        
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
        
    async def connect(self, room_name: Optional[str] = None, participant_name: Optional[str] = None) -> None:
        """
        Connect to LiveKit room.
        
        For remote mode: Authenticates using API key and device ID.
        For local mode: Connects to local LiveKit server.
        
        Args:
            room_name: Room name for local mode (ignored in remote mode)
            participant_name: Participant name for local mode (ignored in remote mode)
        
        Raises:
            Exception: If quota is exceeded, displays "Quota reached." message
            Exception: If authentication fails for other reasons
        """
        print("[CORE TEST] Core library edits are working!")
        
        if self.use_local:
            logger.info("Connecting to local LiveKit server...")
            
            # Use provided names or generate defaults for local mode
            if not room_name:
                room_name = "local-room"
            if not participant_name:
                participant_name = f"local-user-{self.device_id}"
                
            # Use local authentication
            auth_func = authenticate_local
        else:
            logger.info("Connecting to Lightberry service...")
            
            # For remote mode, generate participant name from device_id
            participant_name = f"sdk-user-{self.device_id}"
            room_name = os.environ.get("ROOM_NAME", "default-room")
            
            # Use remote authentication
            auth_func = authenticate
        
        try:
            # Pass flag indicating if we have initial transcripts
            has_initial_transcripts = self.initial_transcripts is not None
            
            token, room_name, livekit_url = await auth_func(
                participant_name, 
                room_name, 
                self.assistant_name,
                has_initial_transcripts=has_initial_transcripts,
                session_instructions=self.session_instructions
            )
            
            self._participant_name = participant_name
            self._room_name = room_name
            self._token = token
            self._livekit_url = livekit_url
            
            logger.info(f"Successfully authenticated - Room: {room_name}, Participant: {participant_name}")
            
        except Exception as e:
            # Check for quota exceeded (when server side is implemented)
            if "quota" in str(e).lower():
                raise Exception("Quota reached.")
            else:
                raise e
    
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
        
        # Call the existing main_with_tools function with our parameters and token
        await main_with_tools(
            participant_name=self._participant_name,
            device_index=self.device_index,
            enable_aec=self.enable_aec,
            data_channel_name=self._data_channel_name,
            initial_transcripts=self.initial_transcripts,
            token=self._token,
            livekit_url=self._livekit_url
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
        self._token = None
        self._livekit_url = None
    
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