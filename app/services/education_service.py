from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from ..models.education import (
    EducationalContent, Course, CourseModule, CourseEnrollment, 
    UserProgress, ContentType, DifficultyLevel
)

class EducationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_content(
        self,
        title: str,
        content: str,
        content_type: ContentType,
        difficulty_level: DifficultyLevel,
        author_id: int,
        summary: Optional[str] = None,
        tags: Optional[str] = None
    ) -> EducationalContent:
        db_content = EducationalContent(
            title=title,
            content=content,
            content_type=content_type,
            difficulty_level=difficulty_level,
            author_id=author_id,
            summary=summary,
            tags=tags
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        return db_content
    
    def get_content(
        self,
        skip: int = 0,
        limit: int = 20,
        content_type: Optional[ContentType] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        search: Optional[str] = None
    ) -> List[EducationalContent]:
        query = self.db.query(EducationalContent).filter(
            EducationalContent.is_published == True
        )
        
        if content_type:
            query = query.filter(EducationalContent.content_type == content_type)
        
        if difficulty_level:
            query = query.filter(EducationalContent.difficulty_level == difficulty_level)
        
        if search:
            query = query.filter(
                or_(
                    EducationalContent.title.ilike(f"%{search}%"),
                    EducationalContent.content.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(EducationalContent.created_at)).offset(skip).limit(limit).all()
    
    def get_content_by_id(self, content_id: int) -> Optional[EducationalContent]:
        return self.db.query(EducationalContent).filter(
            and_(
                EducationalContent.id == content_id,
                EducationalContent.is_published == True
            )
        ).first()
    
    def increment_content_views(self, content_id: int):
        content = self.get_content_by_id(content_id)
        if content:
            content.view_count += 1
            self.db.commit()
    
    def create_course(
        self,
        title: str,
        description: str,
        difficulty_level: DifficultyLevel,
        author_id: int
    ) -> Course:
        db_course = Course(
            title=title,
            description=description,
            difficulty_level=difficulty_level,
            author_id=author_id
        )
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course
    
    def get_courses(
        self,
        skip: int = 0,
        limit: int = 20,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> List[Course]:
        query = self.db.query(Course).filter(Course.is_published == True)
        
        if difficulty_level:
            query = query.filter(Course.difficulty_level == difficulty_level)
        
        return query.order_by(desc(Course.created_at)).offset(skip).limit(limit).all()
    
    def enroll_user_in_course(self, course_id: int, user_id: int) -> Optional[CourseEnrollment]:
        # Check if already enrolled
        existing_enrollment = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.user_id == user_id
            )
        ).first()
        
        if existing_enrollment:
            return None
        
        # Check if course exists
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return None
        
        enrollment = CourseEnrollment(course_id=course_id, user_id=user_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        
        # Update enrollment count
        course.enrollment_count += 1
        self.db.commit()
        
        return enrollment
    
    def get_user_progress(self, user_id: int) -> List[UserProgress]:
        return self.db.query(UserProgress).filter(UserProgress.user_id == user_id).all()