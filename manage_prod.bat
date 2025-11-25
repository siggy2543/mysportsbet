@echo off
REM ============================================================
REM Sports Betting Platform - Production Control Script
REM Consolidated script for all deployment operations
REM ============================================================

setlocal enabledelayedexpansion

:MENU
cls
echo ============================================================
echo    SPORTS BETTING PLATFORM - PRODUCTION CONTROL
echo ============================================================
echo.
echo    1. START    - Start all services
echo    2. STOP     - Stop all services  
echo    3. RESTART  - Restart all services
echo    4. STATUS   - Check container status
echo    5. LOGS     - View container logs
echo    6. REBUILD  - Rebuild and restart containers
echo    7. CLEAN    - Clean and rebuild from scratch
echo    8. TEST     - Run test suite
echo    9. EXIT     - Exit script
echo.
echo ============================================================
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto RESTART
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto LOGS
if "%choice%"=="6" goto REBUILD
if "%choice%"=="7" goto CLEAN
if "%choice%"=="8" goto TEST
if "%choice%"=="9" goto EXIT
goto MENU

:START
echo.
echo [START] Starting all services...
docker-compose up -d
echo.
echo ✅ Services started!
pause
goto MENU

:STOP
echo.
echo [STOP] Stopping all services...
docker-compose down
echo.
echo ✅ Services stopped!
pause
goto MENU

:RESTART
echo.
echo [RESTART] Restarting all services...
docker-compose restart
echo.
echo ✅ Services restarted!
pause
goto MENU

:STATUS
echo.
echo [STATUS] Container status:
echo ============================================================
docker-compose ps
echo.
echo [HEALTH] Checking API health...
curl -s http://localhost:8000/api/platform-stats
echo.
pause
goto MENU

:LOGS
echo.
echo [LOGS] Select container:
echo    1. API (Backend)
echo    2. Frontend
echo    3. Database
echo    4. Redis
echo    5. All containers
echo.
set /p log_choice="Enter choice (1-5): "

if "%log_choice%"=="1" docker logs sports_app-api-1 --tail 100
if "%log_choice%"=="2" docker logs sports_app-frontend-1 --tail 100
if "%log_choice%"=="3" docker logs sports_app-postgres-1 --tail 100
if "%log_choice%"=="4" docker logs sports_app-redis-1 --tail 100
if "%log_choice%"=="5" docker-compose logs --tail 50

pause
goto MENU

:REBUILD
echo.
echo [REBUILD] Rebuilding containers...
echo.
echo Building backend...
docker-compose up -d --build --no-deps api
echo.
echo Building frontend...
docker-compose up -d --build --no-deps frontend
echo.
echo ✅ Rebuild complete!
pause
goto MENU

:CLEAN
echo.
echo [CLEAN] WARNING: This will remove all containers and rebuild from scratch!
set /p confirm="Are you sure? (y/n): "
if /i not "%confirm%"=="y" goto MENU

echo.
echo Stopping containers...
docker-compose down

echo.
echo Removing images...
docker rmi sports_app-api sports_app-frontend 2>nul

echo.
echo Rebuilding all containers...
docker-compose build --no-cache

echo.
echo Starting services...
docker-compose up -d

echo.
echo ✅ Clean rebuild complete!
pause
goto MENU

:TEST
echo.
echo [TEST] Running test suite...
python test_enhancements.py
echo.
pause
goto MENU

:EXIT
echo.
echo Exiting...
exit /b 0
