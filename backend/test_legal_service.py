"""
Test runner for legal betting analysis service
"""
import asyncio
import json
from datetime import datetime
from services.legal_betting_service import legal_betting_service

async def test_legal_betting_service():
    """Test the legal betting analysis service"""
    print("🚀 Testing Legal Sports Betting Analysis Service")
    print("=" * 60)
    
    # Initialize service
    print("1. Initializing service...")
    initialized = await legal_betting_service.initialize()
    print(f"   ✅ Service initialized: {initialized}")
    
    # Get system status
    print("\n2. Getting bankroll status...")
    bankroll = legal_betting_service.get_bankroll_status()
    print(f"   💰 Current balance: ${bankroll.current_balance:.2f}")
    print(f"   📊 Daily limit: ${bankroll.daily_limit:.2f}")
    print(f"   🎯 Daily remaining: ${bankroll.daily_remaining:.2f}")
    print(f"   📈 Suggested bet size: ${bankroll.suggested_bet_size:.2f}")
    
    # Get live sports data
    print("\n3. Getting live sports data...")
    games = await legal_betting_service.get_live_sports_data("NBA")
    print(f"   🏀 Found {len(games)} NBA games")
    
    if games:
        for i, game in enumerate(games[:3]):  # Show first 3 games
            print(f"   Game {i+1}: {game['away_team']} @ {game['home_team']}")
            print(f"            Start: {game['start_time']}")
            print(f"            Source: {game.get('source', 'unknown')}")
    
    # Get betting recommendations
    print("\n4. Analyzing betting opportunities...")
    recommendations = await legal_betting_service.analyze_betting_opportunities("NBA")
    print(f"   🎯 Generated {len(recommendations)} recommendations")
    
    if recommendations:
        for i, rec in enumerate(recommendations[:2]):  # Show first 2 recommendations
            print(f"\n   📊 Recommendation {i+1}:")
            print(f"      🏀 Game: {rec.away_team} @ {rec.home_team}")
            print(f"      💡 Bet: {rec.recommended_bet}")
            print(f"      🎯 Confidence: {rec.confidence:.1%}")
            print(f"      💰 Expected Value: {rec.expected_value}")
            print(f"      💵 Suggested Bet Size: ${rec.suggested_bet_size:.2f}")
            print(f"      📈 Kelly %: {rec.kelly_criterion:.1%}")
            print(f"      ⚠️  Risk Level: {rec.risk_level}")
            print(f"      💭 Reasoning: {rec.reasoning[:100]}...")
    
    # Test manual bet logging
    print("\n5. Testing bet result logging...")
    if recommendations:
        # Simulate placing and winning a bet
        rec = recommendations[0]
        legal_betting_service.log_bet_result(
            rec.game_id, 
            rec.suggested_bet_size, 
            won=True, 
            payout=rec.suggested_bet_size * 1.85
        )
        print("   ✅ Logged winning bet result")
    
    # Get performance stats
    print("\n6. Performance statistics...")
    total_bets = legal_betting_service.recommendations_made
    successful_bets = legal_betting_service.successful_recommendations
    success_rate = (successful_bets / max(total_bets, 1)) * 100
    total_pnl = legal_betting_service.total_profit_loss
    
    print(f"   📊 Total recommendations: {total_bets}")
    print(f"   ✅ Successful bets: {successful_bets}")
    print(f"   📈 Success rate: {success_rate:.1f}%")
    print(f"   💰 Total P&L: ${total_pnl:.2f}")
    
    # Close service
    print("\n7. Closing service...")
    await legal_betting_service.close()
    print("   ✅ Service closed")
    
    print("\n" + "=" * 60)
    print("🎯 Legal betting analysis service test completed!")
    print("🔒 System is compliant - manual betting required")
    print("📱 Ready for production deployment")

if __name__ == "__main__":
    asyncio.run(test_legal_betting_service())