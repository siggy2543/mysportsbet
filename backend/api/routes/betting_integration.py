"""
API routes for the integrated ESPN + OpenAI + DraftKings betting system
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from services.betting_orchestrator import betting_orchestrator
from services.espn_api_service import espn_service
from services.openai_prediction_service import openai_prediction_service
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/betting", tags=["Automated Betting"])

@router.post("/initialize-draftkings")
async def initialize_draftkings_integration(
    username: str,
    password: str,
    state: str = "NY"
):
    """
    Initialize DraftKings integration with user credentials
    """
    try:
        success = await betting_orchestrator.initialize_draftkings(username, password, state)
        
        if success:
            return {
                "status": "success",
                "message": "DraftKings integration initialized successfully",
                "authenticated": True
            }
        else:
            raise HTTPException(status_code=401, detail="Failed to authenticate with DraftKings")
            
    except Exception as e:
        logger.error(f"Error initializing DraftKings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-betting-session")
async def start_betting_session(bankroll: float = 1000.0):
    """
    Start a new automated betting session
    """
    try:
        session = await betting_orchestrator.start_daily_betting_session(bankroll)
        
        return {
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "bankroll": bankroll,
                "status": session.status
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting betting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-full-workflow")
async def execute_full_betting_workflow(
    background_tasks: BackgroundTasks,
    bankroll: float = 1000.0,
    async_execution: bool = False
):
    """
    Execute the complete ESPN → OpenAI → DraftKings workflow
    """
    try:
        if async_execution:
            # Execute in background
            background_tasks.add_task(
                betting_orchestrator.execute_full_betting_workflow,
                bankroll
            )
            return {
                "status": "success",
                "message": "Betting workflow started in background",
                "async_execution": True
            }
        else:
            # Execute synchronously
            results = await betting_orchestrator.execute_full_betting_workflow(bankroll)
            return {
                "status": "success",
                "workflow_results": results
            }
            
    except Exception as e:
        logger.error(f"Error executing betting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/espn-data")
async def get_espn_sports_data(
    sport: Optional[str] = None,
    include_news: bool = True
):
    """
    Get current ESPN sports data and news
    """
    try:
        # Get scores/games data
        if sport:
            # Get specific sport data (you'd need to implement sport-specific methods)
            sports_data = await espn_service.get_all_scores_today()
            sports_data = {k: v for k, v in sports_data.items() if sport.lower() in k.lower()}
        else:
            sports_data = await espn_service.get_all_scores_today()
        
        result = {"sports_data": sports_data}
        
        # Include news if requested
        if include_news:
            news_data = await espn_service.get_all_news_today()
            result["news_data"] = news_data
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting ESPN data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-predictions")
async def generate_ai_predictions(
    espn_data: Optional[Dict[str, Any]] = None,
    use_cached_data: bool = True
):
    """
    Generate OpenAI predictions from ESPN data
    """
    try:
        # Use provided data or fetch fresh data
        if not espn_data and use_cached_data:
            espn_data = await espn_service.get_all_scores_today()
            news_data = await espn_service.get_all_news_today()
        elif not espn_data:
            raise HTTPException(status_code=400, detail="No ESPN data provided and caching disabled")
        else:
            news_data = {}
        
        # Generate predictions
        predictions = await openai_prediction_service.generate_daily_predictions(espn_data, news_data)
        
        return {
            "status": "success",
            "predictions": predictions,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-opportunities")
async def get_live_betting_opportunities():
    """
    Get current live betting opportunities
    """
    try:
        opportunities = await betting_orchestrator.get_live_market_opportunities()
        
        return {
            "status": "success",
            "opportunities": opportunities,
            "count": len(opportunities),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting live opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session-status")
async def get_session_status():
    """
    Get current betting session status
    """
    try:
        session = betting_orchestrator.current_session
        
        if not session:
            return {
                "status": "success",
                "session_active": False,
                "message": "No active betting session"
            }
        
        return {
            "status": "success",
            "session_active": betting_orchestrator.session_active,
            "session": {
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "games_analyzed": session.games_analyzed,
                "predictions_generated": session.predictions_generated,
                "bets_placed": session.bets_placed,
                "total_stake": session.total_stake,
                "potential_payout": session.potential_payout,
                "status": session.status
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-session")
async def stop_betting_session():
    """
    Stop the current betting session
    """
    try:
        session = await betting_orchestrator.stop_betting_session()
        
        if not session:
            return {
                "status": "success",
                "message": "No active session to stop"
            }
        
        return {
            "status": "success",
            "message": "Betting session stopped successfully",
            "session_summary": {
                "session_id": session.session_id,
                "duration_minutes": (session.end_time - session.start_time).total_seconds() / 60,
                "games_analyzed": session.games_analyzed,
                "bets_placed": session.bets_placed,
                "total_stake": session.total_stake,
                "potential_payout": session.potential_payout
            }
        }
        
    except Exception as e:
        logger.error(f"Error stopping session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-stop")
async def emergency_stop_all_betting():
    """
    Emergency stop all betting activities
    """
    try:
        results = await betting_orchestrator.emergency_stop_all_betting()
        
        return {
            "status": "success",
            "message": "Emergency stop executed",
            "emergency_results": results
        }
        
    except Exception as e:
        logger.error(f"Error during emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_betting_performance(days: int = 30):
    """
    Get betting performance analytics
    """
    try:
        performance = await betting_orchestrator.get_betting_performance(days)
        
        if not performance:
            return {
                "status": "success",
                "message": "No performance data available",
                "days_requested": days
            }
        
        return {
            "status": "success",
            "performance": {
                "period_days": days,
                "total_bets": performance.total_bets,
                "total_stake": performance.total_stake,
                "total_payout": performance.total_payout,
                "net_profit": performance.net_profit,
                "roi_percentage": performance.roi_percentage,
                "hit_rate": performance.hit_rate,
                "sessions_count": len(performance.sessions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ESPN-specific endpoints
@router.get("/espn/nfl/scores")
async def get_nfl_scores(date: Optional[str] = None):
    """Get current NFL scores"""
    try:
        scores = await espn_service.get_nfl_scores(date)
        return {"status": "success", "data": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/espn/nba/scores")
async def get_nba_scores(date: Optional[str] = None):
    """Get current NBA scores"""
    try:
        scores = await espn_service.get_nba_scores(date)
        return {"status": "success", "data": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/espn/soccer/scores")
async def get_soccer_scores(league: str = "eng.1", date: Optional[str] = None):
    """Get current soccer scores by league"""
    try:
        scores = await espn_service.get_soccer_scores(league, date)
        return {"status": "success", "data": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/espn/news/{sport}")
async def get_sport_news(sport: str):
    """Get news for a specific sport"""
    try:
        if sport.lower() == "nfl":
            news = await espn_service.get_nfl_news()
        elif sport.lower() == "nba":
            news = await espn_service.get_nba_news()
        elif sport.lower() == "mlb":
            news = await espn_service.get_mlb_news()
        elif sport.lower() == "nhl":
            news = await espn_service.get_nhl_news()
        elif sport.lower() == "college-football":
            news = await espn_service.get_college_football_news()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported sport: {sport}")
        
        return {"status": "success", "data": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))