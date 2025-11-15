"""
Comprehensive Testing Configuration for Sports Betting Application
Includes unit tests, integration tests, and performance tests
"""
import pytest
import asyncio
import aiohttp
from typing import AsyncGenerator, Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from unittest.mock import AsyncMock, MagicMock, patch

# Test configurations
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_REDIS_URL = "redis://localhost:6379/1"  # Use different DB for tests

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False,
    )
    
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def setup_test_db(test_engine):
    """Setup test database with tables"""
    from core.database import Base
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_session(test_engine, setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

@pytest.fixture
async def test_redis() -> AsyncGenerator[redis.Redis, None]:
    """Create test Redis connection"""
    redis_client = redis.from_url(TEST_REDIS_URL)
    
    # Clear test database
    await redis_client.flushdb()
    
    yield redis_client
    
    # Clean up
    await redis_client.flushdb()
    await redis_client.close()

@pytest.fixture
def override_get_db(test_session):
    """Override database dependency for testing"""
    from app import app
    from core.database import get_db
    
    async def _override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def test_client(override_get_db):
    """Create test client"""
    from app import app
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_sports_api():
    """Mock sports API responses"""
    mock_response = {
        "events": [
            {
                "id": "test_game_1",
                "sport": "football",
                "league": "NFL",
                "homeTeam": {"name": "Team A"},
                "awayTeam": {"name": "Team B"},
                "date": "2025-11-01T20:00:00Z",
                "odds": {
                    "moneyline": {"home": 1.85, "away": 2.10},
                    "spread": {"home": -3.5, "away": 3.5}
                }
            }
        ]
    }
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response_obj = MagicMock()
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_response_obj.status = 200
        mock_response_obj.raise_for_status = MagicMock()
        
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
        
        yield mock_response

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def sample_game_data():
    """Sample game data for testing"""
    return {
        "external_id": "test_game_1",
        "sport": "football",
        "league": "NFL",
        "home_team": "Team A",
        "away_team": "Team B",
        "event_date": "2025-11-01T20:00:00Z",
        "odds_data": {
            "moneyline": {"home": 1.85, "away": 2.10},
            "spread": {"home": -3.5, "away": 3.5}
        }
    }

@pytest.fixture
def sample_bet_data():
    """Sample bet data for testing"""
    return {
        "event_id": 1,
        "bet_type": "moneyline",
        "selection": "home",
        "stake": 50.0,
        "odds": 1.85
    }

# Performance test fixtures
@pytest.fixture
def performance_test_data():
    """Generate large dataset for performance testing"""
    return {
        "games": [
            {
                "id": f"game_{i}",
                "sport": "football",
                "home_team": f"Home Team {i}",
                "away_team": f"Away Team {i}",
                "odds": {"moneyline": {"home": 1.8 + (i * 0.01), "away": 2.0 + (i * 0.01)}}
            }
            for i in range(1000)
        ]
    }

# Async HTTP client fixture for integration tests
@pytest.fixture
async def async_http_client():
    """Create async HTTP client for integration tests"""
    async with aiohttp.ClientSession() as session:
        yield session

# Configuration override fixtures
@pytest.fixture
def test_settings():
    """Override settings for testing"""
    from core.config import settings
    
    original_debug = settings.DEBUG
    original_database_url = settings.DATABASE_URL
    
    settings.DEBUG = True
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    yield settings
    
    settings.DEBUG = original_debug
    settings.DATABASE_URL = original_database_url

# Authentication fixtures
@pytest.fixture
async def authenticated_user(test_session, sample_user_data):
    """Create authenticated user for testing"""
    from core.database import User
    from utils.security import hash_password
    
    user = User(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        hashed_password=hash_password(sample_user_data["password"]),
        balance=1000.0
    )
    
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    return user

@pytest.fixture
def auth_headers(authenticated_user):
    """Create authentication headers"""
    from utils.security import create_access_token
    
    token = create_access_token(data={"sub": authenticated_user.username})
    return {"Authorization": f"Bearer {token}"}

# Game theory and prediction fixtures
@pytest.fixture
def mock_game_theory_predictor():
    """Mock game theory predictor"""
    with patch('services.game_theory_predictor.GameTheoryPredictor') as mock:
        predictor_instance = MagicMock()
        predictor_instance.analyze_nash_equilibrium.return_value = {
            "strategy": "conservative",
            "confidence": 0.85,
            "recommended_stake": 0.15
        }
        predictor_instance.calculate_kelly_criterion.return_value = 0.12
        predictor_instance.minimax_strategy.return_value = {
            "optimal_bet": "moneyline_home",
            "expected_value": 0.08
        }
        
        mock.return_value = predictor_instance
        yield predictor_instance

# Cache service fixtures
@pytest.fixture
def mock_cache_service():
    """Mock cache service"""
    with patch('services.cache_service.CacheService') as mock:
        cache_instance = MagicMock()
        cache_instance.get = AsyncMock(return_value=None)
        cache_instance.set = AsyncMock(return_value=True)
        cache_instance.delete = AsyncMock(return_value=True)
        cache_instance.get_many = AsyncMock(return_value={})
        cache_instance.set_many = AsyncMock(return_value=True)
        
        mock.return_value = cache_instance
        yield cache_instance

# External API mocking fixtures
@pytest.fixture
def mock_external_apis():
    """Mock all external APIs"""
    mocks = {}
    
    # ESPN API
    with patch('services.sports_api_service.SportsAPIService.fetch_espn_data') as espn_mock:
        espn_mock.return_value = [
            {
                "external_id": "espn_1",
                "sport": "football",
                "league": "NFL",
                "home_team": "Team A",
                "away_team": "Team B",
                "event_date": "2025-11-01T20:00:00Z",
                "odds": {"moneyline": {"home": 1.85, "away": 2.10}}
            }
        ]
        mocks['espn'] = espn_mock
    
    # DraftKings API
    with patch('services.draftkings_service.DraftKingsService.place_bet') as dk_mock:
        dk_mock.return_value = {
            "bet_id": "dk_123456",
            "status": "pending",
            "amount": 50.0
        }
        mocks['draftkings'] = dk_mock
    
    yield mocks

# Error simulation fixtures
@pytest.fixture
def simulate_database_error():
    """Simulate database errors"""
    with patch('sqlalchemy.ext.asyncio.AsyncSession.execute') as mock:
        mock.side_effect = Exception("Database connection failed")
        yield mock

@pytest.fixture
def simulate_api_error():
    """Simulate API errors"""
    with patch('aiohttp.ClientSession.get') as mock:
        mock.side_effect = aiohttp.ClientError("API request failed")
        yield mock

@pytest.fixture
def simulate_redis_error():
    """Simulate Redis errors"""
    with patch('redis.asyncio.Redis.get') as mock:
        mock.side_effect = redis.RedisError("Redis connection failed")
        yield mock

# Load testing fixtures
@pytest.fixture
def load_test_config():
    """Configuration for load testing"""
    return {
        "concurrent_users": 50,
        "test_duration": 60,  # seconds
        "ramp_up_time": 10,   # seconds
        "endpoints": [
            "/api/v1/sports/games",
            "/api/v1/predictions/daily",
            "/api/v1/bets",
            "/health"
        ]
    }

# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_after_test(test_session, test_redis):
    """Automatic cleanup after each test"""
    yield
    
    # Clean up database
    await test_session.rollback()
    
    # Clean up Redis
    await test_redis.flushdb()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )

