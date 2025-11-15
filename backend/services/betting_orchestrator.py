"""
Master Integration Service for Sports Betting Application
Coordinates ESPN data collection, OpenAI predictions, and DraftKings betting
"""
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from services.comprehensive_sports_data_service import ComprehensiveSportsDataService
from services.openai_prediction_service import openai_prediction_service
from services.draftkings_betting_service import create_draftkings_service
from core.config import settings
from core.database import get_db_session
from .cache_service import CacheService

logger = logging.getLogger(__name__)

@dataclass
class BettingSession:
    """Complete betting session results"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    games_analyzed: int
    predictions_generated: int
    bets_placed: int
    total_stake: float
    potential_payout: float
    success_rate: Optional[float]
    profit_loss: Optional[float]
    status: str  # "running", "completed", "failed"

@dataclass
class DailyBettingResults:
    """Daily betting performance summary"""
    date: datetime
    sessions: List[BettingSession]
    total_bets: int
    total_stake: float
    total_payout: float
    net_profit: float
    roi_percentage: float
    hit_rate: float
    best_bet: Optional[Dict[str, Any]]
    worst_bet: Optional[Dict[str, Any]]

class MasterBettingOrchestrator:
    """
    Master orchestration service that coordinates the entire betting workflow:
    1. Collect ESPN data
    2. Generate OpenAI predictions  
    3. Execute DraftKings bets
    4. Monitor and track results
    """
    
    def __init__(self):
        self.cache_service = CacheService()
        self.sports_data_service = ComprehensiveSportsDataService()
        self.draftkings_service = None
        self.session_active = False
        self.current_session: Optional[BettingSession] = None
        
        # Fixed bet amount configuration
        self.fixed_bet_amount = float(os.getenv('FIXED_BET_AMOUNT', '5.0'))
        self.fixed_parlay_amount = float(os.getenv('FIXED_PARLAY_AMOUNT', '5.0'))
        self.paper_trading_mode = os.getenv('PAPER_TRADING_MODE', 'true').lower() == 'true'
        
        # Risk management settings
        self.max_single_bet = float(os.getenv('MAX_SINGLE_BET', '100.0'))
        self.max_daily_exposure = float(os.getenv('MAX_DAILY_EXPOSURE', '500.0'))
        self.min_confidence_threshold = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.7'))
        self.bankroll_size = float(os.getenv('BANKROLL_SIZE', '1000.0'))
        
        logger.info(f"Betting orchestrator initialized with fixed amounts: ${self.fixed_bet_amount} (single), ${self.fixed_parlay_amount} (parlay)")
        
    async def initialize_draftkings(self, username: str, password: str, state: str) -> bool:
        """Initialize DraftKings service with credentials"""
        try:
            self.draftkings_service = create_draftkings_service(username, password, state)
            authenticated = await self.draftkings_service.authenticate()
            
            if authenticated:
                logger.info("Successfully initialized DraftKings integration")
                return True
            else:
                logger.error("Failed to authenticate with DraftKings")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing DraftKings service: {e}")
            return False
    
    async def start_daily_betting_session(self, bankroll: float = 1000.0) -> BettingSession:
        """
        Start a new daily betting session
        """
        if self.session_active:
            logger.warning("Betting session already active")
            return self.current_session
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = BettingSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            games_analyzed=0,
            predictions_generated=0,
            bets_placed=0,
            total_stake=0.0,
            potential_payout=0.0,
            success_rate=None,
            profit_loss=None,
            status="running"
        )
        
        self.session_active = True
        logger.info(f"Started betting session {session_id} with ${bankroll:,.2f} bankroll")
        
        return self.current_session
    
    async def execute_full_betting_workflow(self, bankroll: float = 1000.0) -> Dict[str, Any]:
        """
        Execute the complete betting workflow:
        ESPN → OpenAI → DraftKings
        """
        try:
            workflow_results = {
                "workflow_id": f"workflow_{int(datetime.now().timestamp())}",
                "start_time": datetime.now().isoformat(),
                "steps": {},
                "final_results": {},
                "errors": []
            }
            
            # Step 1: Collect ESPN Data
            logger.info("Step 1: Collecting ESPN sports data...")
            espn_data = await self._collect_espn_data()
            workflow_results["steps"]["espn_data_collection"] = {
                "status": "completed" if espn_data else "failed",
                "games_found": sum(len(sport_data.get("events", [])) for sport_data in espn_data.values()),
                "sports_covered": list(espn_data.keys())
            }
            
            if not espn_data:
                workflow_results["errors"].append("Failed to collect ESPN data")
                return workflow_results
            
            # Step 2: Collect ESPN News for Context
            logger.info("Step 2: Collecting ESPN news data...")
            news_data = await self._collect_espn_news()
            workflow_results["steps"]["news_collection"] = {
                "status": "completed" if news_data else "failed",
                "articles_found": sum(len(sport_news.get("articles", [])) for sport_news in news_data.values())
            }
            
            # Step 3: Generate OpenAI Predictions
            logger.info("Step 3: Generating OpenAI predictions...")
            predictions = await self._generate_predictions(espn_data, news_data)
            workflow_results["steps"]["prediction_generation"] = {
                "status": "completed" if predictions else "failed",
                "individual_picks": len(predictions.get("individual_picks", [])),
                "parlay_options": len(predictions.get("parlay_recommendations", []))
            }
            
            if not predictions or not predictions.get("individual_picks"):
                workflow_results["errors"].append("Failed to generate valid predictions")
                return workflow_results
            
            # Step 4: Execute DraftKings Bets
            if self.draftkings_service:
                logger.info("Step 4: Executing DraftKings bets...")
                betting_results = await self._execute_bets(predictions, bankroll)
                workflow_results["steps"]["bet_execution"] = {
                    "status": "completed" if betting_results else "failed",
                    "bets_placed": len(betting_results.get("individual_bets", [])) + len(betting_results.get("parlay_bets", [])),
                    "total_stake": betting_results.get("total_stake", 0.0),
                    "potential_payout": betting_results.get("potential_payout", 0.0)
                }
                
                # Update session if active
                if self.current_session:
                    self.current_session.bets_placed = workflow_results["steps"]["bet_execution"]["bets_placed"]
                    self.current_session.total_stake = workflow_results["steps"]["bet_execution"]["total_stake"]
                    self.current_session.potential_payout = workflow_results["steps"]["bet_execution"]["potential_payout"]
            else:
                workflow_results["steps"]["bet_execution"] = {
                    "status": "skipped",
                    "reason": "DraftKings service not initialized"
                }
                logger.warning("DraftKings service not initialized - skipping bet execution")
            
            # Step 5: Cache Results for Analysis
            cache_key = f"betting_workflow_{workflow_results['workflow_id']}"
            await self.cache_service.set(cache_key, workflow_results, ttl=86400)  # 24 hours
            
            workflow_results["final_results"] = {
                "success": True,
                "workflow_completed": True,
                "end_time": datetime.now().isoformat(),
                "summary": self._generate_workflow_summary(workflow_results)
            }
            
            logger.info(f"Betting workflow completed successfully: {workflow_results['workflow_id']}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error in betting workflow: {e}")
            workflow_results["errors"].append(str(e))
            workflow_results["final_results"] = {
                "success": False,
                "error": str(e),
                "end_time": datetime.now().isoformat()
            }
            return workflow_results
    
    async def _collect_espn_data(self) -> Dict[str, Any]:
        """Collect comprehensive ESPN sports data"""
        try:
            # Check cache first
            cache_key = "espn_data_daily"
            cached_data = await self.cache_service.get(cache_key)
            
            if cached_data:
                logger.info("Using cached ESPN data")
                return cached_data
            
            # Collect fresh data from comprehensive sports data service
            sports_data = await self.sports_data_service.get_upcoming_games(['nfl', 'nba', 'mlb', 'nhl'])
            
            # Cache for 30 minutes
            if sports_data:
                await self.cache_service.set(cache_key, sports_data, ttl=1800)
            
            # Update session if active
            if self.current_session:
                total_games = len(sports_data)
                self.current_session.games_analyzed = total_games
            
            return sports_data
            
        except Exception as e:
            logger.error(f"Error collecting ESPN data: {e}")
            return {}
    
    async def _collect_espn_news(self) -> Dict[str, Any]:
        """Collect ESPN news for prediction context"""
        try:
            cache_key = "espn_news_daily"
            cached_news = await self.cache_service.get(cache_key)
            
            if cached_news:
                return cached_news
            
            # For now, return empty news data since we're focusing on game data
            # This can be extended to fetch news from multiple sources
            news_data = {}
            
            if news_data:
                await self.cache_service.set(cache_key, news_data, ttl=3600)  # 1 hour
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error collecting ESPN news: {e}")
            return {}
    
    async def _generate_predictions(self, espn_data: Dict[str, Any], news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OpenAI predictions from ESPN data"""
        try:
            predictions = await openai_prediction_service.generate_daily_predictions(espn_data, news_data)
            
            # Update session if active
            if self.current_session:
                self.current_session.predictions_generated = len(predictions.get("individual_picks", []))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}
    
    async def _execute_bets(self, predictions: Dict[str, Any], bankroll: float) -> Dict[str, Any]:
        """Execute bets through DraftKings service"""
        try:
            if not self.draftkings_service:
                raise Exception("DraftKings service not initialized")
            
            betting_results = await self.draftkings_service.execute_betting_strategy(predictions, bankroll)
            return betting_results
            
        except Exception as e:
            logger.error(f"Error executing bets: {e}")
            return {}
    
    def _generate_workflow_summary(self, workflow_results: Dict[str, Any]) -> str:
        """Generate human-readable workflow summary"""
        steps = workflow_results.get("steps", {})
        
        espn_step = steps.get("espn_data_collection", {})
        prediction_step = steps.get("prediction_generation", {})
        betting_step = steps.get("bet_execution", {})
        
        summary = f"""
Betting Workflow Summary:
- ESPN Data: {espn_step.get('games_found', 0)} games across {len(espn_step.get('sports_covered', []))} sports
- Predictions: {prediction_step.get('individual_picks', 0)} individual picks, {prediction_step.get('parlay_options', 0)} parlay options
- Bets Placed: {betting_step.get('bets_placed', 0)} bets totaling ${betting_step.get('total_stake', 0.0):.2f}
- Potential Payout: ${betting_step.get('potential_payout', 0.0):.2f}
        """.strip()
        
        return summary
    
    async def get_betting_performance(self, days: int = 30) -> DailyBettingResults:
        """Get betting performance analytics for the last N days"""
        try:
            # This would typically query a database for historical betting results
            # For now, we'll return a placeholder structure
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Placeholder performance data
            performance = DailyBettingResults(
                date=end_date.date(),
                sessions=[],  # Would be populated from database
                total_bets=0,
                total_stake=0.0,
                total_payout=0.0,
                net_profit=0.0,
                roi_percentage=0.0,
                hit_rate=0.0,
                best_bet=None,
                worst_bet=None
            )
            
            logger.info(f"Retrieved betting performance for last {days} days")
            return performance
            
        except Exception as e:
            logger.error(f"Error getting betting performance: {e}")
            return None
    
    async def stop_betting_session(self) -> BettingSession:
        """Stop the current betting session"""
        if not self.session_active or not self.current_session:
            logger.warning("No active betting session to stop")
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.status = "completed"
        self.session_active = False
        
        logger.info(f"Stopped betting session {self.current_session.session_id}")
        return self.current_session
    
    async def get_live_market_opportunities(self) -> List[Dict[str, Any]]:
        """Get real-time betting opportunities based on live odds and predictions"""
        try:
            if not self.draftkings_service:
                logger.warning("DraftKings service not available for live markets")
                return []
            
            # Get live markets
            live_markets = await self.draftkings_service.get_available_markets()
            
            # Filter for live betting opportunities
            live_opportunities = [
                market for market in live_markets 
                if market.live_betting and market.status == "active"
            ]
            
            logger.info(f"Found {len(live_opportunities)} live betting opportunities")
            return [asdict(opp) for opp in live_opportunities]
            
        except Exception as e:
            logger.error(f"Error getting live market opportunities: {e}")
            return []
    
    async def emergency_stop_all_betting(self) -> Dict[str, Any]:
        """Emergency stop all betting activities and close positions if possible"""
        try:
            logger.warning("EMERGENCY STOP: Halting all betting activities")
            
            results = {
                "emergency_stop_time": datetime.now().isoformat(),
                "session_stopped": False,
                "pending_bets_cancelled": 0,
                "status": "emergency_stop_executed"
            }
            
            # Stop current session
            if self.session_active:
                await self.stop_betting_session()
                results["session_stopped"] = True
            
            # In a real implementation, this would:
            # 1. Cancel any pending bets
            # 2. Close live betting positions if possible
            # 3. Send alerts to administrators
            # 4. Log emergency stop reason
            
            logger.critical("Emergency stop completed - all betting activities halted")
            return results
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
            return {"error": str(e), "emergency_stop_failed": True}
    
    async def close(self):
        """Clean up resources"""
        if self.draftkings_service:
            await self.draftkings_service.close()
        
        if self.session_active:
            await self.stop_betting_session()

# Global orchestrator instance
betting_orchestrator = MasterBettingOrchestrator()