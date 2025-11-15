# =============================================================================
# ENHANCED API DOCUMENTATION SYSTEM
# =============================================================================

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import os

# Create FastAPI app with comprehensive documentation
app = FastAPI(
    title="Sports Betting API",
    description="""
    ## 🏆 Advanced Sports Betting System

    This API provides comprehensive sports betting functionality including:

    * **🔐 Authentication**: JWT-based user authentication and authorization
    * **📊 Sports Data**: Real-time sports data from ESPN and other providers
    * **🤖 AI Predictions**: Machine learning-powered betting predictions
    * **💰 Betting Operations**: Place, track, and manage bets
    * **📈 Analytics**: Performance analytics and reporting
    * **⚡ Real-time Updates**: Live odds and game updates

    ### 🚀 Quick Start
    1. Register a new user account
    2. Login to get your JWT token
    3. Use the token to access protected endpoints
    4. Start making predictions and placing bets!

    ### 🔑 Authentication
    All protected endpoints require a valid JWT token in the Authorization header:
    ```
    Authorization: Bearer your_jwt_token_here
    ```
    """,
    version="2.0.0",
    contact={
        "name": "Sports Betting API Support",
        "email": "support@sportsbetting.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "https://localhost", "description": "SSL Development Server"},
        {"url": "http://localhost:8000", "description": "Development Server"},
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# =============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION
# =============================================================================

class UserRegistration(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Strong password (min 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")

class UserLogin(BaseModel):
    """Model for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID")

class BetRequest(BaseModel):
    """Model for placing a bet"""
    game_id: str = Field(..., description="Unique game identifier")
    bet_type: str = Field(..., description="Type of bet (moneyline, spread, total)")
    selection: str = Field(..., description="Bet selection")
    amount: float = Field(..., gt=0, le=1000, description="Bet amount ($5-$1000)")
    odds: float = Field(..., description="Betting odds")

class BetResponse(BaseModel):
    """Model for bet response"""
    bet_id: str = Field(..., description="Unique bet identifier")
    status: str = Field(..., description="Bet status")
    potential_payout: float = Field(..., description="Potential payout amount")
    placed_at: datetime = Field(..., description="Bet placement timestamp")

class GameData(BaseModel):
    """Model for game data"""
    game_id: str = Field(..., description="Unique game identifier")
    sport: str = Field(..., description="Sport type")
    home_team: str = Field(..., description="Home team name")
    away_team: str = Field(..., description="Away team name")
    game_time: datetime = Field(..., description="Game start time")
    odds: Dict[str, Any] = Field(..., description="Current odds")
    predictions: Optional[Dict[str, Any]] = Field(None, description="AI predictions")

class PredictionRequest(BaseModel):
    """Model for prediction request"""
    game_id: str = Field(..., description="Game identifier")
    include_analysis: bool = Field(default=True, description="Include detailed analysis")

class SystemStatus(BaseModel):
    """Model for system status"""
    status: str = Field(..., description="System status")
    message: str = Field(..., description="Status message")
    features: List[str] = Field(..., description="Available features")
    supported_sports: List[str] = Field(..., description="Supported sports")
    betting_limits: Dict[str, float] = Field(..., description="Betting limits")

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/v1/auth/register", 
         response_model=TokenResponse,
         tags=["🔐 Authentication"],
         summary="Register New User",
         description="Create a new user account and receive JWT token")
async def register_user(user_data: UserRegistration):
    """
    Register a new user account with the following requirements:
    
    - Username must be unique and 3-50 characters
    - Email must be valid format
    - Password must be at least 8 characters
    - Returns JWT token for immediate access
    """
    # Implementation would go here
    return {
        "access_token": "jwt_token_here",
        "token_type": "bearer",
        "expires_in": 3600,
        "user_id": "user_123"
    }

@app.post("/api/v1/auth/login",
         response_model=TokenResponse,
         tags=["🔐 Authentication"],
         summary="User Login",
         description="Authenticate user and receive JWT token")
async def login_user(credentials: UserLogin):
    """
    Authenticate user with username/email and password.
    Returns JWT token valid for 1 hour.
    """
    # Implementation would go here
    return {
        "access_token": "jwt_token_here",
        "token_type": "bearer", 
        "expires_in": 3600,
        "user_id": "user_123"
    }

@app.post("/api/v1/auth/refresh",
         response_model=TokenResponse,
         tags=["🔐 Authentication"],
         summary="Refresh Token",
         description="Refresh expired JWT token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh an expired JWT token with a new one."""
    return {
        "access_token": "new_jwt_token_here",
        "token_type": "bearer",
        "expires_in": 3600,
        "user_id": "user_123"
    }

# =============================================================================
# SPORTS DATA ENDPOINTS
# =============================================================================

@app.get("/api/v1/sports/games",
        response_model=List[GameData],
        tags=["📊 Sports Data"],
        summary="Get Available Games",
        description="Retrieve list of available games for betting")
async def get_available_games(
    sport: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = Field(default=20, le=100),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get list of available games with current odds and predictions.
    
    **Query Parameters:**
    - `sport`: Filter by sport (NBA, NFL, MLB, NHL, Soccer)
    - `date`: Filter by date (YYYY-MM-DD format)
    - `limit`: Maximum number of games to return (1-100)
    """
    # Implementation would go here
    return [
        {
            "game_id": "game_123",
            "sport": "NBA",
            "home_team": "Lakers",
            "away_team": "Warriors",
            "game_time": datetime.now(),
            "odds": {"moneyline": {"home": -150, "away": 130}},
            "predictions": {"confidence": 0.75, "predicted_winner": "Lakers"}
        }
    ]

@app.get("/api/v1/sports/games/{game_id}",
        response_model=GameData,
        tags=["📊 Sports Data"],
        summary="Get Game Details",
        description="Get detailed information about a specific game")
async def get_game_details(
    game_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get comprehensive details for a specific game including odds and predictions."""
    return {
        "game_id": game_id,
        "sport": "NBA",
        "home_team": "Lakers",
        "away_team": "Warriors", 
        "game_time": datetime.now(),
        "odds": {"moneyline": {"home": -150, "away": 130}},
        "predictions": {"confidence": 0.75, "predicted_winner": "Lakers"}
    }

# =============================================================================
# AI PREDICTIONS ENDPOINTS
# =============================================================================

@app.post("/api/v1/predictions/generate",
         tags=["🤖 AI Predictions"],
         summary="Generate Game Prediction",
         description="Generate AI-powered prediction for a specific game")
async def generate_prediction(
    request: PredictionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate comprehensive AI prediction for a game including:
    - Win probability for each team
    - Recommended bet types
    - Confidence levels
    - Historical analysis
    """
    return {
        "game_id": request.game_id,
        "predictions": {
            "winner": "Lakers",
            "confidence": 0.78,
            "win_probability": {"Lakers": 0.65, "Warriors": 0.35},
            "recommended_bets": [
                {"type": "moneyline", "selection": "Lakers", "confidence": 0.78}
            ]
        },
        "analysis": "Detailed analysis..." if request.include_analysis else None
    }

# =============================================================================
# BETTING ENDPOINTS
# =============================================================================

@app.post("/api/v1/bets/place",
         response_model=BetResponse,
         tags=["💰 Betting Operations"],
         summary="Place New Bet",
         description="Place a new bet on a game")
async def place_bet(
    bet_request: BetRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Place a new bet with the following limits:
    - Minimum bet: $5
    - Maximum bet: $1000
    - Supported bet types: moneyline, spread, total
    """
    return {
        "bet_id": "bet_123",
        "status": "placed",
        "potential_payout": bet_request.amount * (bet_request.odds + 1),
        "placed_at": datetime.now()
    }

@app.get("/api/v1/bets/active",
        tags=["💰 Betting Operations"],
        summary="Get Active Bets",
        description="Retrieve user's active bets")
async def get_active_bets(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all active bets for the authenticated user."""
    return [
        {
            "bet_id": "bet_123",
            "game_id": "game_123",
            "bet_type": "moneyline",
            "selection": "Lakers",
            "amount": 100.0,
            "potential_payout": 250.0,
            "status": "active",
            "placed_at": datetime.now()
        }
    ]

@app.get("/api/v1/bets/history",
        tags=["💰 Betting Operations"],
        summary="Get Betting History",
        description="Retrieve user's betting history")
async def get_betting_history(
    limit: int = Field(default=50, le=200),
    offset: int = Field(default=0, ge=0),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get paginated betting history for the authenticated user."""
    return {
        "bets": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

# =============================================================================
# SYSTEM STATUS ENDPOINTS
# =============================================================================

@app.get("/api/v1/bets/public/status",
        response_model=SystemStatus,
        tags=["📈 System Status"],
        summary="System Status",
        description="Get current system status and capabilities")
async def get_system_status():
    """Get current system status, available features, and configuration."""
    return {
        "status": "active",
        "message": "Sports betting system is operational",
        "features": [
            "Live sports data collection",
            "AI-powered predictions", 
            "Automated bet placement",
            "Real-time odds tracking"
        ],
        "supported_sports": ["NBA", "NFL", "MLB", "NHL", "Soccer"],
        "betting_limits": {
            "min_bet": 5.0,
            "max_bet": 1000.0,
            "max_daily_exposure": 5000.0
        }
    }

@app.get("/health",
        tags=["📈 System Status"],
        summary="Health Check",
        description="Simple health check endpoint")
async def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/ssl-health",
        tags=["📈 System Status"], 
        summary="SSL Health Check",
        description="SSL-specific health check endpoint")
async def ssl_health_check():
    """SSL-specific health check for HTTPS endpoints."""
    return {"status": "healthy ssl", "secure": True, "timestamp": datetime.now()}

# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.get("/api/v1/analytics/performance",
        tags=["📈 Analytics"],
        summary="Get Performance Analytics",
        description="Retrieve betting performance analytics")
async def get_performance_analytics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get comprehensive betting performance analytics."""
    return {
        "total_bets": 150,
        "win_rate": 0.68,
        "total_profit": 2500.50,
        "roi": 0.25,
        "best_sport": "NBA",
        "monthly_performance": []
    }

@app.get("/api/v1/analytics/predictions",
        tags=["📈 Analytics"],
        summary="Get Prediction Analytics", 
        description="Retrieve AI prediction accuracy analytics")
async def get_prediction_analytics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get AI prediction accuracy and performance metrics."""
    return {
        "prediction_accuracy": 0.72,
        "total_predictions": 500,
        "accuracy_by_sport": {
            "NBA": 0.75,
            "NFL": 0.68,
            "MLB": 0.71
        },
        "model_performance": "excellent"
    }

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )

# =============================================================================
# STARTUP CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )