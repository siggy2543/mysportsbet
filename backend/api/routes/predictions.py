"""
Prediction API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from datetime import datetime, date

router = APIRouter()

@router.get("/predictions/{game_id}")
async def get_game_prediction(game_id: str) -> Dict:
    """Get AI prediction for a specific game"""
    return {
        "game_id": game_id,
        "predictions": {
            "home_win_probability": 0.65,
            "away_win_probability": 0.35,
            "recommended_bet": "home",
            "confidence_score": 0.78
        },
        "factors": [
            "Home team has won 8 of last 10 games",
            "Away team missing key players",
            "Weather conditions favor home team"
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/predictions")
async def get_daily_predictions(date_filter: date = None) -> List[Dict]:
    """Get predictions for all games on a specific date"""
    return [
        {
            "game_id": "game_1",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "prediction": {
                "home_win_probability": 0.65,
                "away_win_probability": 0.35,
                "recommended_bet": "home"
            }
        }
    ]

@router.get("/model/accuracy")
async def get_model_accuracy() -> Dict:
    """Get current prediction model accuracy statistics"""
    return {
        "overall_accuracy": 0.68,
        "last_30_days_accuracy": 0.72,
        "total_predictions": 2500,
        "correct_predictions": 1700,
        "model_version": "2.1.0",
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/trends/{sport}")
async def get_sport_trends(sport: str) -> Dict:
    """Get betting trends for a specific sport"""
    return {
        "sport": sport,
        "trends": {
            "home_team_win_rate": 0.58,
            "over_hit_rate": 0.52,
            "favorite_cover_rate": 0.48
        },
        "hot_teams": ["Lakers", "Celtics"],
        "cold_teams": ["Pistons", "Rockets"]
    }