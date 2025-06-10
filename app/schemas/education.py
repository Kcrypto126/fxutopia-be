from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.models.education import ContentType, DifficultyLevel

class EducationalContentBase(BaseModel):
    title: str
    content: str
    content_type: ContentType
    difficulty_level: DifficultyLevel
    summary: Optional[str] = None
    tags: Optional[str] = None

class EducationalContentCreate(EducationalContentBase):
    pass

class EducationalContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    is_published: Optional[bool] = None

class EducationalContentInDB(EducationalContentBase):
    id: int
    author_id: int
    is_published: bool
    is_featured: bool
    view_count: int
    estimated_read_time: Optional[int]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    difficulty_level: DifficultyLevel

class CourseCreate(CourseBase):
    pass

class CourseInDB(CourseBase):
    id: int
    author_id: int
    is_published: bool
    thumbnail_url: Optional[str]
    estimated_duration: Optional[int]
    enrollment_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True