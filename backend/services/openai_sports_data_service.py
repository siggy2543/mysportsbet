"""
OpenAI Sports Data Fallback Service
Uses ChatGPT to collect sports data when primary APIs fail
Provides game data, predictions, and betting recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import os
import openai
from dataclasses import dataclass, asdict

from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class OpenAIGameData:
    """Game data structure for OpenAI-collected information"""
    game_id: str
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    game_time: Optional[str] = None
    game_status: str = "scheduled"
    sport: str = "NBA"
    venue: Optional[str] = None
    home_team_record: Optional[str] = None
    away_team_record: Optional[str] = None
    spread: Optional[float] = None
    total: Optional[float] = None
    moneyline_home: Optional[int] = None
    moneyline_away: Optional[int] = None
    predicted_winner: Optional[str] = None
    confidence: Optional[float] = None
    key_factors: List[str] = None

    def __post_init__(self):
        if self.key_factors is None:
            self.key_factors = []

class OpenAISportsDataService:
    """
    OpenAI-powered sports data collection service
    Uses ChatGPT to gather sports information when primary APIs fail
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        self.max_retries = 3
        self.timeout = 30
        
    async def get_today_games(self, sport: str = "NBA") -> List[OpenAIGameData]:
        """Get today's games using OpenAI"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""
            Please provide today's {sport} games for {today}. For each game, provide:
            1. Home team and away team names
            2. Game time (EST)
            3. Current score (if game is in progress or finished)
            4. Game status (scheduled, in_progress, final)
            5. Venue name
            6. Team records (wins-losses)
            7. Betting lines: spread, total points (over/under), moneyline odds
            8. Your prediction for the winner with confidence percentage
            9. Key factors influencing the game (injuries, recent form, head-to-head)
            
            Format as JSON array with this structure:
            [{{
                "game_id": "unique_game_id",
                "home_team": "Team Name",
                "away_team": "Team Name", 
                "home_score": null_or_number,
                "away_score": null_or_number,
                "game_time": "7:30 PM EST",
                "game_status": "scheduled",
                "sport": "{sport}",
                "venue": "Arena Name",
                "home_team_record": "25-15",
                "away_team_record": "20-20",
                "spread": -5.5,
                "total": 215.5,
                "moneyline_home": -220,
                "moneyline_away": +180,
                "predicted_winner": "Home/Away",
                "confidence": 0.65,
                "key_factors": ["injury report", "recent form", "matchup advantage"]
            }}]
            
            Only return valid JSON, no additional text.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a sports data analyst providing accurate, up-to-date sports information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            games_data = json.loads(content)
            
            # Convert to OpenAIGameData objects
            games = []
            for game_data in games_data:
                game = OpenAIGameData(
                    game_id=game_data.get("game_id", f"{sport}_{datetime.now().timestamp()}"),
                    home_team=game_data["home_team"],
                    away_team=game_data["away_team"],
                    home_score=game_data.get("home_score"),
                    away_score=game_data.get("away_score"),
                    game_time=game_data.get("game_time"),
                    game_status=game_data.get("game_status", "scheduled"),
                    sport=game_data.get("sport", sport),
                    venue=game_data.get("venue"),
                    home_team_record=game_data.get("home_team_record"),
                    away_team_record=game_data.get("away_team_record"),
                    spread=game_data.get("spread"),
                    total=game_data.get("total"),
                    moneyline_home=game_data.get("moneyline_home"),
                    moneyline_away=game_data.get("moneyline_away"),
                    predicted_winner=game_data.get("predicted_winner"),
                    confidence=game_data.get("confidence"),
                    key_factors=game_data.get("key_factors", [])
                )
                games.append(game)
                
            logger.info(f"Retrieved {len(games)} games from OpenAI for {sport}")
            return games
            
        except Exception as e:
            logger.error(f"Error getting games from OpenAI: {str(e)}")
            return []
    
    async def get_game_prediction(self, home_team: str, away_team: str, sport: str = "NBA") -> Dict[str, Any]:
        """Get detailed game prediction from OpenAI"""
        try:
            prompt = f"""
            Analyze the upcoming {sport} game between {away_team} (away) vs {home_team} (home).
            
            Provide a detailed analysis including:
            1. Recent team performance and form
            2. Head-to-head history
            3. Key player statuses and injuries
            4. Betting line analysis (spread, total, moneyline)
            5. Value bet recommendations
            6. Final prediction with confidence percentage
            7. Key factors that could influence the outcome
            
            Format as JSON:
            {{
                "matchup": "{away_team} @ {home_team}",
                "sport": "{sport}",
                "analysis": "detailed analysis text",
                "predicted_winner": "team name",
                "confidence": 0.75,
                "recommended_bets": [
                    {{
                        "bet_type": "spread",
                        "selection": "home -5.5",
                        "odds": -110,
                        "confidence": 0.7,
                        "reasoning": "explanation"
                    }}
                ],
                "key_factors": ["factor1", "factor2"],
                "final_score_prediction": "105-98",
                "value_rating": "High/Medium/Low"
            }}
            
            Only return valid JSON.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sports analyst and betting strategist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            prediction_data = json.loads(content)
            logger.info(f"Generated prediction for {away_team} @ {home_team}")
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error getting prediction from OpenAI: {str(e)}")
            return {}
    
    async def get_betting_recommendations(self, sport: str = "NBA", max_bets: int = 5) -> List[Dict[str, Any]]:
        """Get betting recommendations for today's games"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""
            Provide the top {max_bets} betting recommendations for {sport} games today ({today}).
            
            For each recommendation, analyze:
            1. The specific bet (spread, total, moneyline, player props)
            2. Why it's a good value bet
            3. Confidence level (1-10)
            4. Risk level (Low/Medium/High)
            5. Expected return
            
            Focus on:
            - Value bets where the odds don't reflect true probability
            - Line movements and sharp money indicators
            - Recent team/player trends
            - Situational advantages
            
            Format as JSON array:
            [{{
                "game": "Team1 vs Team2",
                "bet_type": "spread",
                "selection": "Team1 -5.5",
                "odds": -110,
                "confidence": 8,
                "risk_level": "Medium",
                "reasoning": "detailed explanation",
                "expected_value": "+12%",
                "stake_recommendation": 5.0,
                "sport": "{sport}"
            }}]
            
            Only return valid JSON.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional sports bettor and value bet finder."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            recommendations = json.loads(content)
            logger.info(f"Generated {len(recommendations)} betting recommendations for {sport}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting betting recommendations from OpenAI: {str(e)}")
            return []
    
    async def get_live_game_updates(self, game_id: str, home_team: str, away_team: str) -> Dict[str, Any]:
        """Get live game updates and analysis"""
        try:
            prompt = f"""
            Provide a live update for the game between {away_team} and {home_team}.
            
            Include:
            1. Current score (if available)
            2. Game status and time remaining
            3. Key plays or momentum shifts
            4. In-game betting opportunities
            5. Live betting recommendations
            
            Format as JSON:
            {{
                "game_id": "{game_id}",
                "current_score": "Away 95, Home 92",
                "game_status": "4th Quarter - 3:45 remaining",
                "momentum": "Home team",
                "key_plays": ["3-pointer by Player X", "turnover"],
                "live_betting_opportunities": [
                    {{
                        "bet_type": "next_team_to_score",
                        "recommendation": "Home team",
                        "confidence": 7,
                        "reasoning": "momentum and home crowd"
                    }}
                ],
                "final_outcome_probability": {{
                    "home_win": 0.65,
                    "away_win": 0.35
                }}
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a live sports analyst providing real-time game insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            live_data = json.loads(content)
            return live_data
            
        except Exception as e:
            logger.error(f"Error getting live updates from OpenAI: {str(e)}")
            return {}
    
    async def health_check(self) -> bool:
        """Check if OpenAI service is available"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "Reply with just 'OK' if you're working."}
                ],
                max_tokens=5,
                temperature=0
            )
            
            return response.choices[0].message.content.strip().upper() == "OK"
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return False

# Global instance
openai_sports_service = OpenAISportsDataService()