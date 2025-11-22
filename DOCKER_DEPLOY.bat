@echo off
setlocal EnableDelayedExpansion
cd /d "c:\Users\cigba\sports_app"

echo.
echo ============================================================================
echo                    DOCKER PRODUCTION DEPLOYMENT
echo ============================================================================
echo.
echo 🚀 Rebuilding containerized image and deploying to production...
echo 📊 This will fix the "Failed to fetch" API error
echo.

:: Run the Python deployment script
python deploy_enhanced.py

:: Check if deployment was successful
if !ERRORLEVEL! EQU 0 (
    echo.
    echo ============================================================================
    echo                          DEPLOYMENT SUCCESS!
    echo ============================================================================
    echo.
    echo 🎉 Your enhanced sports platform is now live!
    echo 🌐 Frontend: http://localhost:3000
    echo 🔌 API: http://localhost:8000
    echo.
    echo 🎯 Features Available:
    echo ✅ 22+ Global Sports (EPL, NBA, NFL, ATP, Cricket, etc.)
    echo ✅ Live Data Updates (20-second refresh)
    echo ✅ Player Props with Statistical Confidence
    echo ✅ Intelligent Parlays with Risk Assessment
    echo ✅ Game Theory Algorithms
    echo.
    echo 🔍 Quick Test Commands:
    echo    curl http://localhost:8000/api/global-sports
    echo    curl http://localhost:8000/api/recommendations/NBA
    echo.
    pause
) else (
    echo.
    echo ============================================================================
    echo                          DEPLOYMENT FAILED
    echo ============================================================================
    echo.
    echo ❌ Something went wrong during deployment
    echo 🔧 Check the logs above for specific error details
    echo.
    echo 🛠️ Manual Recovery Options:
    echo    1. docker-compose down
    echo    2. docker-compose up -d --build
    echo    3. docker-compose logs -f
    echo.
    pause
)