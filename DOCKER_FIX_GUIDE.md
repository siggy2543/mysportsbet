# Docker Production Deployment & API Fix Guide

## Problem
You're getting "⚠️ API error: Failed to fetch - Showing available data" on the frontend because the containerized deployment is still trying to use the old `app:app` structure instead of the new `standalone_api.py` with 22+ sports support.

## Solution Status ✅
The Docker configuration has been **FIXED**:
- ✅ `docker-compose.yml` updated to use `python standalone_api.py`
- ✅ `backend/Dockerfile.production` updated with correct CMD
- ✅ Comprehensive deployment scripts created

## Quick Deployment Commands

### Option 1: Use the Automated Script
```bash
# Run the comprehensive deployment script
python deploy_enhanced.py

# OR use the Windows batch file
DOCKER_DEPLOY.bat
```

### Option 2: Manual Docker Commands
```bash
# Navigate to project directory
cd "C:\Users\cigba\sports_app"

# Step 1: Stop and clean up
docker-compose down -v
docker system prune -f

# Step 2: Rebuild images with new changes
docker-compose build --no-cache

# Step 3: Start containers
docker-compose up -d

# Step 4: Check status
docker ps
docker-compose logs
```

### Option 3: Quick Rebuild
```bash
# Use the quick rebuild script
QUICK_DOCKER_REBUILD.bat
```

## Verification Steps

### 1. Check Containers Are Running
```bash
docker ps
```
You should see both `sports_app_api` and `sports_app_frontend` containers running.

### 2. Test API Endpoints
```bash
# Test API health
curl http://localhost:8000/api/health

# Test global sports (should return 22+ sports)
curl http://localhost:8000/api/global-sports

# Test NBA recommendations
curl http://localhost:8000/api/recommendations/NBA
```

### 3. Test Frontend
- Open: http://localhost:3000
- You should see 22+ sports in the selector
- Live data should update every 20 seconds
- No more "Failed to fetch" errors

## What Was Fixed

### Docker Configuration Issues ✅
**Before (Broken):**
```yaml
# docker-compose.yml
entrypoint: ["python", "-m", "uvicorn", "app:app"]
```

**After (Fixed):**
```yaml
# docker-compose.yml  
entrypoint: ["python", "standalone_api.py"]
```

**Before (Broken):**
```dockerfile
# Dockerfile.production
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**After (Fixed):**
```dockerfile  
# Dockerfile.production
CMD ["python", "standalone_api.py"]
```

### API Structure ✅
- ✅ Using `standalone_api.py` with 22+ global sports
- ✅ CORS enabled for frontend communication
- ✅ Game theory algorithms integrated
- ✅ Live data generation for all sports

### Frontend Integration ✅
- ✅ Updated API endpoints to port 8000
- ✅ Enhanced sports selector with 22+ options
- ✅ Live data indicators and 20-second refresh
- ✅ Error handling for API connectivity

## Expected Results

After running the deployment:

### Backend (http://localhost:8000)
- ✅ 22+ sports available via `/api/global-sports`
- ✅ Live recommendations for all sports
- ✅ Player props with statistical confidence
- ✅ Intelligent parlays with risk assessment
- ✅ Game theory algorithm integration

### Frontend (http://localhost:3000)  
- ✅ Sports selector with 22+ global sports
- ✅ Live data updates every 20 seconds
- ✅ No more "Failed to fetch" errors
- ✅ Real-time global sports dashboard
- ✅ Interactive betting recommendations

### Available Sports
NBA, NFL, NHL, MLB, EPL, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, ATP Tennis, WTA Tennis, Cricket, Formula 1, MMA, Boxing, Golf, E-Sports, and more.

## Troubleshooting

### If containers won't start:
```bash
docker-compose logs
docker system prune -af
docker-compose build --no-cache
```

### If API still shows errors:
```bash
# Check API logs
docker-compose logs api

# Restart just the API
docker-compose restart api
```

### If frontend can't connect:
```bash
# Check network connectivity
docker network ls
docker network inspect sports_app_default

# Restart frontend
docker-compose restart frontend
```

## Success Indicators

✅ **Docker containers running**: `docker ps` shows both api and frontend
✅ **API responding**: `curl http://localhost:8000/api/health` returns 200
✅ **22+ sports available**: `curl http://localhost:8000/api/global-sports` returns array with 20+ sports
✅ **Frontend accessible**: http://localhost:3000 loads without errors
✅ **No API fetch errors**: Frontend shows live data, not "Failed to fetch"

## Manual Recovery

If automatic deployment fails:
1. Stop everything: `docker-compose down -v`
2. Clean Docker: `docker system prune -af`
3. Rebuild images: `docker-compose build --no-cache`
4. Start services: `docker-compose up -d`
5. Check logs: `docker-compose logs -f`

The "Failed to fetch" error should be completely resolved once the containers are rebuilt with the new `standalone_api.py` configuration!