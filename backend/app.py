"""
Modern FastAPI-based sports betting backend
Optimized for performance, scalability, and cloud deployment
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import uvicorn
import os
from celery import Celery

from core.config import settings
from core.database import init_db, get_db
from api.routes import auth, bets, sports_data, predictions, betting_integration
from services.sports_api_service import SportsAPIService
from services.betting_service import BettingService
from services.prediction_service import PredictionService
from services.cache_service import CacheService
from services.live_draftkings_service import live_draftkings_service
from utils.logging_config import setup_logging
from utils.performance_monitor import setup_metrics, performance_monitor

# Setup logging
logger = setup_logging()

# Initialize services with proper dependency injection
cache_service = CacheService()
sports_api_service = SportsAPIService(cache_service)
betting_service = BettingService()
prediction_service = PredictionService(sports_api_service, cache_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting sports betting application...")
    await init_db()
    
    # Start performance monitoring
    await performance_monitor.start_monitoring()
    
    # Start background tasks for data collection
    asyncio.create_task(sports_api_service.start_data_collection())
    
    # Initialize live DraftKings betting service
    await live_draftkings_service.initialize()
    
    # Start automated betting cycle (runs every 30 minutes)
    async def automated_betting_loop():
        while True:
            try:
                await live_draftkings_service.run_automated_betting_cycle()
                await asyncio.sleep(1800)  # 30 minutes
            except Exception as e:
                logger.error(f"Error in automated betting loop: {e}")
                await asyncio.sleep(300)  # 5 minutes on error
    
    asyncio.create_task(automated_betting_loop())
    
    yield
    
    # Shutdown
    logger.info("Shutting down sports betting application...")
    await sports_api_service.stop_data_collection()
    await live_draftkings_service.close()
    await performance_monitor.stop_monitoring()

# Create FastAPI app
app = FastAPI(
    title="Sports Betting API",
    description="Advanced sports betting platform with AI-powered predictions",
    version="2.0.0",
    lifespan=lifespan
)

# Create Celery app for background tasks
celery = Celery(
    "sports_betting",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['tasks.betting_tasks', 'tasks.prediction_tasks']
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup performance monitoring and metrics
setup_metrics(app)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(bets.router, prefix="/api/v1/bets", tags=["betting"])
app.include_router(sports_data.router, prefix="/api/v1/sports", tags=["sports-data"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(betting_integration.router, prefix="/api/v1/betting-automation", tags=["betting-automation"])

# Live DraftKings betting endpoints
@app.get("/api/v1/draftkings/status")
async def get_draftkings_status():
    """Get DraftKings betting service status"""
    return await live_draftkings_service.get_betting_status()

@app.get("/api/v1/draftkings/opportunities")
async def get_betting_opportunities(sport: str = "NBA"):
    """Get current betting opportunities"""
    return await live_draftkings_service.get_betting_opportunities(sport)

@app.get("/api/v1/draftkings/active-bets")
async def get_active_bets():
    """Get active bets"""
    return await live_draftkings_service.get_active_bets()

@app.post("/api/v1/draftkings/run-betting-cycle")
async def run_betting_cycle():
    """Manually trigger a betting cycle"""
    await live_draftkings_service.run_automated_betting_cycle()
    return {"message": "Betting cycle completed"}

@app.get("/api/v1/games/today")
async def get_today_games(sport: str = "NBA"):
    """Get today's games with betting opportunities"""
    opportunities = await live_draftkings_service.get_betting_opportunities(sport)
    return opportunities

@app.get("/")
async def root():
    return {"message": "Sports Betting API v2.0 - Live DraftKings Integration", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "sports_apis": await sports_api_service.health_check(),
            "prediction_engine": prediction_service.is_healthy()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )