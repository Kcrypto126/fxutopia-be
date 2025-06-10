from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.reviews import ReviewCategory
from app.core.deps import get_current_active_user
from app.services.review_service import ReviewService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    title: str,
    content: str,
    category: ReviewCategory,
    subject_name: str,
    overall_rating: float,
    subject_url: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a review"""
    review_service = ReviewService(db)
    return review_service.create_review(
        title=title,
        content=content,
        category=category,
        subject_name=subject_name,
        overall_rating=overall_rating,
        author_id=current_user.id,
        subject_url=subject_url
    )

@router.get("/")
async def get_reviews(
    skip: int = 0,
    limit: int = 20,
    category: Optional[ReviewCategory] = None,
    subject_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get reviews"""
    review_service = ReviewService(db)
    return review_service.get_reviews(
        skip=skip,
        limit=limit,
        category=category,
        subject_name=subject_name
    )

@router.get("/{review_id}")
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get review by ID"""
    review_service = ReviewService(db)
    review = review_service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: int,
    is_helpful: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark review as helpful or not"""
    review_service = ReviewService(db)
    result = review_service.mark_review_helpful(review_id, current_user.id, is_helpful)
    return {"marked_helpful": result}