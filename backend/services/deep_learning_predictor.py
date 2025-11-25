"""
Deep Learning Prediction Engine
Advanced neural networks for sports betting predictions
Uses LSTM, Transformer, and ensemble deep learning models
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import asyncio
import pickle
import os

logger = logging.getLogger(__name__)

# Try to import deep learning libraries
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Attention
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TF_AVAILABLE = True
except ImportError:
    logger.warning("TensorFlow not available, using fallback predictions")
    TF_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    logger.warning("Scikit-learn/XGBoost not available")
    ML_AVAILABLE = False


@dataclass
class PredictionFeatures:
    """Features used for deep learning prediction"""
    # Team metrics
    home_win_rate: float
    away_win_rate: float
    home_points_avg: float
    away_points_avg: float
    home_points_allowed_avg: float
    away_points_allowed_avg: float
    
    # Recent form (last 5 games)
    home_recent_wins: int
    away_recent_wins: int
    home_winning_streak: int
    away_winning_streak: int
    
    # Advanced metrics
    home_strength_score: float
    away_strength_score: float
    injury_impact_home: float
    injury_impact_away: float
    news_sentiment_home: float
    news_sentiment_away: float
    
    # Market data
    home_odds: float
    away_odds: float
    public_betting_pct: float
    market_inefficiency: float
    
    # Contextual
    home_field_advantage: float
    days_rest_home: int
    days_rest_away: int
    season_factor: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for model input"""
        return np.array([
            self.home_win_rate, self.away_win_rate,
            self.home_points_avg, self.away_points_avg,
            self.home_points_allowed_avg, self.away_points_allowed_avg,
            self.home_recent_wins, self.away_recent_wins,
            self.home_winning_streak, self.away_winning_streak,
            self.home_strength_score, self.away_strength_score,
            self.injury_impact_home, self.injury_impact_away,
            self.news_sentiment_home, self.news_sentiment_away,
            self.home_odds, self.away_odds,
            self.public_betting_pct, self.market_inefficiency,
            self.home_field_advantage, self.days_rest_home, self.days_rest_away,
            self.season_factor
        ])


@dataclass
class DeepLearningPrediction:
    """Deep learning prediction result"""
    home_win_probability: float
    away_win_probability: float
    confidence: float
    expected_margin: float
    model_ensemble_agreement: float
    lstm_prediction: float
    xgboost_prediction: float
    rf_prediction: float
    features_used: PredictionFeatures


