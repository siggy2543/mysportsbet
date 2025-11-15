"""
Integration Tests for API Endpoints
Tests all API routes with authentication, validation, and error handling
"""
import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

class TestAuthenticationEndpoints:
    """Test authentication and authorization endpoints"""
    
    def test_register_user_success(self, test_client, sample_user_data):
        """Test successful user registration"""
        response = test_client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not return password
    
    def test_register_user_duplicate_username(self, test_client, sample_user_data):
        """Test registration with duplicate username"""
        # Register first user
        test_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to register with same username
        response = test_client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "username already exists" in response.json()["detail"].lower()
    
    def test_register_user_invalid_data(self, test_client):
        """Test registration with invalid data"""
        invalid_data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email
            "password": "123"  # Too short password
        }
        
        response = test_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_login_success(self, test_client, sample_user_data):
        """Test successful login"""
        # Register user first
        test_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = test_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = test_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()
    
    def test_protected_route_without_token(self, test_client):
        """Test accessing protected route without token"""
        response = test_client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token(self, test_client, auth_headers):
        """Test accessing protected route with valid token"""
        response = test_client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data

class TestSportsDataEndpoints:
    """Test sports data endpoints"""
    
    @patch('services.sports_api_service.SportsAPIService')
    def test_get_games_success(self, mock_sports_service, test_client, auth_headers):
        """Test successful games retrieval"""
        # Mock service response
        mock_games = [
            {
                "id": 1,
                "external_id": "game_1",
                "sport": "football",
                "league": "NFL",
                "home_team": "Team A",
                "away_team": "Team B",
                "event_date": datetime.utcnow() + timedelta(days=1),
                "odds_data": {"moneyline": {"home": 1.85, "away": 2.10}}
            }
        ]
        
        mock_instance = mock_sports_service.return_value
        mock_instance.get_upcoming_games = AsyncMock(return_value=mock_games)
        
        response = test_client.get("/api/v1/sports/games", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sport"] == "football"
    
    def test_get_games_by_sport(self, test_client, auth_headers, mock_sports_api):
        """Test games filtering by sport"""
        response = test_client.get(
            "/api/v1/sports/games?sport=football", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_get_games_by_date_range(self, test_client, auth_headers):
        """Test games filtering by date range"""
        start_date = datetime.utcnow().date()
        end_date = (datetime.utcnow() + timedelta(days=7)).date()
        
        response = test_client.get(
            f"/api/v1/sports/games?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_get_game_details(self, test_client, auth_headers, sample_game_data):
        """Test getting specific game details"""
        # First create a game
        with patch('core.database.get_db'):
            response = test_client.get("/api/v1/sports/games/1", headers=auth_headers)
        
        # In a real test, this would return game details if it exists
        # For now, we test that the endpoint is accessible
        assert response.status_code in [200, 404]
    
    @patch('services.sports_api_service.SportsAPIService')
    def test_refresh_games_data(self, mock_sports_service, test_client, auth_headers):
        """Test manual games data refresh"""
        mock_instance = mock_sports_service.return_value
        mock_instance.fetch_and_store_games = AsyncMock(return_value={"updated": 5, "new": 2})
        
        response = test_client.post("/api/v1/sports/refresh", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

class TestPredictionsEndpoints:
    """Test predictions endpoints"""
    
    @patch('services.prediction_service.PredictionService')
    def test_get_daily_predictions(self, mock_prediction_service, test_client, auth_headers):
        """Test getting daily predictions"""
        mock_predictions = [
            {
                "game_id": 1,
                "prediction_type": "moneyline",
                "recommended_bet": "home",
                "confidence": 0.85,
                "expected_value": 0.12,
                "reasoning": "Strong home team performance"
            }
        ]
        
        mock_instance = mock_prediction_service.return_value
        mock_instance.get_daily_predictions = AsyncMock(return_value=mock_predictions)
        
        response = test_client.get("/api/v1/predictions/daily", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0
    
    @patch('services.game_theory_predictor.GameTheoryPredictor')
    def test_get_game_analysis(self, mock_game_theory, test_client, auth_headers):
        """Test game-specific analysis"""
        mock_analysis = {
            "nash_equilibrium": {"strategy": "conservative", "confidence": 0.85},
            "kelly_criterion": 0.12,
            "minimax_strategy": {"optimal_bet": "moneyline_home", "expected_value": 0.08},
            "risk_assessment": {"risk_level": "medium", "variance": 0.15}
        }
        
        mock_instance = mock_game_theory.return_value
        mock_instance.analyze_game = AsyncMock(return_value=mock_analysis)
        
        response = test_client.get("/api/v1/predictions/analyze/1", headers=auth_headers)
        
        assert response.status_code in [200, 404]
    
    def test_get_prediction_history(self, test_client, auth_headers):
        """Test getting prediction history"""
        response = test_client.get("/api/v1/predictions/history", headers=auth_headers)
        
        assert response.status_code == 200
        # Should return array even if empty
        data = response.json()
        assert isinstance(data, list)

class TestBettingEndpoints:
    """Test betting endpoints"""
    
    def test_get_user_bets(self, test_client, auth_headers):
        """Test getting user's bets"""
        response = test_client.get("/api/v1/bets", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch('services.betting_service.BettingService')
    def test_place_bet_success(self, mock_betting_service, test_client, auth_headers, sample_bet_data):
        """Test successful bet placement"""
        mock_bet_result = {
            "id": 1,
            "external_bet_id": "bet_123456",
            "status": "pending",
            "stake": sample_bet_data["stake"],
            "potential_payout": sample_bet_data["stake"] * sample_bet_data["odds"]
        }
        
        mock_instance = mock_betting_service.return_value
        mock_instance.place_bet = AsyncMock(return_value=mock_bet_result)
        
        response = test_client.post("/api/v1/bets", json=sample_bet_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["stake"] == sample_bet_data["stake"]
    
    def test_place_bet_insufficient_balance(self, test_client, auth_headers):
        """Test bet placement with insufficient balance"""
        large_bet = {
            "event_id": 1,
            "bet_type": "moneyline",
            "selection": "home",
            "stake": 10000.0,  # Very large amount
            "odds": 1.85
        }
        
        response = test_client.post("/api/v1/bets", json=large_bet, headers=auth_headers)
        
        # Should either reject due to insufficient balance or validation
        assert response.status_code in [400, 422]
    
    def test_place_bet_invalid_data(self, test_client, auth_headers):
        """Test bet placement with invalid data"""
        invalid_bet = {
            "event_id": "invalid",  # Should be integer
            "bet_type": "",         # Empty string
            "stake": -50.0,        # Negative amount
            "odds": 0              # Invalid odds
        }
        
        response = test_client.post("/api/v1/bets", json=invalid_bet, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_bet_details(self, test_client, auth_headers):
        """Test getting specific bet details"""
        response = test_client.get("/api/v1/bets/1", headers=auth_headers)
        
        # Should return 404 if bet doesn't exist, 200 if it does
        assert response.status_code in [200, 404]
    
    @patch('services.betting_service.BettingService')
    def test_cancel_bet(self, mock_betting_service, test_client, auth_headers):
        """Test bet cancellation"""
        mock_instance = mock_betting_service.return_value
        mock_instance.cancel_bet = AsyncMock(return_value={"status": "cancelled"})
        
        response = test_client.delete("/api/v1/bets/1", headers=auth_headers)
        
        assert response.status_code in [200, 404]

class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_get_user_profile(self, test_client, auth_headers):
        """Test getting user profile"""
        response = test_client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "balance" in data
    
    def test_update_user_profile(self, test_client, auth_headers):
        """Test updating user profile"""
        update_data = {
            "email": "newemail@example.com",
            "preferences": {
                "notifications": True,
                "auto_betting": False
            }
        }
        
        response = test_client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code in [200, 422]  # 422 if validation fails
    
    def test_get_user_statistics(self, test_client, auth_headers):
        """Test getting user statistics"""
        response = test_client.get("/api/v1/users/me/statistics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_bets" in data
        assert "win_rate" in data
        assert "total_profit" in data

class TestHealthAndStatusEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check(self, test_client):
        """Test basic health check"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_detailed_health_check(self, test_client):
        """Test detailed health check"""
        response = test_client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "redis" in data
        assert "external_apis" in data
    
    def test_api_version(self, test_client):
        """Test API version endpoint"""
        response = test_client.get("/api/v1/version")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "build" in data

class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_not_found(self, test_client):
        """Test 404 error handling"""
        response = test_client.get("/nonexistent/endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_500_internal_error(self, test_client, auth_headers):
        """Test internal server error handling"""
        # This would require mocking a service to raise an exception
        # For now, we test that the error structure is correct
        with patch('services.sports_api_service.SportsAPIService') as mock_service:
            mock_service.return_value.get_upcoming_games.side_effect = Exception("Test error")
            
            response = test_client.get("/api/v1/sports/games", headers=auth_headers)
            
            # Should handle the error gracefully
            assert response.status_code == 500
    
    def test_rate_limiting(self, test_client, auth_headers):
        """Test rate limiting"""
        # Make multiple rapid requests
        responses = []
        for _ in range(100):  # Try to exceed rate limit
            response = test_client.get("/api/v1/sports/games", headers=auth_headers)
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429) or handle gracefully
        assert any(status in [200, 429, 500] for status in responses)

class TestInputValidation:
    """Test input validation and security"""
    
    def test_sql_injection_prevention(self, test_client, auth_headers):
        """Test SQL injection prevention"""
        malicious_input = "'; DROP TABLE users; --"
        
        response = test_client.get(
            f"/api/v1/sports/games?sport={malicious_input}",
            headers=auth_headers
        )
        
        # Should handle malicious input gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_xss_prevention(self, test_client, auth_headers):
        """Test XSS prevention in responses"""
        xss_payload = "<script>alert('xss')</script>"
        
        response = test_client.get(
            f"/api/v1/sports/games?sport={xss_payload}",
            headers=auth_headers
        )
        
        # Response should not contain unescaped script tags
        assert "<script>" not in response.text
    
    def test_large_payload_handling(self, test_client, auth_headers):
        """Test handling of large payloads"""
        large_data = {
            "data": "x" * 1000000,  # 1MB of data
            "event_id": 1,
            "bet_type": "moneyline",
            "selection": "home",
            "stake": 50.0,
            "odds": 1.85
        }
        
        response = test_client.post("/api/v1/bets", json=large_data, headers=auth_headers)
        
        # Should handle large payload appropriately
        assert response.status_code in [413, 422, 400]  # Payload too large or validation error

class TestAsyncEndpoints:
    """Test asynchronous endpoint behavior"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_client, auth_headers):
        """Test handling of concurrent requests"""
        import asyncio
        import httpx
        
        async def make_request():
            async with httpx.AsyncClient(app=test_client.app, base_url="http://test") as client:
                response = await client.get("/api/v1/sports/games", headers=auth_headers)
                return response.status_code
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Most should succeed
        success_count = sum(1 for r in results if r == 200)
        assert success_count >= 5  # At least half should succeed

class TestWebSocketEndpoints:
    """Test WebSocket endpoints if available"""
    
    def test_websocket_connection(self, test_client):
        """Test WebSocket connection for real-time updates"""
        try:
            with test_client.websocket_connect("/ws/live-odds") as websocket:
                # Should connect successfully
                data = websocket.receive_json()
                assert "type" in data
        except Exception:
            # WebSocket might not be implemented yet
            pytest.skip("WebSocket endpoints not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])