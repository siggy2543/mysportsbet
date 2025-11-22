#!/usr/bin/env python3
"""
Test TheSportsDB API endpoints to find the correct authentication method
"""

import asyncio
import aiohttp
import os

async def test_thesportsdb_endpoints():
    """Test different TheSportsDB endpoints"""
    print("🏀 Testing TheSportsDB API Endpoints")
    print("=" * 50)
    
    username = os.getenv('THESPORTSDB_USERNAME', 'cigbat2543')
    password = os.getenv('THESPORTSDB_PASSWORD', 'Jets2543!')
    
    # Test endpoints
    endpoints = [
        "https://www.thesportsdb.com/api/v1/json/eventsnextleague.php?id=4387",  # Free NBA
        f"https://www.thesportsdb.com/api/v1/json/{username}_{password}/eventsnextleague.php?id=4387",  # Auth NBA
        "https://www.thesportsdb.com/api/v1/json/all_sports.php",  # All sports free
        f"https://www.thesportsdb.com/api/v1/json/{username}_{password}/all_sports.php",  # All sports auth
        "https://www.thesportsdb.com/api/v1/json/searchteams.php?t=Lakers",  # Team search
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(endpoints, 1):
            print(f"\n{i}. Testing: {url[:80]}...")
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Status: {response.status}")
                        if isinstance(data, dict):
                            for key in list(data.keys())[:3]:  # Show first 3 keys
                                print(f"      - {key}: {type(data[key])}")
                        else:
                            print(f"      - Response type: {type(data)}")
                    else:
                        print(f"   ❌ Status: {response.status}")
                        text = await response.text()
                        print(f"      - Error: {text[:100]}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    print("\n🎯 TheSportsDB API Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_thesportsdb_endpoints())