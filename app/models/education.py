from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ContentType(str, enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"
    COURSE = "course"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EducationalContent(Base):
    __tablename__ = "educational_content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    estimated_read_time = Column(Integer, nullable=True)  # in minutes
    video_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # JSON array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User")
    course_modules = relationship("CourseModule", back_populates="content")
    user_progress = relationship("UserProgress", back_populates="content")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    thumbnail_url = Column(String, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    enrollment_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User")
    modules = relationship("CourseModule", back_populates="course", order_by="CourseModule.order")
    enrollments = relationship("CourseEnrollment", back_populates="course")

class CourseModule(Base):
    __tablename__ = "course_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("educational_content.id"), nullable=False)
    order = Column(Integer, nullable=False)
    is_preview = Column(Boolean, default=False)
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    content = relationship("EducationalContent", back_populates="course_modules")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress_percentage = Column(Float, default=0.0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    course = relationship("Course", back_populates="enrollments")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("educational_content.id"), nullable=False)
    completed = Column(Boolean, default=False)
    time_spent = Column(Integer, default=0)  # in seconds
    completed_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    content = relationship("EducationalContent", back_populates="user_progress")