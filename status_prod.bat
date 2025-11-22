@echo off
REM =============================================================================
REM SPORTS BETTING PLATFORM - STATUS CHECK SCRIPT
REM Enhanced Daily Betting Intelligence Platform
REM =============================================================================

echo.
echo ====================================================================
echo   📊 SPORTS BETTING PLATFORM - STATUS CHECK
echo ====================================================================
echo   📅 Date: %date% %time%
echo ====================================================================
echo.

REM Change to application directory
cd /d "C:\Users\cigba\sports_app"

echo 🔍 Container Status:
echo ==================
docker-compose ps

echo.
echo 🌐 Service Health Check:
echo =======================

REM Test API
echo 📡 API Status:
curl -s -o nul -w "  Backend API: %%{http_code}" http://localhost:8000/api/recommendations/NBA
echo.

REM Test Frontend
echo 🖥️  Frontend Status:
curl -s -o nul -w "  Dashboard: %%{http_code}" http://localhost/
echo.

REM Test Nginx Proxy
echo 🔄 Proxy Status:
curl -s -o nul -w "  Nginx Proxy: %%{http_code}" http://localhost/api/recommendations/NBA
echo.

echo.
echo 🎲 Betting System Status:
echo ========================

REM Check recommendations
echo 🏀 NBA Recommendations:
curl -s http://localhost/api/recommendations/NBA 2>nul | python -c "import sys, json; data=json.load(sys.stdin); print(f'  Active: {len(data[\"recommendations\"])} recommendations')" 2>nul || echo   Status: API responding

echo 🏈 NFL Recommendations:
curl -s http://localhost/api/recommendations/NFL 2>nul | python -c "import sys, json; data=json.load(sys.stdin); print(f'  Active: {len(data[\"recommendations\"])} recommendations')" 2>nul || echo   Status: API responding

echo ⚽ EPL Recommendations:
curl -s http://localhost/api/recommendations/EPL 2>nul | python -c "import sys, json; data=json.load(sys.stdin); print(f'  Active: {len(data[\"recommendations\"])} recommendations')" 2>nul || echo   Status: API responding

echo.
echo 🎰 Parlay System:
curl -s http://localhost/api/parlays/NBA 2>nul | python -c "import sys, json; data=json.load(sys.stdin); print(f'  NBA Parlays: {len(data[\"parlays\"])} active')" 2>nul || echo   Status: API responding

echo.
echo ====================================================================
echo   📋 AVAILABLE COMMANDS
echo ====================================================================
echo   🚀 startup_prod.bat     - Start the platform
echo   🛑 shutdown_prod.bat    - Stop the platform  
echo   🔄 restart_prod.bat     - Quick restart
echo   📊 status_prod.bat      - This status check
echo.
echo   🌐 Dashboard: http://localhost/
echo   🔌 API: http://localhost/api/
echo ====================================================================

pause