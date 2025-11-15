# =============================================================================
# ENHANCED ESPN SPORTS DATA INTEGRATION SERVICE
# =============================================================================

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cachetools import TTLCache
import redis
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GameData:
    """Data structure for game information"""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    game_time: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    odds: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None

@dataclass
class TeamStats:
    """Data structure for team statistics"""
    team_id: str
    team_name: str
    wins: int
    losses: int
    win_percentage: float
    points_per_game: float
    points_allowed: float
    last_10_games: List[str]

class ESPNSportsDataService:
    """Enhanced ESPN Sports Data Integration Service"""
    
    def __init__(self):
        self.api_key = os.getenv('ESPN_API_KEY', '')
        self.base_url = "https://sports.api.espn.com/v1"
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
        
        # Initialize cache
        self.memory_cache = TTLCache(maxsize=1000, ttl=self.cache_ttl)
        
        # Initialize Redis cache
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using memory cache only: {e}")
            self.redis_client = None
        
        # Supported sports configuration
        self.supported_sports = {
            'nfl': {'league': 'nfl', 'season_type': 2},
            'nba': {'league': 'nba', 'season_type': 2},
            'mlb': {'league': 'mlb', 'season_type': 1},
            'nhl': {'league': 'nhl', 'season_type': 2},
            'soccer': {'league': 'mls', 'season_type': 1}
        }

    async def _make_request(self, session: aiohttp.ClientSession, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling and caching"""
        cache_key = f"api_request:{url}:{json.dumps(params or {}, sort_keys=True)}"
        
        # Check cache first
        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._set_cache(cache_key, data)
                    return data
                elif response.status == 429:
                    logger.warning("Rate limit exceeded, waiting...")
                    await asyncio.sleep(60)
                    return None
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache (Redis first, then memory)"""
        try:
            if self.redis_client:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
        except Exception:
            pass
        
        return self.memory_cache.get(key)

    async def _set_cache(self, key: str, data: Dict, ttl: Optional[int] = None) -> None:
        """Set data in cache (both Redis and memory)"""
        ttl = ttl or self.cache_ttl
        
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass
        
        self.memory_cache[key] = data

    async def get_games_for_sport(self, sport: str, date: Optional[str] = None) -> List[GameData]:
        """Get games for a specific sport"""
        if sport.lower() not in self.supported_sports:
            logger.error(f"Unsupported sport: {sport}")
            return []

        sport_config = self.supported_sports[sport.lower()]
        
        # Use provided date or today
        target_date = date or datetime.now().strftime('%Y%m%d')
        
        async with aiohttp.ClientSession() as session:
            # Get scoreboard data
            scoreboard_url = f"{self.base_url}/sports/{sport_config['league']}/scoreboard"
            params = {'dates': target_date}
            
            scoreboard_data = await self._make_request(session, scoreboard_url, params)
            
            if not scoreboard_data or 'events' not in scoreboard_data:
                logger.warning(f"No games found for {sport} on {target_date}")
                return []

            games = []
            for event in scoreboard_data['events']:
                try:
                    game_data = await self._parse_game_event(event, sport.upper())
                    if game_data:
                        games.append(game_data)
                except Exception as e:
                    logger.error(f"Error parsing game event: {e}")
                    continue

            return games

    async def _parse_game_event(self, event: Dict, sport: str) -> Optional[GameData]:
        """Parse ESPN game event data into GameData object"""
        try:
            # Extract basic game information
            game_id = event['id']
            status = event['status']['type']['name']
            game_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
            
            # Extract team information
            competitions = event['competitions'][0]
            competitors = competitions['competitors']
            
            home_team = None
            away_team = None
            home_score = None
            away_score = None
            
            for competitor in competitors:
                team_name = competitor['team']['displayName']
                score = int(competitor.get('score', 0))
                
                if competitor['homeAway'] == 'home':
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score
            
            # Extract odds if available
            odds = None
            if 'odds' in competitions:
                odds_data = competitions['odds'][0] if competitions['odds'] else None
                if odds_data:
                    odds = {
                        'provider': odds_data.get('provider', {}).get('name', 'Unknown'),
                        'spread': odds_data.get('spread'),
                        'overUnder': odds_data.get('overUnder'),
                        'moneyline': {
                            'home': odds_data.get('homeTeamOdds', {}).get('moneyLine'),
                            'away': odds_data.get('awayTeamOdds', {}).get('moneyLine')
                        }
                    }
            
            return GameData(
                game_id=game_id,
                sport=sport,
                home_team=home_team,
                away_team=away_team,
                game_time=game_time,
                status=status,
                home_score=home_score if status != 'STATUS_SCHEDULED' else None,
                away_score=away_score if status != 'STATUS_SCHEDULED' else None,
                odds=odds
            )
            
        except Exception as e:
            logger.error(f"Error parsing game event: {e}")
            return None

    async def get_team_stats(self, sport: str, team_id: str) -> Optional[TeamStats]:
        """Get detailed team statistics"""
        if sport.lower() not in self.supported_sports:
            return None

        sport_config = self.supported_sports[sport.lower()]
        
        async with aiohttp.ClientSession() as session:
            # Get team stats
            stats_url = f"{self.base_url}/sports/{sport_config['league']}/teams/{team_id}/statistics"
            stats_data = await self._make_request(session, stats_url)
            
            if not stats_data:
                return None

            try:
                # Parse team statistics
                team_info = stats_data.get('team', {})
                stats = stats_data.get('statistics', {})
                
                return TeamStats(
                    team_id=team_id,
                    team_name=team_info.get('displayName', 'Unknown'),
                    wins=stats.get('wins', 0),
                    losses=stats.get('losses', 0),
                    win_percentage=stats.get('winPercentage', 0.0),
                    points_per_game=stats.get('pointsPerGame', 0.0),
                    points_allowed=stats.get('pointsAllowedPerGame', 0.0),
                    last_10_games=stats.get('last10', [])
                )
                
            except Exception as e:
                logger.error(f"Error parsing team stats: {e}")
                return None

    async def get_live_scores(self) -> List[GameData]:
        """Get all live/in-progress games across all sports"""
        live_games = []
        
        # Check all supported sports concurrently
        tasks = []
        for sport in self.supported_sports.keys():
            tasks.append(self.get_games_for_sport(sport))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                # Filter for live games only
                live_games.extend([
                    game for game in result 
                    if game.status in ['STATUS_IN_PROGRESS', 'STATUS_HALFTIME', 'STATUS_OVERTIME']
                ])
        
        return live_games

    async def get_upcoming_games(self, hours_ahead: int = 24) -> List[GameData]:
        """Get upcoming games within specified hours"""
        upcoming_games = []
        
        # Get games for today and tomorrow
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        dates = [
            today.strftime('%Y%m%d'),
            tomorrow.strftime('%Y%m%d')
        ]
        
        for date in dates:
            tasks = []
            for sport in self.supported_sports.keys():
                tasks.append(self.get_games_for_sport(sport, date))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    # Filter for upcoming games within time window
                    cutoff_time = today + timedelta(hours=hours_ahead)
                    upcoming_games.extend([
                        game for game in result
                        if game.status == 'STATUS_SCHEDULED' and game.game_time <= cutoff_time
                    ])
        
        # Sort by game time
        upcoming_games.sort(key=lambda x: x.game_time)
        return upcoming_games

    async def refresh_cache(self) -> Dict[str, int]:
        """Refresh all cached data"""
        logger.info("Starting cache refresh...")
        
        refresh_stats = {
            'games_updated': 0,
            'teams_updated': 0,
            'errors': 0
        }
        
        try:
            # Refresh games for all sports
            for sport in self.supported_sports.keys():
                try:
                    games = await self.get_games_for_sport(sport)
                    refresh_stats['games_updated'] += len(games)
                except Exception as e:
                    logger.error(f"Error refreshing {sport} games: {e}")
                    refresh_stats['errors'] += 1
            
            logger.info(f"Cache refresh completed: {refresh_stats}")
            
        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")
            refresh_stats['errors'] += 1
        
        return refresh_stats

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'memory_cache_size': len(self.memory_cache),
            'memory_cache_maxsize': self.memory_cache.maxsize,
            'cache_ttl': self.cache_ttl,
            'redis_connected': self.redis_client is not None
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats['redis_keys'] = info.get('db0', {}).get('keys', 0)
                stats['redis_memory'] = info.get('used_memory_human', 'Unknown')
            except Exception:
                stats['redis_error'] = True
        
        return stats

# =============================================================================
# GLOBAL SERVICE INSTANCE
# =============================================================================

# Create global service instance
espn_service = ESPNSportsDataService()

# =============================================================================
# ASYNC HELPER FUNCTIONS
# =============================================================================

async def get_all_games(sport: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all games, optionally filtered by sport and date"""
    if sport:
        games = await espn_service.get_games_for_sport(sport, date)
    else:
        # Get games for all sports
        all_games = []
        tasks = []
        for sport_name in espn_service.supported_sports.keys():
            tasks.append(espn_service.get_games_for_sport(sport_name, date))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_games.extend(result)
        
        games = all_games
    
    # Convert to dictionaries for JSON serialization
    return [asdict(game) for game in games]

async def get_live_games() -> List[Dict[str, Any]]:
    """Get all live games"""
    games = await espn_service.get_live_scores()
    return [asdict(game) for game in games]

async def get_upcoming_games_data(hours: int = 24) -> List[Dict[str, Any]]:
    """Get upcoming games"""
    games = await espn_service.get_upcoming_games(hours)
    return [asdict(game) for game in games]

# =============================================================================
# BACKGROUND TASK FOR CACHE REFRESH
# =============================================================================

async def scheduled_cache_refresh():
    """Background task to refresh cache periodically"""
    while True:
        try:
            await espn_service.refresh_cache()
            # Wait 10 minutes before next refresh
            await asyncio.sleep(600)
        except Exception as e:
            logger.error(f"Scheduled cache refresh failed: {e}")
            await asyncio.sleep(60)  # Retry in 1 minute on error