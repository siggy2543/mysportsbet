@echo off
echo Starting Enhanced Sports Betting API with Live Data...
cd /d "c:\Users\cigba\sports_app\backend"

REM Kill any existing process on port 8001
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001"') do (
    echo Killing process %%a on port 8001
    taskkill /F /PID %%a >nul 2>&1
)

echo Starting API server on port 8001...
"C:/Users/cigba/sports_app/.venv/Scripts/python.exe" -c "
import sys
sys.path.append('.')
from standalone_api import app
import uvicorn
print('🚀 Enhanced Sports API - Live Data Service')
print('🌍 Global Sports: 12+ sports supported')
print('🎯 Game Theory: ACTIVE')
print('🎰 Parlays: ENABLED')
print('📊 Player Props: FUNCTIONAL')
print('🔗 API URL: http://localhost:8001')
uvicorn.run(app, host='0.0.0.0', port=8001)
"