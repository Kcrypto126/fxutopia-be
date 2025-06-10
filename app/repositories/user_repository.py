from sqlalchemy.orm import Session
from typing import Optional
from .base import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()