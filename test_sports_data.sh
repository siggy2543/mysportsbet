#!/bin/bash

# Test script to check which sports have live data
echo "Testing Sports Data Availability..."
echo "===================================="
echo ""

# Major US Sports
echo "🏀 Testing NBA..."
curl -s "http://localhost:8200/api/enhanced-recommendations/basketball_nba?date=today" | grep -q '"recommendations":\[' && echo "✅ NBA: Data available" || echo "❌ NBA: No data"

echo "🏒 Testing NHL..."
curl -s "http://localhost:8200/api/enhanced-recommendations/icehockey_nhl?date=today" | grep -q '"recommendations":\[' && echo "✅ NHL: Data available" || echo "❌ NHL: No data"

echo "🏈 Testing NFL..."
curl -s "http://localhost:8200/api/enhanced-recommendations/americanfootball_nfl?date=today" | grep -q '"recommendations":\[' && echo "✅ NFL: Data available" || echo "❌ NFL: No data"

echo "⚾ Testing MLB..."
curl -s "http://localhost:8200/api/enhanced-recommendations/baseball_mlb?date=today" | grep -q '"recommendations":\[' && echo "✅ MLB: Data available" || echo "❌ MLB: No data"

echo "🏀 Testing NCAA Basketball..."
curl -s "http://localhost:8200/api/enhanced-recommendations/basketball_ncaab?date=today" | grep -q '"recommendations":\[' && echo "✅ NCAA Basketball: Data available" || echo "❌ NCAA Basketball: No data"

# International Soccer
echo ""
echo "⚽ Testing Soccer Leagues..."
curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_epl?date=today" | grep -q '"recommendations":\[' && echo "✅ EPL: Data available" || echo "❌ EPL: No data"

curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_spain_la_liga?date=today" | grep -q '"recommendations":\[' && echo "✅ La Liga: Data available" || echo "❌ La Liga: No data"

curl -s "http://localhost:8200/api/enhanced-recommendations/soccer_uefa_champs_league?date=today" | grep -q '"recommendations":\[' && echo "✅ Champions League: Data available" || echo "❌ Champions League: No data"

# Other Sports
echo ""
echo "🎾 Testing Other Sports..."
curl -s "http://localhost:8200/api/enhanced-recommendations/tennis_atp?date=today" | grep -q '"recommendations":\[' && echo "✅ Tennis ATP: Data available" || echo "❌ Tennis ATP: No data"

curl -s "http://localhost:8200/api/enhanced-recommendations/mma_mixed_martial_arts?date=today" | grep -q '"recommendations":\[' && echo "✅ MMA: Data available" || echo "❌ MMA: No data"

curl -s "http://localhost:8200/api/enhanced-recommendations/boxing_boxing?date=today" | grep -q '"recommendations":\[' && echo "✅ Boxing: Data available" || echo "❌ Boxing: No data"

echo ""
echo "===================================="
echo "✅ Test Complete"
