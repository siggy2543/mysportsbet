# 🚀 Sports Betting Platform - Production Management Scripts

## Overview
These scripts provide easy management of your Enhanced Daily Betting Intelligence Platform in production.

## 📋 Available Scripts

### 🚀 `startup_prod.bat` - Start Production Platform
**Primary startup script** - Use this to start your production platform
- Checks Docker status
- Pulls latest images (optional)
- Stops any existing containers
- Starts all services in correct order
- Performs health checks
- Shows access URLs

**Usage:**
```cmd
startup_prod.bat
```

### 🛑 `shutdown_prod.bat` - Stop Production Platform  
**Safe shutdown script** - Gracefully stops all services
- Shows current status
- Confirms shutdown action
- Stops services in proper order
- Cleans up containers and networks
- Preserves data volumes
- Optional Docker cleanup

**Usage:**
```cmd
shutdown_prod.bat
```

### 🔄 `restart_prod.bat` - Quick Restart
**Fast restart** - For quick service restarts
- Stops all containers
- Immediately restarts services
- Performs basic health check

**Usage:**
```cmd
restart_prod.bat
```

### 📊 `status_prod.bat` - System Status Check
**Health monitoring** - Check platform status without changes
- Container status
- Service health checks
- API endpoint testing
- Betting system status
- Available commands reference

**Usage:**
```cmd
status_prod.bat
```

## 🎯 Production Services

When you run the startup script, these services will be launched:

| Service | Description | Port | Health Check |
|---------|-------------|------|--------------|
| **Frontend** | React Dashboard | 3000 | ✅ Nginx serving |
| **API** | FastAPI Backend | 8000 | ✅ Recommendations active |
| **Nginx** | Reverse Proxy | 80, 443 | ✅ Proxy routing |
| **PostgreSQL** | Database | 5432 | ✅ Data persistence |
| **Redis** | Cache | 6379 | ✅ Caching layer |
| **Celery Worker** | Background Tasks | - | ✅ Processing jobs |
| **Celery Beat** | Scheduler | - | ✅ Scheduled tasks |

## 🌐 Access Points

After startup, access your platform at:

- **📱 Main Dashboard:** http://localhost/
- **🔌 API Endpoints:** http://localhost/api/
- **📊 Direct API:** http://localhost:8000/
- **🖥️ Direct Frontend:** http://localhost:3000/

## 🔧 Production Features

### 🧠 AI Integration
- **ChatGPT 5.1** (gpt-4o model) - Enhanced betting intelligence
- **TheSportsDB Premium** (Key: 516953) - Real-time sports data

### 🎲 Betting Intelligence  
- **Daily Analysis** - Automated recommendations for current date
- **Multi-Sport Coverage** - NBA, NFL, EPL, MMA
- **Parlay Optimization** - 3, 4, and 5-leg combinations
- **Confidence Scoring** - Percentage-based success ratings

### 🏗️ Infrastructure
- **Docker Containerization** - Production-grade deployment
- **Health Monitoring** - Automated service checks
- **Data Persistence** - PostgreSQL with volumes
- **Performance Optimization** - Redis caching and Nginx compression

## 🚨 Troubleshooting

### If startup fails:
1. Ensure Docker Desktop is running
2. Check available disk space
3. Run `docker system prune` to clean up
4. Try `restart_prod.bat` for a fresh start

### If services are unhealthy:
1. Run `status_prod.bat` to diagnose
2. Check logs: `docker-compose logs [service]`
3. Restart specific service: `docker-compose restart [service]`

### If API is not responding:
1. Check backend logs: `docker-compose logs api`
2. Verify environment variables in `.env`
3. Ensure API keys are valid

## 📊 Monitoring Commands

```cmd
# Check all container status
docker-compose ps

# View logs for specific service
docker-compose logs api
docker-compose logs frontend
docker-compose logs nginx

# Follow live logs
docker-compose logs -f api

# Check resource usage
docker stats

# Clean up unused resources
docker system prune
```

## 🎯 Quick Commands Reference

```cmd
# Start platform
startup_prod.bat

# Check status
status_prod.bat

# Quick restart
restart_prod.bat

# Stop platform
shutdown_prod.bat

# Manual Docker commands
docker-compose up -d        # Start all services
docker-compose down         # Stop and remove containers
docker-compose restart api  # Restart specific service
```

## 🔐 Environment Configuration

Ensure your `.env` file contains:
```env
OPENAI_MODEL=gpt-4o
THESPORTSDB_API_KEY=516953
OPENAI_API_KEY=your_openai_key
```

## 🎉 Success Indicators

When startup is complete, you should see:
- ✅ All containers running
- ✅ Frontend returns HTTP 200
- ✅ API returns recommendations  
- ✅ Betting analysis active
- ✅ Parlay system generating combinations

---

**🚀 Your Enhanced Daily Betting Intelligence Platform is production-ready!**