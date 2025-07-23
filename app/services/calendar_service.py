from sqlalchemy.orm import Session
from sqlalchemy import and_, between
from typing import List, Optional
from datetime import datetime, date

from app.models.calendar import EconomicEvent, EventImpact

class CalendarService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_economic_event(
        self,
        title: str,
        country: str,
        currency: str,
        impact: EventImpact,
        event_time: datetime,
        description: Optional[str] = None,
        forecast_value: Optional[str] = None,
        previous_value: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> EconomicEvent:
        db_event = EconomicEvent(
            title=title,
            description=description,
            country=country,
            currency=currency,
            impact=impact,
            event_time=event_time,
            forecast_value=forecast_value,
            previous_value=previous_value,
            source_url=source_url
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def get_economic_events(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        impact: Optional[EventImpact] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EconomicEvent]:
        query = self.db.query(EconomicEvent)
        
        if start_date and end_date:
            query = query.filter(
                between(EconomicEvent.event_time, start_date, end_date)
            )
        
        if country:
            query = query.filter(EconomicEvent.country == country)
        
        if currency:
            query = query.filter(EconomicEvent.currency == currency)
        
        if impact:
            query = query.filter(EconomicEvent.impact == impact)
        
        return query.order_by(EconomicEvent.event_time).offset(skip).limit(limit).all()
    
    def update_economic_event(
        self,
        event_id: int,
        actual_value: Optional[str] = None
    ) -> Optional[EconomicEvent]:
        event = self.db.query(EconomicEvent).filter(EconomicEvent.id == event_id).first()
        if not event:
            return None
        
        if actual_value is not None:
            event.actual_value = actual_value
        
        self.db.commit()
        self.db.refresh(event)
        return event