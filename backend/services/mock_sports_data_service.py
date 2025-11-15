"""
Mock Sports Data Service for Testing Live Betting
Provides realistic game data for betting simulation
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)

@dataclass
class MockGame:
    """Mock game data for testing"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    game_time: str
    home_team_record: str
    away_team_record: str
    venue: str
    home_score: int
    away_score: int
    game_status: str
    spread: float
    total: float
    moneyline_home: int
    moneyline_away: int
    predicted_winner: str
    confidence: float
    key_factors: List[str]

class MockSportsDataService:
    """Mock sports data service for testing betting functionality"""
    
    def __init__(self):
        self.current_games = []
        self._generate_mock_games()
    
    def _generate_mock_games(self):
        """Generate realistic mock games for testing"""
        
        # NBA Games
        nba_teams = [
            ("Lakers", "Warriors"), ("Celtics", "Nets"), ("Heat", "76ers"),
            ("Mavericks", "Nuggets"), ("Bucks", "Bulls"), ("Suns", "Clippers")
        ]
        
        # NFL Games  
        nfl_teams = [
            ("Chiefs", "Bills"), ("Ravens", "Steelers"), ("Cowboys", "Eagles"),
            ("49ers", "Rams"), ("Packers", "Vikings"), ("Dolphins", "Jets")
        ]
        
        current_time = datetime.now()
        
        # Generate NBA games
        for i, (home, away) in enumerate(nba_teams):
            game_time = current_time + timedelta(hours=2 + i)
            
            # Generate realistic odds and predictions
            home_ml = random.randint(-200, +150)
            away_ml = -home_ml + random.randint(-50, 50)
            spread = random.uniform(-12.5, +12.5)
            total = random.uniform(210.5, 235.5)
            
            # Determine predicted winner based on odds
            predicted_winner = home if home_ml < away_ml else away
            confidence = random.uniform(0.65, 0.85)  # High confidence for testing
            
            game = MockGame(
                game_id=f"nba_game_{i+1}",
                sport="NBA",
                home_team=f"{home}",
                away_team=f"{away}",
                game_time=game_time.isoformat(),
                home_team_record="25-15",
                away_team_record="22-18",
                venue=f"{home} Arena",
                home_score=0,
                away_score=0,
                game_status="scheduled",
                spread=spread,
                total=total,
                moneyline_home=home_ml,
                moneyline_away=away_ml,
                predicted_winner=predicted_winner,
                confidence=confidence,
                key_factors=[
                    f"{predicted_winner} has won 4 of last 5 games",
                    "Strong home court advantage",
                    "Key players healthy and available",
                    "Favorable matchup statistics"
                ]
            )
            self.current_games.append(game)
        
        # Generate NFL games (fewer games, higher stakes)
        for i, (home, away) in enumerate(nfl_teams[:3]):  # Only 3 NFL games
            game_time = current_time + timedelta(hours=4 + i*3)
            
            home_ml = random.randint(-180, +120)
            away_ml = -home_ml + random.randint(-30, 30)
            spread = random.uniform(-7.5, +7.5)
            total = random.uniform(42.5, 55.5)
            
            predicted_winner = home if home_ml < away_ml else away
            confidence = random.uniform(0.70, 0.90)  # Higher confidence for NFL
            
            game = MockGame(
                game_id=f"nfl_game_{i+1}",
                sport="NFL",
                home_team=f"{home}",
                away_team=f"{away}",
                game_time=game_time.isoformat(),
                home_team_record="8-3",
                away_team_record="6-5",
                venue=f"{home} Stadium",
                home_score=0,
                away_score=0,
                game_status="scheduled",
                spread=spread,
                total=total,
                moneyline_home=home_ml,
                moneyline_away=away_ml,
                predicted_winner=predicted_winner,
                confidence=confidence,
                key_factors=[
                    f"{predicted_winner} defense ranked top 5",
                    "Weather conditions favor running game",
                    "Starting QB fully healthy",
                    "Strong recent head-to-head record"
                ]
            )
            self.current_games.append(game)
    
    async def get_today_games(self, sport: str) -> List[MockGame]:
        """Get mock games for testing"""
        if sport == "NBA":
            return [game for game in self.current_games if game.sport == "NBA"]
        elif sport == "NFL":
            return [game for game in self.current_games if game.sport == "NFL"]
        else:
            return self.current_games[:3]  # Return first 3 games for other sports
    
    async def get_betting_recommendations(self, sport: str, max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get mock betting recommendations"""
        games = await self.get_today_games(sport)
        
        recommendations = []
        for game in games[:max_recommendations]:
            if game.confidence >= 0.65:  # Only high-confidence picks
                rec = {
                    "game_id": game.game_id,
                    "sport": game.sport,
                    "home_team": game.home_team,
                    "away_team": game.away_team,
                    "recommended_bet": f"{game.predicted_winner} Moneyline",
                    "odds": game.moneyline_home if game.predicted_winner == game.home_team else game.moneyline_away,
                    "confidence": game.confidence,
                    "reasoning": f"Model predicts {game.predicted_winner} victory with {game.confidence:.1%} confidence",
                    "key_factors": game.key_factors,
                    "bet_type": "moneyline",
                    "expected_value": round(random.uniform(0.05, 0.15), 3),  # Mock positive EV
                    "risk_level": "low" if game.confidence > 0.75 else "medium"
                }
                recommendations.append(rec)
        
        return recommendations

# Global instance
mock_sports_service = MockSportsDataService()