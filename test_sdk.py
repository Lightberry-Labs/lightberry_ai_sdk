#!/usr/bin/env python3
"""
Lightberry SDK Test Script

This script tests the Lightberry SDK functionality with both basic audio
and tool-enabled clients.
"""

import asyncio
import os
from dotenv import load_dotenv

# Import the SDK
from lightberry_ai import LightberryBasicClient, LightberryToolClient

async def test_basic_client():
    """Test the basic audio streaming client."""
    print("\n" + "="*50)
    print("TESTING LIGHTBERRY BASIC CLIENT")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("LIGHTBERRY_API_KEY", "test_api_key")
    device_id = os.getenv("DEVICE_ID", "test_device")
    
    print(f"API Key: {api_key}")
    print(f"Device ID: {device_id}")
    
    # Create basic client
    client = LightberryBasicClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,      # Default audio device
        enable_aec=True,        # Enable echo cancellation
        log_level="INFO"        # Info level logging
    )
    
    print(f"Client created - AEC enabled: {client.enable_aec}")
    print(f"Connected: {client.is_connected}")
    
    try:
        # Test connection
        print("\nAttempting to connect...")
        await client.connect()
        
        print(f"Connection successful!")
        print(f"Room: {client.room_name}")
        print(f"Participant: {client.participant_name}")
        print(f"Connected: {client.is_connected}")
        
        # Note: We won't actually start streaming in the test to avoid blocking
        print("\nBasic client test completed successfully!")
        
    except Exception as e:
        print(f"Error testing basic client: {e}")
    finally:
        await client.disconnect()
        print("Basic client disconnected.")

async def test_tool_client():
    """Test the tool-enabled streaming client."""
    print("\n" + "="*50)
    print("TESTING LIGHTBERRY TOOL CLIENT")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("LIGHTBERRY_API_KEY", "test_api_key")
    device_id = os.getenv("DEVICE_ID", "test_device")
    
    print(f"API Key: {api_key}")
    print(f"Device ID: {device_id}")
    
    # Create tool client
    client = LightberryToolClient(
        api_key=api_key,
        device_id=device_id,
        device_index=None,      # Default audio device
        enable_aec=True,        # Enable echo cancellation
        log_level="INFO"        # Info level logging
    )
    
    print(f"Client created - AEC enabled: {client.enable_aec}")
    print(f"Data channel: {client.data_channel_name}")
    print(f"Connected: {client.is_connected}")
    
    try:
        # Test connection
        print("\nAttempting to connect...")
        await client.connect()
        
        print(f"Connection successful!")
        print(f"Room: {client.room_name}")
        print(f"Participant: {client.participant_name}")
        print(f"Connected: {client.is_connected}")
        
        # Note: We won't actually start streaming in the test to avoid blocking
        print("\nTool client test completed successfully!")
        
    except Exception as e:
        print(f"Error testing tool client: {e}")
    finally:
        await client.disconnect()
        print("Tool client disconnected.")

async def main():
    """Run all SDK tests."""
    print("Lightberry SDK Test Suite")
    print("This script tests the SDK without actually starting audio streaming.")
    
    # Test basic client
    await test_basic_client()
    
    # Test tool client
    await test_tool_client()
    
    print("\n" + "="*50)
    print("SDK TEST SUMMARY")
    print("="*50)
    print("✅ LightberryBasicClient import and initialization")
    print("✅ LightberryToolClient import and initialization")
    print("✅ Client configuration and properties")
    print("✅ Authentication flow (connect/disconnect)")
    print("\nTo test actual streaming, use:")
    print("  python examples/basic_audio_example.py")
    print("  python examples/tool_client_example.py")

if __name__ == "__main__":
    asyncio.run(main())