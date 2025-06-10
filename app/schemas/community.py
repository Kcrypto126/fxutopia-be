from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from ..models.community import PostCategory

class PostBase(BaseModel):
    title: str
    content: str
    category: PostCategory
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        return v.strip()

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[PostCategory] = None

class PostInDB(PostBase):
    id: int
    author_id: int
    is_pinned: bool
    is_locked: bool
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Post(PostInDB):
    author: "UserPublic"
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Comment must be at least 3 characters long')
        return v.strip()

class CommentCreate(CommentBase):
    parent_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: str

class CommentInDB(CommentBase):
    id: int
    post_id: int
    author_id: int
    parent_id: Optional[int]
    like_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Comment(CommentInDB):
    author: "UserPublic"
    replies: List["Comment"] = []
    
    class Config:
        from_attributes = True