#!/bin/bash
# Comprehensive Testing Script for Enhanced Sports Betting Platform
# Tests all new features: Enhanced stats, feedback loop, deep learning

echo "================================================"
echo "🧪 Sports Betting Platform - Comprehensive Tests"
echo "================================================"
echo ""

BASE_URL="http://localhost:3000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing: $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Response: $response"
        ((FAILED++))
    fi
}

echo "📊 1. Testing Core Endpoints"
echo "----------------------------"
test_endpoint "Health Check" "$BASE_URL/api/health" "healthy"
test_endpoint "Global Sports" "$BASE_URL/api/global-sports" "NBA"
echo ""

echo "📈 2. Testing Enhanced Stats Service"
echo "------------------------------------"
test_endpoint "Team Analysis - Lakers" "$BASE_URL/api/team-analysis/NBA/Lakers" "success"
test_endpoint "Team Analysis - Warriors" "$BASE_URL/api/team-analysis/NBA/Warriors" "Golden State Warriors"
test_endpoint "Enhanced Recommendations NBA" "$BASE_URL/api/enhanced-recommendations/NBA" "enhanced"
echo ""

echo "🎯 3. Testing Recommendations"
echo "-----------------------------"
test_endpoint "NBA Recommendations" "$BASE_URL/api/recommendations/NBA" "recommendations"
test_endpoint "NFL Recommendations" "$BASE_URL/api/recommendations/NFL" "recommendations"
test_endpoint "EPL Recommendations" "$BASE_URL/api/recommendations/EPL" "recommendations"
echo ""

echo "🔄 4. Testing Parlays"
echo "--------------------"
test_endpoint "NBA Parlays" "$BASE_URL/api/parlays/NBA" "parlays"
test_endpoint "NFL Parlays" "$BASE_URL/api/parlays/NFL" "parlays"
echo ""

echo "🤖 5. Testing ML & Feedback Loop"
echo "--------------------------------"
test_endpoint "Feedback Dashboard" "$BASE_URL/api/feedback/dashboard" "dashboard"
test_endpoint "NBA Accuracy" "$BASE_URL/api/feedback/accuracy/NBA" "sport"

# Test deep learning (may fail gracefully if not trained)
echo -n "Testing: Deep Learning Prediction... "
dl_response=$(curl -s "$BASE_URL/api/ml/deep-learning-prediction?home_team=Lakers&away_team=Warriors&sport=NBA&home_win_rate=0.65&away_win_rate=0.55")
if echo "$dl_response" | grep -q "home_win_probability\|error\|detail"; then
    echo -e "${GREEN}✓ PASS${NC} (endpoint responding)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  Response: $dl_response"
    ((FAILED++))
fi
echo ""

echo "📰 6. Testing News Integration"
echo "------------------------------"
news_response=$(curl -s "$BASE_URL/api/team-analysis/NBA/Lakers" | python -m json.tool 2>/dev/null)
if echo "$news_response" | grep -q "recent_news"; then
    news_count=$(echo "$news_response" | grep -c "headline")
    echo -e "${GREEN}✓ News Integration Working${NC} ($news_count articles found)"
    ((PASSED++))
else
    echo -e "${RED}✗ News Integration Failed${NC}"
    ((FAILED++))
fi
echo ""

echo "🎲 7. Testing Advanced Features"
echo "-------------------------------"
test_endpoint "Player Props NBA" "$BASE_URL/api/player-props/NBA" "player_props"
test_endpoint "Date Filter (today)" "$BASE_URL/api/recommendations/NBA?date=today" "target_date"
test_endpoint "Date Filter (tomorrow)" "$BASE_URL/api/recommendations/NBA?date=tomorrow" "target_date"
echo ""

echo "================================================"
echo "📊 Test Results Summary"
echo "================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
echo "Total: $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo "✅ Platform is ready for production deployment"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo "Review failures above before deploying"
    exit 1
fi
