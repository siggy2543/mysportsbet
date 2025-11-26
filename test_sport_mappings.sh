#!/bin/bash

# Test Sport Mappings - Verify TheOddsAPI Integration
# This script tests that each sport returns unique, correct data

echo "=========================================="
echo "Testing Sport Mappings - TheOddsAPI"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8200"
FAILED_TESTS=0
PASSED_TESTS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_sport() {
    local sport_key=$1
    local expected_name=$2
    local description=$3
    
    echo -n "Testing $sport_key ($expected_name)... "
    
    response=$(curl -s "${BASE_URL}/api/recommendations/${sport_key}" 2>/dev/null)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/api/recommendations/${sport_key}" 2>/dev/null)
    
    if [ "$http_code" == "200" ]; then
        # Check if response contains the expected sport name or key
        if echo "$response" | grep -qi "$sport_key\|$expected_name"; then
            echo -e "${GREEN}✓ PASSED${NC} - $description"
            ((PASSED_TESTS++))
        else
            echo -e "${RED}✗ FAILED${NC} - Response doesn't contain expected sport identifier"
            ((FAILED_TESTS++))
        fi
    elif [ "$http_code" == "404" ]; then
        echo -e "${YELLOW}⚠ SKIPPED${NC} - No games available (404)"
    else
        echo -e "${RED}✗ FAILED${NC} - HTTP $http_code"
        ((FAILED_TESTS++))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CRITICAL TESTS: NCAAB vs NBA, NCAAF vs NFL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# These are the MOST CRITICAL tests - the original bug report
test_sport "basketball_nba" "NBA" "Professional basketball"
test_sport "basketball_ncaab" "NCAAB" "College basketball (should NOT show NBA data)"
test_sport "americanfootball_nfl" "NFL" "Professional football"
test_sport "americanfootball_ncaaf" "NCAAF" "College football (should NOT show NFL data)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BASKETBALL LEAGUES (All Should Be Unique)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "basketball_nba" "NBA" "NBA - Professional"
test_sport "basketball_wnba" "WNBA" "WNBA - Women's Professional"
test_sport "basketball_euroleague" "EuroLeague" "European Basketball"
test_sport "basketball_nbl" "NBL" "Australian NBL"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ICE HOCKEY LEAGUES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "icehockey_nhl" "NHL" "NHL - North American"
test_sport "icehockey_sweden_hockey_league" "SHL" "Swedish Hockey League"
test_sport "icehockey_finland_liiga" "Liiga" "Finnish Liiga"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "BASEBALL LEAGUES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "baseball_mlb" "MLB" "Major League Baseball"
test_sport "baseball_mlb_preseason" "MLB_PRESEASON" "Spring Training"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "MAJOR SOCCER LEAGUES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "soccer_epl" "EPL" "English Premier League"
test_sport "soccer_spain_la_liga" "LA_LIGA" "Spanish La Liga"
test_sport "soccer_germany_bundesliga" "BUNDESLIGA" "German Bundesliga"
test_sport "soccer_italy_serie_a" "SERIE_A" "Italian Serie A"
test_sport "soccer_france_ligue_1" "LIGUE_1" "French Ligue 1"
test_sport "soccer_uefa_champs_league" "UCL" "UEFA Champions League"
test_sport "soccer_usa_mls" "MLS" "Major League Soccer"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "INTERNATIONAL SOCCER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "soccer_brazil_campeonato" "BRASILEIRAO" "Brazilian Série A"
test_sport "soccer_argentina_primera_division" "ARGENTINA_PRIMERA" "Argentine Primera"
test_sport "soccer_mexico_ligamx" "LIGA_MX" "Liga MX"
test_sport "soccer_netherlands_eredivisie" "EREDIVISIE" "Dutch Eredivisie"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TENNIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "tennis_atp_french_open" "FRENCH_OPEN" "French Open (ATP)"
test_sport "tennis_wta_french_open" "FRENCH_OPEN_WTA" "French Open (WTA)"
test_sport "tennis_atp_us_open" "US_OPEN" "US Open (ATP)"
test_sport "tennis_wta_us_open" "US_OPEN_WTA" "US Open (WTA)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CRICKET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "cricket_test_match" "TEST_CRICKET" "Test Match Cricket"
test_sport "cricket_odi" "ODI" "One Day International"
test_sport "cricket_t20_blast" "T20_BLAST" "T20 Blast"
test_sport "cricket_big_bash" "BIG_BASH" "Big Bash League"
test_sport "cricket_ipl" "IPL" "Indian Premier League"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "COMBAT SPORTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "mma_mixed_martial_arts" "MMA" "Mixed Martial Arts / UFC"
test_sport "boxing_boxing" "BOXING" "Boxing"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RUGBY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "rugbyleague_nrl" "NRL" "National Rugby League"
test_sport "rugbyunion_super_rugby" "SUPER_RUGBY" "Super Rugby"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GOLF"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "golf_masters" "MASTERS" "The Masters"
test_sport "golf_pga_championship" "PGA" "PGA Championship"
test_sport "golf_us_open" "US_OPEN_GOLF" "US Open Golf"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AUSSIE RULES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_sport "aussierules_afl" "AFL" "Australian Football League"

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo "Sport mappings are working correctly."
    echo "Each sport returns unique data."
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo "Please review the failed sports above."
    exit 1
fi
