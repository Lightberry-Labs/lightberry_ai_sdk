#!/usr/bin/env python3
"""
Test backward compatibility - ensure existing code still works.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the SDK to path
sys.path.insert(0, '.')

from lightberry_ai import LBBasicClient, LBToolClient

# Load environment variables
load_dotenv()


async def test_existing_basic_client_code():
    """Test that existing basic client code still works unchanged"""
    print("Testing existing LBBasicClient code...")
    
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("⚠️  Skipping - no credentials")
        return True
    
    try:
        # This is existing code that should still work
        client = LBBasicClient(
            api_key=api_key,
            device_id=device_id,
            enable_aec=True,
            log_level="WARNING"
        )
        
        await client.connect()
        print(f"✅ Connected: {client.room_name}, {client.participant_name}")
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_existing_tool_client_code():
    """Test that existing tool client code still works unchanged"""
    print("Testing existing LBToolClient code...")
    
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        print("⚠️  Skipping - no credentials")
        return True
    
    try:
        # This is existing code that should still work
        client = LBToolClient(
            api_key=api_key,
            device_id=device_id,
            log_level="WARNING"
        )
        
        await client.connect()
        print(f"✅ Connected: {client.room_name}, {client.participant_name}")
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def main():
    print("\n=== BACKWARD COMPATIBILITY TEST ===")
    print("Testing that existing code still works...\n")
    
    results = []
    
    results.append(await test_existing_basic_client_code())
    results.append(await test_existing_tool_client_code())
    
    if all(results):
        print("\n✅ All backward compatibility tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())