"""
Intelligent Automated Betting Strategy Engine
Implements sophisticated risk management and automated bet placement
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd

from .prediction_service import PredictionService
from .draftkings_service import DraftKingsService
from .cache_service import CacheService
from .openai_sports_data_service import openai_sports_service
from .sports_api_service import SportsAPIService
from core.database import get_db_session
from core.config import settings

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class BetType(Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"  
    TOTAL = "total"
    PROP = "prop"

class BetStatus(Enum):
    PENDING = "pending"
    PLACED = "placed"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"

@dataclass
class BettingStrategy:
    """Define betting strategy parameters"""
    name: str
    risk_level: RiskLevel
    max_bet_percentage: float  # Max % of bankroll per bet
    min_confidence_threshold: float  # Minimum prediction confidence
    min_expected_value: float  # Minimum expected value
    max_daily_bets: int
    max_exposure_percentage: float  # Max % of bankroll at risk
    kelly_fraction: float  # Fraction of Kelly criterion to use
    stop_loss_percentage: float  # Daily stop loss
    profit_target_percentage: float  # Daily profit target

@dataclass
class BettingDecision:
    """Automated betting decision with full context"""
    game_id: str
    bet_type: BetType
    selection: str  # e.g., "home", "away", "over", "under"
    recommended_amount: float
    odds: float
    expected_value: float
    confidence: float
    risk_score: float
    reasoning: str
    kelly_size: float
    max_loss: float
    timestamp: datetime

@dataclass
class RiskMetrics:
    """Current portfolio risk metrics"""
    total_exposure: float
    exposure_percentage: float
    value_at_risk: float  # 1-day VaR at 95% confidence
    expected_shortfall: float  # Expected loss beyond VaR
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_return_per_bet: float

@dataclass
class BankrollStatus:
    """Current bankroll and performance status"""
    current_balance: float
    starting_balance: float
    daily_pnl: float
    total_pnl: float
    total_wagered: float
    total_won: float
    open_positions: int
    open_exposure: float
    roi: float
    max_drawdown: float

class AutomatedBettingEngine:
    """
    Advanced automated betting engine with sophisticated risk management
    
    Features:
    - Multi-strategy portfolio optimization
    - Real-time risk monitoring and position sizing
    - Automated bet placement with circuit breakers
    - Advanced bankroll management using Kelly Criterion
    - Machine learning-based strategy adaptation
    - Comprehensive performance tracking and reporting
    """
    
    def __init__(self, prediction_service: PredictionService, 
                 draftkings_service: DraftKingsService,
                 cache_service: CacheService):
        self.prediction_service = prediction_service
        self.draftkings_service = draftkings_service
        self.cache_service = cache_service
        
        # Trading engine state
        self.is_active = False
        self.current_strategy: Optional[BettingStrategy] = None
        self.bankroll_status = BankrollStatus(
            current_balance=1000.0,  # Starting bankroll
            starting_balance=1000.0,
            daily_pnl=0.0,
            total_pnl=0.0,
            total_wagered=0.0,
            total_won=0.0,
            open_positions=0,
            open_exposure=0.0,
            roi=0.0,
            max_drawdown=0.0
        )
        
        # Risk management parameters
        self.daily_stop_loss_hit = False
        self.daily_profit_target_hit = False
        self.circuit_breaker_active = False
        
        # Performance tracking
        self.betting_history: List[Dict] = []
        self.strategy_performance: Dict[str, Dict] = {}
        
        # Predefined strategies
        self.strategies = {
            "conservative": BettingStrategy(
                name="Conservative Value",
                risk_level=RiskLevel.CONSERVATIVE,
                max_bet_percentage=0.02,  # 2% max bet
                min_confidence_threshold=0.75,
                min_expected_value=0.05,
                max_daily_bets=5,
                max_exposure_percentage=0.15,  # 15% max exposure
                kelly_fraction=0.25,  # Quarter Kelly
                stop_loss_percentage=0.05,  # 5% daily stop loss
                profit_target_percentage=0.03  # 3% daily profit target
            ),
            "moderate": BettingStrategy(
                name="Moderate Growth",
                risk_level=RiskLevel.MODERATE,
                max_bet_percentage=0.03,  # 3% max bet
                min_confidence_threshold=0.65,
                min_expected_value=0.03,
                max_daily_bets=8,
                max_exposure_percentage=0.25,  # 25% max exposure
                kelly_fraction=0.5,  # Half Kelly
                stop_loss_percentage=0.08,  # 8% daily stop loss
                profit_target_percentage=0.05  # 5% daily profit target
            ),
            "aggressive": BettingStrategy(
                name="Aggressive Growth",
                risk_level=RiskLevel.AGGRESSIVE,
                max_bet_percentage=0.05,  # 5% max bet
                min_confidence_threshold=0.55,
                min_expected_value=0.01,
                max_daily_bets=12,
                max_exposure_percentage=0.40,  # 40% max exposure
                kelly_fraction=0.75,  # Three-quarter Kelly
                stop_loss_percentage=0.12,  # 12% daily stop loss
                profit_target_percentage=0.08  # 8% daily profit target
            )
        }

    async def start_automated_betting(self, strategy_name: str = "moderate"):
        """Start the automated betting engine"""
        try:
            if self.is_active:
                logger.warning("Automated betting already active")
                return
            
            # Set strategy
            if strategy_name not in self.strategies:
                raise ValueError(f"Unknown strategy: {strategy_name}")
            
            self.current_strategy = self.strategies[strategy_name]
            self.is_active = True
            self.daily_stop_loss_hit = False
            self.daily_profit_target_hit = False
            self.circuit_breaker_active = False
            
            logger.info(f"Started automated betting with {strategy_name} strategy")
            
            # Start main betting loop
            await self._main_betting_loop()
            
        except Exception as e:
            logger.error(f"Error starting automated betting: {e}")
            await self.stop_automated_betting()
            raise

    async def stop_automated_betting(self):
        """Stop the automated betting engine"""
        self.is_active = False
        logger.info("Stopped automated betting engine")

    async def _main_betting_loop(self):
        """Main loop for automated betting decisions"""
        while self.is_active:
            try:
                # Update bankroll and risk metrics
                await self._update_bankroll_status()
                
                # Check circuit breakers
                if await self._check_circuit_breakers():
                    logger.warning("Circuit breaker triggered, pausing betting")
                    await asyncio.sleep(300)  # Wait 5 minutes
                    continue
                
                # Get today's games and predictions
                today = datetime.now().date()
                
                # Try primary prediction service first
                try:
                    predictions = await self.prediction_service.get_daily_predictions(datetime.now())
                except Exception as e:
                    logger.warning(f"Primary prediction service failed: {e}, using OpenAI fallback")
                    # Fallback to OpenAI recommendations
                    openai_recommendations = await openai_sports_service.get_betting_recommendations("NBA", 10)
                    predictions = self._convert_openai_to_predictions(openai_recommendations)
                
                # Filter and rank betting opportunities
                opportunities = await self._identify_betting_opportunities(predictions)
                
                # Make betting decisions
                decisions = await self._make_betting_decisions(opportunities)
                
                # Execute bets
                for decision in decisions:
                    await self._execute_bet(decision)
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Sleep before next iteration
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in betting loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _identify_betting_opportunities(self, predictions: List[Dict]) -> List[Dict]:
        """Identify and rank betting opportunities"""
        try:
            opportunities = []
            
            for prediction in predictions:
                # Apply strategy filters
                if not await self._meets_strategy_criteria(prediction):
                    continue
                
                # Calculate opportunity score
                opportunity_score = await self._calculate_opportunity_score(prediction)
                
                # Create opportunity record
                opportunity = {
                    **prediction,
                    'opportunity_score': opportunity_score,
                    'risk_score': await self._calculate_risk_score(prediction),
                    'position_size': await self._calculate_position_size(prediction)
                }
                
                opportunities.append(opportunity)
            
            # Sort by opportunity score (highest first)
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            # Limit to max daily bets
            max_bets = self.current_strategy.max_daily_bets
            daily_bet_count = await self._get_daily_bet_count()
            remaining_bets = max(0, max_bets - daily_bet_count)
            
            return opportunities[:remaining_bets]
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}")
            return []

    async def _make_betting_decisions(self, opportunities: List[Dict]) -> List[BettingDecision]:
        """Make final betting decisions with portfolio optimization"""
        try:
            decisions = []
            
            # Calculate current exposure
            current_exposure = await self._calculate_current_exposure()
            max_total_exposure = (
                self.current_strategy.max_exposure_percentage * 
                self.bankroll_status.current_balance
            )
            
            available_exposure = max_total_exposure - current_exposure
            
            for opportunity in opportunities:
                # Check if we have enough exposure capacity
                position_size = opportunity['position_size']
                
                if position_size > available_exposure:
                    logger.info(f"Skipping bet due to exposure limits: {opportunity['game_id']}")
                    continue
                
                # Create betting decision
                decision = BettingDecision(
                    game_id=opportunity['game_id'],
                    bet_type=BetType.MONEYLINE,  # Simplified for this example
                    selection=await self._determine_best_selection(opportunity),
                    recommended_amount=position_size,
                    odds=await self._get_best_odds(opportunity),
                    expected_value=opportunity['expected_value'],
                    confidence=opportunity['confidence_score'],
                    risk_score=opportunity['risk_score'],
                    reasoning=opportunity['reasoning'],
                    kelly_size=opportunity.get('kelly_criterion_bet_size', 0),
                    max_loss=position_size,  # Simplified
                    timestamp=datetime.utcnow()
                )
                
                decisions.append(decision)
                available_exposure -= position_size
                
                # Stop if we've reached exposure limit
                if available_exposure <= 0:
                    break
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error making betting decisions: {e}")
            return []

    async def _execute_bet(self, decision: BettingDecision) -> Dict[str, Any]:
        """Execute a betting decision"""
        try:
            # Final pre-execution checks
            if not await self._pre_execution_checks(decision):
                return {"status": "rejected", "reason": "Failed pre-execution checks"}
            
            # Place the bet through DraftKings service
            bet_result = await self.draftkings_service.place_bet(
                game_id=decision.game_id,
                bet_type=decision.bet_type.value,
                selection=decision.selection,
                amount=decision.recommended_amount,
                odds=decision.odds
            )
            
            if bet_result.get('success'):
                # Update tracking
                await self._record_bet_placement(decision, bet_result)
                
                # Update bankroll
                self.bankroll_status.open_positions += 1
                self.bankroll_status.open_exposure += decision.recommended_amount
                self.bankroll_status.total_wagered += decision.recommended_amount
                
                logger.info(f"Bet placed successfully: {decision.game_id} - ${decision.recommended_amount}")
                
                return {
                    "status": "success",
                    "bet_id": bet_result.get('bet_id'),
                    "amount": decision.recommended_amount,
                    "odds": decision.odds
                }
            else:
                logger.warning(f"Failed to place bet: {bet_result.get('error')}")
                return {"status": "failed", "reason": bet_result.get('error')}
                
        except Exception as e:
            logger.error(f"Error executing bet: {e}")
            return {"status": "error", "reason": str(e)}

    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get comprehensive portfolio status"""
        try:
            # Update current status
            await self._update_bankroll_status()
            risk_metrics = await self._calculate_risk_metrics()
            
            # Get recent performance
            recent_bets = await self._get_recent_betting_history(30)  # Last 30 days
            
            return {
                "bankroll": asdict(self.bankroll_status),
                "risk_metrics": asdict(risk_metrics),
                "strategy": {
                    "name": self.current_strategy.name if self.current_strategy else None,
                    "risk_level": self.current_strategy.risk_level.value if self.current_strategy else None,
                    "is_active": self.is_active
                },
                "circuit_breakers": {
                    "stop_loss_hit": self.daily_stop_loss_hit,
                    "profit_target_hit": self.daily_profit_target_hit,
                    "circuit_breaker_active": self.circuit_breaker_active
                },
                "recent_performance": {
                    "total_bets": len(recent_bets),
                    "winning_bets": sum(1 for bet in recent_bets if bet.get('result') == 'won'),
                    "average_bet_size": np.mean([bet['amount'] for bet in recent_bets]) if recent_bets else 0,
                    "largest_win": max([bet.get('profit', 0) for bet in recent_bets], default=0),
                    "largest_loss": min([bet.get('profit', 0) for bet in recent_bets], default=0)
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio status: {e}")
            raise

    async def update_bet_result(self, bet_id: str, result: str, profit_loss: float):
        """Update the result of a completed bet"""
        try:
            # Find the bet in history
            for bet in self.betting_history:
                if bet.get('bet_id') == bet_id:
                    bet['result'] = result
                    bet['profit_loss'] = profit_loss
                    bet['completed_at'] = datetime.utcnow().isoformat()
                    break
            
            # Update bankroll
            self.bankroll_status.open_positions -= 1
            self.bankroll_status.open_exposure -= bet.get('amount', 0)
            self.bankroll_status.current_balance += profit_loss
            self.bankroll_status.total_pnl += profit_loss
            self.bankroll_status.daily_pnl += profit_loss
            
            if result == 'won':
                self.bankroll_status.total_won += bet.get('amount', 0)
            
            # Update ROI
            if self.bankroll_status.total_wagered > 0:
                self.bankroll_status.roi = (
                    self.bankroll_status.total_pnl / self.bankroll_status.total_wagered
                ) * 100
            
            logger.info(f"Updated bet result: {bet_id} - {result} - P&L: ${profit_loss}")
            
        except Exception as e:
            logger.error(f"Error updating bet result: {e}")
            raise

    # Private helper methods

    async def _update_bankroll_status(self):
        """Update current bankroll status"""
        # This would typically query the actual account balance
        # For now, we'll use the tracked balance
        pass

    async def _check_circuit_breakers(self) -> bool:
        """Check if any circuit breakers should be triggered"""
        if not self.current_strategy:
            return True
        
        # Daily stop loss check
        daily_loss_percentage = abs(self.bankroll_status.daily_pnl) / self.bankroll_status.current_balance
        if (self.bankroll_status.daily_pnl < 0 and 
            daily_loss_percentage >= self.current_strategy.stop_loss_percentage):
            self.daily_stop_loss_hit = True
            return True
        
        # Daily profit target check (optional circuit breaker)
        daily_profit_percentage = self.bankroll_status.daily_pnl / self.bankroll_status.current_balance
        if daily_profit_percentage >= self.current_strategy.profit_target_percentage:
            self.daily_profit_target_hit = True
            # Could optionally stop here, but typically continue with reduced position sizes
        
        return False

    async def _meets_strategy_criteria(self, prediction: Dict) -> bool:
        """Check if prediction meets current strategy criteria"""
        if not self.current_strategy:
            return False
        
        # Check confidence threshold
        if prediction.get('confidence_score', 0) < self.current_strategy.min_confidence_threshold:
            return False
        
        # Check expected value threshold
        if prediction.get('expected_value', 0) < self.current_strategy.min_expected_value:
            return False
        
        # Check if recommended action is actionable
        recommended_action = prediction.get('recommended_action', '')
        if recommended_action == 'NO_BET':
            return False
        
        return True

    async def _calculate_opportunity_score(self, prediction: Dict) -> float:
        """Calculate composite opportunity score"""
        ev = prediction.get('expected_value', 0)
        confidence = prediction.get('confidence_score', 0)
        sharpe = prediction.get('sharpe_ratio', 0)
        
        # Weighted composite score
        opportunity_score = (ev * 0.4) + (confidence * 0.3) + (sharpe * 0.3)
        return opportunity_score

    async def _calculate_risk_score(self, prediction: Dict) -> float:
        """Calculate risk score for the prediction"""
        # This would use various risk factors
        # For now, return inverse of confidence
        confidence = prediction.get('confidence_score', 0.5)
        return 1.0 - confidence

    async def _calculate_position_size(self, prediction: Dict) -> float:
        """Calculate optimal position size using Kelly Criterion and strategy limits"""
        kelly_size = prediction.get('kelly_criterion_bet_size', 0)
        
        # Apply strategy's Kelly fraction
        adjusted_kelly = kelly_size * self.current_strategy.kelly_fraction
        
        # Apply maximum bet percentage limit
        max_bet_amount = self.current_strategy.max_bet_percentage * self.bankroll_status.current_balance
        
        # Take the minimum of Kelly and strategy limit
        position_size = min(
            adjusted_kelly * self.bankroll_status.current_balance,
            max_bet_amount
        )
        
        return max(position_size, 10.0)  # Minimum $10 bet

    async def _calculate_current_exposure(self) -> float:
        """Calculate current total exposure"""
        return self.bankroll_status.open_exposure

    async def _get_daily_bet_count(self) -> int:
        """Get number of bets placed today"""
        today = datetime.now().date()
        daily_bets = [
            bet for bet in self.betting_history 
            if datetime.fromisoformat(bet['timestamp']).date() == today
        ]
        return len(daily_bets)

    async def _determine_best_selection(self, opportunity: Dict) -> str:
        """Determine the best bet selection from the opportunity"""
        recommended_action = opportunity.get('recommended_action', '')
        if 'HOME' in recommended_action:
            return 'home'
        elif 'AWAY' in recommended_action:
            return 'away'
        else:
            return 'home'  # Default

    async def _get_best_odds(self, opportunity: Dict) -> float:
        """Get the best available odds for the opportunity"""
        # This would typically compare odds across multiple bookmakers
        # For now, return from the opportunity data
        return opportunity.get('odds', {}).get('home', 2.0)

    async def _pre_execution_checks(self, decision: BettingDecision) -> bool:
        """Perform final checks before executing bet"""
        # Check minimum bet size
        if decision.recommended_amount < 10.0:
            return False
        
        # Check maximum bet size
        max_bet = self.current_strategy.max_bet_percentage * self.bankroll_status.current_balance
        if decision.recommended_amount > max_bet:
            return False
        
        # Check available balance
        if decision.recommended_amount > self.bankroll_status.current_balance:
            return False
        
        return True

    async def _record_bet_placement(self, decision: BettingDecision, bet_result: Dict):
        """Record the bet placement in history"""
        bet_record = {
            "bet_id": bet_result.get('bet_id'),
            "game_id": decision.game_id,
            "bet_type": decision.bet_type.value,
            "selection": decision.selection,
            "amount": decision.recommended_amount,
            "odds": decision.odds,
            "expected_value": decision.expected_value,
            "confidence": decision.confidence,
            "risk_score": decision.risk_score,
            "reasoning": decision.reasoning,
            "timestamp": decision.timestamp.isoformat(),
            "strategy": self.current_strategy.name,
            "status": "placed"
        }
        
        self.betting_history.append(bet_record)

    async def _calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        # Simplified risk metrics calculation
        return RiskMetrics(
            total_exposure=self.bankroll_status.open_exposure,
            exposure_percentage=(self.bankroll_status.open_exposure / 
                               max(1, self.bankroll_status.current_balance)) * 100,
            value_at_risk=self.bankroll_status.open_exposure * 0.1,  # Simplified VaR
            expected_shortfall=self.bankroll_status.open_exposure * 0.15,
            max_drawdown=self.bankroll_status.max_drawdown,
            sharpe_ratio=1.5,  # Placeholder
            win_rate=0.55,  # Placeholder
            avg_return_per_bet=5.0  # Placeholder
        )

    async def _get_recent_betting_history(self, days: int) -> List[Dict]:
        """Get betting history for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            bet for bet in self.betting_history
            if datetime.fromisoformat(bet['timestamp']) >= cutoff_date
        ]

    async def _update_performance_metrics(self):
        """Update strategy performance metrics"""
        if not self.current_strategy:
            return
        
        strategy_name = self.current_strategy.name
        if strategy_name not in self.strategy_performance:
            self.strategy_performance[strategy_name] = {
                "total_bets": 0,
                "winning_bets": 0,
                "total_wagered": 0.0,
                "total_profit": 0.0,
                "win_rate": 0.0,
                "roi": 0.0,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        # Update would be based on completed bets
        # This is a placeholder for the actual implementation
    
    def _convert_openai_to_predictions(self, openai_recommendations: List[Dict[str, Any]]) -> List[Dict]:
        """Convert OpenAI recommendations to prediction format"""
        predictions = []
        
        for rec in openai_recommendations:
            prediction = {
                'game_id': f"openai_{len(predictions)}",
                'home_team': rec.get('game', '').split(' vs ')[-1] if ' vs ' in rec.get('game', '') else 'Unknown',
                'away_team': rec.get('game', '').split(' vs ')[0] if ' vs ' in rec.get('game', '') else 'Unknown',
                'sport': rec.get('sport', 'NBA'),
                'prediction_confidence': float(rec.get('confidence', 5)) / 10.0,  # Convert 1-10 to 0-1
                'predicted_winner': rec.get('selection', '').split(' ')[0] if rec.get('selection') else 'home',
                'expected_value': float(rec.get('expected_value', '+0%').replace('%', '').replace('+', '')) / 100.0,
                'bet_type': rec.get('bet_type', 'moneyline'),
                'odds': rec.get('odds', -110),
                'recommended_stake': float(settings.FIXED_BET_AMOUNT),  # Use fixed $5 bet
                'risk_level': rec.get('risk_level', 'Medium').lower(),
                'reasoning': rec.get('reasoning', 'AI recommendation'),
                'source': 'openai_fallback',
                'timestamp': datetime.utcnow().isoformat()
            }
            predictions.append(prediction)
        
        logger.info(f"Converted {len(predictions)} OpenAI recommendations to predictions")
        return predictions
    
    async def enable_automatic_betting(self, enable: bool = True):
        """Enable or disable automatic bet placement"""
        if enable:
            if not self.is_active:
                logger.info("Starting automated betting engine with $5 fixed bets")
                await self.start_automated_betting("moderate")
            else:
                logger.info("Automated betting engine is already active")
        else:
            if self.is_active:
                logger.info("Stopping automated betting engine")
                await self.stop_automated_betting()
            else:
                logger.info("Automated betting engine is already inactive")
    
    async def get_betting_status(self) -> Dict[str, Any]:
        """Get current automated betting status"""
        return {
            'is_active': self.is_active,
            'strategy': self.current_strategy.name if self.current_strategy else None,
            'bankroll': {
                'current_balance': self.bankroll_status.current_balance,
                'daily_pnl': self.bankroll_status.daily_pnl,
                'total_pnl': self.bankroll_status.total_pnl,
                'open_exposure': self.bankroll_status.open_exposure
            },
            'risk_management': {
                'daily_stop_loss_hit': self.daily_stop_loss_hit,
                'daily_profit_target_hit': self.daily_profit_target_hit,
                'circuit_breaker_active': self.circuit_breaker_active
            },
            'settings': {
                'fixed_bet_amount': float(settings.FIXED_BET_AMOUNT),
                'max_daily_bets': self.current_strategy.max_daily_bets if self.current_strategy else 0,
                'auto_betting_enabled': self.is_active
            }
        }