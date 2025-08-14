#!/usr/bin/env python3
"""
Test script to verify local mode implementation works correctly.
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add the SDK to path
sys.path.insert(0, '.')

from lightberry_ai import LBBasicClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_local_mode():
    """Test local mode connection"""
    logger.info("=" * 50)
    logger.info("Testing LOCAL mode")
    logger.info("=" * 50)
    
    try:
        # Create client in local mode
        client = LBBasicClient(use_local=True, log_level="INFO")
        
        logger.info(f"Client created with device_id: {client.device_id}")
        
        # Try to connect
        await client.connect(room_name="test-local-room")
        
        logger.info(f"✅ Successfully connected!")
        logger.info(f"   Room: {client.room_name}")
        logger.info(f"   Participant: {client.participant_name}")
        logger.info(f"   URL: {client._livekit_url}")
        
        await client.disconnect()
        logger.info("✅ Disconnected successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Local mode test failed: {e}")
        return False


async def test_remote_mode():
    """Test remote mode connection (existing functionality)"""
    logger.info("=" * 50)
    logger.info("Testing REMOTE mode")
    logger.info("=" * 50)
    
    # Check if we have credentials
    api_key = os.getenv("LIGHTBERRY_API_KEY")
    device_id = os.getenv("DEVICE_ID")
    
    if not api_key or not device_id:
        logger.warning("⚠️  Skipping remote test - no credentials in environment")
        logger.info("   Set LIGHTBERRY_API_KEY and DEVICE_ID to test remote mode")
        return None
    
    try:
        # Create client in remote mode
        client = LBBasicClient(
            api_key=api_key,
            device_id=device_id,
            log_level="INFO"
        )
        
        logger.info(f"Client created with device_id: {device_id}")
        
        # Try to connect
        await client.connect()
        
        logger.info(f"✅ Successfully connected!")
        logger.info(f"   Room: {client.room_name}")
        logger.info(f"   Participant: {client.participant_name}")
        logger.info(f"   URL: {client._livekit_url}")
        
        await client.disconnect()
        logger.info("✅ Disconnected successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Remote mode test failed: {e}")
        return False


async def test_parameter_validation():
    """Test that parameters are validated correctly"""
    logger.info("=" * 50)
    logger.info("Testing parameter validation")
    logger.info("=" * 50)
    
    # Test 1: Remote mode without credentials should fail
    try:
        client = LBBasicClient(use_local=False)
        logger.error("❌ Should have raised ValueError for missing credentials")
        return False
    except ValueError as e:
        logger.info(f"✅ Correctly raised ValueError: {e}")
    
    # Test 2: Local mode without credentials should work
    try:
        client = LBBasicClient(use_local=True)
        logger.info(f"✅ Local mode created without credentials")
        logger.info(f"   device_id defaulted to: {client.device_id}")
    except Exception as e:
        logger.error(f"❌ Local mode should work without credentials: {e}")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LIGHTBERRY SDK - LOCAL MODE TESTS")
    print("=" * 60)
    
    results = {}
    
    # Test parameter validation
    results['validation'] = await test_parameter_validation()
    
    # Test local mode
    print("\n⚠️  Make sure local LiveKit server is running!")
    print("   Run './start-all.sh' in local-livekit directory\n")
    
    results['local'] = await test_local_mode()
    
    # Test remote mode
    results['remote'] = await test_remote_mode()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{test_name.capitalize():15} {status}")
    
    # Overall result
    failures = [r for r in results.values() if r is False]
    if failures:
        print(f"\n❌ {len(failures)} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())