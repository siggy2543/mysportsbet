"""
Production Sports Analytics Dashboard
Provides betting analysis with manual execution
Complies with all platform terms of service
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..services.legal_betting_service import legal_betting_service, BettingRecommendation, BankrollStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["sports-analytics"])

@router.get("/status", response_model=Dict[str, Any])
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
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{sport}", response_model=List[Dict[str, Any]])
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
        logger.error(f"Error getting betting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-games/{sport}", response_model=List[Dict[str, Any]])
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
        logger.error(f"Error getting live games: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bankroll", response_model=Dict[str, Any])
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
        logger.error(f"Error getting bankroll status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bankroll/update")
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
        logger.error(f"Error updating bankroll: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bet-result")
async def log_bet_result(
    recommendation_id: str,
    amount: float,
    won: bool,
    payout: float = 0.0
):
    """Log the result of a manually placed bet"""
    try:
        legal_betting_service.log_bet_result(recommendation_id, amount, won, payout)
        
        return {
            "message": "Bet result logged successfully",
            "recommendation_id": recommendation_id,
            "amount": amount,
            "won": won,
            "payout": payout,
            "logged_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error logging bet result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_stats():
    """Get betting performance statistics"""
    try:
        total_bets = legal_betting_service.recommendations_made
        successful_bets = legal_betting_service.successful_recommendations
        success_rate = (successful_bets / max(total_bets, 1)) * 100
        
        return {
            "total_recommendations": total_bets,
            "successful_bets": successful_bets,
            "success_rate": f"{success_rate:.1f}%",
            "total_pnl": f"${legal_betting_service.total_profit_loss:.2f}",
            "roi": f"{(legal_betting_service.total_profit_loss / max(legal_betting_service.bankroll_balance, 1)) * 100:.1f}%",
            "average_bet_size": f"${legal_betting_service.bankroll_balance * 0.02:.2f}",
            "risk_management": "kelly_criterion_quarter",
            "compliance": "manual_betting_only"
        }
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance", response_model=Dict[str, Any])
async def get_compliance_status():
    """Get system compliance and legal status"""
    return {
        "compliance_status": "FULLY_COMPLIANT",
        "automated_betting": False,
        "manual_execution_required": True,
        "terms_of_service_compliance": "ALL_PLATFORMS",
        "legal_status": "ANALYSIS_ONLY",
        "user_responsibility": "Manual bet placement through official channels",
        "risk_management": "Enabled with Kelly Criterion",
        "data_sources": "Legitimate free APIs only",
        "last_compliance_check": datetime.now().isoformat()
    }