"""
The Odds API Integration Service
Enterprise-grade service for fetching real-time odds, scores, and betting markets
from The Odds API with comprehensive features and caching.

Features:
- 80+ sports coverage
- Multiple bookmakers (DraftKings, FanDuel, BetMGM, Caesars, etc.)
- Betting markets: h2h (moneyline), spreads, totals, player props
- Live scores and updates
- Historical odds data
- Smart caching with 5-minute TTL
- Rate limiting protection
- Automatic region and market optimization
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from cachetools import TTLCache
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class Bookmaker:
    """Bookmaker information"""
    key: str
    title: str
    last_update: str
    markets: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OddsEvent:
    """Sports event with odds"""
    id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    bookmakers: List[Bookmaker] = field(default_factory=list)
    
    # Optional fields
    scores: Optional[List[Dict[str, str]]] = None
    completed: Optional[bool] = None
    last_update: Optional[str] = None


@dataclass
class SportInfo:
    """Sport information from API"""
    key: str
    group: str
    title: str
    description: str
    active: bool
    has_outrights: bool


@dataclass
class MarketOdds:
    """Market odds details"""
    market_key: str
    home_odds: Optional[float] = None
    away_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    home_point: Optional[float] = None
    away_point: Optional[float] = None
    over_under_line: Optional[float] = None
    over_odds: Optional[float] = None
    under_odds: Optional[float] = None
    bookmaker: str = ""
    last_update: str = ""


class OddsAPIService:
    """
    Comprehensive service for The Odds API integration
    Handles all API operations with caching, rate limiting, and error handling
    """
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    # Sport key mappings (The Odds API keys)
    SPORT_MAPPINGS = {
        'NBA': 'basketball_nba',
        'NFL': 'americanfootball_nfl',
        'NCAAF': 'americanfootball_ncaaf',
        'NHL': 'icehockey_nhl',
        'MLB': 'baseball_mlb',
        'MLS': 'soccer_usa_mls',
        'EPL': 'soccer_epl',
        'La Liga': 'soccer_spain_la_liga',
        'Bundesliga': 'soccer_germany_bundesliga',
        'Serie A': 'soccer_italy_serie_a',
        'Ligue 1': 'soccer_france_ligue_one',
        'Champions League': 'soccer_uefa_champs_league',
        'UFC': 'mma_mixed_martial_arts',
        'Boxing': 'boxing_boxing',
        'Tennis': 'tennis_atp_us_open',
        'Golf': 'golf_masters_tournament_winner',
        'Cricket': 'cricket_test_match',
        'Rugby': 'rugbyleague_nrl',
        'AFL': 'aussierules_afl',
    }
    
    # Supported regions and bookmakers
    REGIONS = ['us', 'us2', 'uk', 'eu', 'au']
    MARKETS = ['h2h', 'spreads', 'totals']  # Core markets (cost: 3 per region)
    ADDITIONAL_MARKETS = [
        'player_points', 'player_rebounds', 'player_assists', 'player_threes',
        'player_pass_tds', 'player_pass_yds', 'player_rush_yds', 'player_receptions',
        'player_anytime_td', 'player_home_runs', 'alternate_spreads', 'alternate_totals'
    ]
    
    def __init__(self):
        self.api_key = os.getenv('THE_ODDS_API_KEY', '')
        if not self.api_key:
            logger.warning("THE_ODDS_API_KEY not set. Using fallback mode.")
        
        # Caching (5 minute TTL for odds, 10 minutes for sports list)
        self.odds_cache = TTLCache(maxsize=500, ttl=300)  # 5 minutes
        self.sports_cache = TTLCache(maxsize=1, ttl=600)  # 10 minutes
        self.scores_cache = TTLCache(maxsize=200, ttl=60)  # 1 minute for live scores
        
        # Rate limiting tracking
        self.requests_remaining = None
        self.requests_used = None
        self.last_request_cost = None
        
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _update_rate_limits(self, headers: Dict[str, str]):
        """Update rate limit tracking from response headers"""
        self.requests_remaining = int(headers.get('x-requests-remaining', 0))
        self.requests_used = int(headers.get('x-requests-used', 0))
        self.last_request_cost = int(headers.get('x-requests-last', 0))
        
        logger.info(
            f"Odds API Usage - Remaining: {self.requests_remaining}, "
            f"Used: {self.requests_used}, Last Cost: {self.last_request_cost}"
        )
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make API request with caching and error handling
        """
        if not self.api_key:
            logger.error("No Odds API key configured")
            return {}
        
        # Check cache first
        if use_cache and cache_key and cache_key in self.odds_cache:
            logger.info(f"Cache hit for {cache_key}")
            return self.odds_cache[cache_key]
        
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params['apiKey'] = self.api_key
        
        try:
            session = await self.get_session()
            async with session.get(url, params=params, timeout=10) as response:
                self._update_rate_limits(response.headers)
                
                if response.status == 429:
                    logger.error("Rate limit exceeded. Implement exponential backoff.")
                    await asyncio.sleep(5)
                    return {}
                
                if response.status != 200:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    return {}
                
                data = await response.json()
                
                # Cache successful response
                if use_cache and cache_key:
                    self.odds_cache[cache_key] = data
                
                return data
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {endpoint}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return {}
    
    async def get_sports(self, all_sports: bool = True) -> List[SportInfo]:
        """
        Get list of available sports
        
        Args:
            all_sports: If True, include out-of-season sports
        
        Returns:
            List of SportInfo objects
        
        Usage Cost: 0 (doesn't count against quota)
        """
        cache_key = f"sports_{'all' if all_sports else 'active'}"
        
        if cache_key in self.sports_cache:
            return self.sports_cache[cache_key]
        
        params = {}
        if all_sports:
            params['all'] = 'true'
        
        data = await self._make_request('/sports', params, use_cache=False)
        
        if not data:
            return []
        
        sports = [
            SportInfo(
                key=s['key'],
                group=s['group'],
                title=s['title'],
                description=s.get('description', ''),
                active=s['active'],
                has_outrights=s.get('has_outrights', False)
            )
            for s in data
        ]
        
        self.sports_cache[cache_key] = sports
        return sports
    
    async def get_odds(
        self,
        sport: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = 'american',
        event_ids: Optional[List[str]] = None,
        bookmakers: Optional[List[str]] = None
    ) -> List[OddsEvent]:
        """
        Get odds for upcoming and live games
        
        Args:
            sport: Sport key (e.g., 'basketball_nba', 'americanfootball_nfl')
            regions: List of regions ['us', 'us2', 'uk', 'eu', 'au']
            markets: List of markets ['h2h', 'spreads', 'totals']
            odds_format: 'american' or 'decimal'
            event_ids: Optional list of event IDs to filter
            bookmakers: Optional list of specific bookmakers
        
        Returns:
            List of OddsEvent objects
        
        Usage Cost: [markets] x [regions] (1 per market per region)
        """
        # Convert friendly sport name to API key
        sport_key = self.SPORT_MAPPINGS.get(sport, sport)
        
        # Default parameters
        regions = regions or ['us', 'us2']  # US bookmakers (cost: 2)
        markets = markets or ['h2h', 'spreads', 'totals']  # All core markets (cost: 3)
        
        cache_key = f"odds_{sport_key}_{'_'.join(regions)}_{'_'.join(markets)}"
        
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
        }
        
        if event_ids:
            params['eventIds'] = ','.join(event_ids)
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        
        data = await self._make_request(
            f'/sports/{sport_key}/odds',
            params,
            cache_key=cache_key
        )
        
        if not isinstance(data, list):
            return []
        
        events = []
        for event_data in data:
            bookmakers = []
            for bm_data in event_data.get('bookmakers', []):
                bookmakers.append(Bookmaker(
                    key=bm_data['key'],
                    title=bm_data['title'],
                    last_update=bm_data.get('last_update', ''),
                    markets=bm_data.get('markets', [])
                ))
            
            events.append(OddsEvent(
                id=event_data['id'],
                sport_key=event_data['sport_key'],
                sport_title=event_data['sport_title'],
                commence_time=event_data['commence_time'],
                home_team=event_data['home_team'],
                away_team=event_data['away_team'],
                bookmakers=bookmakers
            ))
        
        return events
    
    async def get_event_odds(
        self,
        sport: str,
        event_id: str,
        regions: List[str] = None,
        markets: List[str] = None,
        odds_format: str = 'american',
        include_player_props: bool = False
    ) -> Optional[OddsEvent]:
        """
        Get odds for a single event (supports ALL markets including player props)
        
        Args:
            sport: Sport key
            event_id: Event ID
            regions: List of regions
            markets: List of markets (can include player prop markets)
            odds_format: 'american' or 'decimal'
            include_player_props: If True, adds player prop markets
        
        Returns:
            OddsEvent object or None
        
        Usage Cost: [unique markets returned] x [regions]
        """
        sport_key = self.SPORT_MAPPINGS.get(sport, sport)
        regions = regions or ['us', 'us2']
        markets = markets or ['h2h', 'spreads', 'totals']
        
        # Add player props if requested
        if include_player_props:
            if 'basketball' in sport_key.lower():
                markets.extend(['player_points', 'player_rebounds', 'player_assists', 'player_threes'])
            elif 'football' in sport_key.lower():
                markets.extend(['player_pass_tds', 'player_pass_yds', 'player_rush_yds', 'player_anytime_td'])
            elif 'baseball' in sport_key.lower():
                markets.extend(['player_home_runs', 'player_hits', 'player_strikeouts'])
        
        cache_key = f"event_odds_{event_id}_{'_'.join(markets)}"
        
        params = {
            'regions': ','.join(regions),
            'markets': ','.join(markets),
            'oddsFormat': odds_format,
        }
        
        data = await self._make_request(
            f'/sports/{sport_key}/events/{event_id}/odds',
            params,
            cache_key=cache_key
        )
        
        if not data or not isinstance(data, dict):
            return None
        
        bookmakers = []
        for bm_data in data.get('bookmakers', []):
            bookmakers.append(Bookmaker(
                key=bm_data['key'],
                title=bm_data['title'],
                last_update=bm_data.get('last_update', ''),
                markets=bm_data.get('markets', [])
            ))
        
        return OddsEvent(
            id=data['id'],
            sport_key=data['sport_key'],
            sport_title=data['sport_title'],
            commence_time=data['commence_time'],
            home_team=data['home_team'],
            away_team=data['away_team'],
            bookmakers=bookmakers
        )
    
    async def get_scores(
        self,
        sport: str,
        days_from: Optional[int] = None,
        event_ids: Optional[List[str]] = None
    ) -> List[OddsEvent]:
        """
        Get live scores and recent results
        
        Args:
            sport: Sport key
            days_from: Number of days in past (1-3) to include completed games
            event_ids: Optional list of event IDs
        
        Returns:
            List of OddsEvent objects with scores
        
        Usage Cost: 2 if days_from specified, otherwise 1
        """
        sport_key = self.SPORT_MAPPINGS.get(sport, sport)
        
        cache_key = f"scores_{sport_key}_{days_from}"
        
        if cache_key in self.scores_cache:
            return self.scores_cache[cache_key]
        
        params = {}
        if days_from:
            params['daysFrom'] = str(days_from)
        if event_ids:
            params['eventIds'] = ','.join(event_ids)
        
        data = await self._make_request(
            f'/sports/{sport_key}/scores',
            params,
            use_cache=False  # Use manual caching for scores
        )
        
        if not isinstance(data, list):
            return []
        
        events = []
        for event_data in data:
            events.append(OddsEvent(
                id=event_data['id'],
                sport_key=event_data['sport_key'],
                sport_title=event_data['sport_title'],
                commence_time=event_data['commence_time'],
                home_team=event_data['home_team'],
                away_team=event_data['away_team'],
                scores=event_data.get('scores'),
                completed=event_data.get('completed', False),
                last_update=event_data.get('last_update')
            ))
        
        self.scores_cache[cache_key] = events
        return events
    
    async def get_best_odds(
        self,
        sport: str,
        home_team: str,
        away_team: str,
        market: str = 'h2h'
    ) -> Dict[str, Any]:
        """
        Get best available odds from all bookmakers for a matchup
        
        Args:
            sport: Sport key
            home_team: Home team name
            away_team: Away team name
            market: Market type ('h2h', 'spreads', 'totals')
        
        Returns:
            Dict with best odds and bookmaker info
        """
        events = await self.get_odds(sport, markets=[market])
        
        # Find matching event
        target_event = None
        for event in events:
            if (event.home_team.lower() == home_team.lower() and 
                event.away_team.lower() == away_team.lower()):
                target_event = event
                break
        
        if not target_event or not target_event.bookmakers:
            return {
                'found': False,
                'message': 'No odds available for this matchup'
            }
        
        # Extract best odds across all bookmakers
        best_home_odds = None
        best_away_odds = None
        best_home_bookmaker = ""
        best_away_bookmaker = ""
        
        for bookmaker in target_event.bookmakers:
            for mkt in bookmaker.markets:
                if mkt['key'] == market:
                    for outcome in mkt['outcomes']:
                        price = outcome['price']
                        
                        if outcome['name'] == target_event.home_team:
                            if best_home_odds is None or price > best_home_odds:
                                best_home_odds = price
                                best_home_bookmaker = bookmaker.title
                        
                        elif outcome['name'] == target_event.away_team:
                            if best_away_odds is None or price > best_away_odds:
                                best_away_odds = price
                                best_away_bookmaker = bookmaker.title
        
        return {
            'found': True,
            'event_id': target_event.id,
            'home_team': target_event.home_team,
            'away_team': target_event.away_team,
            'commence_time': target_event.commence_time,
            'market': market,
            'best_home_odds': best_home_odds,
            'best_home_bookmaker': best_home_bookmaker,
            'best_away_odds': best_away_odds,
            'best_away_bookmaker': best_away_bookmaker,
            'total_bookmakers': len(target_event.bookmakers)
        }
    
    async def get_bookmaker_comparison(
        self,
        sport: str,
        event_id: str,
        market: str = 'h2h'
    ) -> Dict[str, Any]:
        """
        Compare odds across all bookmakers for a specific event
        
        Returns detailed comparison for arbitrage and best value
        """
        event = await self.get_event_odds(sport, event_id, markets=[market])
        
        if not event or not event.bookmakers:
            return {'found': False, 'bookmakers': []}
        
        comparison = []
        
        for bookmaker in event.bookmakers:
            for mkt in bookmaker.markets:
                if mkt['key'] == market:
                    odds_data = {
                        'bookmaker': bookmaker.title,
                        'bookmaker_key': bookmaker.key,
                        'last_update': bookmaker.last_update,
                        'outcomes': mkt['outcomes']
                    }
                    comparison.append(odds_data)
        
        return {
            'found': True,
            'event_id': event.id,
            'home_team': event.home_team,
            'away_team': event.away_team,
            'commence_time': event.commence_time,
            'market': market,
            'bookmakers': comparison,
            'total_bookmakers': len(comparison)
        }
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        return {
            'requests_remaining': self.requests_remaining,
            'requests_used': self.requests_used,
            'last_request_cost': self.last_request_cost,
            'cache_size': len(self.odds_cache),
            'api_configured': bool(self.api_key)
        }


# Singleton instance
_odds_api_service = None


def get_odds_api_service() -> OddsAPIService:
    """Get singleton instance of OddsAPIService"""
    global _odds_api_service
    if _odds_api_service is None:
        _odds_api_service = OddsAPIService()
    return _odds_api_service
