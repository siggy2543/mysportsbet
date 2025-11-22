@echo off
echo.
echo ================================
echo   MANUAL START INSTRUCTIONS
echo ================================
echo.
echo If automated scripts fail, follow these steps:
echo.
echo 1. START BACKEND API:
echo    cd c:\Users\cigba\sports_app\backend
echo    python standalone_api.py
echo.
echo 2. START FRONTEND (new terminal):
echo    cd c:\Users\cigba\sports_app\frontend
echo    set CI=false
echo    npm start
echo.
echo 3. VERIFY WORKING:
echo    Backend: http://localhost:8000/api/global-sports
echo    Frontend: http://localhost:3000
echo.
echo ================================
echo.
pause