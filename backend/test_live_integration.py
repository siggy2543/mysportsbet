#!/usr/bin/env python3
"""
Test script for the new live sports data integration
Tests BetsAPI, TheSportsDB, and OpenAI integration
"""

import asyncio
import sys
import os

# Add the backend directory to the path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from services.live_sports_data_service import live_sports_service

async def test_live_data_integration():
    """Test the live data integration"""
    print("🏀 Testing Live Sports Data Integration")
    print("=" * 50)
    
    # Test sports
    test_sports = ['NBA', 'NFL', 'EPL']
    
    for sport in test_sports:
        print(f"\n📊 Testing {sport} data...")
        
        try:
            # Test live games
            games = await live_sports_service.get_live_games(sport)
            print(f"✅ {sport} Games: {len(games)} games found")
            
            if games:
                sample_game = games[0]
                print(f"   Sample: {sample_game.away_team} @ {sample_game.home_team}")
                print(f"   Status: {sample_game.status}, Start: {sample_game.start_time}")
                
                # Test odds for the sample game
                odds = await live_sports_service.get_live_odds(sample_game.id, sport)
                print(f"   Odds: {len(odds)} bookmaker(s)")
                
            # Test AI predictions
            predictions = await live_sports_service.get_ai_predictions(games[:3], sport)
            print(f"✅ {sport} Predictions: {len(predictions)} predictions generated")
            
            # Test comprehensive data
            comprehensive_data = await live_sports_service.get_comprehensive_live_data(sport)
            print(f"✅ {sport} Comprehensive: {comprehensive_data['total_games']} total games")
            print(f"   Data sources: {comprehensive_data['data_sources']}")
            
        except Exception as e:
            print(f"❌ Error testing {sport}: {e}")
    
    print("\n🎯 Live Data Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_live_data_integration())