@echo off
REM =============================================================================
REM SPORTS BETTING PLATFORM - PRODUCTION STARTUP SCRIPT
REM Enhanced Daily Betting Intelligence Platform
REM =============================================================================

echo.
echo ====================================================================
echo   🚀 SPORTS BETTING PLATFORM - PRODUCTION STARTUP
echo ====================================================================
echo   📅 Date: %date% %time%
echo   🎯 Enhanced Daily Betting Intelligence Platform
echo   🧠 ChatGPT 5.1 (gpt-4o) + TheSportsDB Premium
echo ====================================================================
echo.

REM Change to application directory
cd /d "C:\Users\cigba\sports_app"

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker is not running or not installed
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ ERROR: docker-compose.yml not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

REM Pull latest images (optional - comment out for faster startup)
echo.
echo 📥 Pulling latest Docker images...
docker-compose pull

REM Stop any existing containers
echo.
echo 🛑 Stopping any existing containers...
docker-compose down --remove-orphans

REM Start all services
echo.
echo 🏗️ Starting all production services...
echo   - PostgreSQL Database
echo   - Redis Cache
echo   - Backend API (Enhanced)
echo   - Frontend Dashboard
echo   - Nginx Proxy
echo   - Celery Worker
echo   - Celery Beat Scheduler
echo.

docker-compose up -d

REM Wait for services to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 15 /nobreak >nul

REM Check container health
echo.
echo 📊 Container Status:
docker-compose ps

REM Test system health
echo.
echo 🔍 Testing system health...
echo.

REM Test API
echo 📡 Testing API connection...
curl -s -o nul -w "API Status: %%{http_code}" http://localhost:8000/api/recommendations/NBA
echo.

REM Test Frontend
echo 🌐 Testing Frontend connection...
curl -s -o nul -w "Frontend Status: %%{http_code}" http://localhost/
echo.

REM Test Nginx Proxy
echo 🔄 Testing Nginx Proxy...
curl -s -o nul -w "Proxy Status: %%{http_code}" http://localhost/api/recommendations/NBA
echo.

echo.
echo ====================================================================
echo   ✅ SPORTS BETTING PLATFORM STARTUP COMPLETE
echo ====================================================================
echo.
echo   🌐 Frontend Dashboard: http://localhost/
echo   🔌 API Endpoints: http://localhost/api/
echo   📊 Direct API Access: http://localhost:8000/
echo   📱 Direct Frontend: http://localhost:3000/
echo.
echo   🧠 ChatGPT 5.1: Active (gpt-4o model)
echo   📡 TheSportsDB: Premium Key 516953
echo   🎲 Daily Betting: Enhanced Analysis
echo   💰 Parlay System: Multi-leg Optimization
echo.
echo   📋 Available Commands:
echo   - docker-compose logs [service]  : View logs
echo   - docker-compose ps              : Check status
echo   - shutdown_prod.bat              : Stop platform
echo.
echo ====================================================================

REM Optional: Open browser to dashboard
set /p open_browser="🌐 Open dashboard in browser? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost/
)

echo.
echo 🎯 Production platform is running!
echo Press any key to return to command prompt...
pause >nul