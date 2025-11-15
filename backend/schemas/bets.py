"""
Pydantic schemas for betting operations
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, validator
from enum import Enum

class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"

class BetType(str, Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    OVER_UNDER = "over_under"
    PARLAY = "parlay"

class BetBase(BaseModel):
    game_id: str
    bet_type: BetType
    amount: Decimal
    odds: Decimal
    prediction: str

class BetCreate(BetBase):
    pass

class BetResponse(BetBase):
    id: int
    user_id: int
    status: BetStatus
    created_at: datetime
    settled_at: Optional[datetime]
    payout: Optional[Decimal]
    
    class Config:
        from_attributes = True

class GameBase(BaseModel):
    external_id: str
    home_team: str
    away_team: str
    game_date: datetime
    sport: str

class GameResponse(GameBase):
    id: int
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    
    class Config:
        from_attributes = True