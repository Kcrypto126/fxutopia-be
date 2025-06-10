from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ReviewCategory(str, enum.Enum):
    BROKER = "broker"
    TRADING_PLATFORM = "trading_platform"
    SIGNAL_PROVIDER = "signal_provider"
    EDUCATIONAL_RESOURCE = "educational_resource"

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(ReviewCategory), nullable=False)
    subject_name = Column(String, nullable=False)  # Name of broker, platform, etc.
    subject_url = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    overall_rating = Column(Float, nullable=False)  # 1-5 stars
    ratings_breakdown = Column(JSON, nullable=True)  # Detailed ratings
    pros = Column(JSON, nullable=True)  # Array of pros
    cons = Column(JSON, nullable=True)  # Array of cons
    is_verified = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="reviews")
    helpful_votes = relationship("ReviewHelpfulVote", back_populates="review")

class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    is_helpful = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    review = relationship("Review", back_populates="helpful_votes")