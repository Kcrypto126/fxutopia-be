from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from app.models.reviews import Review, ReviewHelpfulVote, ReviewCategory

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_review(
        self,
        title: str,
        content: str,
        category: ReviewCategory,
        subject_name: str,
        overall_rating: float,
        author_id: int,
        subject_url: Optional[str] = None
    ) -> Review:
        db_review = Review(
            title=title,
            content=content,
            category=category,
            subject_name=subject_name,
            overall_rating=overall_rating,
            author_id=author_id,
            subject_url=subject_url
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review
    
    def get_reviews(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[ReviewCategory] = None,
        subject_name: Optional[str] = None
    ) -> List[Review]:
        query = self.db.query(Review)
        
        if category:
            query = query.filter(Review.category == category)
        
        if subject_name:
            query = query.filter(Review.subject_name.ilike(f"%{subject_name}%"))
        
        return query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    def get_review_by_id(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()
    
    def mark_review_helpful(self, review_id: int, user_id: int, is_helpful: bool) -> bool:
        existing_vote = self.db.query(ReviewHelpfulVote).filter(
            and_(
                ReviewHelpfulVote.review_id == review_id,
                ReviewHelpfulVote.user_id == user_id
            )
        ).first()
        
        if existing_vote:
            existing_vote.is_helpful = is_helpful
        else:
            vote = ReviewHelpfulVote(
                review_id=review_id,
                user_id=user_id,
                is_helpful=is_helpful
            )
            self.db.add(vote)
        
        self.db.commit()
        
        # Update helpful count
        self._update_helpful_count(review_id)
        
        return True
    
    def _update_helpful_count(self, review_id: int):
        helpful_count = self.db.query(ReviewHelpfulVote).filter(
            and_(
                ReviewHelpfulVote.review_id == review_id,
                ReviewHelpfulVote.is_helpful == True
            )
        ).count()
        
        review = self.get_review_by_id(review_id)
        if review:
            review.helpful_count = helpful_count
            self.db.commit()