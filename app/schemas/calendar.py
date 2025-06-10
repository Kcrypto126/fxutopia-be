from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.calendar import EventImpact

class EconomicEventBase(BaseModel):
    title: str
    country: str
    currency: str
    impact: EventImpact
    event_time: datetime
    description: Optional[str] = None
    forecast_value: Optional[str] = None
    previous_value: Optional[str] = None
    source_url: Optional[str] = None

class EconomicEventCreate(EconomicEventBase):
    pass

class EconomicEventUpdate(BaseModel):
    actual_value: Optional[str] = None

class EconomicEventInDB(EconomicEventBase):
    id: int
    actual_value: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True