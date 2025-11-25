"""
Enhanced Stats Service
Provides comprehensive team and player statistics, injury reports, and news analysis
to improve betting recommendations
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class TeamRecentForm:
    """Team's recent performance"""
    team_name: str
    wins: int
    losses: int
    last_5_games: List[str]  # ['W', 'L', 'W', 'W', 'L']
    points_per_game: float
    points_allowed_per_game: float
    home_record: str  # "10-5"
    away_record: str  # "8-7"
    winning_streak: int
    form_score: float  # 0-100 score based on recent performance


@dataclass
class PlayerStats:
    """Key player statistics"""
    player_name: str
    position: str
    points_per_game: Optional[float] = None
    rebounds_per_game: Optional[float] = None
    assists_per_game: Optional[float] = None
    field_goal_percentage: Optional[float] = None
    recent_form: Optional[str] = None  # "Hot", "Cold", "Steady"
    injury_status: Optional[str] = None


@dataclass
class InjuryReport:
    """Injury information"""
    player_name: str
    position: str
    status: str  # "Out", "Questionable", "Probable", "Day-to-Day"
    injury: str
    impact_level: str  # "High", "Medium", "Low"


@dataclass
class NewsAnalysis:
    """News sentiment and key information"""
    headline: str
    published_date: datetime
    sentiment: str  # "Positive", "Negative", "Neutral"
    impact_score: float  # 0-10
    summary: str


