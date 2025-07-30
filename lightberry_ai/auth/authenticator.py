"""
Authentication module for Lightberry AI SDK

Handles authentication with Lightberry API service and fallback to local token generation.
"""

import os
import json
import aiohttp
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv
from livekit import api

# Load environment variables from .env file
load_dotenv()

# Get LiveKit credentials from environment variables
LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET")
DEVICE_ID = os.environ.get("DEVICE_ID")
LIGHTBERRY_API_KEY = os.environ.get("LIGHTBERRY_API_KEY")

# Auth API configuration
AUTH_API_URL = "https://lightberry.vercel.app/api/authenticate/{}"

logger = logging.getLogger(__name__)


def generate_token(room_name, identity=None, name=None):
    """
    Generate a LiveKit access token for room access.
    
    Args:
        room_name: The name of the room to join
        identity: The participant identity
        name: The display name (default: same as identity)
    
    Returns:
        JWT token string
    """
    if not identity:
        identity = f"python-user-{room_name}"
    
    if not name:
        name = identity
        
    # Check if required environment variables are set
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env file")
    
    # Create token with video grants
    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
        .to_jwt()
    )
    
    return token


async def get_credentials_from_api(participant_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches LiveKit token and room name from the authentication API.
    
    Args:
        participant_name: The participant name (username)
    
    Returns:
        Tuple of (token, room_name) or (None, None) if failed
    """
    if not DEVICE_ID:
        logger.error("DEVICE_ID not set in environment variables")
        return None, None
    
    url = AUTH_API_URL.format(DEVICE_ID)
    
    # TODO: Add LIGHTBERRY_API_KEY to payload when server side is ready
    # Current payload format maintained for compatibility
    api_key = LIGHTBERRY_API_KEY  # Reference API key for future use
    payload = {"username": participant_name, "x-device-api-key": participant_name}
    logger.info(f"Attempting to fetch credentials from {url} for username '{participant_name}', device_id '{DEVICE_ID}'")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                
                if data.get("success"):
                    token = data.get("livekit_token")
                    room_name = data.get("room_name")
                    if token and room_name:
                        logger.info(f"Successfully retrieved credentials: {room_name}")
                        return token, room_name
                    else:
                        logger.error("API response missing token or room name.")
                        return None, None
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error(f"API request failed: {error_msg}")
                    return None, None
    except Exception as e:
        logger.error(f"Error fetching credentials from API: {e}")
        return None, None


async def authenticate(participant_name: str, fallback_room_name: str) -> Tuple[str, str]:
    """
    Unified authentication function that tries remote API first, then falls back to local token generation.
    
    Args:
        participant_name: The participant name (username)
        fallback_room_name: Room name to use if API fails
    
    Returns:
        Tuple of (token, room_name)
    """
    # Try to get credentials from auth API first
    api_token, api_room_name = await get_credentials_from_api(participant_name)
    
    if api_token and api_room_name:
        logger.info(f"Using auth API credentials for room: {api_room_name}")
        return api_token, api_room_name
    else:
        logger.info("Auth API failed, falling back to local token generation")
        token = generate_token(fallback_room_name, participant_name, participant_name)
        return token, fallback_room_name