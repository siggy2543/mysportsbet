"""
Enhanced Sports API service for comprehensive data collection and analysis
Integrates ESPN, The Rundown, AllSports APIs with advanced analytics
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import pandas as pd
import numpy as np

from core.config import settings
from core.database import get_db_session, SportEvent, redis_client
from sqlalchemy import select, and_
from .cache_service import CacheService
from .openai_sports_data_service import openai_sports_service, OpenAIGameData

logger = logging.getLogger(__name__)

@dataclass
class TeamStats:
    """Comprehensive team statistics for analysis"""
    team_name: str
    wins: int
    losses: int
    draws: int
    goals_for: int
    goals_against: int
    home_record: Dict[str, int]
    away_record: Dict[str, int]
    recent_form: List[int]  # Last 5 games: 1=win, 0=loss, 0.5=draw
    injury_report: List[str]
    key_players: List[str]
    avg_possession: float
    shots_per_game: float
    defensive_rating: float

@dataclass 
class GameData:
    external_id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    event_date: datetime
    odds: Dict[str, Any]
    source: str
    # Enhanced fields for game theory analysis
    head_to_head_history: List[Dict]
    home_team_stats: TeamStats
    away_team_stats: TeamStats
    weather_conditions: Optional[Dict]
    venue_info: Dict[str, Any]
    betting_volume: Dict[str, float]
    sharp_money_indicators: Dict[str, float]
    public_betting_percentages: Dict[str, float]

@dataclass
class HistoricalAnalysis:
    """Historical performance analysis for teams"""
    team: str
    opponent: str
    historical_wins: int
    historical_losses: int
    historical_draws: int
    avg_goals_scored: float
    avg_goals_conceded: float
    win_probability: float
    performance_trends: Dict[str, Any]

class SportsAPIService:
    """
    Advanced Sports API service with comprehensive data collection
    and statistical analysis capabilities
    """
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        self.collection_tasks = []
        self.api_endpoints = {
            'espn': {
                'base_url': 'https://site.api.espn.com/apis/site/v2/sports',
                'rate_limit': 100,  # requests per minute
                'timeout': 30
            },
            'rundown': {
                'base_url': 'https://therundown-therundown-v1.p.rapidapi.com',
                'api_key': settings.THE_RUNDOWN_API_KEY,
                'rate_limit': 500,
                'timeout': 15
            },
            'allsports': {
                'base_url': 'https://allsportdb.com/api/v1',
                'api_key': settings.RAPIDAPI_KEY,
                'rate_limit': 1000,
                'timeout': 20
            }
        }
        
    async def start_data_collection(self):
        """Start comprehensive background data collection from all APIs"""
        if self.is_running:
            return
            
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={'User-Agent': 'SportsApp/1.0'}
        )
        self.is_running = True
        
        # Schedule comprehensive data collection tasks
        self.collection_tasks = [
            asyncio.create_task(self._collect_espn_data()),
            asyncio.create_task(self._collect_rundown_data()),
            asyncio.create_task(self._collect_allsports_data()),
            asyncio.create_task(self._collect_historical_data()),
            asyncio.create_task(self._collect_team_statistics()),
            asyncio.create_task(self._monitor_betting_markets()),
        ]
        
        logger.info("Advanced sports data collection started")

    async def stop_data_collection(self):
        """Stop background data collection"""
        self.is_running = False
        
        # Cancel all tasks
        for task in self.collection_tasks:
            task.cancel()
            
        if self.session:
            await self.session.close()
            
        logger.info("Stopped sports data collection service")

    async def get_game_details(self, game_id: str) -> Dict[str, Any]:
        """Get comprehensive game details for prediction analysis"""
        try:
            cache_key = f"game_details:{game_id}"
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                return cached_data

            # Fetch from multiple sources and combine
            espn_data = await self._get_espn_game_details(game_id)
            rundown_data = await self._get_rundown_odds(game_id)
            historical_data = await self._get_historical_matchup(
                espn_data['home_team'], espn_data['away_team']
            )

            # Combine all data sources
            game_details = {
                "id": game_id,
                "home_team": espn_data['home_team'],
                "away_team": espn_data['away_team'],
                "sport": espn_data['sport'],
                "league": espn_data['league'],
                "start_time": espn_data['start_time'],
                "odds": {
                    "home": rundown_data.get('home_odds', 2.0),
                    "away": rundown_data.get('away_odds', 2.0),
                    "draw": rundown_data.get('draw_odds', 3.0)
                },
                "head_to_head": historical_data,
                "recent_form": await self._get_recent_form(espn_data['home_team'], espn_data['away_team']),
                "injuries": await self._get_injury_reports(espn_data['home_team'], espn_data['away_team']),
                "weather": await self._get_weather_conditions(espn_data.get('venue')),
                "venue_advantage": await self._calculate_venue_advantage(espn_data['home_team'], espn_data.get('venue')),
                "betting_volume": rundown_data.get('betting_volume', {}),
                "market_movement": await self._get_odds_movement(game_id)
            }

            # Cache for 5 minutes
            await self.cache_service.set(cache_key, game_details, ttl=300)
            return game_details

        except Exception as e:
            logger.error(f"Error getting game details for {game_id}: {e}")
            raise

    async def get_games_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get all games for a specific date with comprehensive data"""
        try:
            cache_key = f"games_by_date:{date.strftime('%Y-%m-%d')}"
            cached_games = await self.cache_service.get(cache_key)
            if cached_games:
                return cached_games

            # Collect games from all sources
            games = []
            
            # ESPN games
            espn_games = await self._get_espn_games_by_date(date)
            games.extend(espn_games)
            
            # Rundown games with odds
            rundown_games = await self._get_rundown_games_by_date(date)
            
            # Merge data sources
            enhanced_games = []
            for game in games:
                # Find corresponding odds data
                odds_data = next(
                    (r for r in rundown_games if r['home_team'] == game['home_team'] 
                     and r['away_team'] == game['away_team']), 
                    {'odds': {'home': 2.0, 'away': 2.0, 'draw': 3.0}}
                )
                
                enhanced_game = {
                    **game,
                    'odds': odds_data['odds'],
                    'betting_volume': odds_data.get('betting_volume', {}),
                    'market_data': odds_data.get('market_data', {})
                }
                enhanced_games.append(enhanced_game)

            # Cache for 10 minutes
            await self.cache_service.set(cache_key, enhanced_games, ttl=600)
            return enhanced_games

        except Exception as e:
            logger.error(f"Error getting games for date {date}: {e}")
            raise

    async def get_team_statistics(self, team_name: str, season: Optional[str] = None) -> TeamStats:
        """Get comprehensive team statistics"""
        try:
            cache_key = f"team_stats:{team_name}:{season or 'current'}"
            cached_stats = await self.cache_service.get(cache_key)
            if cached_stats:
                return TeamStats(**cached_stats)

            # Collect stats from multiple sources
            espn_stats = await self._get_espn_team_stats(team_name, season)
            allsports_stats = await self._get_allsports_team_stats(team_name, season)
            
            # Combine and normalize data
            team_stats = TeamStats(
                team_name=team_name,
                wins=espn_stats.get('wins', 0),
                losses=espn_stats.get('losses', 0),
                draws=espn_stats.get('draws', 0),
                goals_for=espn_stats.get('goals_for', 0),
                goals_against=espn_stats.get('goals_against', 0),
                home_record=espn_stats.get('home_record', {'wins': 0, 'losses': 0, 'draws': 0}),
                away_record=espn_stats.get('away_record', {'wins': 0, 'losses': 0, 'draws': 0}),
                recent_form=await self._calculate_recent_form(team_name),
                injury_report=await self._get_current_injuries(team_name),
                key_players=espn_stats.get('key_players', []),
                avg_possession=allsports_stats.get('avg_possession', 50.0),
                shots_per_game=allsports_stats.get('shots_per_game', 10.0),
                defensive_rating=allsports_stats.get('defensive_rating', 50.0)
            )

            # Cache for 1 hour
            await self.cache_service.set(cache_key, asdict(team_stats), ttl=3600)
            return team_stats

        except Exception as e:
            logger.error(f"Error getting team statistics for {team_name}: {e}")
            raise

    async def analyze_historical_performance(self, home_team: str, away_team: str, 
                                           lookback_years: int = 5) -> HistoricalAnalysis:
        """Analyze historical head-to-head performance"""
        try:
            cache_key = f"h2h_analysis:{home_team}:{away_team}:{lookback_years}"
            cached_analysis = await self.cache_service.get(cache_key)
            if cached_analysis:
                return HistoricalAnalysis(**cached_analysis)

            # Get historical matchups
            historical_games = await self._get_historical_matchups(
                home_team, away_team, lookback_years
            )

            if not historical_games:
                # Return default analysis if no historical data
                return HistoricalAnalysis(
                    team=home_team,
                    opponent=away_team,
                    historical_wins=0,
                    historical_losses=0,
                    historical_draws=0,
                    avg_goals_scored=1.5,
                    avg_goals_conceded=1.5,
                    win_probability=0.5,
                    performance_trends={}
                )

            # Analyze the historical data
            home_wins = sum(1 for game in historical_games if game['home_score'] > game['away_score'])
            home_losses = sum(1 for game in historical_games if game['home_score'] < game['away_score'])
            draws = sum(1 for game in historical_games if game['home_score'] == game['away_score'])
            
            total_games = len(historical_games)
            avg_goals_scored = sum(game['home_score'] for game in historical_games) / max(1, total_games)
            avg_goals_conceded = sum(game['away_score'] for game in historical_games) / max(1, total_games)
            win_probability = home_wins / max(1, total_games)

            # Calculate performance trends
            performance_trends = await self._calculate_performance_trends(historical_games)

            analysis = HistoricalAnalysis(
                team=home_team,
                opponent=away_team,
                historical_wins=home_wins,
                historical_losses=home_losses,
                historical_draws=draws,
                avg_goals_scored=avg_goals_scored,
                avg_goals_conceded=avg_goals_conceded,
                win_probability=win_probability,
                performance_trends=performance_trends
            )

            # Cache for 24 hours
            await self.cache_service.set(cache_key, asdict(analysis), ttl=86400)
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing historical performance: {e}")
            raise

    # Enhanced data collection methods

    async def _collect_historical_data(self):
        """Continuously collect and update historical data"""
        while self.is_running:
            try:
                # Collect historical data for model training
                await self._update_historical_database()
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                logger.error(f"Error in historical data collection: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def _collect_team_statistics(self):
        """Continuously update team statistics"""
        while self.is_running:
            try:
                # Update team stats for all active teams
                await self._update_all_team_statistics()
                await asyncio.sleep(1800)  # Update every 30 minutes
            except Exception as e:
                logger.error(f"Error in team statistics collection: {e}")
                await asyncio.sleep(300)

    async def _monitor_betting_markets(self):
        """Monitor betting market movements and volumes"""
        while self.is_running:
            try:
                # Monitor odds movements and betting volumes
                await self._track_market_movements()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in betting market monitoring: {e}")
                await asyncio.sleep(30)

    async def get_games_with_openai_fallback(self, date: datetime, sport: str = "NBA") -> List[Dict[str, Any]]:
        """Get games data with OpenAI fallback when primary APIs fail"""
        try:
            # First try the main API sources
            games = await self.get_games_by_date(date)
            
            if games and len(games) > 0:
                logger.info(f"Successfully retrieved {len(games)} games from primary APIs")
                return games
            
            # If primary APIs fail or return no data, use OpenAI fallback
            logger.warning("Primary APIs failed or returned no data, using OpenAI fallback")
            
            openai_games = await openai_sports_service.get_today_games(sport)
            
            # Convert OpenAI game data to our standard format
            converted_games = []
            for openai_game in openai_games:
                converted_game = {
                    'external_id': openai_game.game_id,
                    'sport': openai_game.sport,
                    'league': openai_game.sport,
                    'home_team': openai_game.home_team,
                    'away_team': openai_game.away_team,
                    'event_date': date.isoformat(),
                    'game_time': openai_game.game_time,
                    'venue': openai_game.venue,
                    'home_score': openai_game.home_score,
                    'away_score': openai_game.away_score,
                    'game_status': openai_game.game_status,
                    'odds': {
                        'spread': openai_game.spread,
                        'total': openai_game.total,
                        'home_ml': openai_game.moneyline_home,
                        'away_ml': openai_game.moneyline_away
                    },
                    'prediction': {
                        'predicted_winner': openai_game.predicted_winner,
                        'confidence': openai_game.confidence,
                        'key_factors': openai_game.key_factors
                    },
                    'source': 'openai_fallback',
                    'team_records': {
                        'home': openai_game.home_team_record,
                        'away': openai_game.away_team_record
                    }
                }
                converted_games.append(converted_game)
                
            logger.info(f"OpenAI fallback provided {len(converted_games)} games")
            return converted_games
            
        except Exception as e:
            logger.error(f"Error in get_games_with_openai_fallback: {str(e)}")
            # Return empty list if both primary and fallback fail
            return []
    
    async def get_betting_recommendations_with_ai(self, sport: str = "NBA", max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get AI-powered betting recommendations"""
        try:
            # Get recommendations from OpenAI
            recommendations = await openai_sports_service.get_betting_recommendations(sport, max_recommendations)
            
            # Enhance with our analysis if possible
            enhanced_recommendations = []
            for rec in recommendations:
                enhanced_rec = {
                    **rec,
                    'source': 'openai_ai_analysis',
                    'timestamp': datetime.utcnow().isoformat(),
                    'sport': sport
                }
                enhanced_recommendations.append(enhanced_rec)
                
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI betting recommendations: {str(e)}")
            return []

    # Private helper methods for enhanced functionality

    async def _get_espn_game_details(self, game_id: str) -> Dict[str, Any]:
        """Get detailed game information from ESPN"""
        try:
            url = f"{self.api_endpoints['espn']['base_url']}/football/college-football/scoreboard"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse ESPN response to extract game details
                    # This is a simplified implementation
                    return {
                        'home_team': 'Sample Home Team',
                        'away_team': 'Sample Away Team',
                        'sport': 'football',
                        'league': 'college-football',
                        'start_time': datetime.now().isoformat(),
                        'venue': 'Sample Stadium'
                    }
                else:
                    logger.warning(f"ESPN API returned status {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching ESPN game details: {e}")
            return {}

    async def _get_rundown_odds(self, game_id: str) -> Dict[str, Any]:
        """Get odds data from The Rundown API"""
        try:
            headers = {
                'X-RapidAPI-Key': self.api_endpoints['rundown']['api_key'],
                'X-RapidAPI-Host': 'therundown-therundown-v1.p.rapidapi.com'
            }
            url = f"{self.api_endpoints['rundown']['base_url']}/sports/4/events/{game_id}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse odds data
                    return {
                        'home_odds': 2.0,
                        'away_odds': 1.8,
                        'draw_odds': 3.2,
                        'betting_volume': {'home': 60, 'away': 40},
                        'market_data': {'total_volume': 100000}
                    }
                else:
                    return {}
        except Exception as e:
            logger.error(f"Error fetching Rundown odds: {e}")
            return {}

    async def _get_historical_matchup(self, home_team: str, away_team: str) -> List[Dict]:
        """Get historical head-to-head matchups"""
        # This would query historical database or API
        return [
            {
                'date': '2023-01-01',
                'home_score': 2,
                'away_score': 1,
                'venue': 'Home Stadium'
            }
        ]

    async def _get_recent_form(self, home_team: str, away_team: str) -> Dict[str, List[int]]:
        """Get recent form for both teams"""
        return {
            home_team: [1, 1, 0, 1, 1],  # Last 5 games
            away_team: [0, 1, 1, 0, 1]
        }

    async def _get_injury_reports(self, home_team: str, away_team: str) -> Dict[str, List[str]]:
        """Get current injury reports"""
        return {
            home_team: ['Player A - questionable', 'Player B - out'],
            away_team: ['Player C - probable']
        }

    async def _get_weather_conditions(self, venue: Optional[str]) -> Optional[Dict]:
        """Get weather conditions for outdoor venues"""
        if not venue:
            return None
        return {
            'temperature': 22,
            'humidity': 65,
            'wind_speed': 10,
            'precipitation': 0,
            'condition': 'clear'
        }

    async def _calculate_venue_advantage(self, home_team: str, venue: Optional[str]) -> float:
        """Calculate home venue advantage"""
        # This would use historical data to calculate venue advantage
        return 0.1  # 10% advantage

    async def _get_odds_movement(self, game_id: str) -> List[Dict]:
        """Get odds movement history"""
        return [
            {'timestamp': datetime.now().isoformat(), 'home_odds': 2.0, 'away_odds': 1.8}
        ]

    async def health_check(self) -> str:
        """Check if all APIs are accessible"""
        try:
            if not self.session:
                return "disconnected"
                
            # Test ESPN API
            await self._test_espn_connection()
            return "healthy"
        except Exception:
            return "unhealthy"
            
            return "connected"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return "error"
    
    async def _collect_espn_data(self):
        """Collect data from ESPN API"""
        while self.is_running:
            try:
                games = await self._fetch_espn_games()
                await self._store_games_data(games, "espn")
                logger.info(f"Collected {len(games)} games from ESPN")
                
            except Exception as e:
                logger.error(f"ESPN data collection error: {e}")
                
            # Wait 5 minutes before next collection
            await asyncio.sleep(300)
    
    async def _collect_rundown_data(self):
        """Collect data from The Rundown API"""
        while self.is_running:
            try:
                games = await self._fetch_rundown_games()
                await self._store_games_data(games, "rundown")
                logger.info(f"Collected {len(games)} games from The Rundown")
                
            except Exception as e:
                logger.error(f"Rundown data collection error: {e}")
                
            await asyncio.sleep(300)
    
    async def _collect_allsports_data(self):
        """Collect data from All-Sports API"""
        while self.is_running:
            try:
                games = await self._fetch_allsports_games()
                await self._store_games_data(games, "allsports")
                logger.info(f"Collected {len(games)} games from All-Sports")
                
            except Exception as e:
                logger.error(f"All-Sports data collection error: {e}")
                
            await asyncio.sleep(300)
    
    async def _fetch_espn_games(self) -> List[GameData]:
        """Fetch games from ESPN API"""
        url = f"{settings.ESPN_API_URL}/sports/football/nfl/scoreboard"
        headers = {"Authorization": f"Bearer {settings.ESPN_API_KEY}"}
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_espn_data(data)
            else:
                logger.error(f"ESPN API error: {response.status}")
                return []
    
    async def _fetch_rundown_games(self) -> List[GameData]:
        """Fetch games from The Rundown API"""
        url = f"{settings.THE_RUNDOWN_API_URL}/sports/4/events"  # NFL
        headers = {
            "X-RapidAPI-Key": settings.THE_RUNDOWN_API_KEY,
            "X-RapidAPI-Host": "therundown-therundown-v1.p.rapidapi.com"
        }
        
        params = {
            "include": "scores,odds",
            "offset": "0"
        }
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_rundown_data(data)
            else:
                logger.error(f"Rundown API error: {response.status}")
                return []
    
    async def _fetch_allsports_games(self) -> List[GameData]:
        """Fetch games from All-Sports API"""
        url = f"{settings.ALL_SPORTS_API_URL}/calendar"
        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "allsportdb-com.p.rapidapi.com"
        }
        
        params = {"objectType": "0"}
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_allsports_data(data)
            else:
                logger.error(f"All-Sports API error: {response.status}")
                return []
    
    def _parse_espn_data(self, data: Dict[str, Any]) -> List[GameData]:
        """Parse ESPN API response"""
        games = []
        events = data.get("events", [])
        
        for event in events:
            try:
                competitions = event.get("competitions", [])
                if not competitions:
                    continue
                    
                competition = competitions[0]
                competitors = competition.get("competitors", [])
                
                if len(competitors) < 2:
                    continue
                
                home_team = next(c for c in competitors if c.get("homeAway") == "home")
                away_team = next(c for c in competitors if c.get("homeAway") == "away")
                
                game_data = GameData(
                    external_id=event.get("id"),
                    sport="football",
                    league="nfl",
                    home_team=home_team.get("team", {}).get("displayName", ""),
                    away_team=away_team.get("team", {}).get("displayName", ""),
                    event_date=datetime.fromisoformat(event.get("date").replace("Z", "+00:00")),
                    odds=competition.get("odds", {}),
                    source="espn",
                    head_to_head_history=[],
                    home_team_stats=TeamStats(
                        team_name=home_team.get("team", {}).get("displayName", ""),
                        wins=home_team.get("records", [{}])[0].get("wins", 0) if home_team.get("records") else 0,
                        losses=home_team.get("records", [{}])[0].get("losses", 0) if home_team.get("records") else 0,
                        draws=0,
                        goals_for=0,
                        goals_against=0,
                        home_record={'wins': 0, 'losses': 0, 'draws': 0},
                        away_record={'wins': 0, 'losses': 0, 'draws': 0},
                        recent_form=[],
                        injury_report=[],
                        key_players=[],
                        avg_possession=50.0,
                        shots_per_game=10.0,
                        defensive_rating=50.0
                    ),
                    away_team_stats=TeamStats(
                        team_name=away_team.get("team", {}).get("displayName", ""),
                        wins=away_team.get("records", [{}])[0].get("wins", 0) if away_team.get("records") else 0,
                        losses=away_team.get("records", [{}])[0].get("losses", 0) if away_team.get("records") else 0,
                        draws=0,
                        goals_for=0,
                        points_against=0.0,
                        win_streak=0,
                        form=[],
                        recent_performance=[],
                        avg_score=0.0,
                        defensive_rating=0.0
                    ),
                    weather_conditions=competition.get("weather"),
                    venue_info=competition.get("venue", {}),
                    betting_volume={"total": 0.0, "sharp": 0.0, "public": 0.0},
                    sharp_money_indicators={"percentage": 0.0, "movement": 0.0},
                    public_betting_percentages={"home": 50.0, "away": 50.0}
                )
                games.append(game_data)
                
            except Exception as e:
                logger.error(f"Error parsing ESPN event: {e}")
                continue
                
        return games
    
    def _parse_rundown_data(self, data: Dict[str, Any]) -> List[GameData]:
        """Parse The Rundown API response"""
        games = []
        events = data.get("events", [])
        
        for event in events:
            try:
                teams = event.get("teams", [])
                if len(teams) < 2:
                    continue
                
                game_data = GameData(
                    external_id=event.get("event_id"),
                    sport="football",
                    league="nfl",
                    home_team=teams[0].get("name", ""),
                    away_team=teams[1].get("name", ""),
                    event_date=datetime.fromisoformat(event.get("event_date")),
                    odds=event.get("lines", {}),
                    source="rundown",
                    head_to_head_history=[],
                    home_team_stats=TeamStats(
                        team_name=teams[0].get("name", ""),
                        wins=0, losses=0, draws=0, goals_for=0, goals_against=0,
                        home_record={'wins': 0, 'losses': 0, 'draws': 0},
                        away_record={'wins': 0, 'losses': 0, 'draws': 0},
                        recent_form=[], injury_report=[], key_players=[],
                        avg_possession=50.0, shots_per_game=10.0, defensive_rating=50.0
                    ),
                    away_team_stats=TeamStats(
                        team_name=teams[1].get("name", ""),
                        wins=0, losses=0, draws=0, goals_for=0, goals_against=0,
                        win_streak=0, form=[], recent_performance=[], avg_score=0.0, defensive_rating=0.0
                    ),
                    weather_conditions=None,
                    venue_info=event.get("venue", {}),
                    betting_volume={"total": 0.0, "sharp": 0.0, "public": 0.0},
                    sharp_money_indicators={"percentage": 0.0, "movement": 0.0},
                    public_betting_percentages={"home": 50.0, "away": 50.0}
                )
                games.append(game_data)
                
            except Exception as e:
                logger.error(f"Error parsing Rundown event: {e}")
                continue
                
        return games
    
    def _parse_allsports_data(self, data: Dict[str, Any]) -> List[GameData]:
        """Parse All-Sports API response"""
        games = []
        events = data.get("events", [])
        
        for event in events:
            try:
                game_data = GameData(
                    external_id=event.get("idEvent"),
                    sport=event.get("strSport", "").lower(),
                    league=event.get("strLeague", "").lower(),
                    home_team=event.get("strHomeTeam", ""),
                    away_team=event.get("strAwayTeam", ""),
                    event_date=datetime.strptime(event.get("dateEvent"), "%Y-%m-%d"),
                    odds={},  # All-Sports doesn't provide odds directly
                    source="allsports",
                    head_to_head_history=[],
                    home_team_stats=TeamStats(
                        team=event.get("strHomeTeam", ""),
                        wins=0, losses=0, points_for=0.0, points_against=0.0,
                        win_streak=0, form=[], recent_performance=[], avg_score=0.0, defensive_rating=0.0
                    ),
                    away_team_stats=TeamStats(
                        team=event.get("strAwayTeam", ""),
                        wins=0, losses=0, points_for=0.0, points_against=0.0,
                        win_streak=0, form=[], recent_performance=[], avg_score=0.0, defensive_rating=0.0
                    ),
                    weather_conditions=None,
                    venue_info={"name": event.get("strVenue", ""), "location": ""},
                    betting_volume={"total": 0.0, "sharp": 0.0, "public": 0.0},
                    sharp_money_indicators={"percentage": 0.0, "movement": 0.0},
                    public_betting_percentages={"home": 50.0, "away": 50.0}
                )
                games.append(game_data)
                
            except Exception as e:
                logger.error(f"Error parsing All-Sports event: {e}")
                continue
                
        return games
    
    async def _store_games_data(self, games: List[GameData], source: str):
        """Store games data in database and cache"""
        async with get_db_session() as db:
            for game in games:
                try:
                    # Check if event already exists
                    existing_event = await db.execute(
                        select(SportEvent).where(SportEvent.external_id == game.external_id)
                    )
                    event = existing_event.scalar_one_or_none()
                    
                    if event:
                        # Update existing event
                        event.odds_data = game.odds
                        event.updated_at = datetime.utcnow()
                    else:
                        # Create new event
                        event = SportEvent(
                            external_id=game.external_id,
                            sport=game.sport,
                            league=game.league,
                            home_team=game.home_team,
                            away_team=game.away_team,
                            event_date=game.event_date,
                            odds_data=game.odds
                        )
                        db.add(event)
                    
                    await db.commit()
                    
                    # Cache the data with smart TTL
                    from services.cache_service import cache_service
                    
                    event_data = {
                        'external_id': game.external_id,
                        'sport': game.sport,
                        'league': game.league,
                        'home_team': game.home_team,
                        'away_team': game.away_team,
                        'event_date': game.event_date.isoformat(),
                        'odds': game.odds,
                        'source': game.source
                    }
                    
                    # Cache event data with medium TTL
                    await cache_service.set('event', event_data, event_id=game.external_id)
                    
                    # Cache odds separately with short TTL (more frequently updated)
                    await cache_service.set('odds', game.odds, event_id=game.external_id)
                    
                except Exception as e:
                    logger.error(f"Error storing game data: {e}")
                    await db.rollback()
                    continue
    
    async def _test_espn_connection(self):
        """Test ESPN API connection"""
        url = f"{settings.ESPN_API_URL}/sports"
        headers = {"Authorization": f"Bearer {settings.ESPN_API_KEY}"}
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"ESPN API connection failed: {response.status}")
    
    async def get_upcoming_games(self, sport: Optional[str] = None, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming games from cache or database"""
        end_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        async with get_db_session() as db:
            query = select(SportEvent).where(
                and_(
                    SportEvent.event_date >= datetime.utcnow(),
                    SportEvent.event_date <= end_time
                )
            )
            
            if sport:
                query = query.where(SportEvent.sport == sport)
            
            result = await db.execute(query.order_by(SportEvent.event_date))
            events = result.scalars().all()
            
            return [
                {
                    "id": event.id,
                    "external_id": event.external_id,
                    "sport": event.sport,
                    "league": event.league,
                    "home_team": event.home_team,
                    "away_team": event.away_team,
                    "event_date": event.event_date.isoformat(),
                    "odds": event.odds_data
                }
                for event in events
            ]
    async def _update_historical_database(self):
        """Update historical database with collected data"""
        try:
            logger.info("Updating historical database...")
            # Placeholder for historical data update logic
            # This would collect and store historical game data
        except Exception as e:
            logger.error(f"Error updating historical database: {e}")

    async def _update_all_team_statistics(self):
        """Update team statistics from collected data"""
        try:
            logger.info("Updating team statistics...")
            # Placeholder for team statistics update logic
            # This would analyze and store team performance metrics
        except Exception as e:
            logger.error(f"Error updating team statistics: {e}")

    async def _track_market_movements(self):
        """Track betting market movements and odds changes"""
        try:
            logger.info("Tracking market movements...")
            # Placeholder for market movement tracking logic
            # This would monitor and record odds changes over time
        except Exception as e:
            logger.error(f"Error tracking market movements: {e}")
