from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.user import User
from app.models.calendar import EventImpact
from app.core.deps import get_current_admin_user
from app.services.calendar_service import CalendarService

router = APIRouter()

@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_economic_event(
    title: str,
    country: str,
    currency: str,
    impact: EventImpact,
    event_time: datetime,
    description: Optional[str] = None,
    forecast_value: Optional[str] = None,
    previous_value: Optional[str] = None,
    source_url: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create economic event (admin only)"""
    calendar_service = CalendarService(db)
    return calendar_service.create_economic_event(
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

@router.get("/events")
async def get_economic_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    country: Optional[str] = None,
    currency: Optional[str] = None,
    impact: Optional[EventImpact] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get economic events"""
    calendar_service = CalendarService(db)
    return calendar_service.get_economic_events(
        start_date=start_date,
        end_date=end_date,
        country=country,
        currency=currency,
        impact=impact,
        skip=skip,
        limit=limit
    )

@router.put("/events/{event_id}")
async def update_economic_event(
    event_id: int,
    actual_value: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update economic event with actual value (admin only)"""
    calendar_service = CalendarService(db)
    event = calendar_service.update_economic_event(event_id, actual_value=actual_value)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event