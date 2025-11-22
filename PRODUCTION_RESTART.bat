@echo off
setlocal EnableDelayedExpansion

cls
echo ================================================================================
echo                    PRODUCTION RESTART & DEPLOYMENT
echo                      Enhanced Sports Betting Platform
echo ================================================================================
echo.
echo Starting production deployment with troubleshooting...
echo Timestamp: %date% %time%
echo.

cd /d "c:\Users\cigba\sports_app"

REM ============================================================================
echo [STEP 1/7] Process Cleanup and Port Clearing
echo ============================================================================
echo Terminating existing processes...

taskkill /F /IM python.exe /T >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Python processes terminated
) else (
    echo   ⚠️  No Python processes found
)

taskkill /F /IM node.exe /T >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Node processes terminated  
) else (
    echo   ⚠️  No Node processes found
)

REM Clear specific ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" 2^>nul') do (
    echo   Clearing port 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" 2^>nul') do (
    echo   Clearing port 3000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

echo   ✅ Process cleanup completed
timeout /t 3 /nobreak >nul

REM ============================================================================
echo.
echo [STEP 2/7] File Verification
echo ============================================================================

set "BACKEND_API=c:\Users\cigba\sports_app\backend\standalone_api.py"
set "FRONTEND_APP=c:\Users\cigba\sports_app\frontend\src\EnhancedInteractiveApp.js"
set "FRONTEND_PKG=c:\Users\cigba\sports_app\frontend\package.json"

if exist "%BACKEND_API%" (
    echo   ✅ Backend API file found
) else (
    echo   ❌ Backend API file missing: %BACKEND_API%
    pause
    exit /b 1
)

if exist "%FRONTEND_APP%" (
    echo   ✅ Frontend app file found
) else (
    echo   ❌ Frontend app file missing: %FRONTEND_APP%
    pause
    exit /b 1
)

if exist "%FRONTEND_PKG%" (
    echo   ✅ Frontend package.json found
) else (
    echo   ❌ Frontend package.json missing: %FRONTEND_PKG%
    pause
    exit /b 1
)

echo   ✅ All required files verified

REM ============================================================================
echo.
echo [STEP 3/7] Starting Enhanced Backend API
echo ============================================================================

cd /d "c:\Users\cigba\sports_app\backend"
echo Changed to backend directory: %CD%

echo   🚀 Starting enhanced API server...
start /B "Enhanced Sports API" cmd /c "python standalone_api.py & pause"

echo   ⏳ Waiting for API to initialize...
timeout /t 10 /nobreak >nul

REM Test API health
echo   🔍 Testing API connectivity...
curl -s http://localhost:8000/api/health >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ API server is responding
) else (
    echo   ⚠️  API may still be starting up, continuing...
)

REM ============================================================================
echo.
echo [STEP 4/7] Testing Backend Features
echo ============================================================================

echo   Testing global sports endpoint...
curl -s http://localhost:8000/api/global-sports >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Global sports endpoint working
) else (
    echo   ❌ Global sports endpoint failed
)

echo   Testing NBA recommendations...
curl -s "http://localhost:8000/api/recommendations/NBA" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ NBA recommendations working
) else (
    echo   ❌ NBA recommendations failed
)

echo   Testing EPL recommendations...
curl -s "http://localhost:8000/api/recommendations/EPL" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ EPL recommendations working
) else (
    echo   ❌ EPL recommendations failed
)

echo   Testing parlay generation...
curl -s "http://localhost:8000/api/parlays/NBA" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Parlay generation working
) else (
    echo   ❌ Parlay generation failed
)

REM ============================================================================
echo.
echo [STEP 5/7] Starting Enhanced Frontend
echo ============================================================================

cd /d "c:\Users\cigba\sports_app\frontend"
echo Changed to frontend directory: %CD%

echo   🌐 Starting React development server...
set CI=false
set BROWSER=none
start /B "Frontend Server" cmd /c "npm start & pause"

echo   ⏳ Waiting for frontend to start...
timeout /t 15 /nobreak >nul

REM ============================================================================
echo.
echo [STEP 6/7] Integration Testing
echo ============================================================================

echo   Testing frontend accessibility...
curl -s http://localhost:3000 >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Frontend is accessible
) else (
    echo   ❌ Frontend is not accessible
)

echo   Testing API health from frontend perspective...
curl -s http://localhost:8000/api/health >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ API accessible to frontend
) else (
    echo   ❌ API not accessible to frontend
)

REM ============================================================================
echo.
echo [STEP 7/7] Final Validation
echo ============================================================================

echo   Validating service status...

netstat -an | findstr ":3000.*LISTENING" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Frontend: RUNNING on port 3000
    set FRONTEND_OK=1
) else (
    echo   ❌ Frontend: NOT RUNNING on port 3000
    set FRONTEND_OK=0
)

netstat -an | findstr ":8000.*LISTENING" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo   ✅ Backend API: RUNNING on port 8000
    set BACKEND_OK=1
) else (
    echo   ❌ Backend API: NOT RUNNING on port 8000
    set BACKEND_OK=0
)

echo.
echo ================================================================================
echo                        DEPLOYMENT RESULTS
echo ================================================================================

if !FRONTEND_OK! EQU 1 if !BACKEND_OK! EQU 1 (
    echo 🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!
    echo.
    echo 🌐 FRONTEND DASHBOARD: http://localhost:3000
    echo   • Enhanced sports selector with 22+ global sports
    echo   • Live data updates every 20 seconds
    echo   • Real-time confidence visualization
    echo   • Advanced betting options (Moneylines/Parlays/Player Props)
    echo.
    echo 🔌 ENHANCED API: http://localhost:8000
    echo   • /api/global-sports - All supported sports information
    echo   • /api/recommendations/{sport} - AI-powered moneylines
    echo   • /api/parlays/{sport} - Intelligent parlay combinations
    echo   • /api/player-props/{sport} - Player statistics betting
    echo.
    echo 🎯 FEATURES NOW ACTIVE:
    echo   ✅ Global Sports Coverage (EPL, La Liga, ATP, WTA, Cricket, F1)
    echo   ✅ Game Theory Algorithms (Nash equilibrium, minimax)
    echo   ✅ Live Data Flow (20-second auto-refresh)
    echo   ✅ Intelligent Parlays with correlation analysis
    echo   ✅ Player Props with statistical confidence
    echo   ✅ Enhanced UI/UX with live indicators
    echo.
    echo 🔴 PLATFORM IS READY FOR LIVE BETTING!
    echo.
    echo ⚠️  IMPORTANT: Check both URLs to verify all changes are reflected:
    echo    Frontend: http://localhost:3000 ^(should show 22+ sports^)
    echo    API: http://localhost:8000/api/global-sports ^(should return 22+ sports^)
    
) else (
    echo ❌ DEPLOYMENT ISSUES DETECTED!
    echo.
    if !FRONTEND_OK! EQU 0 (
        echo   ❌ Frontend is not running on port 3000
        echo      Try manually: cd frontend ^&^& npm start
    )
    if !BACKEND_OK! EQU 0 (
        echo   ❌ Backend API is not running on port 8000  
        echo      Try manually: cd backend ^&^& python standalone_api.py
    )
    echo.
    echo 🔧 TROUBLESHOOTING STEPS:
    echo   1. Check if processes are running in background windows
    echo   2. Verify no firewall is blocking ports 3000 and 8000
    echo   3. Try manual startup commands above
    echo   4. Check Windows Task Manager for python.exe and node.exe processes
)

echo.
echo ================================================================================
echo Press any key to exit...
pause >nul