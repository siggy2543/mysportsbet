"""
DraftKings API Integration Service for Automated Sports Betting
Handles authentication, market analysis, and bet placement automation
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import hashlib
import hmac
import base64
from urllib.parse import urlencode, urlparse
import time

from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class DraftKingsCredentials:
    """DraftKings account credentials"""
    username: str
    password: str
    state: str  # US state for legal compliance
    api_key: Optional[str] = None
    session_token: Optional[str] = None

@dataclass
class BettingMarket:
    """DraftKings betting market structure"""
    market_id: str
    sport: str
    league: str
    event_id: str
    home_team: str
    away_team: str
    event_date: datetime
    market_type: str  # "moneyline", "spread", "total", "props"
    selections: List[Dict[str, Any]]
    status: str
    live_betting: bool

@dataclass
class BetSelection:
    """Individual bet selection"""
    selection_id: str
    market_id: str
    selection_name: str
    odds: float  # Decimal odds
    american_odds: int
    price: float
    line: Optional[float]  # For spreads/totals
    is_available: bool

@dataclass
class PlacedBet:
    """Placed bet details"""
    bet_id: str
    selection_ids: List[str]
    bet_type: str  # "single", "parlay"
    stake: float
    potential_payout: float
    odds: float
    status: str
    placed_at: datetime
    settled_at: Optional[datetime] = None
    result: Optional[str] = None  # "won", "lost", "void"

@dataclass 
class ParlayBet:
    """Multi-selection parlay bet"""
    selections: List[BetSelection]
    combined_odds: float
    stake: float
    potential_payout: float
    correlation_risk: str  # "low", "medium", "high"

class DraftKingsBettingService:
    """
    Automated DraftKings betting service with market analysis and bet placement
    Implements DraftKings Sportsbook API for programmatic betting
    """
    
    # DraftKings API endpoints (these would be the actual DK API URLs)
    BASE_URL = "https://api.draftkings.com"  # Placeholder - actual API endpoints
    SPORTSBOOK_URL = "https://sportsbook-api.draftkings.com"
    
    def __init__(self, credentials: DraftKingsCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
        self.session_token = None
        self.user_id = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        # Betting limits and controls
        self.max_single_bet = 100.0  # Maximum single bet amount
        self.max_daily_exposure = 500.0  # Maximum daily total exposure
        self.current_daily_exposure = 0.0
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with proper headers"""
        if self.session is None or self.session.closed:
            headers = {
                'User-Agent': 'SportsApp/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if self.session_token:
                headers['Authorization'] = f'Bearer {self.session_token}'
                
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=headers
            )
        return self.session
    
    async def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def _make_authenticated_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to DraftKings API"""
        await self._rate_limit()
        
        if not self.authenticated:
            await self.authenticate()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == "GET":
                async with session.get(url, params=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == "PUT":
                async with session.put(url, json=data) as response:
                    return await self._handle_response(response)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except Exception as e:
            logger.error(f"DraftKings API request failed: {e}")
            return {"error": str(e)}
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response with proper error handling"""
        if response.status == 401:
            logger.warning("Authentication expired, re-authenticating...")
            self.authenticated = False
            await self.authenticate()
            raise Exception("Authentication required")
        elif response.status == 429:
            logger.warning("Rate limit exceeded, waiting...")
            await asyncio.sleep(5)
            raise Exception("Rate limited")
        elif response.status in [200, 201]:
            try:
                return await response.json()
            except Exception:
                return {"status": "success", "data": await response.text()}
        else:
            error_text = await response.text()
            logger.error(f"DraftKings API error {response.status}: {error_text}")
            return {"error": f"API error {response.status}: {error_text}"}
    
    async def authenticate(self) -> bool:
        """
        Authenticate with DraftKings API
        NOTE: This is a placeholder implementation. Real DraftKings integration
        would require their official API access and proper OAuth flow.
        """
        try:
            # Placeholder authentication logic
            # In reality, this would involve:
            # 1. OAuth flow or API key authentication
            # 2. Session management
            # 3. Token refresh handling
            
            auth_data = {
                "username": self.credentials.username,
                "password": self.credentials.password,
                "state": self.credentials.state
            }
            
            # Simulate authentication (placeholder)
            logger.info("Authenticating with DraftKings...")
            
            # For demo purposes, we'll simulate successful authentication
            self.session_token = f"demo_token_{int(time.time())}"
            self.user_id = "demo_user_123"
            self.authenticated = True
            
            logger.info("Successfully authenticated with DraftKings")
            return True
            
        except Exception as e:
            logger.error(f"DraftKings authentication failed: {e}")
            self.authenticated = False
            return False
    
    async def get_available_markets(self, sport: Optional[str] = None, league: Optional[str] = None) -> List[BettingMarket]:
        """
        Retrieve available betting markets from DraftKings
        """
        try:
            params = {}
            if sport:
                params['sport'] = sport
            if league:
                params['league'] = league
            
            # Placeholder for actual DraftKings API call
            response = await self._make_authenticated_request("GET", "/sportsbook/markets", params)
            
            markets = []
            
            # In a real implementation, this would parse actual DraftKings market data
            # For demo purposes, we'll create sample markets
            if not response.get("error"):
                sample_markets = self._generate_sample_markets()
                markets.extend(sample_markets)
            
            logger.info(f"Retrieved {len(markets)} betting markets")
            return markets
            
        except Exception as e:
            logger.error(f"Error retrieving betting markets: {e}")
            return []
    
    def _generate_sample_markets(self) -> List[BettingMarket]:
        """Generate sample betting markets for demonstration"""
        today = datetime.now()
        return [
            BettingMarket(
                market_id="nfl_game_1",
                sport="football",
                league="nfl", 
                event_id="event_123",
                home_team="Kansas City Chiefs",
                away_team="Buffalo Bills",
                event_date=today + timedelta(days=1),
                market_type="moneyline",
                selections=[
                    {"id": "sel_1", "name": "Kansas City Chiefs", "odds": 1.85, "american_odds": -118},
                    {"id": "sel_2", "name": "Buffalo Bills", "odds": 2.05, "american_odds": +105}
                ],
                status="active",
                live_betting=False
            ),
            BettingMarket(
                market_id="nba_game_1",
                sport="basketball",
                league="nba",
                event_id="event_456", 
                home_team="Los Angeles Lakers",
                away_team="Boston Celtics",
                event_date=today + timedelta(hours=6),
                market_type="spread",
                selections=[
                    {"id": "sel_3", "name": "Lakers -5.5", "odds": 1.91, "american_odds": -110, "line": -5.5},
                    {"id": "sel_4", "name": "Celtics +5.5", "odds": 1.91, "american_odds": -110, "line": +5.5}
                ],
                status="active",
                live_betting=True
            )
        ]
    
    async def place_single_bet(self, selection: BetSelection, stake: float) -> PlacedBet:
        """
        Place a single bet on DraftKings
        """
        try:
            # Risk management checks
            if stake > self.max_single_bet:
                raise ValueError(f"Stake ${stake} exceeds maximum single bet limit ${self.max_single_bet}")
            
            if self.current_daily_exposure + stake > self.max_daily_exposure:
                raise ValueError(f"Bet would exceed daily exposure limit ${self.max_daily_exposure}")
            
            # Prepare bet slip
            bet_data = {
                "selections": [selection.selection_id],
                "stake": stake,
                "bet_type": "single",
                "odds": selection.odds
            }
            
            # Place bet via API
            response = await self._make_authenticated_request("POST", "/sportsbook/bets", bet_data)
            
            if response.get("error"):
                raise Exception(f"Bet placement failed: {response['error']}")
            
            # Create placed bet record
            placed_bet = PlacedBet(
                bet_id=response.get("bet_id", f"demo_bet_{int(time.time())}"),
                selection_ids=[selection.selection_id],
                bet_type="single",
                stake=stake,
                potential_payout=stake * selection.odds,
                odds=selection.odds,
                status="placed",
                placed_at=datetime.now()
            )
            
            # Update exposure tracking
            self.current_daily_exposure += stake
            
            logger.info(f"Successfully placed single bet: ${stake} on {selection.selection_name}")
            return placed_bet
            
        except Exception as e:
            logger.error(f"Error placing single bet: {e}")
            raise
    
    async def place_parlay_bet(self, parlay: ParlayBet) -> PlacedBet:
        """
        Place a parlay bet with multiple selections
        """
        try:
            # Risk management checks
            if parlay.stake > self.max_single_bet:
                raise ValueError(f"Parlay stake ${parlay.stake} exceeds maximum bet limit")
            
            if self.current_daily_exposure + parlay.stake > self.max_daily_exposure:
                raise ValueError(f"Parlay would exceed daily exposure limit")
            
            # Validate selections are still available
            for selection in parlay.selections:
                if not selection.is_available:
                    raise ValueError(f"Selection {selection.selection_name} is no longer available")
            
            # Check for correlation risk
            if parlay.correlation_risk == "high":
                logger.warning("High correlation risk detected in parlay")
            
            # Prepare parlay bet slip
            bet_data = {
                "selections": [sel.selection_id for sel in parlay.selections],
                "stake": parlay.stake,
                "bet_type": "parlay",
                "combined_odds": parlay.combined_odds
            }
            
            # Place parlay bet
            response = await self._make_authenticated_request("POST", "/sportsbook/parlays", bet_data)
            
            if response.get("error"):
                raise Exception(f"Parlay placement failed: {response['error']}")
            
            # Create placed bet record
            placed_bet = PlacedBet(
                bet_id=response.get("bet_id", f"parlay_{int(time.time())}"),
                selection_ids=[sel.selection_id for sel in parlay.selections],
                bet_type="parlay",
                stake=parlay.stake,
                potential_payout=parlay.potential_payout,
                odds=parlay.combined_odds,
                status="placed",
                placed_at=datetime.now()
            )
            
            # Update exposure tracking
            self.current_daily_exposure += parlay.stake
            
            logger.info(f"Successfully placed parlay bet: ${parlay.stake} on {len(parlay.selections)} selections")
            return placed_bet
            
        except Exception as e:
            logger.error(f"Error placing parlay bet: {e}")
            raise
    
    async def get_bet_status(self, bet_id: str) -> Dict[str, Any]:
        """Check the status of a placed bet"""
        try:
            response = await self._make_authenticated_request("GET", f"/sportsbook/bets/{bet_id}")
            
            if response.get("error"):
                return {"error": response["error"]}
            
            return response
            
        except Exception as e:
            logger.error(f"Error checking bet status: {e}")
            return {"error": str(e)}
    
    async def get_account_balance(self) -> Dict[str, float]:
        """Get current account balance and betting limits"""
        try:
            response = await self._make_authenticated_request("GET", "/account/balance")
            
            if response.get("error"):
                return {"error": response["error"]}
            
            # Return demo balance data
            return {
                "available_balance": 1000.0,
                "pending_bets": self.current_daily_exposure,
                "daily_limit": self.max_daily_exposure,
                "remaining_daily": self.max_daily_exposure - self.current_daily_exposure
            }
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return {"error": str(e)}
    
    async def find_best_odds(self, markets: List[BettingMarket], bet_type: str) -> List[BetSelection]:
        """
        Find the best odds for a specific bet type across markets
        """
        best_selections = []
        
        try:
            filtered_markets = [m for m in markets if m.market_type == bet_type]
            
            for market in filtered_markets:
                for selection_data in market.selections:
                    selection = BetSelection(
                        selection_id=selection_data["id"],
                        market_id=market.market_id,
                        selection_name=selection_data["name"],
                        odds=selection_data["odds"],
                        american_odds=selection_data["american_odds"],
                        price=selection_data["odds"],
                        line=selection_data.get("line"),
                        is_available=True
                    )
                    best_selections.append(selection)
            
            # Sort by best odds (highest for positive bets)
            best_selections.sort(key=lambda x: x.odds, reverse=True)
            
            logger.info(f"Found {len(best_selections)} selections for {bet_type}")
            return best_selections
            
        except Exception as e:
            logger.error(f"Error finding best odds: {e}")
            return []
    
    async def create_optimized_parlay(self, individual_picks: List[Dict[str, Any]], max_legs: int = 6) -> List[ParlayBet]:
        """
        Create optimized parlay combinations from individual picks
        """
        try:
            parlays = []
            
            # Filter high-confidence picks
            high_confidence_picks = [
                pick for pick in individual_picks 
                if pick.get("confidence_score", 0) >= 0.7
            ]
            
            if len(high_confidence_picks) < 2:
                logger.warning("Insufficient high-confidence picks for parlay creation")
                return []
            
            # Create 2-leg to max_legs parlays
            for num_legs in range(2, min(len(high_confidence_picks) + 1, max_legs + 1)):
                from itertools import combinations
                
                for combo in combinations(high_confidence_picks, num_legs):
                    # Calculate combined odds (simplified)
                    combined_odds = 1.0
                    selections = []
                    
                    for pick in combo:
                        # Create dummy selection for demo
                        selection = BetSelection(
                            selection_id=f"sel_{pick.get('game_id', 'unknown')}",
                            market_id=f"market_{pick.get('game_id', 'unknown')}",
                            selection_name=pick.get("prediction", "Unknown"),
                            odds=2.0,  # Default odds
                            american_odds=100,
                            price=2.0,
                            line=None,
                            is_available=True
                        )
                        selections.append(selection)
                        combined_odds *= selection.odds
                    
                    # Determine stake based on confidence and risk
                    avg_confidence = sum(pick.get("confidence_score", 0.5) for pick in combo) / len(combo)
                    base_stake = 20.0  # Base parlay stake
                    risk_adjusted_stake = base_stake * avg_confidence
                    
                    parlay = ParlayBet(
                        selections=selections,
                        combined_odds=combined_odds,
                        stake=min(risk_adjusted_stake, self.max_single_bet),
                        potential_payout=risk_adjusted_stake * combined_odds,
                        correlation_risk="low" if num_legs <= 3 else "medium"
                    )
                    
                    parlays.append(parlay)
                    
                    # Limit number of parlays generated
                    if len(parlays) >= 10:
                        break
                
                if len(parlays) >= 10:
                    break
            
            # Sort by potential ROI
            parlays.sort(key=lambda p: (p.potential_payout / p.stake), reverse=True)
            
            logger.info(f"Generated {len(parlays)} optimized parlay combinations")
            return parlays[:5]  # Return top 5 parlays
            
        except Exception as e:
            logger.error(f"Error creating optimized parlays: {e}")
            return []
    
    async def execute_betting_strategy(self, predictions: Dict[str, Any], bankroll: float = 1000.0) -> Dict[str, Any]:
        """
        Execute complete betting strategy based on AI predictions
        """
        try:
            results = {
                "individual_bets": [],
                "parlay_bets": [],
                "total_stake": 0.0,
                "potential_payout": 0.0,
                "errors": []
            }
            
            # Get available markets
            markets = await self.get_available_markets()
            
            if not markets:
                return {"error": "No betting markets available"}
            
            # Process individual picks
            individual_picks = predictions.get("individual_picks", [])
            
            for pick in individual_picks:
                if pick.get("confidence_score", 0) >= 0.8:  # High confidence threshold
                    try:
                        # Find matching market (simplified matching)
                        matching_selections = await self.find_best_odds(markets, pick.get("recommended_bet_type", "moneyline"))
                        
                        if matching_selections:
                            selection = matching_selections[0]  # Best odds
                            stake = min(pick.get("suggested_stake", 0.02) * bankroll, self.max_single_bet)
                            
                            placed_bet = await self.place_single_bet(selection, stake)
                            results["individual_bets"].append(asdict(placed_bet))
                            results["total_stake"] += stake
                            results["potential_payout"] += placed_bet.potential_payout
                            
                    except Exception as e:
                        results["errors"].append(f"Failed to place individual bet: {str(e)}")
            
            # Process parlay recommendations
            parlay_recommendations = predictions.get("parlay_recommendations", [])
            
            for parlay_rec in parlay_recommendations[:3]:  # Limit to top 3 parlays
                try:
                    # Create parlay from recommendation (simplified)
                    optimized_parlays = await self.create_optimized_parlay(individual_picks, 4)
                    
                    if optimized_parlays:
                        parlay = optimized_parlays[0]  # Best parlay
                        placed_bet = await self.place_parlay_bet(parlay)
                        results["parlay_bets"].append(asdict(placed_bet))
                        results["total_stake"] += parlay.stake
                        results["potential_payout"] += placed_bet.potential_payout
                        
                except Exception as e:
                    results["errors"].append(f"Failed to place parlay bet: {str(e)}")
            
            # Risk management summary
            results["risk_summary"] = {
                "total_exposure": results["total_stake"],
                "exposure_percentage": (results["total_stake"] / bankroll) * 100,
                "potential_roi": ((results["potential_payout"] - results["total_stake"]) / results["total_stake"]) * 100 if results["total_stake"] > 0 else 0,
                "daily_limit_remaining": self.max_daily_exposure - self.current_daily_exposure
            }
            
            logger.info(f"Executed betting strategy: ${results['total_stake']} staked, ${results['potential_payout']} potential payout")
            return results
            
        except Exception as e:
            logger.error(f"Error executing betting strategy: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Clean up session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Factory function for creating DraftKings service
def create_draftkings_service(username: str, password: str, state: str) -> DraftKingsBettingService:
    """Create DraftKings service with credentials"""
    credentials = DraftKingsCredentials(
        username=username,
        password=password,
        state=state
    )
    return DraftKingsBettingService(credentials)