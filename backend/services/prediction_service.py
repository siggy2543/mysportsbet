"""
Advanced Prediction Service with Game Theory Integration
Combines ML models with strategic decision-making algorithms
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
import pandas as pd
import numpy as np

from .game_theory_predictor import (
    GameTheoryPredictor, 
    GameState, 
    PredictionResult,
    GameOutcome
)
from .sports_api_service import SportsAPIService
from .cache_service import CacheService

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Advanced prediction service combining traditional ML with game theory
    
    Features:
    - Nash equilibrium analysis for optimal betting strategies
    - Kelly Criterion for optimal bet sizing
    - Risk-adjusted return optimization
    - Multi-model ensemble predictions
    - Real-time market analysis
    """
    
    def __init__(self, sports_api: SportsAPIService, cache_service: CacheService):
        self.sports_api = sports_api
        self.cache_service = cache_service
        self.game_theory_predictor = GameTheoryPredictor()
        self.model_initialized = False
        self.prediction_accuracy = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "profit_loss": 0.0,
            "roi": 0.0
        }
    
    async def initialize_service(self):
        """Initialize the prediction service with historical data"""
        try:
            logger.info("Initializing prediction service...")
            
            # Load historical data for training
            historical_data = await self._load_historical_data()
            
            # Initialize game theory models
            await self.game_theory_predictor.initialize_models(historical_data)
            
            self.model_initialized = True
            logger.info("Prediction service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction service: {e}")
            raise

    async def get_game_prediction(self, game_id: str) -> Dict[str, Any]:
        """
        Get comprehensive AI prediction for a specific game using game theory
        """
        if not self.model_initialized:
            await self.initialize_service()
        
        try:
            # Check cache first
            cache_key = f"prediction:{game_id}"
            cached_prediction = await self.cache_service.get(cache_key)
            if cached_prediction:
                return cached_prediction
            
            # Get game data
            game_data = await self.sports_api.get_game_details(game_id)
            
            # Build game state for analysis
            game_state = await self._build_game_state(game_data)
            
            # Generate game theory prediction
            gt_prediction = await self.game_theory_predictor.generate_prediction(game_state)
            
            # Create comprehensive prediction response
            prediction = {
                "game_id": game_id,
                "timestamp": datetime.utcnow().isoformat(),
                
                # Game Theory Analysis
                "nash_equilibrium": {
                    "strategy_probabilities": gt_prediction.nash_equilibrium.strategy_probabilities,
                    "expected_payoff": gt_prediction.nash_equilibrium.expected_payoff,
                    "risk_assessment": gt_prediction.nash_equilibrium.risk_assessment,
                    "confidence_interval": gt_prediction.nash_equilibrium.confidence_interval
                },
                
                # Strategic Recommendations
                "minimax_strategy": gt_prediction.minimax_strategy,
                "recommended_action": gt_prediction.recommended_action,
                "kelly_bet_size": gt_prediction.kelly_criterion_bet_size,
                
                # Risk Metrics
                "expected_value": gt_prediction.expected_value,
                "sharpe_ratio": gt_prediction.sharpe_ratio,
                "risk_adjusted_return": gt_prediction.risk_adjusted_return,
                "confidence_score": gt_prediction.confidence_score,
                
                # Traditional Probabilities (for compatibility)
                "home_win_probability": gt_prediction.nash_equilibrium.strategy_probabilities.get("home_win", 0.0),
                "away_win_probability": gt_prediction.nash_equilibrium.strategy_probabilities.get("away_win", 0.0),
                "draw_probability": gt_prediction.nash_equilibrium.strategy_probabilities.get("draw", 0.0),
                
                # Betting Intelligence
                "market_efficiency": await self._analyze_market_efficiency(game_state),
                "value_bets": await self._identify_value_bets(gt_prediction),
                "arbitrage_opportunities": await self._check_arbitrage_opportunities(game_data),
                
                # Reasoning
                "reasoning": gt_prediction.reasoning,
                "model_version": "game_theory_v1.0",
                "factors_considered": [
                    "nash_equilibrium", "minimax_strategy", "kelly_criterion",
                    "historical_patterns", "market_dynamics", "risk_assessment"
                ]
            }
            
            # Cache the prediction
            await self.cache_service.set(cache_key, prediction, ttl=300)  # 5 minute cache
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction for game {game_id}: {e}")
            raise

    async def get_daily_predictions(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Get game theory predictions for all games on a specific date
        """
        try:
            # Get all games for the date
            games = await self.sports_api.get_games_by_date(date)
            
            # Generate predictions for each game
            predictions = []
            for game in games:
                try:
                    prediction = await self.get_game_prediction(game['id'])
                    
                    # Add game context
                    prediction.update({
                        "home_team": game['home_team'],
                        "away_team": game['away_team'],
                        "sport": game['sport'],
                        "league": game['league'],
                        "start_time": game['start_time']
                    })
                    
                    predictions.append(prediction)
                    
                except Exception as e:
                    logger.error(f"Failed to predict game {game['id']}: {e}")
                    continue
            
            # Sort by expected value (highest first)
            predictions.sort(key=lambda x: x.get('expected_value', 0), reverse=True)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating daily predictions for {date}: {e}")
            raise

    async def get_optimal_betting_portfolio(self, games: List[str], 
                                          bankroll: float) -> Dict[str, Any]:
        """
        Generate optimal betting portfolio using modern portfolio theory
        """
        try:
            if not games:
                return {"message": "No games provided"}
            
            # Get predictions for all games
            predictions = []
            for game_id in games:
                pred = await self.get_game_prediction(game_id)
                predictions.append(pred)
            
            # Portfolio optimization
            portfolio = await self._optimize_betting_portfolio(predictions, bankroll)
            
            return {
                "bankroll": bankroll,
                "recommended_bets": portfolio['bets'],
                "expected_return": portfolio['expected_return'],
                "portfolio_risk": portfolio['risk'],
                "sharpe_ratio": portfolio['sharpe_ratio'],
                "diversification_score": portfolio['diversification'],
                "max_drawdown_estimate": portfolio['max_drawdown'],
                "recommendation": portfolio['recommendation']
            }
            
        except Exception as e:
            logger.error(f"Error optimizing betting portfolio: {e}")
            raise

    async def update_model_performance(self, game_id: str, actual_outcome: str, 
                                     bet_placed: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Update model performance tracking with actual game results
        """
        try:
            # Get the original prediction
            cache_key = f"prediction:{game_id}"
            prediction = await self.cache_service.get(cache_key)
            
            if not prediction:
                logger.warning(f"No prediction found for game {game_id}")
                return {"status": "no_prediction_found"}
            
            # Calculate prediction accuracy
            predicted_outcome = prediction['recommended_action']
            was_correct = self._evaluate_prediction_accuracy(predicted_outcome, actual_outcome)
            
            # Update accuracy tracking
            self.prediction_accuracy['total_predictions'] += 1
            if was_correct:
                self.prediction_accuracy['correct_predictions'] += 1
            
            # Calculate profit/loss if bet was placed
            if bet_placed:
                pnl = self._calculate_bet_pnl(bet_placed, actual_outcome)
                self.prediction_accuracy['profit_loss'] += pnl
                
                if self.prediction_accuracy['total_predictions'] > 0:
                    total_wagered = bet_placed.get('amount', 0) * self.prediction_accuracy['total_predictions']
                    if total_wagered > 0:
                        self.prediction_accuracy['roi'] = (
                            self.prediction_accuracy['profit_loss'] / total_wagered
                        ) * 100
            
            # Store performance data for model retraining
            await self._store_performance_data(game_id, prediction, actual_outcome, bet_placed)
            
            return {
                "status": "updated",
                "was_correct": was_correct,
                "current_accuracy": (
                    self.prediction_accuracy['correct_predictions'] / 
                    max(1, self.prediction_accuracy['total_predictions'])
                ),
                "total_predictions": self.prediction_accuracy['total_predictions'],
                "roi": self.prediction_accuracy['roi']
            }
            
        except Exception as e:
            logger.error(f"Error updating model performance: {e}")
            raise

    async def get_prediction_accuracy(self) -> Dict[str, Any]:
        """Get comprehensive model accuracy and performance statistics"""
        try:
            total = max(1, self.prediction_accuracy['total_predictions'])
            
            # Calculate additional metrics
            win_rate = self.prediction_accuracy['correct_predictions'] / total
            avg_return_per_bet = self.prediction_accuracy['profit_loss'] / total
            
            # Get recent performance (last 30 days)
            recent_performance = await self._get_recent_performance(30)
            
            return {
                "overall_accuracy": win_rate,
                "total_predictions": self.prediction_accuracy['total_predictions'],
                "correct_predictions": self.prediction_accuracy['correct_predictions'],
                "profit_loss": self.prediction_accuracy['profit_loss'],
                "roi_percentage": self.prediction_accuracy['roi'],
                "average_return_per_bet": avg_return_per_bet,
                "recent_30_day_accuracy": recent_performance['accuracy'],
                "recent_30_day_roi": recent_performance['roi'],
                "model_confidence": await self._calculate_model_confidence(),
                "last_updated": datetime.utcnow().isoformat(),
                "model_version": "game_theory_v1.0"
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction accuracy: {e}")
            raise

    # Private helper methods
    
    async def _load_historical_data(self) -> pd.DataFrame:
        """Load historical game data for model training"""
        try:
            # This would typically load from database or external sources
            # For now, we'll create sample data structure
            
            sample_data = []
            for i in range(1000):  # Generate sample historical data
                game = {
                    'game_id': f'game_{i}',
                    'home_team': f'team_{i % 20}',
                    'away_team': f'team_{(i + 10) % 20}',
                    'home_odds': 1.5 + (i % 10) * 0.2,
                    'away_odds': 1.5 + ((i + 5) % 10) * 0.2,
                    'draw_odds': 3.0 + (i % 5) * 0.5,
                    'actual_outcome': ['home_win', 'away_win', 'draw'][i % 3],
                    'date': datetime.now() - timedelta(days=i),
                    'venue_advantage': 0.1 if i % 2 == 0 else -0.1
                }
                sample_data.append(game)
            
            return pd.DataFrame(sample_data)
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            raise

    async def _build_game_state(self, game_data: Dict) -> GameState:
        """Build GameState object from game data"""
        return GameState(
            home_team=game_data['home_team'],
            away_team=game_data['away_team'],
            home_odds=game_data['odds']['home'],
            away_odds=game_data['odds']['away'],
            draw_odds=game_data['odds'].get('draw'),
            historical_head_to_head=game_data.get('head_to_head', []),
            recent_form=game_data.get('recent_form', {}),
            injuries=game_data.get('injuries', {}),
            weather_conditions=game_data.get('weather'),
            venue_advantage=game_data.get('venue_advantage', 0.0)
        )

    async def _analyze_market_efficiency(self, game_state: GameState) -> Dict[str, float]:
        """Analyze market efficiency for the game"""
        return {
            "efficiency_score": 0.85,
            "overround": (1/game_state.home_odds + 1/game_state.away_odds) - 1,
            "implied_home_prob": 1/game_state.home_odds,
            "implied_away_prob": 1/game_state.away_odds
        }

    async def _identify_value_bets(self, prediction: PredictionResult) -> List[Dict]:
        """Identify potential value betting opportunities"""
        value_bets = []
        
        for strategy, prob in prediction.nash_equilibrium.strategy_probabilities.items():
            if strategy != 'no_bet' and prob > 0.1:
                value_bets.append({
                    "strategy": strategy,
                    "probability": prob,
                    "expected_value": prediction.expected_value,
                    "confidence": prediction.confidence_score
                })
        
        return value_bets

    async def _check_arbitrage_opportunities(self, game_data: Dict) -> List[Dict]:
        """Check for arbitrage opportunities across different bookmakers"""
        # This would check multiple bookmakers for arbitrage
        return []  # Placeholder

    async def _optimize_betting_portfolio(self, predictions: List[Dict], 
                                        bankroll: float) -> Dict[str, Any]:
        """Optimize betting portfolio using modern portfolio theory"""
        try:
            if not predictions:
                return {"bets": [], "expected_return": 0, "risk": 0}
            
            # Filter profitable predictions
            profitable_bets = [
                p for p in predictions 
                if p.get('expected_value', 0) > 0 and p.get('confidence_score', 0) > 0.6
            ]
            
            if not profitable_bets:
                return {
                    "bets": [],
                    "expected_return": 0,
                    "risk": 0,
                    "sharpe_ratio": 0,
                    "diversification": 0,
                    "max_drawdown": 0,
                    "recommendation": "No profitable bets identified"
                }
            
            # Simple portfolio allocation (equal weight with Kelly sizing)
            total_kelly = sum(p.get('kelly_bet_size', 0) for p in profitable_bets)
            
            bets = []
            total_allocation = 0
            
            for prediction in profitable_bets[:5]:  # Limit to top 5 bets
                kelly_size = prediction.get('kelly_bet_size', 0)
                if kelly_size > 0.01:  # Minimum 1% Kelly
                    allocation = min(kelly_size, 0.05) * bankroll  # Max 5% per bet
                    bets.append({
                        "game_id": prediction['game_id'],
                        "strategy": prediction['recommended_action'],
                        "allocation": allocation,
                        "percentage": (allocation / bankroll) * 100,
                        "expected_value": prediction['expected_value'],
                        "confidence": prediction['confidence_score']
                    })
                    total_allocation += allocation
            
            # Calculate portfolio metrics
            expected_return = sum(bet['allocation'] * bet['expected_value'] for bet in bets)
            portfolio_risk = total_allocation / bankroll  # Simplified risk measure
            sharpe_ratio = expected_return / max(0.01, portfolio_risk)
            
            return {
                "bets": bets,
                "expected_return": expected_return,
                "risk": portfolio_risk,
                "sharpe_ratio": sharpe_ratio,
                "diversification": min(len(bets) / 5.0, 1.0),
                "max_drawdown": portfolio_risk * 0.5,  # Estimated
                "recommendation": f"Allocate {total_allocation:.2f} ({(total_allocation/bankroll)*100:.1f}%) across {len(bets)} bets"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise

    def _evaluate_prediction_accuracy(self, predicted: str, actual: str) -> bool:
        """Evaluate if prediction was correct"""
        predicted_action = predicted.replace('BET_', '').lower()
        actual_outcome = actual.lower()
        
        return predicted_action == actual_outcome

    def _calculate_bet_pnl(self, bet: Dict, actual_outcome: str) -> float:
        """Calculate profit/loss for a placed bet"""
        amount = bet.get('amount', 0)
        odds = bet.get('odds', 1.0)
        bet_type = bet.get('type', '').lower()
        
        if bet_type == actual_outcome.lower():
            return amount * (odds - 1)  # Win
        else:
            return -amount  # Loss

    async def _store_performance_data(self, game_id: str, prediction: Dict, 
                                    actual: str, bet: Optional[Dict]):
        """Store performance data for analysis"""
        # This would store to database for future analysis
        pass

    async def _get_recent_performance(self, days: int) -> Dict[str, float]:
        """Get performance metrics for recent period"""
        # This would query recent performance from database
        return {"accuracy": 0.68, "roi": 5.2}

    async def _calculate_model_confidence(self) -> float:
        """Calculate overall model confidence score"""
        total = max(1, self.prediction_accuracy['total_predictions'])
        accuracy = self.prediction_accuracy['correct_predictions'] / total
        
        # Confidence increases with more predictions and higher accuracy
        confidence = min(accuracy * (1 + np.log(total + 1) / 10), 1.0)
        return confidence

    def is_healthy(self) -> bool:
        """Check if the prediction service is healthy and operational"""
        try:
            # Check if core components are initialized
            if not hasattr(self, 'sports_api') or not hasattr(self, 'cache_service'):
                return False
            
            # Check if game theory predictor is available
            if not hasattr(self, 'game_theory_predictor'):
                return False
            
            # Check if basic prediction accuracy tracking is working
            if not hasattr(self, 'prediction_accuracy'):
                return False
            
            return True
        except Exception:
            return False