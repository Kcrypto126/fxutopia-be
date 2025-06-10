from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from typing import List, Dict, Any, Optional
from app.models.community import Post
from app.models.education import EducationalContent
from app.models.marketplace import MarketplaceProduct
from app.models.reviews import Review

class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    def global_search(
        self,
        query: str,
        limit: int = 20,
        content_types: Optional[List[str]] = None
    ) -> Dict[str, List[Any]]:
        """Perform global search across all content types"""
        
        results = {
            "posts": [],
            "articles": [],
            "products": [],
            "reviews": []
        }
        
        if not content_types or "posts" in content_types:
            results["posts"] = self.search_posts(query, limit)
        
        if not content_types or "articles" in content_types:
            results["articles"] = self.search_articles(query, limit)
        
        if not content_types or "products" in content_types:
            results["products"] = self.search_products(query, limit)
        
        if not content_types or "reviews" in content_types:
            results["reviews"] = self.search_reviews(query, limit)
        
        return results
    
    def search_posts(self, query: str, limit: int = 20) -> List[Post]:
        """Search community posts"""
        return self.db.query(Post).filter(
            or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
        ).order_by(
            func.greatest(
                func.similarity(Post.title, query),
                func.similarity(Post.content, query)
            ).desc()
        ).limit(limit).all()
    
    def search_articles(self, query: str, limit: int = 20) -> List[EducationalContent]:
        """Search educational content"""
        return self.db.query(EducationalContent).filter(
            and_(
                EducationalContent.is_published == True,
                or_(
                    EducationalContent.title.ilike(f"%{query}%"),
                    EducationalContent.content.ilike(f"%{query}%"),
                    EducationalContent.summary.ilike(f"%{query}%")
                )
            )
        ).order_by(
            func.greatest(
                func.similarity(EducationalContent.title, query),
                func.similarity(EducationalContent.content, query)
            ).desc()
        ).limit(limit).all()
    
    def search_products(self, query: str, limit: int = 20) -> List[MarketplaceProduct]:
        """Search marketplace products"""
        return self.db.query(MarketplaceProduct).filter(
            and_(
                MarketplaceProduct.status == "approved",
                or_(
                    MarketplaceProduct.title.ilike(f"%{query}%"),
                    MarketplaceProduct.description.ilike(f"%{query}%")
                )
            )
        ).order_by(
            func.greatest(
                func.similarity(MarketplaceProduct.title, query),
                func.similarity(MarketplaceProduct.description, query)
            ).desc()
        ).limit(limit).all()
    
    def search_reviews(self, query: str, limit: int = 20) -> List[Review]:
        """Search reviews"""
        return self.db.query(Review).filter(
            or_(
                Review.title.ilike(f"%{query}%"),
                Review.content.ilike(f"%{query}%"),
                Review.subject_name.ilike(f"%{query}%")
            )
        ).order_by(
            func.greatest(
                func.similarity(Review.title, query),
                func.similarity(Review.content, query),
                func.similarity(Review.subject_name, query)
            ).desc()
        ).limit(limit).all()