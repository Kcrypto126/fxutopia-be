from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import secrets

from app.models.user import User, UserSession, UserRole
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash
from app.config import get_settings

settings = get_settings()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_create: UserCreate) -> User:
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            bio=user_create.bio,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_refresh_token(self, user_id: int) -> str:
        # Clean up expired tokens
        self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.expires_at < datetime.utcnow()
            )
        ).delete()
        
        # Create new refresh token
        refresh_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        self.db.add(session)
        self.db.commit()
        
        return refresh_token
    
    def verify_refresh_token(self, refresh_token: str) -> Optional[User]:
        session = self.db.query(UserSession).filter(
            and_(
                UserSession.refresh_token == refresh_token,
                UserSession.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not session:
            return None
        
        return self.get_user_by_id(session.user_id)
    
    def create_verification_token(self, email: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = {"sub": email, "exp": expire, "type": "verification"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def verify_email_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if email is None or token_type != "verification":
                return False
            
            user = self.get_user_by_email(email)
            if user:
                user.is_verified = True
                self.db.commit()
                return True
                
        except JWTError:
            pass
        
        return False
    
    def create_password_reset_token(self, email: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    def reset_password(self, token: str, new_password: str) -> bool:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if email is None or token_type != "password_reset":
                return False
            
            user = self.get_user_by_email(email)
            if user:
                user.hashed_password = get_password_hash(new_password)
                self.db.commit()
                return True
                
        except JWTError:
            pass
        
        return False
    
    def update_last_login(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
