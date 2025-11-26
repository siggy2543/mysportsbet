#!/usr/bin/env python3
"""
Test Sport Configurations - Verify Unique Mappings
This validates that each sport has a unique configuration
"""

import sys
sys.path.append('./backend')

from comprehensive_sports_config import THE_ODDS_API_SPORTS_CONFIG, get_sport_config, get_all_sports

def test_unique_configs():
    """Test that similar sports have unique configurations"""
    
    print("=" * 60)
    print("TESTING UNIQUE SPORT CONFIGURATIONS")
    print("=" * 60)
    print()
    
    # Test 1: NCAAB vs NBA (the original bug)
    print("Test 1: NCAAB vs NBA (Original Bug)")
    print("-" * 60)
    
    nba_config = get_sport_config('basketball_nba')
    ncaab_config = get_sport_config('basketball_ncaab')
    
    print(f"NBA Display Name: {nba_config.get('display_name')}")
    print(f"NBA Description: {nba_config.get('description')}")
    print(f"NCAAB Display Name: {ncaab_config.get('display_name')}")
    print(f"NCAAB Description: {ncaab_config.get('description')}")
    
    if nba_config.get('display_name') == ncaab_config.get('display_name'):
        print("❌ FAILED: NCAAB and NBA have the same display name!")
        return False
    else:
        print("✓ PASSED: NCAAB and NBA have unique configurations")
    print()
    
    # Test 2: NCAAF vs NFL
    print("Test 2: NCAAF vs NFL")
    print("-" * 60)
    
    nfl_config = get_sport_config('americanfootball_nfl')
    ncaaf_config = get_sport_config('americanfootball_ncaaf')
    
    print(f"NFL Display Name: {nfl_config.get('display_name')}")
    print(f"NFL Description: {nfl_config.get('description')}")
    print(f"NCAAF Display Name: {ncaaf_config.get('display_name')}")
    print(f"NCAAF Description: {ncaaf_config.get('description')}")
    
    if nfl_config.get('display_name') == ncaaf_config.get('display_name'):
        print("❌ FAILED: NCAAF and NFL have the same display name!")
        return False
    else:
        print("✓ PASSED: NCAAF and NFL have unique configurations")
    print()
    
    # Test 3: Count total sports
    print("Test 3: Total Sports Count")
    print("-" * 60)
    
    all_sports = get_all_sports()
    total_count = len(all_sports)
    
    print(f"Total sports configured: {total_count}")
    
    if total_count >= 70:
        print(f"✓ PASSED: {total_count} sports configured (target: 70+)")
    else:
        print(f"⚠ WARNING: Only {total_count} sports configured (target: 70+)")
    print()
    
    # Test 4: Check key sports exist
    print("Test 4: Key Sports Existence")
    print("-" * 60)
    
    key_sports = [
        'basketball_nba',
        'basketball_ncaab',
        'americanfootball_nfl',
        'americanfootball_ncaaf',
        'soccer_epl',
        'soccer_spain_la_liga',
        'icehockey_nhl',
        'baseball_mlb',
        'mma_mixed_martial_arts',
        'cricket_big_bash',
        'tennis_atp_french_open'
    ]
    
    all_exist = True
    for sport_key in key_sports:
        if sport_key in THE_ODDS_API_SPORTS_CONFIG:
            print(f"✓ {sport_key}: Configured")
        else:
            print(f"❌ {sport_key}: MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✓ PASSED: All key sports exist")
    else:
        print("\n❌ FAILED: Some key sports are missing")
        return False
    print()
    
    # Test 5: Check for duplicate display names in same category
    print("Test 5: No Duplicate Display Names in Same Category")
    print("-" * 60)
    
    categories = {}
    for sport_key, config in THE_ODDS_API_SPORTS_CONFIG.items():
        category = config.get('category', 'Unknown')
        display_name = config.get('display_name', '')
        
        if category not in categories:
            categories[category] = {}
        
        if display_name in categories[category]:
            print(f"❌ DUPLICATE: {display_name} in {category}")
            print(f"   - {categories[category][display_name]}")
            print(f"   - {sport_key}")
            return False
        else:
            categories[category][display_name] = sport_key
    
    print("✓ PASSED: No duplicate display names within categories")
    print()
    
    # Test 6: List categories
    print("Test 6: Sport Categories")
    print("-" * 60)
    
    category_counts = {}
    for config in THE_ODDS_API_SPORTS_CONFIG.values():
        category = config.get('category', 'Unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count} sports")
    print()
    
    return True


if __name__ == "__main__":
    print()
    success = test_unique_configs()
    print()
    print("=" * 60)
    
    if success:
        print("✓ ALL CONFIGURATION TESTS PASSED!")
        print("Sport mappings are unique and correct.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the configuration.")
        sys.exit(1)
