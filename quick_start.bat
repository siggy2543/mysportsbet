@echo off
cls
echo ================================================================================
echo                    QUICK START - ENHANCED SPORTS PLATFORM
echo ================================================================================
echo.

cd /d "c:\Users\cigba\sports_app"

REM Kill existing processes
echo [1/4] Cleaning up processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000\|:8000" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo     ✅ Cleanup completed

REM Start backend API
echo.
echo [2/4] Starting Enhanced API Server...
cd /d "c:\Users\cigba\sports_app\backend"
start /B "Sports API" cmd /c "python standalone_api.py"
echo     🚀 API server starting on port 8000...

REM Wait for API to be ready
echo.
echo [3/4] Waiting for API to initialize...
timeout /t 8 /nobreak >nul

REM Start frontend
echo.
echo [4/4] Starting Frontend Dashboard...
cd /d "c:\Users\cigba\sports_app\frontend"
start /B "Frontend" cmd /c "set CI=false && npm start"
echo     🌐 Frontend starting on port 3000...

echo.
echo ================================================================================
echo                        STARTUP COMPLETE!
echo ================================================================================
echo.
echo 🌐 Frontend Dashboard: http://localhost:3000
echo 🔌 API Server: http://localhost:8000
echo.
echo ⏳ Please wait 30-60 seconds for both services to fully initialize...
echo.
echo 🎯 FEATURES AVAILABLE:
echo   ✅ 22+ Global Sports (EPL, La Liga, ATP, WTA, Cricket, F1, etc.)
echo   ✅ Game Theory Algorithms (Nash equilibrium, minimax)
echo   ✅ Intelligent Parlays with correlation analysis
echo   ✅ Player Props with statistical confidence
echo   ✅ Live data updates every 20 seconds
echo.
echo Press any key to open dashboard in browser...
pause >nul
start http://localhost:3000
echo.
echo Dashboard opened! Press any key to exit...
pause >nul