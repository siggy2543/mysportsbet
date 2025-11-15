"""
Application configuration settings
Manages environment variables and application settings
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Sports Betting API"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/sports_betting"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_MAX: int = 20
    
    # Redis Cache - Tiered TTL Strategy
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SHORT: int = 60      # 1 minute for live odds
    CACHE_TTL_MEDIUM: int = 300    # 5 minutes for event data
    CACHE_TTL_LONG: int = 3600     # 1 hour for static data
    CACHE_TTL_USER: int = 1800     # 30 minutes for user data
    
    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-jwt-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    ESPN_API_KEY: str = ""
    RAPIDAPI_KEY: str = ""
    DRAFTKINGS_API_KEY: str = ""
    THE_RUNDOWN_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    THESPORTSDB_API_KEY: str = ""
    SPORTSDATA_API_KEY: str = ""
    SPORTRADAR_API_KEY: str = ""
    
    # DraftKings Configuration
    DRAFTKINGS_USERNAME: str = ""
    DRAFTKINGS_PASSWORD: str = ""
    DRAFTKINGS_STATE: str = ""
    
    # Betting Configuration
    FIXED_BET_AMOUNT: float = 5.0
    FIXED_PARLAY_AMOUNT: float = 5.0
    MAX_SINGLE_BET: float = 100.0
    MAX_DAILY_EXPOSURE: float = 500.0
    MIN_PREDICTION_CONFIDENCE: float = 0.65
    MAX_BETS_PER_DAY: int = 100
    AUTO_BETTING_ENABLED: bool = True
    BETTING_STRATEGY: str = "fixed_amount"
    BETTING_HOURS_START: str = "09:00"
    BETTING_HOURS_END: str = "23:00"
    
    # API URLs
    ESPN_API_URL: str = "https://site.api.espn.com/apis/site/v2"
    ALL_SPORTS_API_URL: str = "https://allsportdb-com.p.rapidapi.com"
    THE_RUNDOWN_API_URL: str = "https://therundown-therundown-v1.p.rapidapi.com"
    DRAFTKINGS_API_URL: str = "https://api.draftkings.com"
    THESPORTSDB_API_URL: str = "https://www.thesportsdb.com/api/v1/json"
    SPORTSDATA_API_URL: str = "https://api.sportsdata.io"
    SPORTRADAR_API_URL: str = "https://api.sportradar.us"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "https://your-frontend-domain.com"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ML Model Settings
    MODEL_RETRAIN_INTERVAL_HOURS: int = 24
    MIN_CONFIDENCE_THRESHOLD: float = 0.6
    MAX_BETS_PER_DAY: int = 10
    
    # Betting Configuration
    MAX_BET_AMOUNT: float = 1000.0
    MIN_BET_AMOUNT: float = 10.0
    BANKROLL_PERCENTAGE_LIMIT: float = 0.05  # 5% of bankroll per bet
    FIXED_BET_AMOUNT: float = 5.0
    FIXED_PARLAY_AMOUNT: float = 5.0
    MAX_SINGLE_BET: float = 100.0
    MAX_DAILY_EXPOSURE: float = 500.0
    BANKROLL_SIZE: float = 1000.0
    MIN_CONFIDENCE_THRESHOLD: float = 0.7
    ENABLE_MOCK_MODE: bool = True
    PAPER_TRADING_MODE: bool = True
    
    # Rate Limiting
    API_RATE_LIMIT: int = 100  # requests per minute
    
    @validator('ALLOWED_HOSTS', pre=True)
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()