# Async test configuration
@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests"""
    return "asyncio"

# Custom test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    async def create_test_user(session: AsyncSession, **kwargs):
        """Create test user with defaults"""
        from core.database import User
        from utils.security import hash_password
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": hash_password("password123"),
            "balance": 1000.0,
            **kwargs
        }
        
        user = User(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user
    
    @staticmethod
    async def create_test_game(session: AsyncSession, **kwargs):
        """Create test game with defaults"""
        from core.database import SportEvent
        from datetime import datetime, timedelta
        
        game_data = {
            "external_id": "test_game",
            "sport": "football",
            "league": "NFL",
            "home_team": "Home Team",
            "away_team": "Away Team",
            "event_date": datetime.utcnow() + timedelta(days=1),
            "odds_data": {"moneyline": {"home": 1.85, "away": 2.10}},
            **kwargs
        }
        
        game = SportEvent(**game_data)
        session.add(game)
        await session.commit()
        await session.refresh(game)
        
        return game
    
    @staticmethod
    async def create_test_bet(session: AsyncSession, user_id: int, event_id: int, **kwargs):
        """Create test bet with defaults"""
        from core.database import Bet
        from datetime import datetime
        
        bet_data = {
            "user_id": user_id,
            "event_id": event_id,
            "bet_type": "moneyline",
            "selection": "home",
            "odds": 1.85,
            "stake": 50.0,
            "potential_payout": 92.5,
            "status": "pending",
            "external_bet_id": "test_bet_123",
            "placed_at": datetime.utcnow(),
            **kwargs
        }
        
        bet = Bet(**bet_data)
        session.add(bet)
        await session.commit()
        await session.refresh(bet)
        
        return bet

@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils