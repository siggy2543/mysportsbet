@echo off
REM ============================================================================
REM SPORTS APP - COMPLETE REBUILD AND PRODUCTION DEPLOYMENT
REM ============================================================================

echo ============================================
echo SPORTS BETTING APP - PRODUCTION DEPLOYMENT
echo ============================================
echo.

REM Stop all running containers
echo [1/6] Stopping all containers...
docker-compose down
if errorlevel 1 (
    echo ERROR: Failed to stop containers
    pause
    exit /b 1
)
echo ✓ Containers stopped
echo.

REM Clean up old images and build cache
echo [2/6] Cleaning up old images and cache...
docker system prune -f
echo ✓ Cleanup complete
echo.

REM Rebuild all images with no cache
echo [3/6] Rebuilding all Docker images (this may take a few minutes)...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Failed to build images
    pause
    exit /b 1
)
echo ✓ Images rebuilt successfully
echo.

REM Start all services
echo [4/6] Starting all services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start services
    pause
    exit /b 1
)
echo ✓ Services started
echo.

REM Wait for services to be healthy
echo [5/6] Waiting for services to be healthy (30 seconds)...
timeout /t 30 /nobreak > nul
echo.

REM Check service health
echo [6/6] Checking service health...
docker-compose ps
echo.

REM Test API endpoint
echo Testing API health endpoint...
curl -s http://localhost:8000/health
echo.
echo.

REM Test Frontend
echo Testing frontend health endpoint...
curl -s http://localhost:3000/health
echo.
echo.

echo ============================================
echo DEPLOYMENT COMPLETE!
echo ============================================
echo.
echo Services Status:
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo.
echo Access Points:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Check logs with:
echo   docker-compose logs -f [service-name]
echo.

pause
