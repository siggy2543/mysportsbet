"""
Sports data API routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime, date

router = APIRouter()

@router.get("/games")
async def get_games(sport: Optional[str] = None, date_filter: Optional[date] = None) -> List[Dict]:
    """Get available games"""
    # Placeholder implementation
    return [
        {
            "id": "game_1",
            "home_team": "Lakers",
            "away_team": "Warriors", 
            "game_date": datetime.utcnow().isoformat(),
            "sport": "NBA",
            "status": "scheduled",
            "odds": {
                "home": -110,
                "away": +105
            }
        }
    ]

@router.get("/games/{game_id}")
async def get_game_details(game_id: str) -> Dict:
    """Get detailed information about a specific game"""
    return {
        "id": game_id,
        "home_team": "Lakers",
        "away_team": "Warriors",
        "game_date": datetime.utcnow().isoformat(),
        "sport": "NBA",
        "status": "scheduled",
        "odds": {
            "home": -110,
            "away": +105,
            "over_under": 215.5
        },
        "statistics": {
            "home_record": "25-15",
            "away_record": "20-20"
        }
    }

@router.get("/sports")
async def get_available_sports() -> List[str]:
    """Get list of available sports"""
    return ["NBA", "NFL", "MLB", "NHL", "Soccer"]

@router.get("/odds/{game_id}")
async def get_game_odds(game_id: str) -> Dict:
    """Get current odds for a specific game"""
    return {
        "game_id": game_id,
        "moneyline": {
            "home": -110,
            "away": +105
        },
        "spread": {
            "home": -2.5,
            "away": +2.5
        },
        "over_under": 215.5,
        "last_updated": datetime.utcnow().isoformat()
    }