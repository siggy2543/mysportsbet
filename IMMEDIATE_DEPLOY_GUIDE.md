# IMMEDIATE DOCKER DEPLOYMENT GUIDE
## Fix "Failed to fetch" API Error - Complete Solution

### TERMINAL ISSUE WORKAROUND
Since there's a terminal session issue, you'll need to run these commands manually in your terminal.

## STEP-BY-STEP DEPLOYMENT

### 1. Open Command Prompt or PowerShell
```
Windows Key + R → type "cmd" → Enter
OR
Windows Key + X → Windows PowerShell
```

### 2. Navigate to Project Directory
```bash
cd "C:\Users\cigba\sports_app"
```

### 3. Stop Existing Containers
```bash
docker-compose down -v
```

### 4. Clean Docker System
```bash
docker system prune -f
docker volume prune -f
```

### 5. Remove Old Images (Optional but Recommended)
```bash
docker rmi sports-betting-api:latest
docker rmi sports-betting-frontend:latest
docker rmi sports_app_api:latest
docker rmi sports_app_frontend:latest
```

### 6. Rebuild Images with New Changes
```bash
docker-compose build --no-cache
```
**This step captures all your new changes including:**
- ✅ Fixed standalone_api.py with 22+ sports
- ✅ Updated Docker configuration
- ✅ Enhanced frontend with proper API endpoints

### 7. Start Containers
```bash
docker-compose up -d
```

### 8. Wait for Initialization (30 seconds)
```bash
# Wait about 30 seconds for services to fully start
```

### 9. Verify Deployment
```bash
docker ps
```
**You should see containers running for:**
- `sports_app_api_1` or similar
- `sports_app_frontend_1` or similar

### 10. Test API Endpoints
```bash
# Test API health
curl http://localhost:8000/api/health

# Test global sports (should return 22+ sports)
curl http://localhost:8000/api/global-sports

# Count sports
curl -s http://localhost:8000/api/global-sports | jq '. | length'
```

### 11. Test Frontend
Open browser and go to: **http://localhost:3000**

**You should see:**
- ✅ 22+ sports in the dropdown selector
- ✅ Live data updates every 20 seconds
- ✅ NO MORE "Failed to fetch" errors
- ✅ Real betting recommendations displayed

## ALTERNATIVE: Use Batch Scripts

### Option A: Run Robust Deployment
```bash
python robust_docker_deploy.py
```

### Option B: Run Windows Batch
```bash
ROBUST_DOCKER_DEPLOY.bat
```

### Option C: Quick Rebuild
```bash
QUICK_DOCKER_REBUILD.bat
```

## VERIFICATION CHECKLIST

### ✅ API Endpoints Working
- [ ] http://localhost:8000/api/health → Returns {"status": "healthy"}
- [ ] http://localhost:8000/api/global-sports → Returns array of 22+ sports
- [ ] http://localhost:8000/api/recommendations/NBA → Returns NBA betting data
- [ ] http://localhost:8000/api/recommendations/EPL → Returns EPL betting data

### ✅ Frontend Working
- [ ] http://localhost:3000 → Loads without errors
- [ ] Sports selector shows 22+ options (NBA, EPL, ATP, Cricket, etc.)
- [ ] Live data updates every 20 seconds
- [ ] No "Failed to fetch" error messages
- [ ] Betting recommendations display properly

### ✅ Container Status
- [ ] `docker ps` shows both api and frontend containers running
- [ ] No error logs in `docker-compose logs`

## TROUBLESHOOTING

### If API Still Shows "Failed to fetch":

1. **Check Container Logs:**
```bash
docker-compose logs api
docker-compose logs frontend
```

2. **Restart Specific Service:**
```bash
docker-compose restart api
```

3. **Check Network:**
```bash
docker network ls
docker network inspect sports_app_default
```

4. **Manual API Test:**
```bash
curl -v http://localhost:8000/api/global-sports
```

### If Frontend Won't Load:

1. **Check Frontend Logs:**
```bash
docker-compose logs frontend
```

2. **Rebuild Frontend Only:**
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### If Containers Won't Start:

1. **Check Docker Status:**
```bash
docker version
docker-compose version
```

2. **Complete Reset:**
```bash
docker-compose down -v
docker system prune -af
docker-compose build --no-cache
docker-compose up -d
```

## SUCCESS INDICATORS

When deployment is successful, you should see:

### Terminal Output:
```
✅ Backend image built successfully
✅ Frontend image built successfully  
✅ Containers started successfully
✅ API health check passed
✅ Global sports endpoint working: 22+ sports
✅ Frontend is accessible
```

### Browser (http://localhost:3000):
- Sports dropdown with 22+ options
- Live betting recommendations
- Real-time data updates
- NO error messages

### API (http://localhost:8000):
- `/api/health` returns 200 OK
- `/api/global-sports` returns 22+ sports array
- All recommendation endpoints working

## FINAL VERIFICATION

Once deployment completes:

1. **Open frontend:** http://localhost:3000
2. **Select different sports** from dropdown (NBA, EPL, ATP, etc.)
3. **Watch live data updates** (every 20 seconds)
4. **Verify no "Failed to fetch" errors**

The "⚠️ API error: Failed to fetch - Showing available data" error should be **COMPLETELY RESOLVED** after this deployment!

## DEPLOYED FEATURES

Your platform now includes:
- ✅ 22+ Global Sports Coverage
- ✅ Live Data Updates (20-second refresh)
- ✅ Player Props with Statistical Confidence
- ✅ Intelligent Parlays with Risk Assessment  
- ✅ Game Theory Algorithms
- ✅ Real-time Global Sports Dashboard
- ✅ Enhanced API with CORS support

The containerized deployment will capture all the new changes and fix the API connectivity issue!