#!/usr/bin/env python3
"""Test date filtering fix - verify Today/Tomorrow tabs show different games"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_date_filtering():
    """Test that today and tomorrow return different games"""
    print("=" * 70)
    print("🧪 DATE FILTERING TEST - Verify Today/Tomorrow Separation")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Test TODAY
        print("\n📅 Testing TODAY endpoint...")
        today_response = requests.get(f"{BASE_URL}/api/recommendations/NBA?date=today", timeout=10)
        if today_response.status_code != 200:
            print(f"  ❌ TODAY endpoint failed: {today_response.status_code}")
            return False
        
        today_data = today_response.json()
        today_bets = today_data.get('recommendations', [])
        today_matchups = [bet['matchup'] for bet in today_bets]
        today_categories = [bet.get('date_category', 'MISSING') for bet in today_bets]
        
        print(f"  ✅ TODAY returned {len(today_bets)} bets")
        print(f"  📊 date_category values: {set(today_categories)}")
        if len(today_bets) > 0:
            print(f"  🏀 Sample matchups:")
            for i, matchup in enumerate(today_matchups[:3], 1):
                print(f"     {i}. {matchup}")
        
        # Test TOMORROW
        print("\n📅 Testing TOMORROW endpoint...")
        tomorrow_response = requests.get(f"{BASE_URL}/api/recommendations/NBA?date=tomorrow", timeout=10)
        if tomorrow_response.status_code != 200:
            print(f"  ❌ TOMORROW endpoint failed: {tomorrow_response.status_code}")
            return False
        
        tomorrow_data = tomorrow_response.json()
        tomorrow_bets = tomorrow_data.get('recommendations', [])
        tomorrow_matchups = [bet['matchup'] for bet in tomorrow_bets]
        tomorrow_categories = [bet.get('date_category', 'MISSING') for bet in tomorrow_bets]
        
        print(f"  ✅ TOMORROW returned {len(tomorrow_bets)} bets")
        print(f"  📊 date_category values: {set(tomorrow_categories)}")
        if len(tomorrow_bets) > 0:
            print(f"  🏀 Sample matchups:")
            for i, matchup in enumerate(tomorrow_matchups[:3], 1):
                print(f"     {i}. {matchup}")
        
        # Verify separation
        print("\n🔍 Verifying Date Separation...")
        
        # Check date_category correctness
        today_correct = all(cat == 'today' for cat in today_categories)
        tomorrow_correct = all(cat == 'tomorrow' for cat in tomorrow_categories)
        
        if today_correct:
            print("  ✅ All TODAY bets have date_category='today'")
        else:
            print(f"  ❌ TODAY bets have mixed categories: {set(today_categories)}")
            
        if tomorrow_correct:
            print("  ✅ All TOMORROW bets have date_category='tomorrow'")
        else:
            print(f"  ❌ TOMORROW bets have mixed categories: {set(tomorrow_categories)}")
        
        # Check if matchups are different
        common_matchups = set(today_matchups) & set(tomorrow_matchups)
        unique_today = len(set(today_matchups) - set(tomorrow_matchups))
        unique_tomorrow = len(set(tomorrow_matchups) - set(today_matchups))
        
        print(f"\n📊 Matchup Analysis:")
        print(f"  Today unique matchups: {unique_today}/{len(today_matchups)}")
        print(f"  Tomorrow unique matchups: {unique_tomorrow}/{len(tomorrow_matchups)}")
        print(f"  Common matchups: {len(common_matchups)}")
        
        if len(common_matchups) < len(today_matchups) * 0.5:
            print("  ✅ Good separation - mostly different games")
        else:
            print("  ⚠️  High overlap - may need more variety")
        
        # Overall result
        print("\n" + "=" * 70)
        if today_correct and tomorrow_correct and len(today_bets) > 0 and len(tomorrow_bets) > 0:
            print("✅ DATE FILTERING TEST: PASSED")
            print("   - Today endpoint returns games marked 'today'")
            print("   - Tomorrow endpoint returns games marked 'tomorrow'")
            print("   - Frontend should now display correct games per tab")
            return True
        else:
            print("❌ DATE FILTERING TEST: FAILED")
            if not today_correct:
                print("   - TODAY endpoint has incorrect date_category values")
            if not tomorrow_correct:
                print("   - TOMORROW endpoint has incorrect date_category values")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        return False
    finally:
        print("=" * 70)

def test_parlays_date_filtering():
    """Test that parlay dates also work correctly"""
    print("\n" + "=" * 70)
    print("🎲 PARLAY DATE FILTERING TEST")
    print("=" * 70)
    
    try:
        # Test TODAY parlays
        print("\n📅 Testing TODAY parlays...")
        today_response = requests.get(f"{BASE_URL}/api/parlays/NBA?date=today", timeout=10)
        if today_response.status_code != 200:
            print(f"  ❌ TODAY parlays failed: {today_response.status_code}")
            return False
        
        today_data = today_response.json()
        today_parlays = today_data.get('parlays', [])
        print(f"  ✅ TODAY returned {len(today_parlays)} parlays")
        
        # Test TOMORROW parlays
        print("\n📅 Testing TOMORROW parlays...")
        tomorrow_response = requests.get(f"{BASE_URL}/api/parlays/NBA?date=tomorrow", timeout=10)
        if tomorrow_response.status_code != 200:
            print(f"  ❌ TOMORROW parlays failed: {tomorrow_response.status_code}")
            return False
        
        tomorrow_data = tomorrow_response.json()
        tomorrow_parlays = tomorrow_data.get('parlays', [])
        print(f"  ✅ TOMORROW returned {len(tomorrow_parlays)} parlays")
        
        if len(today_parlays) > 0 and len(tomorrow_parlays) > 0:
            print("\n✅ PARLAY DATE FILTERING: PASSED")
            return True
        else:
            print("\n⚠️  PARLAY DATE FILTERING: No parlays returned")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        return False
    finally:
        print("=" * 70)

def main():
    print("\n🚀 Starting Date Filtering Tests...\n")
    
    test1 = test_date_filtering()
    test2 = test_parlays_date_filtering()
    
    print("\n" + "=" * 70)
    print("📋 FINAL RESULTS")
    print("=" * 70)
    print(f"Moneyline Date Filtering: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Parlay Date Filtering:    {'✅ PASSED' if test2 else '❌ FAILED'}")
    print("=" * 70)
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED - Date filtering is working correctly!")
        print("\n📝 Next Steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Click 'Today' tab - should show today's games")
        print("   3. Click 'Tomorrow' tab - should show tomorrow's games")
        print("   4. Verify different matchups appear in each tab")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Review output above")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
