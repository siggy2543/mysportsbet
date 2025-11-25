@echo off
REM ============================================================================
REM TROUBLESHOOTING SCRIPT - DIAGNOSE ISSUES
REM ============================================================================

echo ============================================
echo TROUBLESHOOTING - CHECKING SYSTEM STATUS
echo ============================================
echo.

echo [1] Docker Container Status
echo ----------------------------------------
docker-compose ps
echo.

echo [2] Backend API Health
echo ----------------------------------------
curl -s http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo ✗ Backend API is not responding
) else (
    echo ✓ Backend API is healthy
)
echo.

echo [3] Frontend Health
echo ----------------------------------------
curl -s http://localhost:3000/health 2>nul
if errorlevel 1 (
    echo ✗ Frontend is not responding
) else (
    echo ✓ Frontend is healthy
)
echo.

echo [4] Recent Backend Logs (Last 20 lines)
echo ----------------------------------------
docker logs --tail 20 sports_app-api-1 2>&1
echo.

echo [5] Recent Frontend Logs (Last 20 lines)
echo ----------------------------------------
docker logs --tail 20 sports_app-frontend-1 2>&1
echo.

echo [6] Database Connection
echo ----------------------------------------
docker exec sports_app-postgres-1 pg_isready -U sports_user -d sports_betting 2>nul
if errorlevel 1 (
    echo ✗ Database connection failed
) else (
    echo ✓ Database is ready
)
echo.

echo [7] Redis Connection
echo ----------------------------------------
docker exec sports_app-redis-1 redis-cli ping 2>nul
if errorlevel 1 (
    echo ✗ Redis connection failed
) else (
    echo ✓ Redis is ready
)
echo.

echo [8] Test API Endpoint (Today's NBA Games)
echo ----------------------------------------
curl -s "http://localhost:8000/api/recommendations/NBA?date=today" 2>nul | python -c "import sys, json; d=json.load(sys.stdin); print(f'Date: {d.get(\"target_date\", \"N/A\")}\nGames: {d.get(\"count\", 0)}')" 2>nul
if errorlevel 1 (
    echo ✗ API endpoint test failed
)
echo.

echo ============================================
echo TROUBLESHOOTING COMPLETE
echo ============================================
echo.
echo Common fixes:
echo   1. Restart all containers:    docker-compose restart
echo   2. Rebuild everything:        rebuild_deploy.bat
echo   3. Check logs:                docker-compose logs -f api
echo   4. Clear browser cache:       Ctrl+Shift+R (in browser)
echo.

pause
