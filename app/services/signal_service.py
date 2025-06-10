from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional

from ..models.signals import (
    Signal, SignalProvider, SignalSubscription,
    SignalType, SignalStatus
)

class SignalService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_signal(
        self,
        provider_id: int,
        symbol: str,
        signal_type: SignalType,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        description: Optional[str] = None,
        confidence_level: Optional[int] = None
    ) -> Signal:
        db_signal = Signal(
            provider_id=provider_id,
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            description=description,
            confidence_level=confidence_level
        )
        self.db.add(db_signal)
        self.db.commit()
        self.db.refresh(db_signal)
        return db_signal
    
    def get_signals(
        self,
        skip: int = 0,
        limit: int = 20,
        symbol: Optional[str] = None,
        status: Optional[SignalStatus] = None,
        provider_id: Optional[int] = None
    ) -> List[Signal]:
        query = self.db.query(Signal)
        
        if symbol:
            query = query.filter(Signal.symbol == symbol)
        
        if status:
            query = query.filter(Signal.status == status)
        
        if provider_id:
            query = query.filter(Signal.provider_id == provider_id)
        
        return query.order_by(desc(Signal.created_at)).offset(skip).limit(limit).all()
    
    def create_signal_provider(
        self,
        user_id: int,
        display_name: str,
        description: Optional[str] = None,
        subscription_price: float = 0.0
    ) -> Optional[SignalProvider]:
        # Check if user is already a provider
        existing_provider = self.db.query(SignalProvider).filter(
            SignalProvider.user_id == user_id
        ).first()
        
        if existing_provider:
            return None
        
        provider = SignalProvider(
            user_id=user_id,
            display_name=display_name,
            description=description,
            subscription_price=subscription_price
        )
        self.db.add(provider)
        self.db.commit()
        self.db.refresh(provider)
        return provider
    
    def get_signal_providers(self, skip: int = 0, limit: int = 20) -> List[SignalProvider]:
        return self.db.query(SignalProvider).order_by(
            desc(SignalProvider.win_rate)
        ).offset(skip).limit(limit).all()
    
    def subscribe_to_provider(self, provider_id: int, user_id: int) -> Optional[SignalSubscription]:
        # Check if already subscribed
        existing_subscription = self.db.query(SignalSubscription).filter(
            and_(
                SignalSubscription.provider_id == provider_id,
                SignalSubscription.user_id == user_id,
                SignalSubscription.is_active == True
            )
        ).first()
        
        if existing_subscription:
            return existing_subscription
        
        subscription = SignalSubscription(
            provider_id=provider_id,
            user_id=user_id
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Update subscriber count
        provider = self.db.query(SignalProvider).filter(
            SignalProvider.user_id == provider_id
        ).first()
        if provider:
            provider.subscriber_count += 1
            self.db.commit()
        
        return subscription
