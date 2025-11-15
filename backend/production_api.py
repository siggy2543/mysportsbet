"""
Optimized Legal Sports Betting Analysis API
Lightweight production version for AWS deployment
"""
import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from services.legal_betting_service import legal_betting_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting Legal Sports Betting Analysis API...")
    
    # Initialize betting service
    await legal_betting_service.initialize()
    logger.info("✅ Legal betting analysis service ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down...")
    await legal_betting_service.close()
    logger.info("✅ Shutdown complete")

# Create optimized FastAPI app
app = FastAPI(
    title="Legal Sports Betting Analysis",
    description="AI-powered betting recommendations (Manual execution required)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for dashboard
try:
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="dashboard")
except:
    logger.warning("Frontend dashboard not found - API only mode")

@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        bankroll = legal_betting_service.get_bankroll_status()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bankroll": f"${bankroll.current_balance:.2f}",
            "daily_remaining": f"${bankroll.daily_remaining:.2f}",
            "recommendations": legal_betting_service.recommendations_made,
            "compliance": "legal_manual_only"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/status")
async def system_status():
    """Detailed system status"""
    bankroll = legal_betting_service.get_bankroll_status()
    return {
        "system": "operational",
        "analysis_engine": "active",
        "data_sources": ["ESPN", "Mock"],
        "bankroll_balance": bankroll.current_balance,
        "daily_limit": bankroll.daily_limit,
        "daily_remaining": bankroll.daily_remaining,
        "recommendations_made": legal_betting_service.recommendations_made,
        "success_rate": (legal_betting_service.successful_recommendations / max(legal_betting_service.recommendations_made, 1)) * 100,
        "total_pnl": legal_betting_service.total_profit_loss,
        "compliance": "manual_betting_required"
    }

@app.get("/api/recommendations/{sport}")
async def get_recommendations(sport: str = "NBA"):
    """Get betting recommendations"""
    try:
        recommendations = await legal_betting_service.analyze_betting_opportunities(sport)
        
        return [
            {
                "id": rec.game_id,
                "matchup": f"{rec.away_team} @ {rec.home_team}",
                "sport": rec.sport,
                "start_time": rec.start_time.isoformat(),
                "bet": rec.recommended_bet,
                "confidence": round(rec.confidence * 100, 1),
                "expected_value": round(rec.expected_value, 3),
                "bet_size": rec.suggested_bet_size,
                "kelly_pct": round(rec.kelly_criterion * 100, 1),
                "odds": rec.odds,
                "reasoning": rec.reasoning,
                "risk": rec.risk_level,
                "manual_required": True
            }
            for rec in recommendations
        ]
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{sport}")
async def get_games(sport: str = "NBA"):
    """Get live games"""
    try:
        games = await legal_betting_service.get_live_sports_data(sport)
        return [
            {
                "id": game["game_id"],
                "matchup": f"{game['away_team']} @ {game['home_team']}",
                "sport": game["sport"],
                "start_time": game["start_time"],
                "status": game.get("status", "scheduled"),
                "venue": game.get("venue", "TBD"),
                "home_record": game.get("home_record", "0-0"),
                "away_record": game.get("away_record", "0-0")
            }
            for game in games
        ]
    except Exception as e:
        logger.error(f"Error getting games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bankroll")
async def get_bankroll():
    """Get bankroll status"""
    bankroll = legal_betting_service.get_bankroll_status()
    return {
        "balance": bankroll.current_balance,
        "daily_limit": bankroll.daily_limit,
        "daily_used": bankroll.daily_used,
        "daily_remaining": bankroll.daily_remaining,
        "suggested_bet": bankroll.suggested_bet_size,
        "max_bet": bankroll.max_bet_size,
        "kelly_multiplier": bankroll.kelly_multiplier
    }

@app.post("/api/bankroll/update")
async def update_bankroll(balance: float):
    """Update bankroll balance"""
    if balance < 0:
        raise HTTPException(status_code=400, detail="Balance cannot be negative")
    
    legal_betting_service.update_bankroll(balance)
    return {
        "message": f"Bankroll updated to ${balance:.2f}",
        "balance": balance,
        "updated": datetime.now().isoformat()
    }

@app.post("/api/log-bet")
async def log_bet_result(bet_id: str, amount: float, won: bool, payout: float = 0.0):
    """Log bet result"""
    legal_betting_service.log_bet_result(bet_id, amount, won, payout)
    return {
        "message": "Bet result logged",
        "bet_id": bet_id,
        "amount": amount,
        "won": won,
        "payout": payout
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "production_api:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info"
    )