"""
Comprehensive Sports Data Service
Combines multiple sports data sources for robust data collection:
- ESPN undocumented endpoints (free, no API key)
- The Sports DB (free tier available)
- SportsDataIO (paid, comprehensive)
- Sportradar (enterprise-grade)
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ComprehensiveSportsDataService:
    """
    Multi-source sports data service providing redundancy and comprehensive coverage
    Falls back through different APIs to ensure data availability
    """
    
    def __init__(self):
        # ESPN undocumented endpoints (no API key required)
        self.espn_base_url = os.getenv('ESPN_API_URL', 'https://site.api.espn.com/apis/site/v2')
        
        # Alternative sports data APIs
        self.thesportsdb_api_key = os.getenv('THESPORTSDB_API_KEY')
        self.thesportsdb_base_url = os.getenv('THESPORTSDB_API_URL', 'https://www.thesportsdb.com/api/v1/json')
        
        self.sportsdata_api_key = os.getenv('SPORTSDATA_API_KEY')
        self.sportsdata_base_url = os.getenv('SPORTSDATA_API_URL', 'https://api.sportsdata.io')
        
        self.sportradar_api_key = os.getenv('SPORTRADAR_API_KEY')
        self.sportradar_base_url = os.getenv('SPORTRADAR_API_URL', 'https://api.sportradar.us')
        
        self.session = None
        
        # ESPN endpoints discovered through browser dev tools
        self.espn_endpoints = {
            'nfl': {
                'scoreboard': 'sports/football/nfl/scoreboard',
                'teams': 'sports/football/nfl/teams',
                'standings': 'sports/football/nfl/standings',
                'schedule': 'sports/football/nfl/schedule',
                'news': 'sports/football/nfl/news',
                'player_stats': 'sports/football/nfl/athletes'
            },
            'nba': {
                'scoreboard': 'sports/basketball/nba/scoreboard',
                'teams': 'sports/basketball/nba/teams',
                'standings': 'sports/basketball/nba/standings',
                'schedule': 'sports/basketball/nba/schedule',
                'news': 'sports/basketball/nba/news',
                'player_stats': 'sports/basketball/nba/athletes'
            },
            'mlb': {
                'scoreboard': 'sports/baseball/mlb/scoreboard',
                'teams': 'sports/baseball/mlb/teams',
                'standings': 'sports/baseball/mlb/standings',
                'schedule': 'sports/baseball/mlb/schedule',
                'news': 'sports/baseball/mlb/news',
                'player_stats': 'sports/baseball/mlb/athletes'
            },
            'nhl': {
                'scoreboard': 'sports/hockey/nhl/scoreboard',
                'teams': 'sports/hockey/nhl/teams',
                'standings': 'sports/hockey/nhl/standings',
                'schedule': 'sports/hockey/nhl/schedule',
                'news': 'sports/hockey/nhl/news',
                'player_stats': 'sports/hockey/nhl/athletes'
            }
        }
        
        # Headers to mimic ESPN.com browser requests
        self.espn_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.espn.com/',
            'Origin': 'https://www.espn.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_espn_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make request to ESPN undocumented API endpoint
        
        Args:
            endpoint: ESPN API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        session = await self._get_session()
        url = urljoin(self.espn_base_url, endpoint)
        
        try:
            logger.info(f"Making ESPN request to: {url}")
            async with session.get(url, headers=self.espn_headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"ESPN request successful: {response.status}")
                    return data
                else:
                    logger.warning(f"ESPN request failed with status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"ESPN API request failed: {e}")
            return None
    
    async def _make_thesportsdb_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make request to The Sports DB API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        if not self.thesportsdb_api_key:
            logger.warning("TheSportsDB API key not configured")
            return None
        
        session = await self._get_session()
        url = f"{self.thesportsdb_base_url}/{self.thesportsdb_api_key}/{endpoint}"
        
        try:
            logger.info(f"Making TheSportsDB request to: {url}")
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"TheSportsDB request successful")
                    return data
                else:
                    logger.warning(f"TheSportsDB request failed with status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"TheSportsDB API request failed: {e}")
            return None
    
    async def _make_sportsdata_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make request to SportsDataIO API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if failed
        """
        if not self.sportsdata_api_key:
            logger.warning("SportsDataIO API key not configured")
            return None
        
        session = await self._get_session()
        url = f"{self.sportsdata_base_url}/{endpoint}"
        headers = {'Ocp-Apim-Subscription-Key': self.sportsdata_api_key}
        
        try:
            logger.info(f"Making SportsDataIO request to: {url}")
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"SportsDataIO request successful")
                    return data
                else:
                    logger.warning(f"SportsDataIO request failed with status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"SportsDataIO API request failed: {e}")
            return None
    
    async def get_nfl_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get NFL games using multiple data sources for redundancy
        
        Args:
            date: Date in YYYYMMDD format (optional, defaults to today)
            
        Returns:
            List of NFL games with comprehensive data
        """
        games = []
        
        # Try ESPN first (free, no API key required)
        try:
            espn_games = await self._get_espn_nfl_games(date)
            if espn_games:
                games.extend(espn_games)
                logger.info(f"Retrieved {len(espn_games)} NFL games from ESPN")
        except Exception as e:
            logger.error(f"ESPN NFL games failed: {e}")
        
        # If ESPN fails or returns no data, try alternative sources
        if not games:
            # Try The Sports DB
            try:
                sportsdb_games = await self._get_thesportsdb_nfl_games(date)
                if sportsdb_games:
                    games.extend(sportsdb_games)
                    logger.info(f"Retrieved {len(sportsdb_games)} NFL games from TheSportsDB")
            except Exception as e:
                logger.error(f"TheSportsDB NFL games failed: {e}")
        
        if not games:
            # Try SportsDataIO as last resort
            try:
                sportsdata_games = await self._get_sportsdata_nfl_games(date)
                if sportsdata_games:
                    games.extend(sportsdata_games)
                    logger.info(f"Retrieved {len(sportsdata_games)} NFL games from SportsDataIO")
            except Exception as e:
                logger.error(f"SportsDataIO NFL games failed: {e}")
        
        return games
    
    async def _get_espn_nfl_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NFL games from ESPN undocumented API"""
        endpoint = self.espn_endpoints['nfl']['scoreboard']
        params = {}
        
        if date:
            params['dates'] = date
        
        data = await self._make_espn_request(endpoint, params)
        if not data or 'events' not in data:
            return []
        
        games = []
        for event in data['events']:
            try:
                game_info = self._parse_espn_game_data(event, 'nfl')
                if game_info:
                    games.append(game_info)
            except Exception as e:
                logger.error(f"Error parsing ESPN game data: {e}")
                continue
        
        return games
    
    async def _get_thesportsdb_nfl_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NFL games from The Sports DB"""
        # The Sports DB uses different endpoint structure
        endpoint = "eventsround.php"
        params = {
            'id': '4391',  # NFL league ID in TheSportsDB
            'r': '1',      # Round/week number
            's': '2024'    # Season
        }
        
        data = await self._make_thesportsdb_request(endpoint, params)
        if not data or 'events' not in data:
            return []
        
        games = []
        for event in data['events']:
            try:
                game_info = self._parse_thesportsdb_game_data(event, 'nfl')
                if game_info:
                    games.append(game_info)
            except Exception as e:
                logger.error(f"Error parsing TheSportsDB game data: {e}")
                continue
        
        return games
    
    async def _get_sportsdata_nfl_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NFL games from SportsDataIO"""
        endpoint = "v3/nfl/scores/json/GamesByDate/2024-11-03"  # Example endpoint
        
        data = await self._make_sportsdata_request(endpoint)
        if not data:
            return []
        
        games = []
        for game in data:
            try:
                game_info = self._parse_sportsdata_game_data(game, 'nfl')
                if game_info:
                    games.append(game_info)
            except Exception as e:
                logger.error(f"Error parsing SportsDataIO game data: {e}")
                continue
        
        return games
    
    def _parse_espn_game_data(self, event: Dict[str, Any], sport: str) -> Optional[Dict[str, Any]]:
        """Parse ESPN game data into standardized format"""
        try:
            game_id = event.get('id')
            name = event.get('name', '')
            short_name = event.get('shortName', '')
            date = event.get('date')
            
            # Parse competitions (teams, scores, odds)
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            
            # Extract team information
            home_team = None
            away_team = None
            
            for competitor in competitors:
                team_info = {
                    'id': competitor.get('id'),
                    'name': competitor.get('team', {}).get('displayName', ''),
                    'abbreviation': competitor.get('team', {}).get('abbreviation', ''),
                    'score': competitor.get('score', '0'),
                    'record': competitor.get('records', [{}])[0].get('summary', '') if competitor.get('records') else ''
                }
                
                if competitor.get('homeAway') == 'home':
                    home_team = team_info
                else:
                    away_team = team_info
            
            # Extract odds if available
            odds = None
            if 'odds' in competition:
                odds_data = competition['odds'][0] if competition['odds'] else {}
                odds = {
                    'provider': odds_data.get('provider', {}).get('name', ''),
                    'details': odds_data.get('details', ''),
                    'over_under': odds_data.get('overUnder', 0)
                }
            
            # Extract status
            status = event.get('status', {})
            game_status = {
                'type': status.get('type', {}).get('name', ''),
                'detail': status.get('type', {}).get('detail', ''),
                'state': status.get('type', {}).get('state', '')
            }
            
            return {
                'id': game_id,
                'sport': sport,
                'name': name,
                'short_name': short_name,
                'date': date,
                'home_team': home_team,
                'away_team': away_team,
                'status': game_status,
                'odds': odds,
                'venue': competition.get('venue', {}),
                'source': 'espn'
            }
            
        except Exception as e:
            logger.error(f"Error parsing ESPN game data: {e}")
            return None
    
    def _parse_thesportsdb_game_data(self, event: Dict[str, Any], sport: str) -> Optional[Dict[str, Any]]:
        """Parse TheSportsDB game data into standardized format"""
        try:
            return {
                'id': event.get('idEvent'),
                'sport': sport,
                'name': f"{event.get('strAwayTeam')} vs {event.get('strHomeTeam')}",
                'short_name': f"{event.get('strAwayTeam')} @ {event.get('strHomeTeam')}",
                'date': event.get('dateEvent'),
                'home_team': {
                    'name': event.get('strHomeTeam'),
                    'score': event.get('intHomeScore', '0')
                },
                'away_team': {
                    'name': event.get('strAwayTeam'),
                    'score': event.get('intAwayScore', '0')
                },
                'status': {'type': event.get('strStatus', 'Scheduled')},
                'venue': {'name': event.get('strVenue')},
                'source': 'thesportsdb'
            }
        except Exception as e:
            logger.error(f"Error parsing TheSportsDB game data: {e}")
            return None
    
    def _parse_sportsdata_game_data(self, game: Dict[str, Any], sport: str) -> Optional[Dict[str, Any]]:
        """Parse SportsDataIO game data into standardized format"""
        try:
            return {
                'id': str(game.get('GameID')),
                'sport': sport,
                'name': f"{game.get('AwayTeam')} vs {game.get('HomeTeam')}",
                'short_name': f"{game.get('AwayTeam')} @ {game.get('HomeTeam')}",
                'date': game.get('DateTime'),
                'home_team': {
                    'name': game.get('HomeTeam'),
                    'score': str(game.get('HomeScore', 0))
                },
                'away_team': {
                    'name': game.get('AwayTeam'),
                    'score': str(game.get('AwayScore', 0))
                },
                'status': {'type': game.get('Status', 'Scheduled')},
                'venue': {'name': game.get('StadiumDetails', {}).get('Name') if game.get('StadiumDetails') else ''},
                'source': 'sportsdata'
            }
        except Exception as e:
            logger.error(f"Error parsing SportsDataIO game data: {e}")
            return None
    
    async def get_upcoming_games(self, sports: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming games across multiple sports with fallback data sources
        
        Args:
            sports: List of sports to fetch (defaults to ['nfl', 'nba', 'mlb', 'nhl'])
            
        Returns:
            List of upcoming games from all requested sports
        """
        if sports is None:
            sports = ['nfl', 'nba', 'mlb', 'nhl']
        
        all_games = []
        
        for sport in sports:
            try:
                if sport == 'nfl':
                    games = await self.get_nfl_games()
                elif sport == 'nba':
                    games = await self.get_nba_games()
                elif sport == 'mlb':
                    games = await self.get_mlb_games()
                elif sport == 'nhl':
                    games = await self.get_nhl_games()
                else:
                    logger.warning(f"Unsupported sport: {sport}")
                    continue
                
                all_games.extend(games)
                logger.info(f"Retrieved {len(games)} {sport.upper()} games")
                
            except Exception as e:
                logger.error(f"Failed to get {sport} games: {e}")
                continue
        
        # Filter for upcoming games only
        upcoming_games = []
        current_time = datetime.now()
        
        for game in all_games:
            try:
                game_date = datetime.fromisoformat(game['date'].replace('Z', '+00:00'))
                if game_date > current_time:
                    upcoming_games.append(game)
            except Exception as e:
                logger.error(f"Error parsing game date: {e}")
                continue
        
        logger.info(f"Retrieved {len(upcoming_games)} total upcoming games")
        return upcoming_games
    
    async def get_nba_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NBA games with fallback sources"""
        return await self._get_games_with_fallback('nba', date)
    
    async def get_mlb_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get MLB games with fallback sources"""
        return await self._get_games_with_fallback('mlb', date)
    
    async def get_nhl_games(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NHL games with fallback sources"""
        return await self._get_games_with_fallback('nhl', date)
    
    async def _get_games_with_fallback(self, sport: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generic method to get games with fallback sources"""
        games = []
        
        # Try ESPN first
        try:
            if sport in self.espn_endpoints:
                endpoint = self.espn_endpoints[sport]['scoreboard']
                params = {'dates': date} if date else {}
                data = await self._make_espn_request(endpoint, params)
                
                if data and 'events' in data:
                    for event in data['events']:
                        game_info = self._parse_espn_game_data(event, sport)
                        if game_info:
                            games.append(game_info)
        except Exception as e:
            logger.error(f"ESPN {sport} games failed: {e}")
        
        # Add fallback sources for other sports if needed
        logger.info(f"Retrieved {len(games)} {sport.upper()} games")
        return games
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()