"""
Legal Sports Betting Analysis API
Provides AI-powered betting recommendations for manual execution
Fully compliant with all platform terms of service
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import os
from datetime import datetime

from core.simple_config import settings
from core.database import init_db
from api.routes.analytics import router as analytics_router
from services.legal_betting_service import legal_betting_service
from utils.simple_logging import setup_logging

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Legal Sports Betting Analysis Platform...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize legal betting analysis service
    analysis_initialized = await legal_betting_service.initialize()
    if analysis_initialized:
        logger.info("✅ Legal betting analysis service initialized")
    else:
        logger.error("❌ Failed to initialize legal betting analysis service")
    
    logger.info("🎯 System ready - Analysis mode only, manual betting required")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Legal Sports Betting Analysis Platform...")
    await legal_betting_service.close()
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Legal Sports Betting Analysis API",
    description="AI-powered betting analysis platform with manual execution (Compliant with all ToS)",
    version="3.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(analytics_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Sports Betting Analysis API v3.0",
        "status": "operational",
        "compliance": "manual_betting_only",
        "features": [
            "AI-powered betting analysis",
            "Live sports data integration",
            "Kelly Criterion bet sizing",
            "Risk management tools",
            "Performance tracking"
        ],
        "legal_notice": "Analysis only - All bets must be placed manually through official channels",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check system components
        bankroll = legal_betting_service.get_bankroll_status()
        
        return {
            "status": "healthy",
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "analysis_engine": "operational",
                "data_sources": "connected",
                "risk_management": "active",
                "compliance": "fully_compliant"
            },
            "bankroll_status": {
                "balance": f"${bankroll.current_balance:.2f}",
                "daily_remaining": f"${bankroll.daily_remaining:.2f}"
            },
            "performance": {
                "recommendations_made": legal_betting_service.recommendations_made,
                "success_rate": f"{(legal_betting_service.successful_recommendations / max(legal_betting_service.recommendations_made, 1)) * 100:.1f}%",
                "total_pnl": f"${legal_betting_service.total_profit_loss:.2f}"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/live-demo")
async def live_demo():
    """Live demo of betting analysis"""
    try:
        # Get live recommendations
        recommendations = await legal_betting_service.analyze_betting_opportunities("NBA")
        
        return {
            "demo_mode": True,
            "current_opportunities": len(recommendations),
            "sample_recommendation": recommendations[0].__dict__ if recommendations else None,
            "instructions": [
                "1. Review AI-powered betting recommendations",
                "2. Analyze confidence levels and expected value",
                "3. Use Kelly Criterion for bet sizing",
                "4. Manually place bets through official DraftKings website/app",
                "5. Log results for performance tracking"
            ],
            "compliance_notice": "This system provides analysis only - manual betting execution required"
        }
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "legal_app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )