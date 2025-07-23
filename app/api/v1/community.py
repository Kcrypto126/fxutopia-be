from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.community import PostCreate, PostUpdate, Post, CommentCreate, CommentUpdate, Comment
from app.models.community import PostCategory
from app.models.user import User
from app.core.deps import get_current_active_user, get_current_admin_user
from app.services.community_service import CommunityService

router = APIRouter()

# Posts endpoints
@router.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    community_service = CommunityService(db)
    return community_service.create_post(post, current_user.id)

@router.get("/posts", response_model=List[Post])
async def read_posts(
    skip: int = 0,
    limit: int = 20,
    category: Optional[PostCategory] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get posts list"""
    community_service = CommunityService(db)
    return community_service.get_posts(skip=skip, limit=limit, category=category, search=search)

@router.get("/posts/{post_id}", response_model=Post)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by ID"""
    community_service = CommunityService(db)
    post = community_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    community_service.increment_post_views(post_id)
    return post

@router.put("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update post"""
    community_service = CommunityService(db)
    post = community_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return community_service.update_post(post_id, post_update)

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete post"""
    community_service = CommunityService(db)
    post = community_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    community_service.delete_post(post_id)
    return {"message": "Post deleted successfully"}

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like/unlike a post"""
    community_service = CommunityService(db)
    result = community_service.toggle_post_like(post_id, current_user.id)
    return {"liked": result}

# Comments endpoints
@router.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    community_service = CommunityService(db)
    return community_service.create_comment(post_id, comment, current_user.id)

@router.get("/posts/{post_id}/comments", response_model=List[Comment])
async def read_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get comments for a post"""
    community_service = CommunityService(db)
    return community_service.get_comments_by_post(post_id, skip=skip, limit=limit)

@router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update comment"""
    community_service = CommunityService(db)
    comment = community_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return community_service.update_comment(comment_id, comment_update)

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete comment"""
    community_service = CommunityService(db)
    comment = community_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    community_service.delete_comment(comment_id)
    return {"message": "Comment deleted successfully"}

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like/unlike a comment"""
    community_service = CommunityService(db)
    result = community_service.toggle_comment_like(comment_id, current_user.id)
    return {"liked": result}