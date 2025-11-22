@echo off
REM =============================================================================
REM SPORTS BETTING PLATFORM - PRODUCTION SHUTDOWN SCRIPT
REM Enhanced Daily Betting Intelligence Platform
REM =============================================================================

echo.
echo ====================================================================
echo   🛑 SPORTS BETTING PLATFORM - PRODUCTION SHUTDOWN
echo ====================================================================
echo   📅 Date: %date% %time%
echo   🎯 Enhanced Daily Betting Intelligence Platform
echo ====================================================================
echo.

REM Change to application directory
cd /d "C:\Users\cigba\sports_app"

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker is not running
    echo Platform may already be stopped
    pause
    exit /b 0
)
echo ✅ Docker is running

REM Show current container status
echo.
echo 📊 Current Container Status:
docker-compose ps

REM Prompt for confirmation
echo.
set /p confirm="⚠️  Are you sure you want to stop the production platform? (y/n): "
if /i not "%confirm%"=="y" (
    echo ℹ️  Shutdown cancelled
    pause
    exit /b 0
)

echo.
echo 🛑 Stopping Sports Betting Platform services...
echo.

REM Stop services gracefully
echo 📊 Stopping Frontend Dashboard...
docker-compose stop frontend

echo 🔄 Stopping Nginx Proxy...
docker-compose stop nginx

echo 🔌 Stopping Backend API...
docker-compose stop api

echo ⚙️  Stopping Celery Worker...
docker-compose stop celery-worker

echo ⏰ Stopping Celery Beat Scheduler...
docker-compose stop celery-beat

echo 💾 Stopping Redis Cache...
docker-compose stop redis

echo 🗄️  Stopping PostgreSQL Database...
docker-compose stop postgres

REM Wait for graceful shutdown
echo.
echo ⏳ Waiting for graceful shutdown...
timeout /t 5 /nobreak >nul

REM Force stop and remove containers
echo.
echo 🧹 Cleaning up containers and networks...
docker-compose down --remove-orphans

REM Optional: Remove volumes (uncomment if you want to clear all data)
REM echo 🗑️  Removing volumes (this will DELETE all data)...
REM docker-compose down -v

REM Show final status
echo.
echo 📊 Final Container Status:
docker-compose ps

REM Optional: Prune unused Docker resources
set /p cleanup="🧹 Clean up unused Docker resources? (y/n): "
if /i "%cleanup%"=="y" (
    echo 🧹 Cleaning up unused Docker resources...
    docker system prune -f
    echo ✅ Cleanup complete
)

echo.
echo ====================================================================
echo   ✅ SPORTS BETTING PLATFORM SHUTDOWN COMPLETE
echo ====================================================================
echo.
echo   🛑 All services stopped
echo   🧹 Containers removed
echo   💾 Data volumes preserved
echo.
echo   📋 To restart the platform:
echo   - Run: startup_prod.bat
echo   - Or: docker-compose up -d
echo.
echo   🔧 Maintenance Commands:
echo   - docker-compose logs     : View logs
echo   - docker-compose build    : Rebuild images
echo   - docker system prune     : Clean unused resources
echo.
echo ====================================================================

echo.
echo 🎯 Production platform shutdown complete!
echo Press any key to return to command prompt...
pause >nul