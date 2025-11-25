"""
AI Learning Service - Adaptive Intelligence System
Tracks predictions, learns from outcomes, and improves accuracy over time
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncpg
import json
import os

logger = logging.getLogger(__name__)

# Global service instance
_learning_service_instance: Optional['AILearningService'] = None

async def get_learning_service() -> 'AILearningService':
    """Get or create the global AI learning service instance"""
    global _learning_service_instance
    
    if _learning_service_instance is None:
        _learning_service_instance = AILearningService()
        await _learning_service_instance.initialize()
    
    return _learning_service_instance

@dataclass
class PredictionRecord:
    sport: str
    home_team: str
    away_team: str
    game_start_time: datetime
    prediction_type: str
    predicted_winner: str
    confidence_score: float
    ai_reasoning: str
    odds_snapshot: Dict
    game_id: Optional[str] = None

@dataclass
class PredictionOutcome:
    prediction_id: int
    actual_winner: str
    was_correct: bool
    profit_loss: Optional[float] = None

class AILearningService:
    """Service for tracking predictions and improving AI accuracy through learning"""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("✅ AI Learning Service initialized with database connection")
            
            # Run initial calibration check
            await self._check_and_initialize_calibration()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Learning Service: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("🔒 AI Learning Service connections closed")
    
    async def _check_and_initialize_calibration(self):
        """Check if calibration data exists, initialize if needed"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM confidence_calibration"
            )
            if count == 0:
                logger.info("Initializing confidence calibration data...")
                sports = ['NBA', 'NFL', 'EPL', 'MMA', 'MLB', 'NHL']
                buckets = ['80-100', '70-80', '60-70', '50-60', '0-50']
                
                for sport in sports:
                    for bucket in buckets:
                        await conn.execute('''
                            INSERT INTO confidence_calibration 
                            (sport, confidence_bucket, adjustment_factor)
                            VALUES ($1, $2, 1.0)
                            ON CONFLICT (sport, confidence_bucket) DO NOTHING
                        ''', sport, bucket)
    
    async def store_prediction(self, prediction: PredictionRecord) -> int:
        """Store a new prediction for future learning"""
        try:
            async with self.pool.acquire() as conn:
                prediction_id = await conn.fetchval('''
                    INSERT INTO predictions_history (
                        sport, game_id, home_team, away_team, game_start_time,
                        prediction_type, predicted_winner, confidence_score,
                        ai_reasoning, odds_at_prediction
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING id
                ''', 
                    prediction.sport,
                    prediction.game_id,
                    prediction.home_team,
                    prediction.away_team,
                    prediction.game_start_time,
                    prediction.prediction_type,
                    prediction.predicted_winner,
                    prediction.confidence_score,
                    prediction.ai_reasoning,
                    json.dumps(prediction.odds_snapshot)
                )
                
                logger.info(f"📝 Stored prediction {prediction_id} for {prediction.sport}: {prediction.home_team} vs {prediction.away_team}")
                return prediction_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store prediction: {e}")
            return None
    
    async def store_parlay_prediction(self, sport: str, legs: List[Dict], 
                                     total_confidence: float, payout_multiplier: float) -> int:
        """Store a parlay prediction for future tracking"""
        try:
            async with self.pool.acquire() as conn:
                parlay_id = await conn.fetchval('''
                    INSERT INTO parlay_history (
                        sport, num_legs, total_confidence, payout_multiplier, legs
                    ) VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                ''',
                    sport,
                    len(legs),
                    total_confidence,
                    payout_multiplier,
                    json.dumps(legs)
                )
                
                logger.info(f"📝 Stored {len(legs)}-leg parlay {parlay_id} for {sport}")
                return parlay_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store parlay: {e}")
            return None
    
    async def update_prediction_outcome(self, outcome: PredictionOutcome):
        """Update prediction with actual outcome for learning"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    UPDATE predictions_history
                    SET actual_outcome = $1,
                        was_correct = $2,
                        profit_loss = $3,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $4
                ''',
                    outcome.actual_winner,
                    outcome.was_correct,
                    outcome.profit_loss,
                    outcome.prediction_id
                )
                
                # Update team-specific history
                await self._update_team_history(outcome.prediction_id, outcome.was_correct, conn)
                
                # Update calibration data
                await self._update_confidence_calibration(outcome.prediction_id, outcome.was_correct, conn)
                
                logger.info(f"✅ Updated prediction {outcome.prediction_id} outcome: {'Correct' if outcome.was_correct else 'Incorrect'}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update prediction outcome: {e}")
    
    async def _update_team_history(self, prediction_id: int, was_correct: bool, conn):
        """Update team-specific prediction accuracy"""
        try:
            # Get prediction details
            pred = await conn.fetchrow('''
                SELECT sport, home_team, away_team, predicted_winner, confidence_score
                FROM predictions_history WHERE id = $1
            ''', prediction_id)
            
            if not pred:
                return
            
            # Update both teams' history
            for team in [pred['home_team'], pred['away_team']]:
                is_favorite = (team == pred['predicted_winner'])
                
                await conn.execute('''
                    INSERT INTO team_prediction_history (
                        sport, team_name, total_predictions, correct_predictions,
                        as_favorite_accuracy, as_underdog_accuracy
                    ) VALUES ($1, $2, 1, $3, $4, $5)
                    ON CONFLICT (sport, team_name) DO UPDATE SET
                        total_predictions = team_prediction_history.total_predictions + 1,
                        correct_predictions = team_prediction_history.correct_predictions + $3,
                        accuracy_rate = (team_prediction_history.correct_predictions + $3)::DECIMAL / 
                                       (team_prediction_history.total_predictions + 1) * 100,
                        last_updated = CURRENT_TIMESTAMP
                ''',
                    pred['sport'],
                    team,
                    1 if (is_favorite and was_correct) or (not is_favorite and not was_correct) else 0,
                    100.0 if (is_favorite and was_correct) else 0.0,
                    100.0 if (not is_favorite and not was_correct) else 0.0
                )
                
        except Exception as e:
            logger.error(f"Failed to update team history: {e}")
    
    async def _update_confidence_calibration(self, prediction_id: int, was_correct: bool, conn):
        """Update confidence calibration based on actual outcomes"""
        try:
            # Get prediction confidence
            pred = await conn.fetchrow('''
                SELECT sport, confidence_score FROM predictions_history WHERE id = $1
            ''', prediction_id)
            
            if not pred:
                return
            
            # Determine bucket
            confidence = float(pred['confidence_score'])
            if confidence >= 80:
                bucket = '80-100'
            elif confidence >= 70:
                bucket = '70-80'
            elif confidence >= 60:
                bucket = '60-70'
            elif confidence >= 50:
                bucket = '50-60'
            else:
                bucket = '0-50'
            
            # Update calibration
            await conn.execute('''
                UPDATE confidence_calibration SET
                    total_predictions = total_predictions + 1,
                    correct_predictions = correct_predictions + $1,
                    actual_accuracy = (correct_predictions + $1)::DECIMAL / (total_predictions + 1) * 100,
                    adjustment_factor = CASE 
                        WHEN (total_predictions + 1) >= 10 THEN
                            ((correct_predictions + $1)::DECIMAL / (total_predictions + 1)) / 
                            (($2 + $3) / 2 / 100)
                        ELSE adjustment_factor
                    END,
                    last_updated = CURRENT_TIMESTAMP
                WHERE sport = $4 AND confidence_bucket = $5
            ''',
                1 if was_correct else 0,
                confidence - 5,  # Lower bound of expected accuracy
                confidence + 5,  # Upper bound of expected accuracy
                pred['sport'],
                bucket
            )
            
        except Exception as e:
            logger.error(f"Failed to update confidence calibration: {e}")
    
    async def get_calibrated_confidence(self, sport: str, original_confidence: float) -> float:
        """Get calibrated confidence score based on historical accuracy"""
        try:
            async with self.pool.acquire() as conn:
                calibrated = await conn.fetchval(
                    'SELECT get_calibrated_confidence($1, $2)',
                    sport, original_confidence
                )
                
                if calibrated is not None:
                    logger.info(f"🎯 Calibrated confidence for {sport}: {original_confidence}% → {calibrated}%")
                    return float(calibrated)
                
                return original_confidence
                
        except Exception as e:
            logger.error(f"Failed to get calibrated confidence: {e}")
            return original_confidence
    
    async def get_performance_metrics(self, sport: Optional[str] = None, 
                                     days: int = 30) -> Dict[str, Any]:
        """Get AI performance metrics for analysis"""
        try:
            async with self.pool.acquire() as conn:
                if sport:
                    metrics = await conn.fetchrow('''
                        SELECT 
                            sport,
                            COUNT(*) as total_predictions,
                            COUNT(*) FILTER (WHERE was_correct = TRUE) as correct_predictions,
                            ROUND((COUNT(*) FILTER (WHERE was_correct = TRUE)::DECIMAL / 
                                   NULLIF(COUNT(*), 0) * 100), 2) as accuracy_rate,
                            ROUND(AVG(confidence_score), 2) as avg_confidence,
                            ROUND(SUM(COALESCE(profit_loss, 0)), 2) as total_profit_loss
                        FROM predictions_history
                        WHERE sport = $1 
                        AND was_correct IS NOT NULL
                        AND prediction_date >= CURRENT_DATE - $2::INTEGER
                        GROUP BY sport
                    ''', sport, days)
                else:
                    metrics = await conn.fetch('''
                        SELECT * FROM ai_performance_overview
                    ''')
                
                return dict(metrics) if metrics else {}
                
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    async def get_learning_insights(self, sport: str) -> List[Dict[str, Any]]:
        """Get AI-generated insights from historical data analysis"""
        try:
            async with self.pool.acquire() as conn:
                insights = await conn.fetch('''
                    SELECT insight_type, insight_text, confidence_impact, validation_count
                    FROM learning_insights
                    WHERE sport = $1 AND is_active = TRUE
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ORDER BY validation_count DESC, created_at DESC
                    LIMIT 10
                ''', sport)
                
                return [dict(insight) for insight in insights]
                
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return []
    
    async def generate_learning_insights(self, sport: str):
        """Analyze historical data and generate new insights"""
        try:
            async with self.pool.acquire() as conn:
                # Find patterns in successful predictions
                patterns = await conn.fetch('''
                    SELECT 
                        prediction_type,
                        CASE 
                            WHEN confidence_score >= 70 THEN 'high'
                            WHEN confidence_score >= 60 THEN 'medium'
                            ELSE 'low'
                        END as confidence_level,
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE was_correct = TRUE) as correct,
                        ROUND((COUNT(*) FILTER (WHERE was_correct = TRUE)::DECIMAL / 
                               COUNT(*) * 100), 2) as accuracy
                    FROM predictions_history
                    WHERE sport = $1 
                    AND was_correct IS NOT NULL
                    AND prediction_date >= CURRENT_DATE - 30
                    GROUP BY prediction_type, confidence_level
                    HAVING COUNT(*) >= 5
                    ORDER BY accuracy DESC
                ''', sport)
                
                # Generate insights from patterns
                for pattern in patterns:
                    if float(pattern['accuracy']) > 70:
                        insight_text = f"{pattern['prediction_type'].title()} predictions with {pattern['confidence_level']} confidence have {pattern['accuracy']}% accuracy"
                        
                        await conn.execute('''
                            INSERT INTO learning_insights (
                                sport, insight_type, insight_text, confidence_impact, validation_count
                            ) VALUES ($1, 'pattern', $2, $3, $4)
                            ON CONFLICT DO NOTHING
                        ''',
                            sport,
                            insight_text,
                            float(pattern['accuracy']) / 100.0,
                            int(pattern['correct'])
                        )
                
                logger.info(f"🧠 Generated {len(patterns)} learning insights for {sport}")
                
        except Exception as e:
            logger.error(f"Failed to generate learning insights: {e}")
    
    async def update_daily_metrics(self, sport: str, date: datetime.date = None):
        """Update daily AI performance metrics"""
        try:
            if date is None:
                date = datetime.now().date()
            
            async with self.pool.acquire() as conn:
                await conn.execute(
                    'SELECT update_daily_ai_metrics($1, $2)',
                    sport, date
                )
                
                logger.info(f"📊 Updated daily metrics for {sport} on {date}")
                
        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}")

# Global instance
_learning_service = None

async def get_learning_service() -> AILearningService:
    """Get or create the global AI learning service instance"""
    global _learning_service
    if _learning_service is None:
        _learning_service = AILearningService()
        await _learning_service.initialize()
    return _learning_service
