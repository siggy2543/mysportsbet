#!/usr/bin/env python3
"""Quick validation of deployed betting platform"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: ERROR - {e}")
        return False

def test_sports_coverage():
    """Test expanded sports coverage"""
    sports = [
        'NBA', 'NFL', 'NHL', 'MLB', 'NCAAB', 'NCAAF',  # US Sports
        'EPL', 'LALIGA', 'BUNDESLIGA', 'SERIEA', 'LIGUE1', 'UCL', 'MLS',  # Soccer
        'UFC', 'BOXING',  # Combat
        'ATP', 'WTA',  # Tennis
        'GOLF', 'NASCAR', 'F1',  # Individual
        'ESPORTS'  # E-Sports
    ]
    
    print(f"\n🏆 Testing {len(sports)} Sports:")
    passed = 0
    failed = 0
    
    for sport in sports:
        try:
            response = requests.get(
                f"{BASE_URL}/api/recommendations/{sport}?date=today",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                num_bets = len(data.get('recommendations', []))
                print(f"  ✅ {sport}: {num_bets} bets")
                passed += 1
            else:
                print(f"  ❌ {sport}: Failed (Status: {response.status_code})")
                failed += 1
        except Exception as e:
            print(f"  ❌ {sport}: Error - {str(e)[:50]}")
            failed += 1
    
    print(f"\nSports Coverage: {passed}/{len(sports)} passed")
    return passed, failed

def test_parlay_structure():
    """Test parlay generation (3-leg, 4-leg, 5-leg)"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/parlays/NBA?date=today",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            parlays = data.get('parlays', [])
            
            if len(parlays) != 9:
                print(f"❌ Parlay Count: Expected 9, got {len(parlays)}")
                return False
            
            leg_counts = [p['num_legs'] for p in parlays]
            three_leg = leg_counts.count(3)
            four_leg = leg_counts.count(4)
            five_leg = leg_counts.count(5)
            
            print(f"\n🎲 Parlay Structure Test:")
            print(f"  ✅ Total Parlays: {len(parlays)}")
            print(f"  ✅ 3-leg Parlays: {three_leg}")
            print(f"  ✅ 4-leg Parlays: {four_leg}")
            print(f"  ✅ 5-leg Parlays: {five_leg}")
            
            # Check first parlay structure
            first = parlays[0]
            if 'legs' in first and 'matchup' in first['legs'][0]:
                print(f"  ✅ Leg Structure: Valid (has matchup field)")
            else:
                print(f"  ❌ Leg Structure: Invalid")
                return False
            
            if three_leg == 3 and four_leg == 3 and five_leg == 3:
                print(f"  ✅ Distribution: Perfect (3 each of 3/4/5-leg)")
                return True
            else:
                print(f"  ❌ Distribution: Incorrect")
                return False
        else:
            print(f"❌ Parlay Test: Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Parlay Test: ERROR - {e}")
        return False

def test_bet_structure():
    """Test individual bet structure"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/NBA?date=today",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            bets = data.get('recommendations', [])
            
            if not bets:
                print("❌ Bet Structure: No bets returned")
                return False
            
            first_bet = bets[0]
            required_fields = ['matchup', 'bet', 'odds', 'confidence', 'expected_value']
            
            print(f"\n💰 Bet Structure Test:")
            all_present = True
            for field in required_fields:
                if field in first_bet:
                    print(f"  ✅ Field '{field}': Present")
                else:
                    print(f"  ❌ Field '{field}': Missing")
                    all_present = False
            
            # Check odds structure
            if 'recommended_odds' in first_bet.get('odds', {}):
                print(f"  ✅ Odds Structure: Valid (has recommended_odds)")
            else:
                print(f"  ❌ Odds Structure: Invalid")
                all_present = False
            
            return all_present
        else:
            print(f"❌ Bet Structure Test: Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Bet Structure Test: ERROR - {e}")
        return False

def test_frontend():
    """Test frontend is serving"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200 and "Sports Betting Platform" in response.text:
            print("\n🌐 Frontend Test:")
            print("  ✅ Frontend: Serving correctly")
            return True
        else:
            print("\n🌐 Frontend Test:")
            print(f"  ❌ Frontend: Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print("\n🌐 Frontend Test:")
        print(f"  ❌ Frontend: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Sports Betting Platform - Quick Validation Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # Test API Health
    results.append(test_api_health())
    
    # Test Sports Coverage
    passed, failed = test_sports_coverage()
    results.append(failed == 0)
    
    # Test Parlay Structure
    results.append(test_parlay_structure())
    
    # Test Bet Structure
    results.append(test_bet_structure())
    
    # Test Frontend
    results.append(test_frontend())
    
    # Summary
    print("\n" + "=" * 60)
    total_passed = sum(results)
    total_tests = len(results)
    
    if total_passed == total_tests:
        print(f"✅ ALL TESTS PASSED ({total_passed}/{total_tests})")
        print("🎉 DEPLOYMENT SUCCESSFUL - READY FOR PRODUCTION")
    else:
        print(f"⚠️  {total_passed}/{total_tests} tests passed")
        print("❌ Some tests failed - review output above")
    
    print("=" * 60)
    
    return total_passed == total_tests

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
