from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from ..models.reviews import ReviewCategory

class ReviewBase(BaseModel):
    title: str
    content: str
    category: ReviewCategory
    subject_name: str
    overall_rating: float
    subject_url: Optional[str] = None
    
    @validator('overall_rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    id: int
    author_id: int
    ratings_breakdown: Optional[Dict]
    pros: Optional[List[str]]
    cons: Optional[List[str]]
    is_verified: bool
    helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True