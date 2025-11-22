@echo off
cd /d "C:\Users\cigba\sports_app"

echo.
echo ===== QUICK DOCKER REBUILD =====
echo.

echo Step 1: Stop existing containers...
docker-compose down -v

echo Step 2: Remove old images...
docker system prune -f

echo Step 3: Rebuild with new changes...
docker-compose build --no-cache

echo Step 4: Start containers...
docker-compose up -d

echo Step 5: Wait for startup...
timeout /t 15

echo Step 6: Check status...
docker ps

echo.
echo ===== DEPLOYMENT COMPLETE =====
echo Frontend: http://localhost:3000
echo API: http://localhost:8000
echo.

pause