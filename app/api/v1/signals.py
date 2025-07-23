from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.signals import SignalType, SignalStatus
from app.core.deps import get_current_active_user
from app.services.signal_service import SignalService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_signal(
    symbol: str,
    signal_type: SignalType,
    entry_price: float,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    description: Optional[str] = None,
    confidence_level: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a trading signal"""
    signal_service = SignalService(db)
    return signal_service.create_signal(
        provider_id=current_user.id,
        symbol=symbol,
        signal_type=signal_type,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        description=description,
        confidence_level=confidence_level
    )

@router.get("/")
async def get_signals(
    skip: int = 0,
    limit: int = 20,
    symbol: Optional[str] = None,
    status: Optional[SignalStatus] = None,
    provider_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get trading signals"""
    signal_service = SignalService(db)
    return signal_service.get_signals(
        skip=skip,
        limit=limit,
        symbol=symbol,
        status=status,
        provider_id=provider_id
    )

@router.get("/providers")
async def get_signal_providers(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get signal providers"""
    signal_service = SignalService(db)
    return signal_service.get_signal_providers(skip=skip, limit=limit)

@router.post("/providers")
async def become_signal_provider(
    display_name: str,
    description: Optional[str] = None,
    subscription_price: float = 0.0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Become a signal provider"""
    signal_service = SignalService(db)
    provider = signal_service.create_signal_provider(
        user_id=current_user.id,
        display_name=display_name,
        description=description,
        subscription_price=subscription_price
    )
    if not provider:
        raise HTTPException(status_code=400, detail="Unable to become signal provider")
    return provider

@router.post("/providers/{provider_id}/subscribe")
async def subscribe_to_provider(
    provider_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Subscribe to signal provider"""
    signal_service = SignalService(db)
    subscription = signal_service.subscribe_to_provider(provider_id, current_user.id)
    if not subscription:
        raise HTTPException(status_code=400, detail="Unable to subscribe")
    return subscription