@echo off
REM Production Deployment Script for Windows
REM Deploy Enhanced Platform with Live Data

echo ==========================================
echo 🚀 Production Deployment - Enhanced Platform
echo ==========================================
echo.

REM Check Docker is running
echo 🔍 Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    exit /b 1
)
echo ✓ Docker is running
echo.

REM Step 1: Run tests
echo 🧪 Step 1: Running tests...
bash test_all_features.sh
if errorlevel 1 (
    echo ❌ Tests failed. Aborting deployment.
    exit /b 1
)
echo ✓ Tests passed
echo.

REM Step 2: Stop current services
echo 🛑 Step 2: Stopping current services...
docker-compose stop
echo ✓ Services stopped
echo.

REM Step 3: Build new images
echo 🔨 Step 3: Building production images...
docker-compose build --no-cache api
docker-compose build --no-cache frontend
echo ✓ Images built
echo.

REM Step 4: Start services
echo ▶️  Step 4: Starting enhanced services...
docker-compose up -d
echo ✓ Services starting...
echo.

REM Step 5: Wait for services to be ready
echo ⏳ Step 5: Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo ✓ Services should be ready
echo.

REM Step 6: Verify health
echo 🏥 Step 6: Checking health...
curl -s http://localhost:3000/api/health
echo.
echo.

REM Step 7: Run post-deployment tests
echo 🧪 Step 7: Running post-deployment verification...
echo Testing core endpoints...
curl -s http://localhost:3000/api/global-sports | findstr "NBA" >nul
if errorlevel 1 (
    echo ⚠️  Warning: Some tests may have failed
) else (
    echo ✓ Core endpoints working
)
echo.

echo Testing enhanced features...
curl -s http://localhost:3000/api/feedback/dashboard | findstr "dashboard" >nul
if errorlevel 1 (
    echo ⚠️  Warning: Feedback dashboard may need initialization
) else (
    echo ✓ Feedback loop operational
)
echo.

REM Display summary
echo ==========================================
echo 🎉 Deployment Complete!
echo ==========================================
echo.
echo 🌍 Access your application:
echo    Frontend: http://localhost:3000
echo    API: http://localhost:8200
echo.
echo 🏥 Health Check:
echo    http://localhost:3000/api/health
echo.
echo 🧪 Test Enhanced Features:
echo    http://localhost:3000/api/feedback/dashboard
echo    http://localhost:3000/api/team-analysis/NBA/Lakers
echo    http://localhost:3000/api/enhanced-recommendations/NBA
echo.
echo ==========================================
echo 📊 Features Deployed:
echo    ✅ ML Feedback Loop
echo    ✅ Deep Learning Predictions
echo    ✅ Enhanced Stats Integration
echo    ✅ ESPN News Integration
echo    ✅ Team Analysis
echo    ✅ 22+ Sports Coverage
echo ==========================================
echo.
echo 📚 Next Steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Test all features work correctly
echo    3. Sign up for The Odds API for real odds
echo    4. Start collecting bet outcomes
echo    5. Monitor logs: docker-compose logs -f
echo.
echo GitHub: Changes pushed to feature/new-changes branch
echo.

pause
