#!/usr/bin/env python3

"""
Quick test script to debug the live data service
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_standalone_api import LiveDataService

async def test_live_data():
    print("Testing LiveDataService...")
    service = LiveDataService()
    
    try:
        result = await service.get_live_odds('NBA')
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if 'games' in result:
            print(f"Games count: {len(result['games'])}")
            if result['games']:
                print(f"First game keys: {result['games'][0].keys()}")
        else:
            print("No 'games' key found")
            
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_live_data())
    print("Test completed")