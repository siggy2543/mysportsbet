"""
Simplified Legal Sports Betting Analysis API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
import os
from datetime import datetime
from typing import List, Dict, Any

from services.legal_betting_service import legal_betting_service

# Create FastAPI app
app = FastAPI(
    title="Legal Sports Betting Analysis API",
    description="AI-powered betting analysis platform (Manual betting required)",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting Legal Sports Betting Analysis API...")
    await legal_betting_service.initialize()
    print("✅ Legal betting analysis service ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Legal Sports Betting Analysis API...")
    await legal_betting_service.close()
    print("✅ Shutdown complete")

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
        "legal_notice": "Analysis only - All bets must be placed manually",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
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
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/analytics/status")
async def get_system_status():
    """Get analytics system status"""
    try:
        bankroll = legal_betting_service.get_bankroll_status()
        
        return {
            "system_status": "operational",
            "analysis_engine": "active",
            "data_sources": ["ESPN API", "Sports DB", "Mock Data"],
            "bankroll_balance": bankroll.current_balance,
            "daily_limit": bankroll.daily_limit,
            "daily_remaining": bankroll.daily_remaining,
            "recommendations_made": legal_betting_service.recommendations_made,
            "success_rate": (
                legal_betting_service.successful_recommendations / 
                max(legal_betting_service.recommendations_made, 1)
            ) * 100,
            "total_pnl": legal_betting_service.total_profit_loss,
            "last_updated": datetime.now().isoformat(),
            "compliance_status": "legal_manual_betting_only"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/recommendations/{sport}")
async def get_betting_recommendations(sport: str = "NBA"):
    """Get AI-powered betting recommendations for manual execution"""
    try:
        recommendations = await legal_betting_service.analyze_betting_opportunities(sport)
        
        return [
            {
                "game_id": rec.game_id,
                "matchup": f"{rec.away_team} @ {rec.home_team}",
                "sport": rec.sport,
                "start_time": rec.start_time.isoformat(),
                "recommended_bet": rec.recommended_bet,
                "confidence": f"{rec.confidence:.1%}",
                "expected_value": rec.expected_value,
                "suggested_bet_size": f"${rec.suggested_bet_size:.2f}",
                "kelly_percentage": f"{rec.kelly_criterion:.1%}",
                "odds": rec.odds,
                "reasoning": rec.reasoning,
                "risk_level": rec.risk_level,
                "manual_betting_required": True,
                "instructions": "Place this bet manually through official DraftKings website/app"
            }
            for rec in recommendations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/live-games/{sport}")
async def get_live_games(sport: str = "NBA"):
    """Get live games from legitimate sports APIs"""
    try:
        games = await legal_betting_service.get_live_sports_data(sport)
        
        return [
            {
                "game_id": game["game_id"],
                "sport": game["sport"],
                "matchup": f"{game['away_team']} @ {game['home_team']}",
                "start_time": game["start_time"],
                "status": game.get("status", "scheduled"),
                "venue": game.get("venue", "TBD"),
                "home_record": game.get("home_record", "0-0"),
                "away_record": game.get("away_record", "0-0"),
                "data_source": game.get("source", "unknown")
            }
            for game in games
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/bankroll")
async def get_bankroll_status():
    """Get current bankroll and betting limits"""
    try:
        bankroll = legal_betting_service.get_bankroll_status()
        
        return {
            "current_balance": f"${bankroll.current_balance:.2f}",
            "daily_limit": f"${bankroll.daily_limit:.2f}",
            "daily_used": f"${bankroll.daily_used:.2f}",
            "daily_remaining": f"${bankroll.daily_remaining:.2f}",
            "suggested_bet_size": f"${bankroll.suggested_bet_size:.2f}",
            "max_bet_size": f"${bankroll.max_bet_size:.2f}",
            "kelly_multiplier": bankroll.kelly_multiplier,
            "risk_management": "conservative",
            "manual_updates_required": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/bankroll/update")
async def update_bankroll(new_balance: float):
    """Manually update bankroll balance"""
    try:
        if new_balance < 0:
            raise HTTPException(status_code=400, detail="Balance cannot be negative")
        
        legal_betting_service.update_bankroll(new_balance)
        
        return {
            "message": f"Bankroll updated to ${new_balance:.2f}",
            "new_balance": new_balance,
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "simple_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )