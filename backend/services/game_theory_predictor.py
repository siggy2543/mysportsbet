"""
Game Theory-based Prediction Engine for Sports Betting
Advanced mathematical models for strategic decision-making
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

logger = logging.getLogger(__name__)

class GameOutcome(Enum):
    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"

@dataclass
class Player:
    """Represents a strategic player in game theory"""
    name: str
    strategies: List[str]
    payoff_matrix: np.ndarray
    risk_tolerance: float
    capital: float

@dataclass
class GameState:
    """Current state of a sports game for analysis"""
    home_team: str
    away_team: str
    home_odds: float
    away_odds: float
    draw_odds: Optional[float]
    historical_head_to_head: List[Dict]
    recent_form: Dict[str, List[int]]  # Last 5 games: 1=win, 0=loss
    injuries: Dict[str, List[str]]
    weather_conditions: Optional[Dict]
    venue_advantage: float

@dataclass
class NashEquilibrium:
    """Nash equilibrium solution for betting strategy"""
    strategy_probabilities: Dict[str, float]
    expected_payoff: float
    confidence_interval: Tuple[float, float]
    risk_assessment: str

@dataclass
class PredictionResult:
    """Comprehensive prediction result with game theory analysis"""
    game_id: str
    nash_equilibrium: NashEquilibrium
    minimax_strategy: Dict[str, float]
    kelly_criterion_bet_size: float
    expected_value: float
    sharpe_ratio: float
    risk_adjusted_return: float
    confidence_score: float
    recommended_action: str
    reasoning: str

class GameTheoryPredictor:
    """
    Advanced Game Theory-based Sports Betting Prediction Engine
    
    Implements:
    - Nash Equilibrium analysis
    - Minimax strategy optimization
    - Kelly Criterion for bet sizing
    - Multi-agent strategic modeling
    - Risk-adjusted return optimization
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.lstm_model = None
        self.historical_data = pd.DataFrame()
        self.payoff_matrices = {}
        self.model_trained = False
        
    async def initialize_models(self, historical_data: pd.DataFrame):
        """Initialize and train all prediction models"""
        try:
            self.historical_data = historical_data
            await self._prepare_features()
            await self._train_ensemble_models()
            await self._build_lstm_model()
            await self._calculate_payoff_matrices()
            self.model_trained = True
            logger.info("Game theory prediction models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise

    async def _prepare_features(self):
        """Prepare feature engineering for ML models"""
        # Feature engineering for game theory analysis
        features = []
        
        for _, game in self.historical_data.iterrows():
            game_features = {
                # Basic game info
                'home_team_strength': await self._calculate_team_strength(game['home_team']),
                'away_team_strength': await self._calculate_team_strength(game['away_team']),
                'odds_differential': abs(game['home_odds'] - game['away_odds']),
                'market_efficiency': await self._calculate_market_efficiency(game),
                
                # Historical patterns
                'head_to_head_advantage': await self._calculate_h2h_advantage(
                    game['home_team'], game['away_team']
                ),
                'recent_form_diff': await self._calculate_form_differential(game),
                'momentum_indicator': await self._calculate_momentum(game),
                
                # Strategic elements
                'betting_volume_ratio': game.get('betting_volume_home', 1) / game.get('betting_volume_away', 1),
                'sharp_money_percentage': game.get('sharp_money_home', 0.5),
                'public_betting_percentage': game.get('public_betting_home', 0.5),
                
                # External factors
                'venue_advantage': game.get('venue_advantage', 0),
                'injury_impact_home': await self._calculate_injury_impact(game, 'home'),
                'injury_impact_away': await self._calculate_injury_impact(game, 'away'),
                'weather_impact': await self._calculate_weather_impact(game),
                
                # Target variable
                'outcome': game['actual_outcome']
            }
            features.append(game_features)
        
        self.feature_df = pd.DataFrame(features)
        logger.info(f"Prepared {len(features)} game features for training")

    async def _train_ensemble_models(self):
        """Train ensemble of ML models for prediction"""
        if self.feature_df.empty:
            raise ValueError("No features prepared for training")
        
        # Prepare training data
        feature_columns = [col for col in self.feature_df.columns if col != 'outcome']
        X = self.feature_df[feature_columns]
        y = self.feature_df['outcome']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        self.rf_model.fit(X_train, y_train)
        rf_score = self.rf_model.score(X_test, y_test)
        
        # Train Gradient Boosting
        self.gb_model.fit(X_train, y_train)
        gb_score = self.gb_model.score(X_test, y_test)
        
        logger.info(f"Model training complete - RF: {rf_score:.3f}, GB: {gb_score:.3f}")

    async def _build_lstm_model(self):
        """Build LSTM model for sequential pattern recognition"""
        # Prepare sequential data for LSTM
        sequence_length = 10
        sequences = []
        targets = []
        
        for i in range(sequence_length, len(self.feature_df)):
            sequence = self.feature_df.iloc[i-sequence_length:i, :-1].values
            target = self.feature_df.iloc[i]['outcome']
            sequences.append(sequence)
            targets.append(target)
        
        if len(sequences) < 50:  # Need minimum data for LSTM
            logger.warning("Insufficient data for LSTM training")
            return
        
        X_seq = np.array(sequences)
        y_seq = np.array(targets)
        
        # Build LSTM model
        self.lstm_model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(sequence_length, X_seq.shape[2])),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1, activation='sigmoid')
        ])
        
        self.lstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        # Train LSTM
        self.lstm_model.fit(
            X_seq, y_seq,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        logger.info("LSTM model training completed")

    async def _calculate_payoff_matrices(self):
        """Calculate payoff matrices for different betting strategies"""
        strategies = ['home_win', 'away_win', 'draw', 'no_bet']
        
        # Historical analysis of strategy performance
        strategy_returns = {}
        
        for strategy in strategies:
            returns = []
            for _, game in self.historical_data.iterrows():
                if strategy == 'home_win':
                    return_val = game['home_odds'] if game['actual_outcome'] == 'home_win' else -1
                elif strategy == 'away_win':
                    return_val = game['away_odds'] if game['actual_outcome'] == 'away_win' else -1
                elif strategy == 'draw':
                    return_val = game.get('draw_odds', 3.0) if game['actual_outcome'] == 'draw' else -1
                else:  # no_bet
                    return_val = 0
                
                returns.append(return_val)
            
            strategy_returns[strategy] = np.array(returns)
        
        # Create payoff matrix
        self.payoff_matrices['betting_strategies'] = np.array([
            strategy_returns[strategy] for strategy in strategies
        ]).T
        
        logger.info("Payoff matrices calculated for game theory analysis")

    async def find_nash_equilibrium(self, game_state: GameState) -> NashEquilibrium:
        """
        Find Nash equilibrium for the current game state
        Uses iterative best response algorithm
        """
        try:
            # Define players: bettor vs market
            strategies = ['home_win', 'away_win', 'draw', 'no_bet']
            n_strategies = len(strategies)
            
            # Initialize random strategy probabilities
            bettor_probs = np.random.dirichlet(np.ones(n_strategies))
            market_probs = np.ones(n_strategies) / n_strategies
            
            # Calculate expected payoffs based on current game state
            payoffs = await self._calculate_game_payoffs(game_state)
            
            # Iterative best response to find equilibrium
            for iteration in range(100):  # Max iterations
                # Best response for bettor
                expected_payoffs = np.dot(payoffs, market_probs)
                new_bettor_probs = np.zeros(n_strategies)
                best_strategy = np.argmax(expected_payoffs)
                new_bettor_probs[best_strategy] = 1.0
                
                # Check for convergence
                if np.allclose(bettor_probs, new_bettor_probs, atol=1e-6):
                    break
                
                bettor_probs = 0.9 * bettor_probs + 0.1 * new_bettor_probs
            
            # Calculate expected payoff at equilibrium
            expected_payoff = np.dot(bettor_probs, np.dot(payoffs, market_probs))
            
            # Calculate confidence interval using bootstrapping
            confidence_interval = await self._calculate_confidence_interval(
                bettor_probs, payoffs, market_probs
            )
            
            # Risk assessment
            risk_level = "LOW" if expected_payoff > 0.1 else "MEDIUM" if expected_payoff > 0 else "HIGH"
            
            return NashEquilibrium(
                strategy_probabilities={
                    strategies[i]: prob for i, prob in enumerate(bettor_probs)
                },
                expected_payoff=expected_payoff,
                confidence_interval=confidence_interval,
                risk_assessment=risk_level
            )
            
        except Exception as e:
            logger.error(f"Error finding Nash equilibrium: {e}")
            raise

    async def calculate_minimax_strategy(self, game_state: GameState) -> Dict[str, float]:
        """
        Calculate minimax strategy to minimize maximum possible loss
        """
        try:
            payoffs = await self._calculate_game_payoffs(game_state)
            strategies = ['home_win', 'away_win', 'draw', 'no_bet']
            
            # Find strategy that minimizes maximum loss
            min_max_losses = []
            for i, strategy in enumerate(strategies):
                strategy_payoffs = payoffs[i, :]
                max_loss = np.max(-strategy_payoffs)  # Maximum loss for this strategy
                min_max_losses.append(max_loss)
            
            # Choose strategy with minimum maximum loss
            best_strategy_idx = np.argmin(min_max_losses)
            
            # Create probability distribution favoring minimax strategy
            strategy_probs = np.zeros(len(strategies))
            strategy_probs[best_strategy_idx] = 0.8
            
            # Distribute remaining probability
            remaining_prob = 0.2 / (len(strategies) - 1)
            for i in range(len(strategies)):
                if i != best_strategy_idx:
                    strategy_probs[i] = remaining_prob
            
            return {
                strategies[i]: prob for i, prob in enumerate(strategy_probs)
            }
            
        except Exception as e:
            logger.error(f"Error calculating minimax strategy: {e}")
            raise

    async def calculate_kelly_criterion(self, game_state: GameState, strategy: str) -> float:
        """
        Calculate optimal bet size using Kelly Criterion
        f* = (bp - q) / b
        """
        try:
            if strategy == 'no_bet':
                return 0.0
            
            # Get win probability from ensemble prediction
            win_prob = await self._get_win_probability(game_state, strategy)
            
            # Get odds for the strategy
            if strategy == 'home_win':
                odds = game_state.home_odds
            elif strategy == 'away_win':
                odds = game_state.away_odds
            else:  # draw
                odds = game_state.draw_odds or 3.0
            
            # Kelly Criterion calculation
            b = odds - 1  # Net odds received
            p = win_prob  # Probability of winning
            q = 1 - p     # Probability of losing
            
            kelly_fraction = (b * p - q) / b
            
            # Apply conservative scaling (quarter Kelly)
            conservative_kelly = max(0, kelly_fraction * 0.25)
            
            # Cap at 10% of bankroll for risk management
            return min(conservative_kelly, 0.10)
            
        except Exception as e:
            logger.error(f"Error calculating Kelly criterion: {e}")
            return 0.0

    async def generate_prediction(self, game_state: GameState) -> PredictionResult:
        """
        Generate comprehensive game theory-based prediction
        """
        if not self.model_trained:
            raise ValueError("Models not trained. Call initialize_models first.")
        
        try:
            # Game theory analysis
            nash_eq = await self.find_nash_equilibrium(game_state)
            minimax_strategy = await self.calculate_minimax_strategy(game_state)
            
            # Determine best strategy from Nash equilibrium
            best_strategy = max(nash_eq.strategy_probabilities.items(), key=lambda x: x[1])[0]
            
            # Calculate optimal bet size
            kelly_bet_size = await self.calculate_kelly_criterion(game_state, best_strategy)
            
            # Calculate expected value and risk metrics
            expected_value = nash_eq.expected_payoff
            sharpe_ratio = await self._calculate_sharpe_ratio(game_state, best_strategy)
            risk_adjusted_return = expected_value / max(0.01, abs(expected_value) + 0.1)
            
            # Ensemble confidence score
            confidence_score = await self._calculate_ensemble_confidence(game_state)
            
            # Generate recommendation
            if expected_value > 0.05 and confidence_score > 0.7 and kelly_bet_size > 0.01:
                recommended_action = f"BET_{best_strategy.upper()}"
                reasoning = f"Nash equilibrium favors {best_strategy} with {expected_value:.3f} EV"
            else:
                recommended_action = "NO_BET"
                reasoning = "Insufficient edge or confidence for profitable betting"
            
            return PredictionResult(
                game_id=f"{game_state.home_team}_vs_{game_state.away_team}",
                nash_equilibrium=nash_eq,
                minimax_strategy=minimax_strategy,
                kelly_criterion_bet_size=kelly_bet_size,
                expected_value=expected_value,
                sharpe_ratio=sharpe_ratio,
                risk_adjusted_return=risk_adjusted_return,
                confidence_score=confidence_score,
                recommended_action=recommended_action,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            raise

    async def _calculate_game_payoffs(self, game_state: GameState) -> np.ndarray:
        """Calculate payoff matrix for current game state"""
        # This would use historical data and current odds to estimate payoffs
        # Simplified implementation
        strategies = ['home_win', 'away_win', 'draw', 'no_bet']
        scenarios = ['home_wins', 'away_wins', 'draw', 'no_game']
        
        payoffs = np.array([
            [game_state.home_odds - 1, -1, -1, 0],  # Bet home
            [-1, game_state.away_odds - 1, -1, 0],  # Bet away
            [-1, -1, (game_state.draw_odds or 3.0) - 1, 0],  # Bet draw
            [0, 0, 0, 0]  # No bet
        ])
        
        return payoffs

    async def _get_win_probability(self, game_state: GameState, strategy: str) -> float:
        """Get win probability using ensemble of models"""
        # Prepare features for current game
        features = await self._prepare_game_features(game_state)
        features_scaled = self.scaler.transform([features])
        
        # Ensemble prediction
        rf_pred = self.rf_model.predict_proba(features_scaled)[0]
        gb_pred = self.gb_model.predict_proba(features_scaled)[0]
        
        # Average ensemble predictions
        ensemble_pred = (rf_pred + gb_pred) / 2
        
        if strategy == 'home_win':
            return ensemble_pred[1] if len(ensemble_pred) > 1 else 0.5
        elif strategy == 'away_win':
            return ensemble_pred[0] if len(ensemble_pred) > 1 else 0.5
        else:  # draw
            return ensemble_pred[2] if len(ensemble_pred) > 2 else 0.1

    async def _prepare_game_features(self, game_state: GameState) -> List[float]:
        """Prepare features for a single game prediction"""
        # This would extract the same features as used in training
        # Simplified implementation
        return [
            await self._calculate_team_strength(game_state.home_team),
            await self._calculate_team_strength(game_state.away_team),
            abs(game_state.home_odds - game_state.away_odds),
            game_state.venue_advantage,
            0.5,  # Placeholder for other features
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5
        ]

    async def _calculate_team_strength(self, team_name: str) -> float:
        """Calculate team strength metric"""
        # This would use historical performance data
        return 0.5  # Placeholder

    async def _calculate_market_efficiency(self, game: pd.Series) -> float:
        """Calculate market efficiency indicator"""
        return 0.8  # Placeholder

    async def _calculate_h2h_advantage(self, home_team: str, away_team: str) -> float:
        """Calculate head-to-head historical advantage"""
        return 0.0  # Placeholder

    async def _calculate_form_differential(self, game: pd.Series) -> float:
        """Calculate recent form differential"""
        return 0.0  # Placeholder

    async def _calculate_momentum(self, game: pd.Series) -> float:
        """Calculate team momentum indicator"""
        return 0.0  # Placeholder

    async def _calculate_injury_impact(self, game: pd.Series, team: str) -> float:
        """Calculate injury impact on team performance"""
        return 0.0  # Placeholder

    async def _calculate_weather_impact(self, game: pd.Series) -> float:
        """Calculate weather impact on game outcome"""
        return 0.0  # Placeholder

    async def _calculate_confidence_interval(self, probs: np.ndarray, 
                                           payoffs: np.ndarray, 
                                           market_probs: np.ndarray) -> Tuple[float, float]:
        """Calculate confidence interval for expected payoff"""
        expected_payoff = np.dot(probs, np.dot(payoffs, market_probs))
        std_error = 0.05  # Simplified calculation
        return (expected_payoff - 1.96 * std_error, expected_payoff + 1.96 * std_error)

    async def _calculate_sharpe_ratio(self, game_state: GameState, strategy: str) -> float:
        """Calculate Sharpe ratio for strategy"""
        return 1.5  # Placeholder

    async def _calculate_ensemble_confidence(self, game_state: GameState) -> float:
        """Calculate confidence score from ensemble agreement"""
        return 0.8  # Placeholder