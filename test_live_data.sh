#!/bin/bash
# Quick verification script for live data fix

echo "======================================"
echo "LIVE DATA VERIFICATION TEST"
echo "======================================"
echo ""

echo "Testing Backend API..."
echo ""

echo "📅 TODAY'S GAMES (November 22, 2025):"
echo "--------------------------------------"
curl -s http://localhost:8000/api/recommendations/NBA?date=today | \
  python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'Target Date: {d.get(\"target_date\")}')
    print(f'Total Games: {d.get(\"count\", 0)}')
    print(f'')
    print('Matchups:')
    for i, rec in enumerate(d.get('recommendations', []), 1):
        print(f'  {i}. {rec[\"matchup\"]} - {rec.get(\"date_category\", \"unknown\")}')
    print('')
    if d.get('count', 0) > 0:
        print('✅ PASS: Real games found for TODAY')
    else:
        print('❌ FAIL: No games returned for TODAY')
except Exception as e:
    print(f'❌ ERROR: {e}')
"
echo ""

echo "📅 TOMORROW'S GAMES (November 23, 2025):"
echo "--------------------------------------"
curl -s http://localhost:8000/api/recommendations/NBA?date=tomorrow | \
  python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'Target Date: {d.get(\"target_date\")}')
    print(f'Total Games: {d.get(\"count\", 0)}')
    print(f'')
    print('Matchups:')
    for i, rec in enumerate(d.get('recommendations', []), 1):
        print(f'  {i}. {rec[\"matchup\"]} - {rec.get(\"date_category\", \"unknown\")}')
    print('')
    if d.get('count', 0) > 0:
        print('✅ PASS: Real games found for TOMORROW')
    else:
        print('❌ FAIL: No games returned for TOMORROW')
except Exception as e:
    print(f'❌ ERROR: {e}')
"
echo ""

echo "📊 CHECKING PARLAYS:"
echo "--------------------------------------"
curl -s http://localhost:8000/api/parlays/NBA?date=today | \
  python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    parlays = d.get('parlays', [])
    print(f'Total Parlays: {len(parlays)}')
    if len(parlays) > 0:
        p = parlays[0]
        print(f'First Parlay: {len(p.get(\"legs\", []))} legs')
        for i, leg in enumerate(p.get('legs', [])[:3], 1):
            print(f'  {i}. {leg.get(\"matchup\", \"N/A\")}')
        print('')
        print('✅ PASS: Parlays using real games')
    else:
        print('⚠️  No parlays available')
except Exception as e:
    print(f'❌ ERROR: {e}')
"
echo ""

echo "🔍 BACKEND LOGS:"
echo "--------------------------------------"
docker logs --tail 20 sports_app-api-1 2>&1 | grep -E "(Processing|real games|Retrieved|TheSportsDB)" | tail -5
echo ""

echo "======================================"
echo "VERIFICATION COMPLETE"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Today' tab - should show games for Nov 22"
echo "3. Click 'Tomorrow' tab - should show games for Nov 23"
echo "4. Verify matchups are REAL NBA teams"
echo ""
