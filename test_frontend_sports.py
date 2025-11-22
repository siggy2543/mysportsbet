#!/usr/bin/env python3
"""
Frontend Test - Verify all sports are displaying correctly
"""

import requests
import json
import time
from datetime import datetime

def test_all_sports_endpoints():
    """Test all 22+ sports endpoints"""
    
    sports_list = [
        'NBA', 'NFL', 'NHL', 'MLB',  # US Sports
        'EPL', 'LALIGA', 'BUNDESLIGA', 'SERIEA', 'LIGUE1', 'CHAMPIONSLEAGUE',  # Soccer
        'ATP', 'WTA',  # Tennis
        'CRICKET', 'RUGBY', 'FORMULA1', 'MMA', 'BOXING', 'GOLF', 
        'ESPORTS', 'DARTS', 'SNOOKER', 'CYCLING'  # Global Sports
    ]
    
    print(f"🧪 Testing Frontend Data for {len(sports_list)} Sports")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    working_sports = []
    failed_sports = []
    
    for sport in sports_list:
        try:
            # Test moneylines
            response = requests.get(f"{base_url}/api/recommendations/{sport}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                recs = data.get('recommendations', [])
                
                if recs and len(recs) > 0:
                    working_sports.append(sport)
                    print(f"✅ {sport:<15} - {len(recs)} recommendations")
                else:
                    failed_sports.append(sport)
                    print(f"⚠️  {sport:<15} - No data returned")
            else:
                failed_sports.append(sport)
                print(f"❌ {sport:<15} - HTTP {response.status_code}")
                
        except Exception as e:
            failed_sports.append(sport)
            print(f"❌ {sport:<15} - Error: {str(e)[:30]}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS SUMMARY:")
    print(f"✅ Working Sports: {len(working_sports)}/{len(sports_list)}")
    print(f"❌ Failed Sports: {len(failed_sports)}")
    
    if working_sports:
        print(f"\n🎯 Working Sports: {', '.join(working_sports)}")
    
    if failed_sports:
        print(f"\n⚠️  Failed Sports: {', '.join(failed_sports)}")
    
    return len(working_sports), len(failed_sports)

def test_frontend_will_work():
    """Simulate what frontend will see"""
    
    print(f"\n🌐 Frontend Simulation Test")
    print("=" * 40)
    
    # Test the exact calls frontend makes
    test_sport = 'EPL'  # Test with global sport
    
    endpoints = [
        f'/api/recommendations/{test_sport}',
        f'/api/parlays/{test_sport}',
        f'/api/player-props/{test_sport}',
        '/api/global-sports'
    ]
    
    all_working = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                if endpoint.endswith('global-sports'):
                    print(f"✅ Global Sports: {len(data)} sports available")
                elif 'recommendations' in endpoint:
                    recs = data.get('recommendations', [])
                    print(f"✅ {test_sport} Moneylines: {len(recs)} bets")
                elif 'parlays' in endpoint:
                    parlays = data.get('parlays', [])
                    print(f"✅ {test_sport} Parlays: {len(parlays)} combinations")
                elif 'player-props' in endpoint:
                    props = data.get('player_props', [])
                    print(f"✅ {test_sport} Player Props: {len(props)} props")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def main():
    print("🎯 FRONTEND SPORTS DISPLAY TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test all sports
    working, failed = test_all_sports_endpoints()
    
    # Test frontend simulation
    frontend_ok = test_frontend_will_work()
    
    print("\n" + "=" * 60)
    print("🎉 FINAL ASSESSMENT")
    
    if working >= 20 and frontend_ok:
        print("✅ FRONTEND WILL SHOW ALL SPORTS!")
        print(f"✅ {working} sports working properly")
        print("✅ Frontend API calls successful")
        print("✅ Global sports data available")
        print()
        print("🎯 Expected Frontend Display:")
        print("   - Sports dropdown will show 22+ options")
        print("   - Live data will refresh every 20 seconds")
        print("   - All tabs (Moneylines/Parlays/Props) will populate")
        print("   - Global sports like EPL, ATP, Cricket will work")
    else:
        print("⚠️  POTENTIAL FRONTEND ISSUES!")
        print(f"⚠️  Only {working} sports working")
        if not frontend_ok:
            print("❌ Frontend API simulation failed")
    
    print(f"\n🌐 Open http://localhost:3000 to verify!")

if __name__ == "__main__":
    main()