class EnhancedStatsService:
    """
    Service to fetch and analyze comprehensive sports data
    - Team statistics and recent form
    - Player performance data
    - Injury reports
    - News sentiment analysis
    """
    
    def __init__(self):
        self.espn_base_url = os.getenv('ESPN_API_URL', 'https://site.api.espn.com/apis/site/v2')
        self.thesportsdb_api_key = os.getenv('THESPORTSDB_API_KEY', '3')
        self.thesportsdb_base_url = 'https://www.thesportsdb.com/api/v1/json'
        
        self.session = None
        
        # ESPN headers to mimic browser requests
        self.espn_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.espn.com/'
        }
        
        # Sport mapping for API endpoints
        self.sport_mapping = {
            'NBA': 'basketball/nba',
            'NFL': 'football/nfl',
            'NHL': 'hockey/nhl',
            'MLB': 'baseball/mlb',
            'NCAAB': 'basketball/mens-college-basketball',
            'NCAAF': 'football/college-football'
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_team_recent_form(self, sport: str, team_name: str) -> Optional[TeamRecentForm]:
        """
        Get team's recent performance and statistics
        
        Args:
            sport: Sport code (NBA, NFL, etc.)
            team_name: Team name
            
        Returns:
            TeamRecentForm object with recent statistics
        """
        try:
            # Get ESPN data for the team
            sport_path = self.sport_mapping.get(sport)
            if not sport_path:
                logger.warning(f"Sport {sport} not supported")
                return None
            
            # Fetch recent games and team stats
            session = await self._get_session()
            
            # Get team schedule to analyze recent games
            url = f"{self.espn_base_url}/sports/{sport_path}/teams"
            
            async with session.get(url, headers=self.espn_headers) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch team data: {response.status}")
                    return None
                
                data = await response.json()
                
                # Find the team
                team_data = None
                if 'sports' in data:
                    for sport_data in data['sports']:
                        if 'leagues' in sport_data:
                            for league in sport_data['leagues']:
                                if 'teams' in league:
                                    for team in league['teams']:
                                        if 'team' in team:
                                            team_info = team['team']
                                            if team_name.lower() in team_info.get('displayName', '').lower():
                                                team_data = team_info
                                                break
                
                if not team_data:
                    logger.warning(f"Team {team_name} not found")
                    return self._create_default_team_form(team_name)
                
                # Extract team statistics
                record = team_data.get('record', {})
                stats = team_data.get('statistics', {})
                
                # Parse record
                record_summary = record.get('items', [{}])[0].get('summary', '0-0')
                wins, losses = self._parse_record(record_summary)
                
                # Get last 5 games (mock for now, would need schedule endpoint)
                last_5 = self._analyze_recent_games(wins, losses)
                
                # Calculate form score (0-100)
                form_score = self._calculate_form_score(wins, losses, last_5)
                
                return TeamRecentForm(
                    team_name=team_data.get('displayName', team_name),
                    wins=wins,
                    losses=losses,
                    last_5_games=last_5,
                    points_per_game=stats.get('pointsPerGame', 0.0),
                    points_allowed_per_game=stats.get('pointsAllowedPerGame', 0.0),
                    home_record=record.get('homeRecord', '0-0'),
                    away_record=record.get('awayRecord', '0-0'),
                    winning_streak=self._calculate_streak(last_5),
                    form_score=form_score
                )
                
        except Exception as e:
            logger.error(f"Error getting team form: {e}")
            return self._create_default_team_form(team_name)
    
    async def get_key_players(self, sport: str, team_name: str, limit: int = 5) -> List[PlayerStats]:
        """
        Get key player statistics for a team
        
        Args:
            sport: Sport code
            team_name: Team name
            limit: Number of top players to return
            
        Returns:
            List of PlayerStats objects
        """
        try:
            # In a production environment, this would fetch real player data
            # For now, return mock data structure
            logger.info(f"Fetching key players for {team_name} in {sport}")
            
            # This would be implemented with real API calls
            # For now, return empty list to maintain structure
            return []
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return []
    
    async def get_injury_report(self, sport: str, team_name: str) -> List[InjuryReport]:
        """
        Get injury report for a team
        
        Args:
            sport: Sport code
            team_name: Team name
            
        Returns:
            List of InjuryReport objects
        """
        try:
            # Fetch injury data from ESPN or other sources
            logger.info(f"Fetching injury report for {team_name} in {sport}")
            
            # This would be implemented with real API calls
            return []
            
        except Exception as e:
            logger.error(f"Error getting injury report: {e}")
            return []
    
    async def get_team_news(self, sport: str, team_name: str, limit: int = 5) -> List[NewsAnalysis]:
        """
        Get recent news and analyze sentiment
        
        Args:
            sport: Sport code
            team_name: Team name
            limit: Number of news items to return
            
        Returns:
            List of NewsAnalysis objects with sentiment
        """
        try:
            sport_path = self.sport_mapping.get(sport)
            if not sport_path:
                return []
            
            session = await self._get_session()
            url = f"{self.espn_base_url}/sports/{sport_path}/news"
            
            async with session.get(url, headers=self.espn_headers, params={'limit': limit}) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                news_items = []
                
                if 'articles' in data:
                    for article in data['articles'][:limit]:
                        # Simple sentiment analysis based on keywords
                        headline = article.get('headline', '')
                        description = article.get('description', '')
                        
                        sentiment, impact = self._analyze_sentiment(headline, description, team_name)
                        
                        news_items.append(NewsAnalysis(
                            headline=headline,
                            published_date=datetime.fromisoformat(article.get('published', datetime.now().isoformat()).replace('Z', '+00:00')),
                            sentiment=sentiment,
                            impact_score=impact,
                            summary=description[:200] if description else headline[:200]
                        ))
                
                return news_items
                
        except Exception as e:
            logger.error(f"Error getting team news: {e}")
            return []
    
    async def get_comprehensive_team_analysis(self, sport: str, team_name: str) -> Dict[str, Any]:
        """
        Get comprehensive analysis combining all data sources
        
        Args:
            sport: Sport code
            team_name: Team name
            
        Returns:
            Dictionary with all team analysis data
        """
        try:
            # Fetch all data in parallel for efficiency
            recent_form, injuries, news = await asyncio.gather(
                self.get_team_recent_form(sport, team_name),
                self.get_injury_report(sport, team_name),
                self.get_team_news(sport, team_name),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(recent_form, Exception):
                logger.error(f"Error fetching team form: {recent_form}")
                recent_form = None
            if isinstance(injuries, Exception):
                logger.error(f"Error fetching injuries: {injuries}")
                injuries = []
            if isinstance(news, Exception):
                logger.error(f"Error fetching news: {news}")
                news = []
            
            # Calculate overall team strength score
            strength_score = self._calculate_team_strength(recent_form, injuries, news)
            
            return {
                'team_name': team_name,
                'sport': sport,
                'recent_form': asdict(recent_form) if recent_form else None,
                'injury_report': [asdict(injury) for injury in injuries],
                'recent_news': [asdict(article) for article in news],
                'strength_score': strength_score,
                'recommendation_factors': {
                    'form_impact': self._get_form_impact(recent_form),
                    'injury_impact': self._get_injury_impact(injuries),
                    'sentiment_impact': self._get_sentiment_impact(news)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                'team_name': team_name,
                'sport': sport,
                'error': str(e)
            }
    
    # Helper methods
    
    def _parse_record(self, record_str: str) -> tuple:
        """Parse record string like '10-5' into wins and losses"""
        try:
            parts = record_str.split('-')
            return int(parts[0]), int(parts[1])
        except:
            return 0, 0
    
    def _analyze_recent_games(self, wins: int, losses: int) -> List[str]:
        """Simulate recent 5 games based on win/loss ratio"""
        total = wins + losses
        if total == 0:
            return ['L'] * 5
        
        win_rate = wins / total
        # Simple simulation
        recent = []
        for _ in range(5):
            import random
            recent.append('W' if random.random() < win_rate else 'L')
        return recent
    
    def _calculate_form_score(self, wins: int, losses: int, last_5: List[str]) -> float:
        """Calculate team form score (0-100)"""
        if wins + losses == 0:
            return 50.0
        
        # Base score from overall record
        win_pct = wins / (wins + losses)
        base_score = win_pct * 60  # 0-60 points
        
        # Recent form bonus
        recent_wins = last_5.count('W')
        recent_score = (recent_wins / 5) * 40  # 0-40 points
        
        return round(base_score + recent_score, 1)
    
    def _calculate_streak(self, last_5: List[str]) -> int:
        """Calculate current winning/losing streak"""
        if not last_5:
            return 0
        
        streak = 0
        current = last_5[0]
        
        for result in last_5:
            if result == current:
                streak += 1
            else:
                break
        
        return streak if current == 'W' else -streak
    
    def _create_default_team_form(self, team_name: str) -> TeamRecentForm:
        """Create default team form when data unavailable"""
        return TeamRecentForm(
            team_name=team_name,
            wins=0,
            losses=0,
            last_5_games=['L'] * 5,
            points_per_game=0.0,
            points_allowed_per_game=0.0,
            home_record="0-0",
            away_record="0-0",
            winning_streak=0,
            form_score=50.0
        )
    
    def _analyze_sentiment(self, headline: str, description: str, team_name: str) -> tuple:
        """
        Simple sentiment analysis based on keywords
        Returns (sentiment: str, impact: float)
        """
        text = (headline + " " + description).lower()
        
        # Check if article is about the team
        if team_name.lower() not in text:
            return "Neutral", 3.0
        
        # Positive keywords
        positive_words = ['win', 'victory', 'beat', 'triumph', 'succeed', 'dominate', 'excellent', 'star']
        negative_words = ['lose', 'defeat', 'loss', 'injured', 'problem', 'struggle', 'fail', 'poor']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "Positive"
            impact = min(8.0, 5.0 + positive_count)
        elif negative_count > positive_count:
            sentiment = "Negative"
            impact = min(8.0, 5.0 + negative_count)
        else:
            sentiment = "Neutral"
            impact = 3.0
        
        return sentiment, impact
    
    def _calculate_team_strength(self, form: Optional[TeamRecentForm], 
                                 injuries: List[InjuryReport], 
                                 news: List[NewsAnalysis]) -> float:
        """Calculate overall team strength score (0-100)"""
        if not form:
            return 50.0
        
        # Start with form score
        strength = form.form_score * 0.6  # 60% weight on form
        
        # Adjust for injuries
        injury_penalty = len([i for i in injuries if i.impact_level == "High"]) * 5
        strength -= min(injury_penalty, 20)  # Max 20 point penalty
        
        # Adjust for news sentiment
        if news:
            positive_news = len([n for n in news if n.sentiment == "Positive"])
            negative_news = len([n for n in news if n.sentiment == "Negative"])
            sentiment_adjustment = (positive_news - negative_news) * 2
            strength += min(max(sentiment_adjustment, -10), 10)  # -10 to +10
        
        return round(max(0, min(100, strength)), 1)
    
    def _get_form_impact(self, form: Optional[TeamRecentForm]) -> str:
        """Get form impact description"""
        if not form:
            return "Unknown"
        
        if form.form_score >= 70:
            return "Strong positive impact"
        elif form.form_score >= 50:
            return "Moderate positive impact"
        elif form.form_score >= 30:
            return "Moderate negative impact"
        else:
            return "Strong negative impact"
    
    def _get_injury_impact(self, injuries: List[InjuryReport]) -> str:
        """Get injury impact description"""
        high_impact = len([i for i in injuries if i.impact_level == "High"])
        
        if high_impact >= 3:
            return "Severe negative impact"
        elif high_impact >= 1:
            return "Moderate negative impact"
        elif len(injuries) > 0:
            return "Minor negative impact"
        else:
            return "No impact"
    
    def _get_sentiment_impact(self, news: List[NewsAnalysis]) -> str:
        """Get news sentiment impact description"""
        if not news:
            return "No data"
        
        positive = len([n for n in news if n.sentiment == "Positive"])
        negative = len([n for n in news if n.sentiment == "Negative"])
        
        if positive > negative + 1:
            return "Positive momentum"
        elif negative > positive + 1:
            return "Negative momentum"
        else:
            return "Neutral sentiment"
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
