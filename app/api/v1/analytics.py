from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.deps import get_current_admin_user
from app.utils.analytics import AnalyticsService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics (admin only)"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_stats()

@router.get("/popular-content")
async def get_popular_content(
    limit: int = 10,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get popular content (admin only)"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_popular_content(limit)

@router.get("/engagement")
async def get_engagement_stats(
    days: int = 30,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user engagement statistics (admin only)"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_user_engagement_stats(days)