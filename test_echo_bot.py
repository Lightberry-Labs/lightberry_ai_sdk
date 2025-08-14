#!/usr/bin/env python3
"""Test connecting to echo bot in the correct room"""

import asyncio
import sys
sys.path.insert(0, '.')

from lightberry_ai import LBBasicClient

async def test_echo():
    print("\n=== Testing Echo Bot Connection ===")
    print("Connecting to room 'echo-test' where the bot is waiting...\n")
    
    client = LBBasicClient(use_local=True, log_level="WARNING")
    
    await client.connect(room_name="echo-test")
    print(f"✅ Connected to room: {client.room_name}")
    print(f"   Participant: {client.participant_name}")
    print("\n🎤 Starting audio - speak and you should hear an echo!")
    print("   Press Ctrl+C to stop\n")
    
    try:
        await client.enable_audio()
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    await client.disconnect()
    print("Disconnected successfully")

if __name__ == "__main__":
    asyncio.run(test_echo())