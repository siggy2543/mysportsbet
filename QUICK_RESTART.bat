@echo off
echo ================================================================================
echo                    QUICK PRODUCTION RESTART
echo ================================================================================

REM Kill existing processes
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

REM Clear ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000\|:3000" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Process cleanup completed
timeout /t 3 /nobreak >nul

REM Start backend
echo Starting backend API...
cd /d "c:\Users\cigba\sports_app\backend"
start /B "API Server" cmd /c "python standalone_api.py"

REM Wait for backend
echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

REM Start frontend
echo Starting frontend...
cd /d "c:\Users\cigba\sports_app\frontend"
start /B "Frontend" cmd /c "set CI=false && npm start"

echo.
echo ================================================================================
echo Services starting...
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait 1-2 minutes for both services to fully initialize
echo ================================================================================
pause