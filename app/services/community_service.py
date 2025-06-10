from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from ..models.community import Post, Comment, PostLike, CommentLike, PostCategory
from ..models.user import User
from ..schemas.community import PostCreate, PostUpdate, CommentCreate, CommentUpdate

class CommunityService:
    def __init__(self, db: Session):
        self.db = db
    
    # Post methods
    def create_post(self, post_create: PostCreate, author_id: int) -> Post:
        db_post = Post(**post_create.dict(), author_id=author_id)
        self.db.add(db_post)
        self.db.commit()
        self.db.refresh(db_post)
        return db_post
    
    def get_posts(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        category: Optional[PostCategory] = None,
        search: Optional[str] = None
    ) -> List[Post]:
        query = self.db.query(Post)
        
        if category:
            query = query.filter(Post.category == category)
        
        if search:
            query = query.filter(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.content.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()
    
    def update_post(self, post_id: int, post_update: PostUpdate) -> Post:
        post = self.get_post_by_id(post_id)
        if not post:
            return None
        
        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)
        
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def delete_post(self, post_id: int) -> bool:
        post = self.get_post_by_id(post_id)
        if not post:
            return False
        
        self.db.delete(post)
        self.db.commit()
        return True
    
    def increment_post_views(self, post_id: int):
        post = self.get_post_by_id(post_id)
        if post:
            post.view_count += 1
            self.db.commit()
    
    def toggle_post_like(self, post_id: int, user_id: int) -> bool:
        existing_like = self.db.query(PostLike).filter(
            and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
        ).first()
        
        if existing_like:
            self.db.delete(existing_like)
            self.db.commit()
            
            # Update like count
            post = self.get_post_by_id(post_id)
            post.like_count -= 1
            self.db.commit()
            return False
        else:
            new_like = PostLike(post_id=post_id, user_id=user_id)
            self.db.add(new_like)
            self.db.commit()
            
            # Update like count
            post = self.get_post_by_id(post_id)
            post.like_count += 1
            self.db.commit()
            return True
    
    # Comment methods
    def create_comment(self, post_id: int, comment_create: CommentCreate, author_id: int) -> Comment:
        db_comment = Comment(
            **comment_create.dict(),
            post_id=post_id,
            author_id=author_id
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_comments_by_post(self, post_id: int, skip: int = 0, limit: int = 50) -> List[Comment]:
        return self.db.query(Comment).filter(
            and_(Comment.post_id == post_id, Comment.parent_id.is_(None))
        ).order_by(Comment.created_at).offset(skip).limit(limit).all()
    
    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def update_comment(self, comment_id: int, comment_update: CommentUpdate) -> Comment:
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return None
        
        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def delete_comment(self, comment_id: int) -> bool:
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            return False
        
        self.db.delete(comment)
        self.db.commit()
        return True
    
    def toggle_comment_like(self, comment_id: int, user_id: int) -> bool:
        existing_like = self.db.query(CommentLike).filter(
            and_(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id)
        ).first()
        
        if existing_like:
            self.db.delete(existing_like)
            self.db.commit()
            
            # Update like count
            comment = self.get_comment_by_id(comment_id)
            comment.like_count -= 1
            self.db.commit()
            return False
        else:
            new_like = CommentLike(comment_id=comment_id, user_id=user_id)
            self.db.add(new_like)
            self.db.commit()
            
            # Update like count
            comment = self.get_comment_by_id(comment_id)
            comment.like_count += 1
            self.db.commit()
            return True