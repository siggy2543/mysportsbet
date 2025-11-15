"""
Modern ESPN API Service using the Zuplo OpenAPI specification
Provides comprehensive sports data collection for all major leagues
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import json
from urllib.parse import urlencode

from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ESPNTeam:
    """ESPN Team data structure"""
    id: str
    name: str
    abbreviation: str
    display_name: str
    location: str
    color: str
    logo: str
    record: Dict[str, Any]
    stats: Dict[str, Any]

@dataclass
class ESPNGame:
    """ESPN Game/Event data structure"""
    id: str
    sport: str
    league: str
    home_team: ESPNTeam
    away_team: ESPNTeam
    date: datetime
    status: str
    venue: Dict[str, Any]
    weather: Optional[Dict[str, Any]]
    odds: Optional[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    situation: Optional[Dict[str, Any]]

@dataclass
class ESPNNews:
    """ESPN News article structure"""
    id: str
    headline: str
    description: str
    published: datetime
    type: str
    premium: bool
    images: List[Dict[str, Any]]
    categories: List[str]
    keywords: List[str]

class ModernESPNService:
    """
    Modern ESPN API service implementing the Zuplo OpenAPI specification
    Base URL: http://site.api.espn.com/apis/site/v2
    """
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2"
    
    # Supported sports and leagues from ESPN API
    SPORTS_CONFIG = {
        "nfl": {
            "sport": "football",
            "league": "nfl",
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "nba": {
            "sport": "basketball", 
            "league": "nba",
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "mlb": {
            "sport": "baseball",
            "league": "mlb", 
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "nhl": {
            "sport": "hockey",
            "league": "nhl",
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "college-football": {
            "sport": "football",
            "league": "college-football",
            "endpoints": ["news", "rankings", "scoreboard", "summary", "teams/{team}"]
        },
        "mens-college-basketball": {
            "sport": "basketball",
            "league": "mens-college-basketball", 
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "womens-college-basketball": {
            "sport": "basketball",
            "league": "womens-college-basketball",
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "wnba": {
            "sport": "basketball",
            "league": "wnba",
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"]
        },
        "college-baseball": {
            "sport": "baseball", 
            "league": "college-baseball",
            "endpoints": ["scoreboard"]
        },
        "soccer": {
            "sport": "soccer",
            "league": "eng.1",  # Premier League default
            "endpoints": ["news", "scoreboard", "teams", "teams/{team}"],
            "leagues": ["eng.1", "esp.1", "ger.1", "ita.1", "fra.1", "usa.1"]  # Major soccer leagues
        }
    }
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Sports-Betting-App/1.0',
                    'Accept': 'application/json'
                }
            )
        return self.session
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to ESPN API"""
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint}"
        
        if params:
            url += f"?{urlencode(params)}"
            
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched ESPN data from {endpoint}")
                    return data
                else:
                    logger.error(f"ESPN API error {response.status} for {endpoint}")
                    return {}
        except Exception as e:
            logger.error(f"ESPN API request failed for {endpoint}: {e}")
            return {}
    
    # ============= NFL ENDPOINTS =============
    async def get_nfl_scores(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get latest NFL scores"""
        params = {"dates": date} if date else None
        return await self._make_request("sports/football/nfl/scoreboard", params)
    
    async def get_nfl_news(self) -> Dict[str, Any]:
        """Get latest NFL news"""
        return await self._make_request("sports/football/nfl/news")
    
    async def get_nfl_teams(self) -> Dict[str, Any]:
        """Get all NFL teams"""
        return await self._make_request("sports/football/nfl/teams")
    
    async def get_nfl_team(self, team_abbr: str) -> Dict[str, Any]:
        """Get specific NFL team information"""
        return await self._make_request(f"sports/football/nfl/teams/{team_abbr}")
    
    # ============= NBA ENDPOINTS =============
    async def get_nba_scores(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get latest NBA scores"""
        params = {"dates": date} if date else None
        return await self._make_request("sports/basketball/nba/scoreboard", params)
    
    async def get_nba_news(self) -> Dict[str, Any]:
        """Get latest NBA news"""
        return await self._make_request("sports/basketball/nba/news")
    
    async def get_nba_teams(self) -> Dict[str, Any]:
        """Get all NBA teams"""
        return await self._make_request("sports/basketball/nba/teams")
    
    async def get_nba_team(self, team_abbr: str) -> Dict[str, Any]:
        """Get specific NBA team information"""
        return await self._make_request(f"sports/basketball/nba/teams/{team_abbr}")
    
    # ============= MLB ENDPOINTS =============
    async def get_mlb_scores(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get latest MLB scores"""
        params = {"dates": date} if date else None
        return await self._make_request("sports/baseball/mlb/scoreboard", params)
    
    async def get_mlb_news(self) -> Dict[str, Any]:
        """Get latest MLB news"""
        return await self._make_request("sports/baseball/mlb/news")
    
    async def get_mlb_teams(self) -> Dict[str, Any]:
        """Get all MLB teams"""
        return await self._make_request("sports/baseball/mlb/teams")
    
    async def get_mlb_team(self, team_abbr: str) -> Dict[str, Any]:
        """Get specific MLB team information"""
        return await self._make_request(f"sports/baseball/mlb/teams/{team_abbr}")
    
    # ============= NHL ENDPOINTS =============
    async def get_nhl_scores(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get latest NHL scores"""
        params = {"dates": date} if date else None
        return await self._make_request("sports/hockey/nhl/scoreboard", params)
    
    async def get_nhl_news(self) -> Dict[str, Any]:
        """Get latest NHL news"""
        return await self._make_request("sports/hockey/nhl/news")
    
    async def get_nhl_teams(self) -> Dict[str, Any]:
        """Get all NHL teams"""
        return await self._make_request("sports/hockey/nhl/teams")
    
    async def get_nhl_team(self, team_abbr: str) -> Dict[str, Any]:
        """Get specific NHL team information"""
        return await self._make_request(f"sports/hockey/nhl/teams/{team_abbr}")
    
    # ============= COLLEGE SPORTS ENDPOINTS =============
    async def get_college_football_scores(self, date: Optional[str] = None, calendar: Optional[str] = None) -> Dict[str, Any]:
        """Get latest college football scores"""
        params = {}
        if date:
            params["dates"] = date
        if calendar:
            params["calendar"] = calendar
        return await self._make_request("sports/football/college-football/scoreboard", params or None)
    
    async def get_college_football_rankings(self) -> Dict[str, Any]:
        """Get college football rankings"""
        return await self._make_request("sports/football/college-football/rankings")
    
    async def get_college_football_news(self) -> Dict[str, Any]:
        """Get latest college football news"""
        return await self._make_request("sports/football/college-football/news")
    
    async def get_college_football_game_summary(self, event_id: str) -> Dict[str, Any]:
        """Get specific college football game information"""
        return await self._make_request("sports/football/college-football/summary", {"event": event_id})
    
    async def get_college_football_team(self, team_abbr: str) -> Dict[str, Any]:
        """Get college football team information"""
        return await self._make_request(f"sports/football/college-football/teams/{team_abbr}")
    
    # ============= SOCCER ENDPOINTS =============
    async def get_soccer_scores(self, league: str = "eng.1", date: Optional[str] = None) -> Dict[str, Any]:
        """Get latest soccer scores by league"""
        params = {"league": league}
        if date:
            params["dates"] = date
        return await self._make_request("sports/soccer/scoreboard", params)
    
    async def get_soccer_news(self, league: str = "eng.1") -> Dict[str, Any]:
        """Get latest soccer news by league"""
        return await self._make_request("sports/soccer/news", {"league": league})
    
    async def get_soccer_teams(self, league: str = "eng.1") -> Dict[str, Any]:
        """Get all soccer teams by league"""
        return await self._make_request("sports/soccer/teams", {"league": league})
    
    async def get_soccer_team(self, team_abbr: str, league: str = "eng.1") -> Dict[str, Any]:
        """Get specific soccer team information by league"""
        return await self._make_request(f"sports/soccer/teams/{team_abbr}", {"league": league})
    
    # Alternative soccer endpoints using path parameters
    async def get_soccer_scores_by_league(self, league: str) -> Dict[str, Any]:
        """Get latest soccer scores using league path parameter"""
        return await self._make_request(f"sports/soccer/{league}/scoreboard")
    
    async def get_soccer_news_by_league(self, league: str) -> Dict[str, Any]:
        """Get latest soccer news using league path parameter"""
        return await self._make_request(f"sports/soccer/{league}/news")
    
    async def get_soccer_teams_by_league(self, league: str) -> Dict[str, Any]:
        """Get all soccer teams using league path parameter"""
        return await self._make_request(f"sports/soccer/{league}/teams")
    
    async def get_soccer_team_by_league(self, league: str, team_abbr: str) -> Dict[str, Any]:
        """Get specific soccer team using league path parameter"""
        return await self._make_request(f"sports/soccer/{league}/teams/{team_abbr}")
    
    # ============= COMPREHENSIVE DATA COLLECTION =============
    async def get_all_scores_today(self) -> Dict[str, Any]:
        """Get scores for all major sports today"""
        today = datetime.now().strftime("%Y%m%d")
        
        tasks = [
            ("nfl", self.get_nfl_scores(today)),
            ("nba", self.get_nba_scores(today)),
            ("mlb", self.get_mlb_scores(today)),
            ("nhl", self.get_nhl_scores(today)),
            ("college_football", self.get_college_football_scores(today)),
            ("premier_league", self.get_soccer_scores("eng.1", today)),
            ("mls", self.get_soccer_scores("usa.1", today))
        ]
        
        results = {}
        try:
            responses = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            for i, (sport, _) in enumerate(tasks):
                if not isinstance(responses[i], Exception):
                    results[sport] = responses[i]
                else:
                    logger.error(f"Failed to get {sport} scores: {responses[i]}")
                    results[sport] = {}
        except Exception as e:
            logger.error(f"Error collecting all scores: {e}")
        
        return results
    
    async def get_all_news_today(self) -> Dict[str, Any]:
        """Get news for all major sports"""
        tasks = [
            ("nfl", self.get_nfl_news()),
            ("nba", self.get_nba_news()),
            ("mlb", self.get_mlb_news()),
            ("nhl", self.get_nhl_news()),
            ("college_football", self.get_college_football_news()),
            ("premier_league", self.get_soccer_news("eng.1")),
            ("mls", self.get_soccer_news("usa.1"))
        ]
        
        results = {}
        try:
            responses = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            for i, (sport, _) in enumerate(tasks):
                if not isinstance(responses[i], Exception):
                    results[sport] = responses[i]
                else:
                    logger.error(f"Failed to get {sport} news: {responses[i]}")
                    results[sport] = {}
        except Exception as e:
            logger.error(f"Error collecting all news: {e}")
        
        return results
    
    # ============= DATA PROCESSING UTILITIES =============
    def parse_game_data(self, espn_data: Dict[str, Any], sport: str) -> List[ESPNGame]:
        """Parse ESPN API response into structured game data"""
        games = []
        
        if "events" in espn_data:
            for event in espn_data["events"]:
                try:
                    # Extract basic game info
                    game_id = event.get("id", "")
                    date = datetime.fromisoformat(event.get("date", "").replace("Z", "+00:00"))
                    status = event.get("status", {}).get("type", {}).get("name", "")
                    
                    # Extract teams
                    competitors = event.get("competitions", [{}])[0].get("competitors", [])
                    home_team = away_team = None
                    
                    for comp in competitors:
                        team_data = comp.get("team", {})
                        team = ESPNTeam(
                            id=team_data.get("id", ""),
                            name=team_data.get("name", ""),
                            abbreviation=team_data.get("abbreviation", ""),
                            display_name=team_data.get("displayName", ""),
                            location=team_data.get("location", ""),
                            color=team_data.get("color", ""),
                            logo=team_data.get("logo", ""),
                            record=comp.get("records", [{}])[0] if comp.get("records") else {},
                            stats=comp.get("statistics", [])
                        )
                        
                        if comp.get("homeAway") == "home":
                            home_team = team
                        else:
                            away_team = team
                    
                    if home_team and away_team:
                        game = ESPNGame(
                            id=game_id,
                            sport=sport,
                            league=espn_data.get("leagues", [{}])[0].get("abbreviation", ""),
                            home_team=home_team,
                            away_team=away_team,
                            date=date,
                            status=status,
                            venue=event.get("competitions", [{}])[0].get("venue", {}),
                            weather=event.get("weather"),
                            odds=event.get("competitions", [{}])[0].get("odds"),
                            competitors=competitors,
                            situation=event.get("competitions", [{}])[0].get("situation")
                        )
                        games.append(game)
                        
                except Exception as e:
                    logger.error(f"Error parsing game data: {e}")
                    continue
        
        return games
    
    def parse_news_data(self, espn_data: Dict[str, Any]) -> List[ESPNNews]:
        """Parse ESPN news API response into structured news data"""
        articles = []
        
        if "articles" in espn_data:
            for article in espn_data["articles"]:
                try:
                    news = ESPNNews(
                        id=str(article.get("id", "")),
                        headline=article.get("headline", ""),
                        description=article.get("description", ""),
                        published=datetime.fromisoformat(article.get("published", "").replace("Z", "+00:00")),
                        type=article.get("type", ""),
                        premium=article.get("premium", False),
                        images=article.get("images", []),
                        categories=[cat.get("description", "") for cat in article.get("categories", [])],
                        keywords=article.get("keywords", [])
                    )
                    articles.append(news)
                except Exception as e:
                    logger.error(f"Error parsing news data: {e}")
                    continue
        
        return articles
    
    async def close(self):
        """Clean up aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Global instance
espn_service = ModernESPNService()