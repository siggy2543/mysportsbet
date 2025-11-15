"""
Comprehensive Integration Tests for Sports Betting Automation System
Tests the complete workflow: ESPN API → OpenAI Predictions → DraftKings Betting
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Import our services
from backend.services.espn_api_service import ModernESPNService
from backend.services.openai_prediction_service import OpenAIPredictionService
from backend.services.draftkings_betting_service import DraftKingsBettingService
from backend.services.betting_orchestrator import MasterBettingOrchestrator


class TestIntegrationWorkflow:
    """Test the complete betting automation workflow"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing"""
        with patch.dict(os.environ, {
            'ESPN_API_KEY': 'test_espn_key',
            'ESPN_API_URL': 'https://site.api.espn.com/apis/site/v2',
            'OPENAI_API_KEY': 'test_openai_key',
            'OPENAI_MODEL': 'gpt-4-turbo-preview',
            'DRAFTKINGS_USERNAME': 'test_user',
            'DRAFTKINGS_PASSWORD': 'test_pass',
            'DRAFTKINGS_STATE': 'NY',
            'DRAFTKINGS_API_URL': 'https://api.draftkings.com',
            'MAX_SINGLE_BET': '100.0',
            'MAX_DAILY_EXPOSURE': '500.0',
            'MIN_CONFIDENCE_THRESHOLD': '0.7',
            'BANKROLL_SIZE': '1000.0',
            'CACHE_TTL': '3600',
            'PREDICTION_CACHE_TTL': '7200',
        }):
            yield
    
    @pytest.fixture
    def espn_service(self, mock_env_vars):
        """Create ESPN service instance"""
        return ModernESPNService()
    
    @pytest.fixture
    def openai_service(self, mock_env_vars):
        """Create OpenAI service instance"""
        return OpenAIPredictionService()
    
    @pytest.fixture
    def draftkings_service(self, mock_env_vars):
        """Create DraftKings service instance"""
        return DraftKingsBettingService()
    
    @pytest.fixture
    def betting_orchestrator(self, mock_env_vars):
        """Create betting orchestrator instance"""
        return MasterBettingOrchestrator()
    
    @pytest.fixture
    def sample_espn_games(self):
        """Sample ESPN games data"""
        return {
            "events": [
                {
                    "id": "401547439",
                    "name": "Buffalo Bills at Miami Dolphins",
                    "shortName": "BUF @ MIA",
                    "date": (datetime.now() + timedelta(hours=2)).isoformat(),
                    "competitions": [{
                        "id": "401547439",
                        "competitors": [
                            {
                                "id": "16",
                                "team": {
                                    "id": "16",
                                    "displayName": "Buffalo Bills",
                                    "abbreviation": "BUF"
                                },
                                "homeAway": "away",
                                "score": "0"
                            },
                            {
                                "id": "15",
                                "team": {
                                    "id": "15",
                                    "displayName": "Miami Dolphins",
                                    "abbreviation": "MIA"
                                },
                                "homeAway": "home",
                                "score": "0"
                            }
                        ],
                        "odds": [{
                            "provider": {
                                "name": "DraftKings"
                            },
                            "details": "BUF -3.5",
                            "overUnder": 45.5
                        }]
                    }],
                    "status": {
                        "type": {
                            "name": "STATUS_SCHEDULED"
                        }
                    }
                }
            ]
        }
    
    @pytest.fixture
    def sample_openai_prediction(self):
        """Sample OpenAI prediction response"""
        return {
            "game_analysis": {
                "game_id": "401547439",
                "matchup": "Buffalo Bills @ Miami Dolphins",
                "confidence": 0.85,
                "prediction": "Buffalo Bills to win by 7-10 points",
                "key_factors": [
                    "Buffalo's strong defensive performance",
                    "Miami's home field advantage",
                    "Weather conditions favoring running game"
                ]
            },
            "betting_recommendations": [
                {
                    "bet_type": "spread",
                    "selection": "Buffalo Bills -3.5",
                    "confidence": 0.85,
                    "recommended_stake": 50,
                    "reasoning": "Strong value with Bills' recent form"
                },
                {
                    "bet_type": "total",
                    "selection": "Under 45.5",
                    "confidence": 0.75,
                    "recommended_stake": 30,
                    "reasoning": "Weather conditions suggest lower scoring"
                }
            ],
            "parlay_opportunities": [
                {
                    "legs": [
                        "Buffalo Bills -3.5",
                        "Under 45.5"
                    ],
                    "combined_confidence": 0.78,
                    "recommended_stake": 25,
                    "expected_odds": 2.8
                }
            ],
            "risk_assessment": {
                "overall_risk": "Medium",
                "max_exposure": 105,
                "bankroll_percentage": 0.105
            }
        }
    
    @pytest.fixture
    def sample_draftkings_markets(self):
        """Sample DraftKings betting markets"""
        return {
            "markets": [
                {
                    "market_id": "12345",
                    "market_type": "spread",
                    "game_id": "401547439",
                    "selections": [
                        {
                            "selection_id": "s1",
                            "name": "Buffalo Bills -3.5",
                            "odds": 1.91
                        },
                        {
                            "selection_id": "s2", 
                            "name": "Miami Dolphins +3.5",
                            "odds": 1.91
                        }
                    ]
                },
                {
                    "market_id": "12346",
                    "market_type": "total",
                    "game_id": "401547439",
                    "selections": [
                        {
                            "selection_id": "s3",
                            "name": "Over 45.5",
                            "odds": 1.87
                        },
                        {
                            "selection_id": "s4",
                            "name": "Under 45.5", 
                            "odds": 1.95
                        }
                    ]
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_espn_api_integration(self, espn_service, sample_espn_games):
        """Test ESPN API data collection"""
        with patch.object(espn_service, '_make_api_request') as mock_request:
            mock_request.return_value = sample_espn_games
            
            games = await espn_service.get_nfl_games()
            
            assert len(games) > 0
            assert games[0]['name'] == "Buffalo Bills at Miami Dolphins"
            assert 'competitions' in games[0]
            mock_request.assert_called_once()

    @pytest.mark.asyncio 
    async def test_openai_prediction_service(self, openai_service, sample_espn_games, sample_openai_prediction):
        """Test OpenAI prediction generation"""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = AsyncMock()
            mock_response.choices = [
                MagicMock(message=MagicMock(content=json.dumps(sample_openai_prediction)))
            ]
            mock_client.chat.completions.create.return_value = mock_response
            
            games_data = sample_espn_games['events']
            predictions = await openai_service.analyze_games(games_data)
            
            assert len(predictions) > 0
            assert predictions[0]['game_analysis']['confidence'] >= 0.7
            assert 'betting_recommendations' in predictions[0]
            assert 'parlay_opportunities' in predictions[0]

    @pytest.mark.asyncio
    async def test_draftkings_betting_service(self, draftkings_service, sample_draftkings_markets):
        """Test DraftKings betting integration"""
        with patch.object(draftkings_service, '_make_authenticated_request') as mock_request:
            mock_request.return_value = sample_draftkings_markets
            
            # Test authentication
            with patch.object(draftkings_service, 'authenticate') as mock_auth:
                mock_auth.return_value = True
                auth_result = await draftkings_service.authenticate()
                assert auth_result is True
            
            # Test market data retrieval
            markets = await draftkings_service.get_game_markets("401547439")
            assert len(markets['markets']) > 0
            assert markets['markets'][0]['market_type'] == 'spread'

    @pytest.mark.asyncio
    async def test_complete_betting_workflow(self, betting_orchestrator, sample_espn_games, 
                                          sample_openai_prediction, sample_draftkings_markets):
        """Test the complete end-to-end betting workflow"""
        
        # Mock all external API calls
        with patch.object(betting_orchestrator.espn_service, 'get_upcoming_games') as mock_espn, \
             patch.object(betting_orchestrator.openai_service, 'analyze_games') as mock_openai, \
             patch.object(betting_orchestrator.draftkings_service, 'authenticate') as mock_auth, \
             patch.object(betting_orchestrator.draftkings_service, 'get_game_markets') as mock_markets, \
             patch.object(betting_orchestrator.draftkings_service, 'place_bet') as mock_place_bet:
            
            # Setup mocks
            mock_espn.return_value = sample_espn_games['events']
            mock_openai.return_value = [sample_openai_prediction]
            mock_auth.return_value = True
            mock_markets.return_value = sample_draftkings_markets
            mock_place_bet.return_value = {
                "bet_id": "bet_12345",
                "status": "confirmed",
                "stake": 50,
                "potential_return": 95.5
            }
            
            # Execute the complete workflow
            session_id = await betting_orchestrator.start_betting_session({
                "sports": ["nfl"],
                "max_bets": 3,
                "risk_level": "medium"
            })
            
            result = await betting_orchestrator.execute_complete_workflow(session_id)
            
            # Verify workflow execution
            assert result is not None
            assert result['session_id'] == session_id
            assert 'bets_placed' in result
            assert 'total_stake' in result
            assert result['status'] == 'completed'
            
            # Verify all services were called
            mock_espn.assert_called_once()
            mock_openai.assert_called_once()
            mock_auth.assert_called_once()
            mock_markets.assert_called()
            mock_place_bet.assert_called()

    @pytest.mark.asyncio
    async def test_risk_management_controls(self, betting_orchestrator):
        """Test risk management and safety controls"""
        
        # Test maximum bet limits
        session_id = await betting_orchestrator.start_betting_session({
            "sports": ["nfl"],
            "max_bets": 1,
            "risk_level": "high"
        })
        
        # Test that large bets are rejected
        with patch.object(betting_orchestrator.draftkings_service, 'place_bet') as mock_place_bet:
            mock_place_bet.side_effect = Exception("Bet amount exceeds maximum limit")
            
            with pytest.raises(Exception, match="Bet amount exceeds maximum limit"):
                await betting_orchestrator.place_single_bet(
                    session_id, 
                    "spread",
                    "Buffalo Bills -3.5", 
                    1000  # Exceeds max single bet
                )

    @pytest.mark.asyncio
    async def test_session_management(self, betting_orchestrator):
        """Test betting session management"""
        
        # Create a new session
        session_id = await betting_orchestrator.start_betting_session({
            "sports": ["nfl", "nba"],
            "max_bets": 5,
            "risk_level": "low"
        })
        
        assert session_id is not None
        
        # Verify session exists
        session = await betting_orchestrator.get_session_status(session_id)
        assert session['status'] == 'active'
        assert session['settings']['max_bets'] == 5
        
        # Stop the session
        result = await betting_orchestrator.stop_betting_session(session_id)
        assert result['status'] == 'stopped'

    @pytest.mark.asyncio
    async def test_performance_tracking(self, betting_orchestrator):
        """Test performance tracking and analytics"""
        
        # Mock some betting activity
        with patch.object(betting_orchestrator, '_calculate_performance_metrics') as mock_perf:
            mock_perf.return_value = {
                "total_bets": 10,
                "winning_bets": 6,
                "win_rate": 0.6,
                "total_stake": 500,
                "total_return": 580,
                "roi": 0.16,
                "profit": 80
            }
            
            performance = await betting_orchestrator.get_performance_analytics()
            
            assert performance['win_rate'] == 0.6
            assert performance['roi'] == 0.16
            assert performance['profit'] == 80

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, betting_orchestrator):
        """Test error handling and system recovery"""
        
        # Test ESPN API failure
        with patch.object(betting_orchestrator.espn_service, 'get_upcoming_games') as mock_espn:
            mock_espn.side_effect = Exception("ESPN API temporarily unavailable")
            
            session_id = await betting_orchestrator.start_betting_session({
                "sports": ["nfl"],
                "max_bets": 1,
                "risk_level": "low"
            })
            
            with pytest.raises(Exception, match="ESPN API temporarily unavailable"):
                await betting_orchestrator.execute_complete_workflow(session_id)
        
        # Test OpenAI API failure with fallback
        with patch.object(betting_orchestrator.openai_service, 'analyze_games') as mock_openai:
            mock_openai.side_effect = Exception("OpenAI API rate limit exceeded")
            
            # Should handle gracefully and not place bets without predictions
            result = await betting_orchestrator.execute_complete_workflow(session_id)
            assert result['status'] == 'failed'
            assert 'error' in result

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])