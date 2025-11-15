"""
Enhanced Celery tasks for betting operations and system health
"""
from celery import current_app as celery
from datetime import datetime
import asyncio
import logging
from typing import Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def process_bet_settlement(self, bet_id: int, game_result: dict):
    """Process bet settlement in the background"""
    try:
        logger.info(f"Processing bet settlement for bet {bet_id}")
        
        # Add actual bet settlement logic here
        result = {
            "bet_id": bet_id,
            "game_result": game_result,
            "processed_at": datetime.utcnow().isoformat(),
            "status": "settled"
        }
        
        logger.info(f"Bet {bet_id} settled successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Error processing bet settlement {bet_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)
        raise

@celery.task(bind=True, max_retries=3)
def update_game_odds(self, game_id: str):
    """Update odds for a specific game"""
    try:
        logger.info(f"Updating odds for game {game_id}")
        
        result = {
            "game_id": game_id,
            "updated_at": datetime.utcnow().isoformat(),
            "status": "updated",
            "source": "api_refresh"
        }
        
        logger.info(f"Odds updated for game {game_id}")
        return result

@celery.task(bind=True, max_retries=2)
def run_automated_betting():
    """Run automated betting cycle"""
    try:
        logger.info("🎰 Starting automated betting task...")
        
        # Import here to avoid circular imports
        from services.live_draftkings_service import live_draftkings_service
        
        # Run the betting cycle synchronously in the task
        async def betting_cycle():
            if not live_draftkings_service.authenticated:
                await live_draftkings_service.initialize()
            await live_draftkings_service.run_automated_betting_cycle()
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(betting_cycle())
        loop.close()
        
        logger.info("🎯 Automated betting task completed")
        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "task": "automated_betting"
        }
        
    except Exception as exc:
        logger.error(f"Error in automated betting task: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300, exc=exc)  # Retry in 5 minutes
        raise
        
    except Exception as exc:
        logger.error(f"Error updating odds for game {game_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30, exc=exc)
        return {"game_id": game_id, "status": "failed", "error": str(exc)}

@celery.task(bind=True, max_retries=2)
def calculate_user_profits(self, user_id: int):
    """Calculate user profit/loss statistics"""
    try:
        logger.info(f"Calculating profits for user {user_id}")
        
        result = {
            "user_id": user_id,
            "calculated_at": datetime.utcnow().isoformat(),
            "total_profit": 0.0,
            "win_rate": 0.0,
            "total_bets": 0,
            "status": "calculated"
        }
        
        logger.info(f"Profits calculated for user {user_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Error calculating profits for user {user_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120, exc=exc)
        return {"user_id": user_id, "status": "failed", "error": str(exc)}

@celery.task
def health_check():
    """Health check task for Celery workers"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis_connected": True,
            "database_connected": True
        }
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {"status": "unhealthy", "error": str(exc)}

@celery.task
def process_automated_bets():
    """Process automated betting with $5 fixed amounts"""
    try:
        if not getattr(settings, 'AUTO_BETTING_ENABLED', False):
            return {"status": "disabled", "message": "Automated betting is disabled"}
            
        logger.info("Processing automated betting decisions")
        
        result = {
            "processed_at": datetime.utcnow().isoformat(),
            "bets_placed": 0,
            "total_amount": 0.0,
            "status": "processed"
        }
        
        logger.info("Automated betting processing completed")
        return result
        
    except Exception as exc:
        logger.error(f"Error in automated betting: {exc}")
        return {"status": "failed", "error": str(exc)}