class DeepLearningPredictor:
    """
    Advanced deep learning predictor using multiple neural network architectures
    
    Models:
    1. LSTM for time-series patterns
    2. Dense neural network for feature relationships
    3. XGBoost for gradient boosting
    4. Random Forest for ensemble
    5. Ensemble meta-model combining all
    """
    
    def __init__(self, models_dir: str = "/app/models"):
        self.models_dir = models_dir
        self.lstm_model = None
        self.dense_model = None
        self.xgb_model = None
        self.rf_model = None
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.models_trained = False
        
        # Create models directory
        os.makedirs(models_dir, exist_ok=True)
        
        # Load pre-trained models if available
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models from disk"""
        try:
            if TF_AVAILABLE:
                lstm_path = os.path.join(self.models_dir, "lstm_model.h5")
                dense_path = os.path.join(self.models_dir, "dense_model.h5")
                
                if os.path.exists(lstm_path):
                    self.lstm_model = keras.models.load_model(lstm_path)
                    logger.info("Loaded pre-trained LSTM model")
                
                if os.path.exists(dense_path):
                    self.dense_model = keras.models.load_model(dense_path)
                    logger.info("Loaded pre-trained Dense model")
            
            if ML_AVAILABLE:
                xgb_path = os.path.join(self.models_dir, "xgb_model.pkl")
                rf_path = os.path.join(self.models_dir, "rf_model.pkl")
                scaler_path = os.path.join(self.models_dir, "scaler.pkl")
                
                if os.path.exists(xgb_path):
                    with open(xgb_path, 'rb') as f:
                        self.xgb_model = pickle.load(f)
                    logger.info("Loaded pre-trained XGBoost model")
                
                if os.path.exists(rf_path):
                    with open(rf_path, 'rb') as f:
                        self.rf_model = pickle.load(f)
                    logger.info("Loaded pre-trained RandomForest model")
                
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    logger.info("Loaded feature scaler")
            
            self.models_trained = True
            
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
    
    def _build_lstm_model(self, input_shape: Tuple[int, int]) -> Model:
        """Build LSTM model for time-series prediction"""
        if not TF_AVAILABLE:
            return None
        
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.3),
            BatchNormalization(),
            LSTM(64, return_sequences=True),
            Dropout(0.3),
            BatchNormalization(),
            LSTM(32),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return model
    
    def _build_dense_model(self, input_dim: int) -> Model:
        """Build dense neural network"""
        if not TF_AVAILABLE:
            return None
        
        model = Sequential([
            Dense(128, activation='relu', input_dim=input_dim),
            BatchNormalization(),
            Dropout(0.4),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        return model
    
    async def train_models(self, training_data: pd.DataFrame, 
                          labels: np.ndarray, epochs: int = 50):
        """
        Train all models on historical data
        
        Args:
            training_data: DataFrame with features
            labels: Binary labels (1 = home win, 0 = away win)
            epochs: Number of training epochs
        """
        logger.info(f"Training deep learning models on {len(training_data)} samples...")
        
        # Prepare data
        X = training_data.values
        y = labels
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train LSTM (requires 3D input)
        if TF_AVAILABLE and self.lstm_model is None:
            logger.info("Training LSTM model...")
            X_train_3d = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
            X_val_3d = X_val.reshape((X_val.shape[0], 1, X_val.shape[1]))
            
            self.lstm_model = self._build_lstm_model((1, X_train.shape[1]))
            
            early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            
            self.lstm_model.fit(
                X_train_3d, y_train,
                validation_data=(X_val_3d, y_val),
                epochs=epochs,
                batch_size=32,
                callbacks=[early_stop],
                verbose=0
            )
            
            # Save model
            self.lstm_model.save(os.path.join(self.models_dir, "lstm_model.h5"))
            logger.info("LSTM model trained and saved")
        
        # Train Dense model
        if TF_AVAILABLE and self.dense_model is None:
            logger.info("Training Dense neural network...")
            self.dense_model = self._build_dense_model(X_train.shape[1])
            
            early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            
            self.dense_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=32,
                callbacks=[early_stop],
                verbose=0
            )
            
            self.dense_model.save(os.path.join(self.models_dir, "dense_model.h5"))
            logger.info("Dense model trained and saved")
        
        # Train XGBoost
        if ML_AVAILABLE and self.xgb_model is None:
            logger.info("Training XGBoost model...")
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=7,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            self.xgb_model.fit(X_train, y_train)
            
            with open(os.path.join(self.models_dir, "xgb_model.pkl"), 'wb') as f:
                pickle.dump(self.xgb_model, f)
            logger.info("XGBoost model trained and saved")
        
        # Train Random Forest
        if ML_AVAILABLE and self.rf_model is None:
            logger.info("Training Random Forest...")
            self.rf_model = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            self.rf_model.fit(X_train, y_train)
            
            with open(os.path.join(self.models_dir, "rf_model.pkl"), 'wb') as f:
                pickle.dump(self.rf_model, f)
            logger.info("Random Forest trained and saved")
        
        # Save scaler
        with open(os.path.join(self.models_dir, "scaler.pkl"), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        self.models_trained = True
        logger.info("All models trained successfully!")
    
    async def predict(self, features: PredictionFeatures) -> DeepLearningPrediction:
        """
        Make prediction using ensemble of deep learning models
        
        Args:
            features: PredictionFeatures object
            
        Returns:
            DeepLearningPrediction with ensemble results
        """
        if not self.models_trained:
            logger.warning("Models not trained, using fallback prediction")
            return self._fallback_prediction(features)
        
        # Prepare input
        X = features.to_array().reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        predictions = []
        
        # LSTM prediction
        lstm_pred = 0.5
        if TF_AVAILABLE and self.lstm_model is not None:
            X_3d = X_scaled.reshape((1, 1, X_scaled.shape[1]))
            lstm_pred = float(self.lstm_model.predict(X_3d, verbose=0)[0][0])
            predictions.append(lstm_pred)
        
        # Dense model prediction
        dense_pred = 0.5
        if TF_AVAILABLE and self.dense_model is not None:
            dense_pred = float(self.dense_model.predict(X_scaled, verbose=0)[0][0])
            predictions.append(dense_pred)
        
        # XGBoost prediction
        xgb_pred = 0.5
        if ML_AVAILABLE and self.xgb_model is not None:
            xgb_pred = float(self.xgb_model.predict_proba(X_scaled)[0][1])
            predictions.append(xgb_pred)
        
        # Random Forest prediction
        rf_pred = 0.5
        if ML_AVAILABLE and self.rf_model is not None:
            rf_pred = float(self.rf_model.predict(X_scaled)[0])
            predictions.append(rf_pred)
        
        # Ensemble prediction (weighted average)
        if predictions:
            # Weight: LSTM=30%, Dense=25%, XGBoost=25%, RF=20%
            weights = [0.30, 0.25, 0.25, 0.20][:len(predictions)]
            weights = np.array(weights) / sum(weights)  # Normalize
            
            home_win_prob = float(np.average(predictions, weights=weights))
        else:
            home_win_prob = 0.5
        
        away_win_prob = 1.0 - home_win_prob
        
        # Calculate confidence (agreement between models)
        if len(predictions) > 1:
            model_agreement = 1.0 - np.std(predictions)
        else:
            model_agreement = 0.5
        
        # Overall confidence
        confidence = max(home_win_prob, away_win_prob) * model_agreement * 100
        
        # Expected margin (simplified)
        expected_margin = (home_win_prob - 0.5) * 20  # Scale to points
        
        return DeepLearningPrediction(
            home_win_probability=home_win_prob,
            away_win_probability=away_win_prob,
            confidence=confidence,
            expected_margin=expected_margin,
            model_ensemble_agreement=model_agreement,
            lstm_prediction=lstm_pred,
            xgboost_prediction=xgb_pred,
            rf_prediction=rf_pred,
            features_used=features
        )
    
    def _fallback_prediction(self, features: PredictionFeatures) -> DeepLearningPrediction:
        """Fallback prediction when models not available"""
        # Simple heuristic based on features
        home_score = (
            features.home_win_rate * 0.3 +
            features.home_strength_score / 100 * 0.3 +
            features.home_recent_wins / 5 * 0.2 +
            features.home_field_advantage / 10 * 0.2
        )
        
        away_score = (
            features.away_win_rate * 0.3 +
            features.away_strength_score / 100 * 0.3 +
            features.away_recent_wins / 5 * 0.2
        )
        
        total = home_score + away_score
        home_win_prob = home_score / total if total > 0 else 0.5
        away_win_prob = 1.0 - home_win_prob
        
        confidence = max(home_win_prob, away_win_prob) * 80
        
        return DeepLearningPrediction(
            home_win_probability=home_win_prob,
            away_win_probability=away_win_prob,
            confidence=confidence,
            expected_margin=(home_win_prob - 0.5) * 15,
            model_ensemble_agreement=0.5,
            lstm_prediction=home_win_prob,
            xgboost_prediction=home_win_prob,
            rf_prediction=home_win_prob,
            features_used=features
        )
    
    async def evaluate_models(self, test_data: pd.DataFrame, 
                             test_labels: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        if not self.models_trained:
            return {"error": "Models not trained"}
        
        X_test = self.scaler.transform(test_data.values)
        
        results = {}
        
        # LSTM
        if TF_AVAILABLE and self.lstm_model is not None:
            X_test_3d = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
            lstm_loss, lstm_acc, lstm_auc = self.lstm_model.evaluate(
                X_test_3d, test_labels, verbose=0
            )
            results['lstm_accuracy'] = lstm_acc
            results['lstm_auc'] = lstm_auc
        
        # Dense
        if TF_AVAILABLE and self.dense_model is not None:
            dense_loss, dense_acc, dense_auc = self.dense_model.evaluate(
                X_test, test_labels, verbose=0
            )
            results['dense_accuracy'] = dense_acc
            results['dense_auc'] = dense_auc
        
        # XGBoost
        if ML_AVAILABLE and self.xgb_model is not None:
            xgb_acc = self.xgb_model.score(X_test, test_labels)
            results['xgboost_accuracy'] = xgb_acc
        
        # Random Forest
        if ML_AVAILABLE and self.rf_model is not None:
            rf_acc = self.rf_model.score(X_test, test_labels)
            results['rf_accuracy'] = rf_acc
        
        return results


# Singleton instance
_dl_predictor = None


async def get_deep_learning_predictor() -> DeepLearningPredictor:
    """Get or create deep learning predictor singleton"""
    global _dl_predictor
    
    if _dl_predictor is None:
        _dl_predictor = DeepLearningPredictor()
    
    return _dl_predictor
