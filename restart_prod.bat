@echo off
REM =============================================================================
REM SPORTS BETTING PLATFORM - QUICK RESTART SCRIPT
REM Enhanced Daily Betting Intelligence Platform
REM =============================================================================

echo.
echo ====================================================================
echo   🔄 SPORTS BETTING PLATFORM - QUICK RESTART
echo ====================================================================
echo   📅 Date: %date% %time%
echo   🎯 Restarting Enhanced Daily Betting Platform
echo ====================================================================
echo.

REM Change to application directory
cd /d "C:\Users\cigba\sports_app"

echo 🛑 Stopping current services...
docker-compose down --remove-orphans

echo ⏳ Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for initialization...
timeout /t 15 /nobreak >nul

echo.
echo 📊 Container Status:
docker-compose ps

echo.
echo 🔍 Quick Health Check:
curl -s -o nul -w "API: %%{http_code} " http://localhost:8000/api/recommendations/NBA
curl -s -o nul -w "Frontend: %%{http_code}" http://localhost/
echo.

echo.
echo ✅ Quick restart complete!
echo 🌐 Dashboard: http://localhost/
pause