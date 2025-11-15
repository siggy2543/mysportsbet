"""
Pydantic schemas for betting operations
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
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

class BetCreate(BaseModel):
    game_id: str
    bet_type: BetType
    amount: Decimal
    odds: Decimal
    prediction: str
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Bet amount must be positive')
        return v

class BetResponse(BaseModel):
    id: int
    user_id: int
    game_id: str
    bet_type: BetType
    amount: Decimal
    odds: Decimal
    prediction: str
    status: BetStatus
    created_at: datetime
    settled_at: Optional[datetime]
    payout: Optional[Decimal]
    
    class Config:
        from_attributes = True

class ParlayBetCreate(BaseModel):
    bets: List[BetCreate]
    total_amount: Decimal
    
class BettingStrategy(BaseModel):
    strategy_name: str
    parameters: Dict[str, Any]
    expected_roi: Optional[float]

class BetAnalysis(BaseModel):
    game_id: str
    recommended_bet: str
    confidence: float
    expected_value: float
    risk_level: str
    analysis_factors: List[str]