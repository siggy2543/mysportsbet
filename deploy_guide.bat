@echo off
REM =============================================================================
REM SPORTS BETTING PLATFORM - DEPLOYMENT GUIDE
REM Complete setup and deployment instructions
REM =============================================================================

echo.
echo ====================================================================
echo   🎯 SPORTS BETTING PLATFORM - DEPLOYMENT GUIDE
echo ====================================================================
echo   📅 Enhanced Daily Betting Intelligence Platform
echo   🧠 ChatGPT 5.1 + TheSportsDB Premium Integration
echo ====================================================================
echo.

echo 📋 DEPLOYMENT CHECKLIST:
echo ========================
echo.
echo ✅ 1. Docker Desktop is installed and running
echo ✅ 2. All source code is in C:\Users\cigba\sports_app
echo ✅ 3. Environment variables configured (.env file)
echo ✅ 4. API keys are valid (OpenAI + TheSportsDB)
echo ✅ 5. Production scripts are available
echo.

echo 🚀 AVAILABLE DEPLOYMENT SCRIPTS:
echo =================================
echo.
echo   📁 startup_prod.bat     - 🚀 Start the production platform
echo   📁 shutdown_prod.bat    - 🛑 Stop the production platform
echo   📁 restart_prod.bat     - 🔄 Quick restart all services
echo   📁 status_prod.bat      - 📊 Check system status
echo   📁 deploy_guide.bat     - 📋 This deployment guide
echo.

echo 🎯 QUICK START INSTRUCTIONS:
echo =============================
echo.
echo   1️⃣  Double-click: startup_prod.bat
echo   2️⃣  Wait for "✅ STARTUP COMPLETE" message
echo   3️⃣  Open browser to: http://localhost/
echo   4️⃣  Verify API at: http://localhost/api/
echo.

echo 🔧 SYSTEM REQUIREMENTS:
echo =======================
echo   - Windows 10/11
echo   - Docker Desktop 4.0+
echo   - 8GB RAM minimum
echo   - 10GB free disk space
echo   - Internet connection for API calls
echo.

echo 🌐 ACCESS POINTS AFTER DEPLOYMENT:
echo ==================================
echo   📱 Main Dashboard:    http://localhost/
echo   🔌 API Endpoints:     http://localhost/api/
echo   📊 Direct API:        http://localhost:8000/
echo   🖥️  Direct Frontend:   http://localhost:3000/
echo.

echo 🎲 BETTING FEATURES:
echo ===================
echo   🏀 NBA Recommendations    - 8 daily picks
echo   🏈 NFL Recommendations    - 8 daily picks  
echo   ⚽ EPL Recommendations    - 8 daily picks
echo   🥊 MMA Recommendations    - 8 daily picks
echo   🎰 Parlay Combinations   - 3-5 leg optimization
echo   🧠 AI Analysis           - ChatGPT 5.1 powered
echo   📡 Live Data             - TheSportsDB Premium
echo.

echo 🚨 TROUBLESHOOTING:
echo ==================
echo   Problem: Docker not found
echo   Solution: Install Docker Desktop, restart system
echo.
echo   Problem: Port conflicts
echo   Solution: Stop other services on ports 80, 3000, 8000
echo.
echo   Problem: API not responding  
echo   Solution: Check .env file, verify API keys
echo.
echo   Problem: Container health issues
echo   Solution: Run restart_prod.bat
echo.

echo 📞 SUPPORT COMMANDS:
echo ===================
echo   docker-compose logs api      - View API logs
echo   docker-compose ps            - Check container status
echo   docker system prune          - Clean up Docker
echo   status_prod.bat              - Full system check
echo.

set /p deploy="🚀 Ready to deploy? Start the platform now? (y/n): "
if /i "%deploy%"=="y" (
    echo.
    echo 🚀 Starting production deployment...
    call startup_prod.bat
) else (
    echo.
    echo 📋 Deployment guide complete.
    echo Run startup_prod.bat when ready to deploy.
)

echo.
echo ====================================================================
echo   🎯 DEPLOYMENT GUIDE COMPLETE
echo ====================================================================
pause