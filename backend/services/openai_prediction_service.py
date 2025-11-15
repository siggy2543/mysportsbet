"""
OpenAI GPT Integration Service for Advanced Sports Predictions
Uses GPT-4 to analyze sports data and generate betting recommendations
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import openai
from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PredictionRequest:
    """Structure for prediction requests to OpenAI"""
    sport: str
    league: str
    home_team: str
    away_team: str
    game_date: datetime
    historical_data: Dict[str, Any]
    team_stats: Dict[str, Any]
    recent_news: List[str]
    weather_conditions: Optional[Dict[str, Any]] = None
    injury_reports: Optional[List[str]] = None

@dataclass
class BettingRecommendation:
    """OpenAI betting recommendation structure"""
    game_id: str
    confidence_score: float  # 0.0 to 1.0
    recommended_bet_type: str  # "moneyline", "spread", "over_under", "parlay"
    prediction: str
    reasoning: str
    risk_level: str  # "low", "medium", "high"
    suggested_stake: float  # percentage of bankroll
    key_factors: List[str]
    alternative_bets: List[Dict[str, Any]]

@dataclass
class ParlayRecommendation:
    """Multi-game parlay recommendation"""
    games: List[str]  # game IDs
    total_confidence: float
    combined_odds: float
    expected_payout: float
    risk_assessment: str
    reasoning: str
    individual_picks: List[BettingRecommendation]

class OpenAIPredictonService:
    """
    Advanced sports prediction service using OpenAI GPT models
    Analyzes comprehensive sports data to generate intelligent betting recommendations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # Use latest GPT-4 model
        
        # Betting strategy templates
        self.system_prompts = {
            "game_analysis": """You are an expert sports analyst and betting strategist with deep knowledge of statistical analysis, team performance metrics, and betting market dynamics. 

Analyze the provided sports data and generate intelligent betting recommendations based on:
1. Team statistics and recent performance
2. Historical head-to-head records
3. Player injuries and availability
4. Weather conditions (for outdoor sports)
5. Recent news and team dynamics
6. Market sentiment and public betting trends

Provide specific, actionable betting recommendations with detailed reasoning and risk assessment.""",

            "parlay_optimizer": """You are a sophisticated parlay betting optimizer. Your goal is to identify the best combination of individual bets that maximize expected value while managing risk.

Consider:
1. Correlation between games (avoid conflicting bets)
2. Individual confidence levels for each pick
3. Combined probability and expected payout
4. Risk diversification across different sports/leagues
5. Bankroll management principles

Generate parlay combinations that offer the best risk-adjusted returns.""",

            "risk_manager": """You are a professional bankroll management advisor specializing in sports betting. Your primary concern is capital preservation while maximizing long-term profitability.

Evaluate each betting opportunity for:
1. Kelly Criterion optimal bet sizing
2. Risk-reward ratio assessment
3. Variance and drawdown potential
4. Portfolio diversification
5. Market efficiency and edge identification

Recommend appropriate stake sizes and risk management strategies."""
        }
    
    async def analyze_game(self, prediction_request: PredictionRequest) -> BettingRecommendation:
        """
        Analyze a single game and generate betting recommendation using OpenAI
        """
        try:
            # Prepare comprehensive data for analysis
            analysis_prompt = self._build_game_analysis_prompt(prediction_request)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompts["game_analysis"]},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            recommendation_data = json.loads(response.choices[0].message.content)
            
            # Convert to structured recommendation
            recommendation = BettingRecommendation(
                game_id=f"{prediction_request.home_team}_vs_{prediction_request.away_team}_{prediction_request.game_date.strftime('%Y%m%d')}",
                confidence_score=float(recommendation_data.get("confidence_score", 0.5)),
                recommended_bet_type=recommendation_data.get("recommended_bet_type", "moneyline"),
                prediction=recommendation_data.get("prediction", ""),
                reasoning=recommendation_data.get("reasoning", ""),
                risk_level=recommendation_data.get("risk_level", "medium"),
                suggested_stake=float(recommendation_data.get("suggested_stake", 0.02)),  # 2% default
                key_factors=recommendation_data.get("key_factors", []),
                alternative_bets=recommendation_data.get("alternative_bets", [])
            )
            
            logger.info(f"Generated prediction for {prediction_request.home_team} vs {prediction_request.away_team}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating game prediction: {e}")
            # Return conservative default recommendation
            return BettingRecommendation(
                game_id=f"{prediction_request.home_team}_vs_{prediction_request.away_team}_{prediction_request.game_date.strftime('%Y%m%d')}",
                confidence_score=0.0,
                recommended_bet_type="no_bet",
                prediction="Analysis failed - no recommendation",
                reasoning=f"Error in analysis: {str(e)}",
                risk_level="high",
                suggested_stake=0.0,
                key_factors=["Analysis error"],
                alternative_bets=[]
            )
    
    async def optimize_parlay(self, individual_picks: List[BettingRecommendation], bankroll: float = 1000) -> List[ParlayRecommendation]:
        """
        Generate optimized parlay combinations from individual game predictions
        """
        try:
            # Filter picks with minimum confidence threshold
            viable_picks = [pick for pick in individual_picks if pick.confidence_score >= 0.6]
            
            if len(viable_picks) < 2:
                logger.warning("Insufficient high-confidence picks for parlay optimization")
                return []
            
            # Prepare parlay optimization prompt
            parlay_prompt = self._build_parlay_optimization_prompt(viable_picks, bankroll)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompts["parlay_optimizer"]},
                    {"role": "user", "content": parlay_prompt}
                ],
                temperature=0.2,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            # Parse parlay recommendations
            parlay_data = json.loads(response.choices[0].message.content)
            
            parlays = []
            for parlay_info in parlay_data.get("recommended_parlays", []):
                parlay = ParlayRecommendation(
                    games=parlay_info.get("game_ids", []),
                    total_confidence=float(parlay_info.get("total_confidence", 0.0)),
                    combined_odds=float(parlay_info.get("combined_odds", 1.0)),
                    expected_payout=float(parlay_info.get("expected_payout", 0.0)),
                    risk_assessment=parlay_info.get("risk_assessment", "medium"),
                    reasoning=parlay_info.get("reasoning", ""),
                    individual_picks=[pick for pick in viable_picks if pick.game_id in parlay_info.get("game_ids", [])]
                )
                parlays.append(parlay)
            
            logger.info(f"Generated {len(parlays)} parlay recommendations")
            return parlays
            
        except Exception as e:
            logger.error(f"Error optimizing parlays: {e}")
            return []
    
    async def assess_bankroll_risk(self, recommendations: List[BettingRecommendation], current_bankroll: float) -> Dict[str, Any]:
        """
        Assess overall portfolio risk and adjust stake recommendations
        """
        try:
            risk_prompt = self._build_risk_assessment_prompt(recommendations, current_bankroll)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompts["risk_manager"]},
                    {"role": "user", "content": risk_prompt}
                ],
                temperature=0.1,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            risk_assessment = json.loads(response.choices[0].message.content)
            
            logger.info("Completed bankroll risk assessment")
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing bankroll risk: {e}")
            return {
                "overall_risk": "high",
                "max_total_exposure": 0.05,  # Conservative 5% max exposure
                "recommendations": "Error in risk assessment - use conservative betting"
            }
    
    def _build_game_analysis_prompt(self, request: PredictionRequest) -> str:
        """Build comprehensive analysis prompt for a single game"""
        prompt = f"""
Analyze the following game and provide a detailed betting recommendation:

GAME DETAILS:
- Sport: {request.sport}
- League: {request.league}
- Matchup: {request.home_team} (Home) vs {request.away_team} (Away)
- Date: {request.game_date.strftime('%Y-%m-%d %H:%M')}

TEAM STATISTICS:
{json.dumps(request.team_stats, indent=2)}

HISTORICAL DATA:
{json.dumps(request.historical_data, indent=2)}

RECENT NEWS:
{chr(10).join(f"- {news}" for news in request.recent_news[:10])}

WEATHER CONDITIONS:
{json.dumps(request.weather_conditions, indent=2) if request.weather_conditions else "Indoor venue or conditions not available"}

INJURY REPORTS:
{chr(10).join(f"- {injury}" for injury in (request.injury_reports or []))}

Please provide your analysis in the following JSON format:
{{
    "confidence_score": 0.0-1.0,
    "recommended_bet_type": "moneyline|spread|over_under|no_bet",
    "prediction": "Specific prediction (e.g., 'Lakers -5.5' or 'Over 215.5')",
    "reasoning": "Detailed analysis explaining your prediction",
    "risk_level": "low|medium|high",
    "suggested_stake": 0.01-0.10,
    "key_factors": ["factor1", "factor2", "factor3"],
    "alternative_bets": [
        {{
            "bet_type": "spread",
            "prediction": "Lakers -3.5",
            "confidence": 0.7,
            "reasoning": "Alternative reasoning"
        }}
    ]
}}
"""
        return prompt
    
    def _build_parlay_optimization_prompt(self, picks: List[BettingRecommendation], bankroll: float) -> str:
        """Build parlay optimization prompt"""
        picks_summary = []
        for pick in picks:
            picks_summary.append({
                "game_id": pick.game_id,
                "prediction": pick.prediction,
                "confidence": pick.confidence_score,
                "bet_type": pick.recommended_bet_type,
                "reasoning": pick.reasoning[:200]  # Truncate for prompt length
            })
        
        prompt = f"""
Optimize parlay combinations from the following individual betting recommendations:

INDIVIDUAL PICKS:
{json.dumps(picks_summary, indent=2)}

BANKROLL: ${bankroll:,.2f}

Create 2-5 parlay combinations that:
1. Maximize expected value while managing risk
2. Avoid conflicting or correlated bets
3. Include 2-6 legs per parlay
4. Consider appropriate stake sizing

Provide recommendations in this JSON format:
{{
    "recommended_parlays": [
        {{
            "game_ids": ["game1", "game2", "game3"],
            "total_confidence": 0.0-1.0,
            "combined_odds": estimated_decimal_odds,
            "expected_payout": estimated_payout_amount,
            "risk_assessment": "low|medium|high",
            "reasoning": "Why this combination works well together"
        }}
    ],
    "overall_strategy": "General approach and risk management advice"
}}
"""
        return prompt
    
    def _build_risk_assessment_prompt(self, recommendations: List[BettingRecommendation], bankroll: float) -> str:
        """Build risk assessment prompt for portfolio management"""
        total_exposure = sum(rec.suggested_stake for rec in recommendations)
        
        prompt = f"""
Assess the risk profile of the following betting portfolio:

CURRENT BANKROLL: ${bankroll:,.2f}
TOTAL RECOMMENDATIONS: {len(recommendations)}
TOTAL SUGGESTED EXPOSURE: {total_exposure:.1%} of bankroll

INDIVIDUAL BETS:
{json.dumps([{
    "game": rec.game_id,
    "confidence": rec.confidence_score,
    "stake": rec.suggested_stake,
    "risk_level": rec.risk_level,
    "bet_type": rec.recommended_bet_type
} for rec in recommendations], indent=2)}

Provide risk assessment in this JSON format:
{{
    "overall_risk": "low|medium|high",
    "max_total_exposure": 0.01-0.20,
    "individual_adjustments": [
        {{
            "game_id": "game1",
            "original_stake": 0.05,
            "adjusted_stake": 0.03,
            "reason": "Risk adjustment reasoning"
        }}
    ],
    "portfolio_recommendations": "Overall strategy advice",
    "kelly_criterion_analysis": "Mathematical betting sizing analysis",
    "diversification_score": 0.0-1.0
}}
"""
        return prompt
    
    async def analyze_multiple_games(self, requests: List[PredictionRequest]) -> Tuple[List[BettingRecommendation], List[ParlayRecommendation]]:
        """
        Analyze multiple games and generate individual + parlay recommendations
        """
        # Generate individual game predictions in parallel
        individual_tasks = [self.analyze_game(request) for request in requests]
        individual_picks = await asyncio.gather(*individual_tasks, return_exceptions=True)
        
        # Filter out failed predictions
        valid_picks = [pick for pick in individual_picks if isinstance(pick, BettingRecommendation)]
        
        # Generate parlay recommendations
        parlay_recommendations = await self.optimize_parlay(valid_picks)
        
        return valid_picks, parlay_recommendations
    
    async def generate_daily_predictions(self, espn_data: Dict[str, Any], news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive daily predictions from ESPN data
        """
        try:
            # Extract games from ESPN data
            prediction_requests = self._extract_prediction_requests_from_espn(espn_data, news_data)
            
            if not prediction_requests:
                logger.warning("No games found for prediction")
                return {"individual_picks": [], "parlay_recommendations": [], "summary": "No games available"}
            
            # Generate predictions
            individual_picks, parlay_recommendations = await self.analyze_multiple_games(prediction_requests)
            
            # Assess overall risk
            risk_assessment = await self.assess_bankroll_risk(individual_picks, 1000.0)  # Default $1000 bankroll
            
            return {
                "individual_picks": [asdict(pick) for pick in individual_picks],
                "parlay_recommendations": [asdict(parlay) for parlay in parlay_recommendations],
                "risk_assessment": risk_assessment,
                "summary": f"Generated {len(individual_picks)} individual picks and {len(parlay_recommendations)} parlay options",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating daily predictions: {e}")
            return {"error": str(e), "individual_picks": [], "parlay_recommendations": []}
    
    def _extract_prediction_requests_from_espn(self, espn_data: Dict[str, Any], news_data: Dict[str, Any]) -> List[PredictionRequest]:
        """Extract prediction requests from ESPN API data"""
        requests = []
        
        for sport, data in espn_data.items():
            if "events" in data:
                for event in data["events"]:
                    try:
                        competitors = event.get("competitions", [{}])[0].get("competitors", [])
                        if len(competitors) >= 2:
                            home_team = away_team = None
                            
                            for comp in competitors:
                                team_name = comp.get("team", {}).get("displayName", "")
                                if comp.get("homeAway") == "home":
                                    home_team = team_name
                                else:
                                    away_team = team_name
                            
                            if home_team and away_team:
                                request = PredictionRequest(
                                    sport=sport,
                                    league=data.get("leagues", [{}])[0].get("abbreviation", ""),
                                    home_team=home_team,
                                    away_team=away_team,
                                    game_date=datetime.fromisoformat(event.get("date", "").replace("Z", "+00:00")),
                                    historical_data={"head_to_head": "Limited data available"},
                                    team_stats={
                                        "home_team_record": competitors[0].get("records", [{}])[0] if competitors else {},
                                        "away_team_record": competitors[1].get("records", [{}])[0] if len(competitors) > 1 else {}
                                    },
                                    recent_news=news_data.get(sport, {}).get("articles", [{}])[:5],
                                    weather_conditions=event.get("weather"),
                                    injury_reports=[]
                                )
                                requests.append(request)
                                
                    except Exception as e:
                        logger.error(f"Error extracting prediction request: {e}")
                        continue
        
        return requests

# Global instance
openai_prediction_service = OpenAIPredictonService()