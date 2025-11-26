#!/bin/bash
# Quick health check script - Run anytime to verify system status

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🏆 Sports Betting Platform Health Check           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check containers
echo "📦 Container Status:"
docker-compose ps --format "   {{.Service}}: {{.Status}}" | head -7
echo ""

# Check API
echo "🔌 API Endpoints:"
API_HEALTH=$(curl -s http://localhost:8200/health 2>/dev/null)
if echo "$API_HEALTH" | grep -q "healthy"; then
    echo "   ✅ API Health: OK"
else
    echo "   ❌ API Health: DOWN"
fi

SPORTS_COUNT=$(curl -s http://localhost:8200/api/odds/sports 2>/dev/null | grep -o '"total_sports":[0-9]*' | grep -o '[0-9]*')
if [ "$SPORTS_COUNT" = "149" ]; then
    echo "   ✅ Sports API: 149 sports available"
else
    echo "   ⚠️  Sports API: $SPORTS_COUNT sports (expected 149)"
fi

# Test sample sport
NBA_TEST=$(curl -s "http://localhost:8200/api/enhanced-recommendations/basketball_nba?date=today" 2>/dev/null | grep -o '"sport":"NBA"')
if [ ! -z "$NBA_TEST" ]; then
    echo "   ✅ Sport Data: Working (tested basketball_nba)"
else
    echo "   ❌ Sport Data: Failed"
fi

echo ""

# Check frontend
echo "🌐 Frontend Status:"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend: Accessible at http://localhost:3000"
else
    echo "   ❌ Frontend: HTTP $FRONTEND_STATUS"
fi

echo ""

# Check for errors
echo "🔍 Error Check:"
API_ERRORS=$(docker logs sports_app-api-1 --tail 50 2>&1 | grep -c "ERROR")
if [ "$API_ERRORS" = "0" ]; then
    echo "   ✅ API Logs: No errors"
else
    echo "   ⚠️  API Logs: $API_ERRORS errors found"
fi

FRONTEND_ERRORS=$(docker logs sports_app-frontend-1 --tail 50 2>&1 | grep -ci "error")
if [ "$FRONTEND_ERRORS" = "0" ]; then
    echo "   ✅ Frontend Logs: No errors"
else
    echo "   ⚠️  Frontend Logs: $FRONTEND_ERRORS errors found"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

# Final verdict
if [ "$SPORTS_COUNT" = "149" ] && [ "$FRONTEND_STATUS" = "200" ] && [ "$API_ERRORS" = "0" ]; then
    echo "   🎉 Status: ALL SYSTEMS OPERATIONAL"
else
    echo "   ⚠️  Status: ATTENTION NEEDED"
fi

echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Quick Links:"
echo "  • Frontend: http://localhost:3000"
echo "  • API Docs: http://localhost:8200/docs"
echo "  • API Health: http://localhost:8200/health"
echo ""
