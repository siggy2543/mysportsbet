#!/usr/bin/env python3
"""
Quick Deployment Status Check
"""
import requests
import sys
from datetime import datetime

def check_deployment():
    print("🔍 DEPLOYMENT STATUS CHECK")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Check API
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend API: RUNNING")
            
            # Check global sports
            sports_response = requests.get("http://localhost:8000/api/global-sports", timeout=3)
            if sports_response.status_code == 200:
                sports = sports_response.json()
                print(f"✅ Global Sports: {len(sports)} available")
                
                # Test a few key sports
                test_sports = ["NBA", "EPL", "ATP", "CRICKET"]
                working_sports = 0
                
                for sport in test_sports:
                    try:
                        sport_response = requests.get(f"http://localhost:8000/api/recommendations/{sport}", timeout=3)
                        if sport_response.status_code == 200:
                            data = sport_response.json()
                            recs = data.get('recommendations', [])
                            if recs:
                                print(f"✅ {sport}: {len(recs)} recommendations")
                                working_sports += 1
                            else:
                                print(f"⚠️ {sport}: No data")
                        else:
                            print(f"❌ {sport}: HTTP {sport_response.status_code}")
                    except:
                        print(f"❌ {sport}: Error")
                
                if working_sports >= 3:
                    print(f"✅ Sports Data: {working_sports}/{len(test_sports)} working")
                else:
                    print(f"⚠️ Sports Data: Only {working_sports}/{len(test_sports)} working")
            else:
                print("❌ Global Sports: Failed")
        else:
            print(f"❌ Backend API: HTTP {response.status_code}")
    except:
        print("❌ Backend API: NOT RESPONDING")
    
    # Check Frontend
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        if response.status_code == 200:
            print("✅ Frontend: RUNNING")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
    except:
        print("❌ Frontend: NOT RESPONDING")
    
    print("\n" + "=" * 40)
    print("🌐 Access URLs:")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8000")
    print("   Global Sports: http://localhost:8000/api/global-sports")

if __name__ == "__main__":
    check_deployment()