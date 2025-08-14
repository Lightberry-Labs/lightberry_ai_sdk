#!/usr/bin/env python3
"""Quick test to verify clean output with WARNING log level"""

import asyncio
import sys
sys.path.insert(0, '.')

from lightberry_ai import LBBasicClient

async def test_local_audio():
    print("\n=== Testing Local Audio with WARNING log level ===\n")
    
    client = LBBasicClient(use_local=True, log_level="WARNING")
    
    await client.connect(room_name="test-room")
    print(f"Connected to room: {client.room_name}")
    print(f"Participant: {client.participant_name}")
    print("\nStarting audio stream for 3 seconds...")
    
    # Start audio in background
    audio_task = asyncio.create_task(client.enable_audio())
    
    # Wait 3 seconds
    await asyncio.sleep(3)
    
    # Cancel audio
    audio_task.cancel()
    try:
        await audio_task
    except asyncio.CancelledError:
        pass
    
    await client.disconnect()
    print("Disconnected successfully\n")

if __name__ == "__main__":
    asyncio.run(test_local_audio())