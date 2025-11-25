"""
Enhanced Betting service for managing bets, calculations, and AI recommendations
Integrated with The Odds API for real-time odds data
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging
import asyncio

from .sports_api_service import SportsAPIService
from .cache_service import CacheService
from .openai_sports_data_service import openai_sports_service
from .odds_api_service import get_odds_api_service

logger = logging.getLogger(__name__)

class BettingService:
    """Service for managing betting operations with real odds from The Odds API"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.sports_api_service = SportsAPIService(self.cache_service)
        self.odds_api = get_odds_api_service()
    
    async def calculate_payout(self, amount: Decimal, odds: Decimal) -> Decimal:
        """Calculate potential payout for a bet"""
        if odds > 0:
            return amount * (odds / 100)
        else:
            return amount * (100 / abs(odds))
    
    async def place_bet(self, user_id: int, game_id: str, bet_type: str, 
                       amount: Decimal, odds: Decimal) -> dict:
        """Place a new bet"""
        # Placeholder implementation
        return {
            "id": 1,
            "user_id": user_id,
            "game_id": game_id,
            "bet_type": bet_type,
            "amount": amount,
            "odds": odds,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
    
    async def get_user_bets(self, user_id: int) -> List[dict]:
        """Get all bets for a user"""
        # Placeholder implementation
        return []
    
    async def settle_bet(self, bet_id: int, result: str) -> dict:
        """Settle a bet with win/loss result"""
        # Placeholder implementation
        return {"bet_id": bet_id, "result": result, "settled_at": datetime.utcnow()}
    
    async def get_bet_recommendations(self, user_id: Optional[int] = None, sport: str = "NBA", max_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Get AI-powered betting recommendations with REAL ODDS from The Odds API"""
        try:
            # Get real-time odds from The Odds API
            live_odds = await self.odds_api.get_odds(
                sport=sport,
                regions=['us', 'us2'],
                markets=['h2h', 'spreads', 'totals']
            )
            
            if not live_odds:
                logger.warning(f"No live odds available for {sport}, falling back to AI recommendations")
                # Fallback to AI-only recommendations
                ai_recommendations = await self.sports_api_service.get_betting_recommendations_with_ai(sport, max_recommendations)
                return self._enhance_recommendations(ai_recommendations, sport, user_id)
            
            # Build recommendations from real odds data
            enhanced_recommendations = []
            
            for event in live_odds[:max_recommendations]:
                if not event.bookmakers:
                    continue
                
                # Get best odds across all bookmakers
                best_home_odds = None
                best_away_odds = None
                best_home_bm = ""
                best_away_bm = ""
                
                # Extract moneyline odds
                for bookmaker in event.bookmakers:
                    for market in bookmaker.markets:
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                price = outcome['price']
                                if outcome['name'] == event.home_team:
                                    if best_home_odds is None or price > best_home_odds:
                                        best_home_odds = price
                                        best_home_bm = bookmaker.title
                                elif outcome['name'] == event.away_team:
                                    if best_away_odds is None or price > best_away_odds:
                                        best_away_odds = price
                                        best_away_bm = bookmaker.title
                
                if best_home_odds and best_away_odds:
                    # Create recommendation for best value bet
                    is_home_underdog = best_home_odds > 0
                    is_away_underdog = best_away_odds > 0
                    
                    # Recommend underdog with better odds (if any)
                    if is_home_underdog or is_away_underdog:
                        if is_home_underdog and (not is_away_underdog or best_home_odds > best_away_odds):
                            selection = event.home_team
                            odds = best_home_odds
                            bookmaker = best_home_bm
                        else:
                            selection = event.away_team
                            odds = best_away_odds
                            bookmaker = best_away_bm
                    else:
                        # Both favorites, pick less favorite
                        if abs(best_home_odds) < abs(best_away_odds):
                            selection = event.home_team
                            odds = best_home_odds
                            bookmaker = best_home_bm
                        else:
                            selection = event.away_team
                            odds = best_away_odds
                            bookmaker = best_away_bm
                    
                    # Calculate confidence based on odds
                    confidence = self._calculate_confidence_from_odds(odds)
                    
                    enhanced_rec = {
                        'id': len(enhanced_recommendations) + 1,
                        'game': f"{event.away_team} @ {event.home_team}",
                        'event_id': event.id,
                        'bet_type': 'moneyline',
                        'selection': selection,
                        'odds': int(odds),
                        'confidence': confidence,
                        'risk_level': 'Low' if odds > 150 else 'Medium' if odds > 0 else 'High',
                        'reasoning': f'Best available odds from {bookmaker}. {len(event.bookmakers)} bookmakers compared.',
                        'expected_value': self._calculate_expected_value(odds, confidence),
                        'stake_recommendation': self._calculate_kelly_stake(odds, confidence / 10),
                        'sport': sport,
                        'commence_time': event.commence_time,
                        'bookmaker': bookmaker,
                        'total_bookmakers': len(event.bookmakers),
                        'source': 'live_odds_api',
                        'timestamp': datetime.utcnow().isoformat(),
                        'user_id': user_id
                    }
                    enhanced_recommendations.append(enhanced_rec)
            
            logger.info(f"Generated {len(enhanced_recommendations)} LIVE betting recommendations for {sport} from {self.odds_api.get_usage_info()['requests_used']} API calls")
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error getting betting recommendations: {str(e)}")
            return []
    
    def _enhance_recommendations(self, ai_recommendations: List[Dict], sport: str, user_id: Optional[int]) -> List[Dict[str, Any]]:
        """Enhance AI recommendations (fallback when no live odds)"""
        enhanced = []
        for rec in ai_recommendations:
            enhanced_rec = {
                'id': len(enhanced) + 1,
                'game': rec.get('game', 'Unknown Matchup'),
                'bet_type': rec.get('bet_type', 'moneyline'),
                'selection': rec.get('selection', ''),
                'odds': rec.get('odds', -110),
                'confidence': rec.get('confidence', 5),
                'risk_level': rec.get('risk_level', 'Medium'),
                'reasoning': rec.get('reasoning', 'AI analysis recommendation'),
                'expected_value': rec.get('expected_value', '+0%'),
                'stake_recommendation': float(rec.get('stake_recommendation', 5.0)),
                'sport': rec.get('sport', sport),
                'source': 'ai_analysis_fallback',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id
            }
            enhanced.append(enhanced_rec)
        return enhanced
    
    def _calculate_confidence_from_odds(self, odds: float) -> int:
        """Calculate confidence score (1-10) from American odds"""
        if odds < 0:
            # Favorite: higher magnitude = higher confidence
            implied_prob = abs(odds) / (abs(odds) + 100)
            confidence = int(implied_prob * 10)
        else:
            # Underdog: lower odds = higher confidence
            implied_prob = 100 / (odds + 100)
            confidence = int(implied_prob * 10)
        return max(1, min(10, confidence))
    
    def _calculate_expected_value(self, odds: float, confidence: int) -> str:
        """Calculate expected value percentage"""
        if odds < 0:
            decimal_odds = 1 + (100 / abs(odds))
        else:
            decimal_odds = 1 + (odds / 100)
        
        # Simple EV calculation
        win_prob = confidence / 10
        ev = (decimal_odds * win_prob) - 1
        return f"{ev:+.1%}"
    
    def _calculate_kelly_stake(self, odds: float, win_prob: float, kelly_fraction: float = 0.25) -> float:
        """Calculate Kelly Criterion stake recommendation"""
        if odds < 0:
            decimal_odds = 1 + (100 / abs(odds))
        else:
            decimal_odds = 1 + (odds / 100)
        
        # Kelly formula: (bp - q) / b where b=decimal odds-1, p=win prob, q=1-p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        kelly = (b * p - q) / b
        
        # Use fractional Kelly (typically 25% of full Kelly)
        fractional_kelly = kelly * kelly_fraction
        
        # Convert to percentage of bankroll (assuming $200 bankroll)
        stake = max(1.0, min(10.0, fractional_kelly * 200))
        
        return round(stake, 2)
    
    async def analyze_user_strategy(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's betting strategy and performance"""
        try:
            # Get user's betting history
            user_bets = await self.get_user_bets(user_id)
            
            # Basic strategy analysis
            total_bets = len(user_bets)
            if total_bets == 0:
                return {
                    'total_bets': 0,
                    'win_rate': 0.0,
                    'profit_loss': 0.0,
                    'average_stake': 0.0,
                    'favorite_sports': [],
                    'recommendations': ['Start with small stakes', 'Focus on value bets', 'Track your performance']
                }
            
            # Calculate basic metrics
            wins = len([bet for bet in user_bets if bet.get('result') == 'win'])
            win_rate = wins / total_bets if total_bets > 0 else 0
            
            strategy_analysis = {
                'total_bets': total_bets,
                'win_rate': win_rate,
                'profit_loss': 0.0,  # Calculate from bet history
                'average_stake': 5.0,  # Default stake
                'favorite_sports': ['NBA', 'NFL'],  # Extract from bet history
                'betting_patterns': {
                    'most_common_bet_type': 'moneyline',
                    'average_odds': -110,
                    'risk_tolerance': 'Medium'
                },
                'recommendations': [
                    'Consider diversifying bet types',
                    'Track line movements for better value',
                    'Set strict bankroll limits'
                ]
            }
            
            return strategy_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user strategy: {str(e)}")
            return {}
    
    async def monitor_bet_result(self, bet_id: int):
        """Monitor a bet and update result when available"""
        try:
            # Background task to monitor bet results
            # This would typically check with the sportsbook API
            logger.info(f"Monitoring bet {bet_id} for result updates")
            
            # Simulate monitoring logic
            await asyncio.sleep(300)  # Wait 5 minutes
            
            # Check bet status and update if needed
            # In a real implementation, this would query the external betting API
            
        except Exception as e:
            logger.error(f"Error monitoring bet {bet_id}: {str(e)}")