#!/usr/bin/env python3
"""
Quick validation script for the enhanced sports platform
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/global-sports",
        "/api/recommendations/NBA",
        "/api/recommendations/EPL",
        "/api/parlays/NBA",
        "/api/player-props/NBA"
    ]
    
    print("🔍 Testing API Endpoints...")
    print("=" * 50)
    
    all_working = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - OK ({len(str(data))} chars)")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
                all_working = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - ERROR: {str(e)}")
            all_working = False
    
    return all_working

def test_global_sports():
    """Test global sports coverage"""
    try:
        response = requests.get("http://localhost:8000/api/global-sports", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🌍 Global Sports Coverage:")
            print(f"Total Sports: {len(data)}")
            
            categories = {}
            for sport, info in data.items():
                category = info.get('category', 'Unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append(sport)
            
            for category, sports in categories.items():
                print(f"  {category}: {', '.join(sports)}")
            
            return True
        else:
            print(f"❌ Global sports endpoint failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Global sports test failed: {e}")
        return False

def test_live_data():
    """Test live data generation"""
    print(f"\n📊 Testing Live Data Generation...")
    
    sports_to_test = ['NBA', 'EPL', 'ATP', 'CRICKET']
    
    for sport in sports_to_test:
        try:
            response = requests.get(f"http://localhost:8000/api/recommendations/{sport}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                recs = data.get('recommendations', [])
                print(f"  {sport}: {len(recs)} recommendations generated")
            else:
                print(f"  {sport}: Failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"  {sport}: Error - {e}")

def main():
    print("🎯 Enhanced Sports Platform - System Validation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Test global sports
    sports_ok = test_global_sports()
    
    # Test live data
    test_live_data()
    
    print("\n" + "=" * 60)
    
    if api_ok and sports_ok:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("✅ All systems operational")
        print("🌐 Frontend: http://localhost:3000")
        print("🔌 API: http://localhost:8000")
        sys.exit(0)
    else:
        print("⚠️  VALIDATION FAILED!")
        print("❌ Some systems not working properly")
        sys.exit(1)

if __name__ == "__main__":
    main()