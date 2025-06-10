from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON
from sqlalchemy.sql import func
from ..database import Base
import enum

class EventImpact(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EconomicEvent(Base):
    __tablename__ = "economic_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    impact = Column(Enum(EventImpact), nullable=False)
    actual_value = Column(String, nullable=True)
    forecast_value = Column(String, nullable=True)
    previous_value = Column(String, nullable=True)
    event_time = Column(DateTime(timezone=True), nullable=False)
    source_url = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())