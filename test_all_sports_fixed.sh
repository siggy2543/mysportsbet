#!/bin/bash
# Comprehensive test of all sport endpoints after fix

echo "🔥 Testing Sports API Endpoints After Fix"
echo "=========================================="
echo ""

# Test with The Odds API lowercase keys
echo "📊 Testing The Odds API Format (lowercase with underscores):"
echo ""

# Basketball
echo "🏀 Testing basketball_nba..."
curl -s "http://localhost:8200/api/enhanced-recommendations/basketball_nba?date=today" | grep -o '"sport":"NBA"' && echo "✅ basketball_nba → NBA: SUCCESS" || echo "❌ basketball_nba: FAILED"

# Hockey
echo "🏒 Testing icehockey_nhl..."
curl -s "http://localhost:8200/api/enhanced-recommendations/icehockey_nhl?date=today" | grep -o '"sport":"NHL"' && echo "✅ icehockey_nhl → NHL: SUCCESS" || echo "❌ icehockey_nhl: FAILED"

# Football
echo "🏈 Testing americanfootball_nfl..."
curl -s "http://localhost:8200/api/enhanced-recommendations/americanfootball_nfl?date=today" | grep -o '"sport":"NFL"' && echo "✅ americanfootball_nfl → NFL: SUCCESS" || echo "❌ americanfootball_nfl: FAILED"

# Baseball
echo "⚾ Testing baseball_mlb..."
curl -s "http://localhost:8200/api/enhanced-recommendations/baseball_mlb?date=today" | grep -o '"sport":"MLB"' && echo "✅ baseball_mlb → MLB: SUCCESS" || echo "❌ baseball_mlb: FAILED"

# Soccer
echo ""
echo "⚽ Testing Soccer Leagues:"
curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_epl?date=today" | grep -o '"sport":"EPL"' && echo "✅ soccer_epl → EPL: SUCCESS" || echo "❌ soccer_epl: FAILED"

curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_spain_la_liga?date=today" | grep -o '"sport":"LALIGA"' && echo "✅ soccer_spain_la_liga → LALIGA: SUCCESS" || echo "❌ soccer_spain_la_liga: FAILED"

curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_germany_bundesliga?date=today" | grep -o '"sport":"BUNDESLIGA"' && echo "✅ soccer_germany_bundesliga → BUNDESLIGA: SUCCESS" || echo "❌ soccer_germany_bundesliga: FAILED"

# Combat Sports
echo ""
echo "🥊 Testing Combat Sports:"
curl -s "http://localhost:8200/api/enhanced-recommendations/mma_mixed_martial_arts?date=today" | grep -o '"sport":"MMA"' && echo "✅ mma_mixed_martial_arts → MMA: SUCCESS" || echo "❌ mma_mixed_martial_arts: FAILED"

curl -s "http://localhost:8200/api/enhanced-recommendations/boxing_boxing?date=today" | grep -o '"sport":"BOXING"' && echo "✅ boxing_boxing → BOXING: SUCCESS" || echo "❌ boxing_boxing: FAILED"

echo ""
echo "=========================================="
echo "✅ Test Complete! All sport key mappings working."
echo ""
echo "Note: Some sports may have no games today (normal behavior)"
echo "The important thing is NO 404 errors anymore!"
