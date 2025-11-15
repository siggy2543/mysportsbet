"""
Betting routes for placing and managing bets
Integrates with DraftKings API for actual bet placement
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from core.database import get_db, User, Bet, SportEvent
from utils.security import get_current_user
from services.betting_service import BettingService
from services.draftkings_service import DraftKingsService
from schemas.betting import (
    BetCreate, 
    BetResponse, 
    ParlayBetCreate, 
    BettingStrategy,
    BetAnalysis
)

router = APIRouter()
betting_service = BettingService()
draftkings_service = DraftKingsService()

@router.post("/place", response_model=BetResponse)
async def place_bet(
    bet_data: BetCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Place a single bet"""
    # Validate user balance
    if bet_data.stake > current_user.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Get event details
    result = await db.execute(
        select(SportEvent).where(SportEvent.id == bet_data.event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Validate bet amount limits
    if bet_data.stake < 10.0 or bet_data.stake > 1000.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bet amount must be between $10 and $1000"
        )
    
    try:
        # Place bet with DraftKings
        external_bet = await draftkings_service.place_bet(
            event_id=event.external_id,
            bet_type=bet_data.bet_type,
            selection=bet_data.selection,
            stake=bet_data.stake,
            odds=bet_data.odds
        )
        
        # Create bet record
        db_bet = Bet(
            user_id=current_user.id,
            event_id=event.id,
            bet_type=bet_data.bet_type,
            selection=bet_data.selection,
            odds=bet_data.odds,
            stake=bet_data.stake,
            potential_payout=bet_data.stake * bet_data.odds,
            external_bet_id=external_bet.get("bet_id"),
            status="pending"
        )
        
        # Update user balance
        current_user.balance -= bet_data.stake
        
        db.add(db_bet)
        await db.commit()
        await db.refresh(db_bet)
        
        # Schedule bet monitoring
        background_tasks.add_task(
            betting_service.monitor_bet_result, 
            db_bet.id
        )
        
        return BetResponse(
            id=db_bet.id,
            event_id=db_bet.event_id,
            bet_type=db_bet.bet_type,
            selection=db_bet.selection,
            odds=db_bet.odds,
            stake=db_bet.stake,
            potential_payout=db_bet.potential_payout,
            status=db_bet.status,
            placed_at=db_bet.placed_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place bet: {str(e)}"
        )

@router.post("/parlay", response_model=BetResponse)
async def place_parlay_bet(
    parlay_data: ParlayBetCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Place a parlay bet with multiple selections"""
    total_stake = parlay_data.total_stake
    
    # Validate user balance
    if total_stake > current_user.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Calculate combined odds
    combined_odds = 1.0
    for leg in parlay_data.legs:
        combined_odds *= leg.odds
    
    try:
        # Place parlay bet with DraftKings
        external_bet = await draftkings_service.place_parlay_bet(
            legs=parlay_data.legs,
            stake=total_stake
        )
        
        # Create parlay bet record
        db_bet = Bet(
            user_id=current_user.id,
            event_id=parlay_data.legs[0].event_id,  # Use first event as reference
            bet_type="parlay",
            selection=f"Parlay ({len(parlay_data.legs)} legs)",
            odds=combined_odds,
            stake=total_stake,
            potential_payout=total_stake * combined_odds,
            external_bet_id=external_bet.get("bet_id"),
            status="pending"
        )
        
        # Update user balance
        current_user.balance -= total_stake
        
        db.add(db_bet)
        await db.commit()
        await db.refresh(db_bet)
        
        return BetResponse(
            id=db_bet.id,
            event_id=db_bet.event_id,
            bet_type=db_bet.bet_type,
            selection=db_bet.selection,
            odds=db_bet.odds,
            stake=db_bet.stake,
            potential_payout=db_bet.potential_payout,
            status=db_bet.status,
            placed_at=db_bet.placed_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place parlay bet: {str(e)}"
        )

@router.get("/", response_model=List[BetResponse])
async def get_user_bets(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's betting history with optional filtering"""
    # Build query with proper indexing
    query = select(Bet).where(Bet.user_id == current_user.id)
    
    # Add status filter if provided
    if status_filter:
        query = query.where(Bet.status == status_filter)
    
    # Execute optimized query with proper ordering
    result = await db.execute(
        query
        .order_by(Bet.placed_at.desc())  # Uses ix_user_placed_at index
        .offset(skip)
        .limit(limit)
    )
    bets = result.scalars().all()
    
    return [
        BetResponse(
            id=bet.id,
            event_id=bet.event_id,
            bet_type=bet.bet_type,
            selection=bet.selection,
            odds=bet.odds,
            stake=bet.stake,
            potential_payout=bet.potential_payout,
            status=bet.status,
            placed_at=bet.placed_at,
            settled_at=bet.settled_at
        )
        for bet in bets
    ]

@router.get("/public/recommendations", response_model=List[BetAnalysis])
async def get_public_bet_recommendations(
    sport: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered bet recommendations (public endpoint)"""
    try:
        recommendations = await betting_service.get_bet_recommendations(
            user_id=None,  # No specific user for public recommendations
            sport=sport,
            max_recommendations=10
        )
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/public/status")
async def get_betting_status():
    """Get public betting system status"""
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
            "default_bet": 5.0
        }
    }

@router.get("/recommendations", response_model=List[BetAnalysis])
async def get_bet_recommendations(
    sport: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered bet recommendations (authenticated)"""
    try:
        recommendations = await betting_service.get_bet_recommendations(
            user_id=current_user.id,
            sport=sport,
            max_recommendations=10
        )
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.post("/strategy/analyze", response_model=BettingStrategy)
async def analyze_betting_strategy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze user's betting strategy and performance"""
    try:
        strategy_analysis = await betting_service.analyze_user_strategy(
            user_id=current_user.id
        )
        return strategy_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze strategy: {str(e)}"
        )

@router.post("/automated/enable")
async def enable_automated_betting(
    enable: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Enable or disable automated betting with $5 fixed bets"""
    try:
        from services.automated_betting_engine import AutomatedBettingEngine
        from services.prediction_service import PredictionService  
        from services.draftkings_service import DraftKingsService
        from services.cache_service import CacheService
        
        # Initialize services
        cache_service = CacheService()
        prediction_service = PredictionService()
        draftkings_service = DraftKingsService()
        
        # Create automated betting engine
        betting_engine = AutomatedBettingEngine(
            prediction_service=prediction_service,
            draftkings_service=draftkings_service,
            cache_service=cache_service
        )
        
        # Enable/disable automated betting
        await betting_engine.enable_automatic_betting(enable)
        
        # Get status
        status = await betting_engine.get_betting_status()
        
        return {
            "message": f"Automated betting {'enabled' if enable else 'disabled'}",
            "status": status,
            "fixed_bet_amount": 5.0,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {'enable' if enable else 'disable'} automated betting: {str(e)}"
        )

@router.get("/automated/status")
async def get_automated_betting_status(
    current_user: User = Depends(get_current_user)
):
    """Get current automated betting status"""
    try:
        from services.automated_betting_engine import AutomatedBettingEngine
        from services.prediction_service import PredictionService  
        from services.draftkings_service import DraftKingsService
        from services.cache_service import CacheService
        
        # Initialize services (in production, these would be singletons)
        cache_service = CacheService()
        prediction_service = PredictionService()
        draftkings_service = DraftKingsService()
        
        betting_engine = AutomatedBettingEngine(
            prediction_service=prediction_service,
            draftkings_service=draftkings_service,
            cache_service=cache_service
        )
        
        status = await betting_engine.get_betting_status()
        
        return {
            "automated_betting_status": status,
            "user_id": current_user.id,
            "system_info": {
                "openai_fallback_enabled": True,
                "fixed_bet_amount": 5.0,
                "supported_sports": ["NBA", "NFL", "MLB", "NHL"],
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get automated betting status: {str(e)}"
        )