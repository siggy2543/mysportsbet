"""
Database configuration and connection management
Uses SQLAlchemy with PostgreSQL and Redis for caching
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, JSON, Index
from datetime import datetime
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Database engine with optimized settings
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX,
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,   # Recycle connections every hour
    pool_timeout=30,     # Timeout for getting connection from pool
    echo=settings.DEBUG,
    # Performance optimizations
    connect_args={
        "server_settings": {
            "application_name": "sports_betting_app",
            "jit": "off",  # Disable JIT compilation for faster queries
        },
        "command_timeout": 60,
    }
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SportEvent(Base):
    __tablename__ = "sport_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    sport: Mapped[str] = mapped_column(String(50), index=True)
    league: Mapped[str] = mapped_column(String(50), index=True)
    home_team: Mapped[str] = mapped_column(String(100), index=True)
    away_team: Mapped[str] = mapped_column(String(100), index=True)
    event_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", index=True)  # scheduled, live, finished
    odds_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes for common queries
    __table_args__ = (
        # Index for finding events by sport and date
        Index('ix_sport_event_date', 'sport', 'event_date'),
        # Index for finding events by league and status
        Index('ix_league_status', 'league', 'status'),
        # Index for finding events by teams
        Index('ix_teams', 'home_team', 'away_team'),
    )

class Bet(Base):
    __tablename__ = "bets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    event_id: Mapped[int] = mapped_column(Integer, index=True)
    bet_type: Mapped[str] = mapped_column(String(20), index=True)  # moneyline, spread, total, parlay
    selection: Mapped[str] = mapped_column(String(100))
    odds: Mapped[float] = mapped_column(Float)
    stake: Mapped[float] = mapped_column(Float)
    potential_payout: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending, won, lost, void
    external_bet_id: Mapped[str] = mapped_column(String(100), index=True)  # DraftKings bet ID
    placed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    settled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        # Index for user bet history queries
        Index('ix_user_placed_at', 'user_id', 'placed_at'),
        # Index for pending bets processing
        Index('ix_status_placed_at', 'status', 'placed_at'),
        # Index for event-based bet lookups
        Index('ix_event_user', 'event_id', 'user_id'),
    )

class Prediction(Base):
    __tablename__ = "predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer, index=True)
    model_version: Mapped[str] = mapped_column(String(20))
    prediction_type: Mapped[str] = mapped_column(String(20))  # winner, spread, total
    predicted_value: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    features_used: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    return redis_client

@asynccontextmanager
async def get_db_session():
    """Context manager for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()