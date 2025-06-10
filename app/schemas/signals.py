from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.signals import SignalType, SignalStatus

class SignalBase(BaseModel):
    symbol: str
    signal_type: SignalType
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    description: Optional[str] = None
    confidence_level: Optional[int] = None
    
    @validator('confidence_level')
    def validate_confidence(cls, v):
        if v is not None and not 1 <= v <= 10:
            raise ValueError('Confidence level must be between 1 and 10')
        return v

class SignalCreate(SignalBase):
    pass

class SignalInDB(SignalBase):
    id: int
    provider_id: int
    current_price: Optional[float]
    status: SignalStatus
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
