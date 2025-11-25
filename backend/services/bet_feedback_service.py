"""
Bet Outcome Feedback Loop Service
Tracks bet outcomes and feeds data back into AI learning system
for continuous prediction improvement
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import asyncio
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BetOutcome:
    """Represents a completed bet with outcome"""
    bet_id: str
    sport: str
    matchup: str
    bet_type: str  # "moneyline", "spread", "total", "prop"
    predicted_outcome: str
    actual_outcome: str
    confidence: float
    odds: float
    stake: float
    profit_loss: float
    timestamp: datetime
    features_used: Dict[str, Any]  # Features that led to prediction
    

@dataclass
class AccuracyMetrics:
    """Accuracy metrics for a sport/bet type"""
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    avg_confidence: float
    avg_actual_confidence: float  # Calibrated based on outcomes
    roi: float  # Return on investment
    kelly_efficiency: float  # How well we followed Kelly criterion
    calibration_error: float  # Difference between predicted and actual confidence


class BetFeedbackService:
    """
    Service to track bet outcomes and provide feedback for AI learning
    
    Features:
    - Track all bet predictions and outcomes
    - Calculate accuracy metrics per sport/bet type
    - Identify which features correlate with wins/losses
    - Provide calibrated confidence scores
    - Feed insights back to prediction models
    """
    
    def __init__(self, storage_path: str = "/app/data/bet_outcomes.json"):
        self.storage_path = storage_path
        self.outcomes: List[BetOutcome] = []
        self.metrics_cache: Dict[str, AccuracyMetrics] = {}
        self.feature_importance: Dict[str, float] = {}
        
        # Load historical data
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical bet outcomes from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.outcomes = [
                    BetOutcome(**outcome) for outcome in data.get('outcomes', [])
                ]
                self.feature_importance = data.get('feature_importance', {})
                logger.info(f"Loaded {len(self.outcomes)} historical bet outcomes")
        except FileNotFoundError:
            logger.info("No historical bet data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    def _save_data(self):
        """Save current data to storage"""
        try:
            data = {
                'outcomes': [asdict(outcome) for outcome in self.outcomes],
                'feature_importance': self.feature_importance,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.outcomes)} bet outcomes to storage")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    async def record_bet_outcome(self, bet_outcome: BetOutcome):
        """
        Record a completed bet outcome
        
        Args:
            bet_outcome: BetOutcome object with all details
        """
        self.outcomes.append(bet_outcome)
        logger.info(f"Recorded bet outcome: {bet_outcome.bet_id} - {bet_outcome.actual_outcome}")
        
        # Update metrics
        await self._update_metrics(bet_outcome)
        
        # Save to storage
        self._save_data()
    
    async def _update_metrics(self, bet_outcome: BetOutcome):
        """Update accuracy metrics based on new outcome"""
        key = f"{bet_outcome.sport}_{bet_outcome.bet_type}"
        
        # Recalculate metrics for this sport/bet type
        relevant_outcomes = [
            o for o in self.outcomes 
            if o.sport == bet_outcome.sport and o.bet_type == bet_outcome.bet_type
        ]
        
        if relevant_outcomes:
            wins = sum(1 for o in relevant_outcomes if o.actual_outcome == o.predicted_outcome)
            losses = len(relevant_outcomes) - wins
            win_rate = wins / len(relevant_outcomes)
            
            avg_confidence = np.mean([o.confidence for o in relevant_outcomes])
            avg_roi = np.mean([o.profit_loss / o.stake for o in relevant_outcomes])
            
            # Calculate calibration error (how well confidence matches reality)
            predicted_confidences = [o.confidence / 100 for o in relevant_outcomes]
            actual_wins = [1 if o.actual_outcome == o.predicted_outcome else 0 for o in relevant_outcomes]
            calibration_error = abs(np.mean(predicted_confidences) - np.mean(actual_wins))
            
            metrics = AccuracyMetrics(
                total_bets=len(relevant_outcomes),
                wins=wins,
                losses=losses,
                win_rate=win_rate,
                avg_confidence=avg_confidence,
                avg_actual_confidence=win_rate * 100,
                roi=avg_roi * 100,
                kelly_efficiency=self._calculate_kelly_efficiency(relevant_outcomes),
                calibration_error=calibration_error
            )
            
            self.metrics_cache[key] = metrics
    
    def _calculate_kelly_efficiency(self, outcomes: List[BetOutcome]) -> float:
        """Calculate how efficiently we followed Kelly criterion"""
        if not outcomes:
            return 0.0
        
        # Kelly efficiency: how well bet sizing matched optimal Kelly
        # Simplified calculation
        efficiencies = []
        for outcome in outcomes:
            # Optimal Kelly would be based on edge and odds
            if outcome.odds > 1:
                edge = (outcome.confidence / 100) - (1 / outcome.odds)
                optimal_kelly = max(0, edge * outcome.odds / (outcome.odds - 1))
                actual_bet_pct = outcome.stake / 100  # Assume $100 bankroll for simplicity
                efficiency = 1 - abs(optimal_kelly - actual_bet_pct)
                efficiencies.append(max(0, efficiency))
        
        return np.mean(efficiencies) if efficiencies else 0.0
    
    async def get_calibrated_confidence(self, sport: str, bet_type: str, 
                                       predicted_confidence: float) -> float:
        """
        Get calibrated confidence based on historical accuracy
        
        Args:
            sport: Sport code
            bet_type: Type of bet
            predicted_confidence: Model's predicted confidence
            
        Returns:
            Calibrated confidence score
        """
        key = f"{sport}_{bet_type}"
        
        if key not in self.metrics_cache:
            # No historical data, return predicted
            return predicted_confidence
        
        metrics = self.metrics_cache[key]
        
        # If we historically overestimate, reduce confidence
        # If we historically underestimate, increase confidence
        calibration_factor = metrics.avg_actual_confidence / max(metrics.avg_confidence, 1)
        
        calibrated = predicted_confidence * calibration_factor
        
        # Keep within reasonable bounds
        return max(50, min(99, calibrated))
    
    async def get_sport_accuracy(self, sport: str) -> Dict[str, Any]:
        """Get accuracy metrics for a specific sport"""
        relevant_metrics = {
            k: v for k, v in self.metrics_cache.items() 
            if k.startswith(sport)
        }
        
        if not relevant_metrics:
            return {
                "sport": sport,
                "status": "insufficient_data",
                "total_bets": 0
            }
        
        # Aggregate metrics
        total_bets = sum(m.total_bets for m in relevant_metrics.values())
        total_wins = sum(m.wins for m in relevant_metrics.values())
        total_roi = np.mean([m.roi for m in relevant_metrics.values()])
        
        return {
            "sport": sport,
            "total_bets": total_bets,
            "win_rate": total_wins / total_bets if total_bets > 0 else 0,
            "roi": total_roi,
            "by_bet_type": {
                k.split('_')[1]: asdict(v) 
                for k, v in relevant_metrics.items()
            },
            "calibration_status": self._get_calibration_status(relevant_metrics)
        }
    
    def _get_calibration_status(self, metrics: Dict[str, AccuracyMetrics]) -> str:
        """Determine if predictions are well-calibrated"""
        if not metrics:
            return "unknown"
        
        avg_calibration_error = np.mean([m.calibration_error for m in metrics.values()])
        
        if avg_calibration_error < 0.05:
            return "excellent"
        elif avg_calibration_error < 0.10:
            return "good"
        elif avg_calibration_error < 0.15:
            return "fair"
        else:
            return "needs_improvement"
    
    async def analyze_feature_importance(self) -> Dict[str, float]:
        """
        Analyze which features correlate with winning bets
        
        Returns:
            Dictionary of feature names to importance scores
        """
        if len(self.outcomes) < 10:
            return {}
        
        feature_wins = defaultdict(list)
        
        for outcome in self.outcomes:
            won = outcome.actual_outcome == outcome.predicted_outcome
            
            # Analyze each feature
            for feature_name, feature_value in outcome.features_used.items():
                feature_wins[feature_name].append((feature_value, won))
        
        # Calculate correlation between feature values and wins
        importance_scores = {}
        
        for feature_name, values_wins in feature_wins.items():
            if len(values_wins) < 5:
                continue
            
            values = [v for v, _ in values_wins]
            wins = [1 if w else 0 for _, w in values_wins]
            
            # Simple correlation
            if len(set(values)) > 1:  # Only if feature has variance
                correlation = np.corrcoef(values, wins)[0, 1]
                importance_scores[feature_name] = abs(correlation)
        
        # Sort by importance
        self.feature_importance = dict(
            sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        )
        
        return self.feature_importance
    
    async def get_recommendations_for_improvement(self) -> List[str]:
        """
        Analyze performance and provide recommendations
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if len(self.outcomes) < 20:
            recommendations.append(
                "Need more bet outcomes (minimum 20) for reliable analysis"
            )
            return recommendations
        
        # Check calibration
        for key, metrics in self.metrics_cache.items():
            sport, bet_type = key.split('_')
            
            if metrics.calibration_error > 0.15:
                recommendations.append(
                    f"Confidence calibration for {sport} {bet_type} needs improvement. "
                    f"Predicted confidence is {metrics.calibration_error*100:.1f}% off from actual."
                )
            
            if metrics.win_rate < 0.52:  # Below breakeven with typical vig
                recommendations.append(
                    f"{sport} {bet_type} win rate ({metrics.win_rate*100:.1f}%) is below profitable threshold. "
                    f"Consider adjusting confidence thresholds or bet selection criteria."
                )
            
            if metrics.roi < -5:
                recommendations.append(
                    f"{sport} {bet_type} has negative ROI ({metrics.roi:.1f}%). "
                    f"Suggest pausing bets or reviewing prediction model."
                )
            
            if metrics.kelly_efficiency < 0.7:
                recommendations.append(
                    f"Kelly criterion efficiency for {sport} {bet_type} is low ({metrics.kelly_efficiency*100:.1f}%). "
                    f"Optimize bet sizing for better bankroll management."
                )
        
        # Feature importance insights
        if self.feature_importance:
            top_features = list(self.feature_importance.items())[:3]
            recommendations.append(
                f"Top predictive features: {', '.join([f[0] for f in top_features])}. "
                f"Focus on improving accuracy of these inputs."
            )
        
        if not recommendations:
            recommendations.append("Performance is good! Continue current strategy.")
        
        return recommendations
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for feedback loop dashboard"""
        if not self.outcomes:
            return {
                "status": "no_data",
                "message": "No bet outcomes recorded yet"
            }
        
        recent_outcomes = self.outcomes[-50:] if len(self.outcomes) > 50 else self.outcomes
        
        # Overall metrics
        total_wins = sum(1 for o in recent_outcomes if o.actual_outcome == o.predicted_outcome)
        total_roi = sum(o.profit_loss for o in recent_outcomes) / sum(o.stake for o in recent_outcomes) * 100
        
        # Per sport breakdown
        sports = list(set(o.sport for o in recent_outcomes))
        sport_metrics = {}
        
        for sport in sports:
            sport_outcomes = [o for o in recent_outcomes if o.sport == sport]
            sport_wins = sum(1 for o in sport_outcomes if o.actual_outcome == o.predicted_outcome)
            sport_metrics[sport] = {
                "total": len(sport_outcomes),
                "wins": sport_wins,
                "win_rate": sport_wins / len(sport_outcomes),
                "roi": sum(o.profit_loss for o in sport_outcomes) / sum(o.stake for o in sport_outcomes) * 100
            }
        
        return {
            "total_bets": len(self.outcomes),
            "recent_bets": len(recent_outcomes),
            "overall_win_rate": total_wins / len(recent_outcomes),
            "overall_roi": total_roi,
            "by_sport": sport_metrics,
            "calibration_status": self._get_calibration_status(self.metrics_cache),
            "feature_importance": self.feature_importance,
            "last_updated": datetime.now().isoformat()
        }


# Singleton instance
_feedback_service = None


async def get_feedback_service() -> BetFeedbackService:
    """Get or create feedback service singleton"""
    global _feedback_service
    
    if _feedback_service is None:
        _feedback_service = BetFeedbackService()
    
    return _feedback_service
