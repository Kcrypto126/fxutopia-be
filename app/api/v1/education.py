from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.education import ContentType, DifficultyLevel
from app.core.deps import get_current_active_user, get_current_admin_user
from app.services.education_service import EducationService

router = APIRouter()

@router.post("/content", status_code=status.HTTP_201_CREATED)
async def create_content(
    title: str,
    content: str,
    content_type: ContentType,
    difficulty_level: DifficultyLevel,
    summary: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create educational content"""
    education_service = EducationService(db)
    return education_service.create_content(
        title=title,
        content=content,
        content_type=content_type,
        difficulty_level=difficulty_level,
        author_id=current_user.id,
        summary=summary,
        tags=tags
    )

@router.get("/content")
async def get_content(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[ContentType] = None,
    difficulty_level: Optional[DifficultyLevel] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get educational content list"""
    education_service = EducationService(db)
    return education_service.get_content(
        skip=skip,
        limit=limit,
        content_type=content_type,
        difficulty_level=difficulty_level,
        search=search
    )

@router.get("/content/{content_id}")
async def get_content_by_id(content_id: int, db: Session = Depends(get_db)):
    """Get educational content by ID"""
    education_service = EducationService(db)
    content = education_service.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Increment view count
    education_service.increment_content_views(content_id)
    return content

@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    title: str,
    description: str,
    difficulty_level: DifficultyLevel,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a course"""
    education_service = EducationService(db)
    return education_service.create_course(
        title=title,
        description=description,
        difficulty_level=difficulty_level,
        author_id=current_user.id
    )

@router.get("/courses")
async def get_courses(
    skip: int = 0,
    limit: int = 20,
    difficulty_level: Optional[DifficultyLevel] = None,
    db: Session = Depends(get_db)
):
    """Get courses list"""
    education_service = EducationService(db)
    return education_service.get_courses(
        skip=skip,
        limit=limit,
        difficulty_level=difficulty_level
    )

@router.post("/courses/{course_id}/enroll")
async def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    education_service = EducationService(db)
    enrollment = education_service.enroll_user_in_course(course_id, current_user.id)
    if not enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled or course not found")
    return enrollment

@router.get("/my-progress")
async def get_my_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's learning progress"""
    education_service = EducationService(db)
    return education_service.get_user_progress(current_user.id)
