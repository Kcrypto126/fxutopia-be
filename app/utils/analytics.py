from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import Dict, List, Any
from app.models.user import User
from app.models.community import Post, Comment
from app.models.education import EducationalContent
from app.models.marketplace import MarketplaceProduct, ProductPurchase

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get overall platform statistics"""
        
        # User stats
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        new_users_this_month = self.db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Content stats
        total_posts = self.db.query(Post).count()
        total_comments = self.db.query(Comment).count()
        total_articles = self.db.query(EducationalContent).count()
        total_products = self.db.query(MarketplaceProduct).count()
        
        # Revenue stats
        total_revenue = self.db.query(func.sum(ProductPurchase.amount_paid)).scalar() or 0
        monthly_revenue = self.db.query(func.sum(ProductPurchase.amount_paid)).filter(
            ProductPurchase.purchased_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new_this_month": new_users_this_month
            },
            "content": {
                "posts": total_posts,
                "comments": total_comments,
                "articles": total_articles,
                "products": total_products
            },
            "revenue": {
                "total": float(total_revenue),
                "monthly": float(monthly_revenue)
            }
        }
    
    def get_popular_content(self, limit: int = 10) -> Dict[str, List[Any]]:
        """Get most popular content by views and engagement"""
        
        popular_posts = self.db.query(Post).order_by(
            desc(Post.view_count)
        ).limit(limit).all()
        
        popular_articles = self.db.query(EducationalContent).filter(
            EducationalContent.is_published == True
        ).order_by(desc(EducationalContent.view_count)).limit(limit).all()
        
        top_products = self.db.query(MarketplaceProduct).filter(
            MarketplaceProduct.status == "approved"
        ).order_by(desc(MarketplaceProduct.downloads_count)).limit(limit).all()
        
        return {
            "posts": popular_posts,
            "articles": popular_articles,
            "products": top_products
        }
    
    def get_user_engagement_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get user engagement statistics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily active users
        daily_active = self.db.query(func.count(User.id)).filter(
            User.last_login >= start_date
        ).scalar()
        
        # Posts created
        posts_created = self.db.query(func.count(Post.id)).filter(
            Post.created_at >= start_date
        ).scalar()
        
        # Comments created
        comments_created = self.db.query(func.count(Comment.id)).filter(
            Comment.created_at >= start_date
        ).scalar()
        
        return {
            "daily_active_users": daily_active,
            "posts_created": posts_created,
            "comments_created": comments_created,
            "engagement_rate": (posts_created + comments_created) / max(daily_active, 1)
        }
