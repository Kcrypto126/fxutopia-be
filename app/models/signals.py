from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class SignalStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class SignalType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    signal_type = Column(Enum(SignalType), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    status = Column(Enum(SignalStatus), default=SignalStatus.PENDING)
    description = Column(Text, nullable=True)
    confidence_level = Column(Integer, nullable=True)  # 1-10
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    provider = relationship("User")
    subscriptions = relationship("SignalSubscription", back_populates="signal")

class SignalProvider(Base):
    __tablename__ = "signal_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    subscription_price = Column(Float, default=0.0)
    total_signals = Column(Integer, default=0)
    successful_signals = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pips = Column(Float, default=0.0)
    subscriber_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

class SignalSubscription(Base):
    __tablename__ = "signal_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="signal_subscriptions", foreign_keys=[user_id])
    provider = relationship("User", foreign_keys=[provider_id])
    signal = relationship("Signal", back_populates="subscriptions")