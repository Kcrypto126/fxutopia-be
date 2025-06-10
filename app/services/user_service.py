from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List, Optional
import os
import uuid

from ..models.user import User
from ..schemas.user import UserUpdate
from ..config import get_settings

settings = get_settings()

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_users(self, skip: int = 0, limit: int = 20) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def upload_avatar(self, user_id: int, file: UploadFile) -> str:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise ValueError("Invalid file type")
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        filename = f"avatar_{user_id}_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, "avatars", filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update user avatar URL
        avatar_url = f"/uploads/avatars/{filename}"
        user = self.get_user_by_id(user_id)
        user.avatar_url = avatar_url
        self.db.commit()
        
        return avatar_url
