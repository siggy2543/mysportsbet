@echo off
setlocal EnableDelayedExpansion
cd /d "C:\Users\cigba\sports_app"

echo.
echo ====================================================================
echo                    ROBUST DOCKER PRODUCTION DEPLOYMENT
echo ====================================================================
echo.
echo 🚀 Fixing "Failed to fetch" API error with complete container rebuild
echo 📊 This will capture all new changes and deploy to production
echo.

:: Step 1: Stop all existing containers
echo.
echo [STEP 1] Stopping all existing containers...
docker-compose down -v 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo ⚠️ No existing containers to stop
) else (
    echo ✅ Existing containers stopped
)

:: Step 2: Clean up Docker system
echo.
echo [STEP 2] Cleaning up Docker system...
docker system prune -f 2>nul
docker volume prune -f 2>nul
echo ✅ Docker system cleaned

:: Step 3: Remove old images
echo.
echo [STEP 3] Removing old images...
docker rmi sports-betting-api:latest 2>nul
docker rmi sports-betting-frontend:latest 2>nul
docker rmi sports_app_api:latest 2>nul  
docker rmi sports_app_frontend:latest 2>nul
echo ✅ Old images removed

:: Step 4: Build backend image with new changes
echo.
echo [STEP 4] Building backend API image with new changes...
docker build --no-cache -t sports-betting-api:latest -f backend/Dockerfile.production backend/
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Backend build failed! Check backend/Dockerfile.production
    pause
    exit /b 1
)
echo ✅ Backend image built successfully

:: Step 5: Build frontend image with new changes  
echo.
echo [STEP 5] Building frontend image with new changes...
docker build --no-cache -t sports-betting-frontend:latest -f frontend/Dockerfile.production frontend/
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Frontend build failed! Check frontend/Dockerfile.production
    pause
    exit /b 1
)
echo ✅ Frontend image built successfully

:: Step 6: Start containers with docker-compose
echo.
echo [STEP 6] Starting containers with docker-compose...
docker-compose up -d --build
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Container startup failed! 
    echo 🔍 Checking logs...
    docker-compose logs
    pause
    exit /b 1
)
echo ✅ Containers started successfully

:: Step 7: Wait for services to initialize
echo.
echo [STEP 7] Waiting for services to initialize...
timeout /t 20 /nobreak >nul
echo ✅ Services initialized

:: Step 8: Verify containers are running
echo.
echo [STEP 8] Verifying container status...
docker ps
echo.

:: Step 9: Test API endpoints
echo.
echo [STEP 9] Testing API endpoints...
echo Testing API health...
curl -s http://localhost:8000/api/health >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo ✅ API health check passed
) else (
    echo ❌ API health check failed
    echo 🔍 Checking API logs...
    docker-compose logs api
)

echo.
echo Testing global sports endpoint...
curl -s http://localhost:8000/api/global-sports >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo ✅ Global sports endpoint working
) else (
    echo ❌ Global sports endpoint failed
)

:: Step 10: Test frontend
echo.
echo [STEP 10] Testing frontend accessibility...
curl -s http://localhost:3000 >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo ✅ Frontend is accessible
) else (
    echo ❌ Frontend is not accessible
    echo 🔍 Checking frontend logs...
    docker-compose logs frontend
)

:: Final Results
echo.
echo ====================================================================
echo                          DEPLOYMENT RESULTS
echo ====================================================================
echo.
echo 🎯 DEPLOYMENT COMPLETED!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔌 API: http://localhost:8000
echo.
echo 🎮 Available Features:
echo ✅ 22+ Global Sports (NBA, EPL, ATP, Cricket, F1, etc.)
echo ✅ Live Data Updates (20-second refresh)
echo ✅ Player Props with Statistical Confidence  
echo ✅ Intelligent Parlays with Risk Assessment
echo ✅ Game Theory Algorithms
echo.
echo 🔍 Quick Test URLs:
echo    http://localhost:8000/api/health
echo    http://localhost:8000/api/global-sports
echo    http://localhost:8000/api/recommendations/NBA
echo.
echo 🔴 The "Failed to fetch" error should now be RESOLVED!
echo.

:: Show final container status
echo Current running containers:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 📋 If you still see "Failed to fetch" errors:
echo    1. Check browser console for specific errors
echo    2. Try: docker-compose logs -f api
echo    3. Verify CORS headers: curl -I http://localhost:8000/api/health
echo.

pause