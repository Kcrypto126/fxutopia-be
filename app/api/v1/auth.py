from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from ...database import get_db
from ...schemas.user import UserCreate, UserInDB, Token, Login, RefreshToken
from ...services.auth_service import AuthService
from ...services.email_service import EmailService
from ...core.security import create_access_token
from ...config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    email_service = EmailService()
    
    # Check if user already exists
    if auth_service.get_user_by_email(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    if auth_service.get_user_by_username(user_in.username):
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create user
    user = auth_service.create_user(user_in)
    
    # Send verification email
    verification_token = auth_service.create_verification_token(user.email)
    background_tasks.add_task(
        email_service.send_verification_email,
        user.email,
        verification_token
    )
    
    return user

@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
    db: Session = Depends(get_db)
):
    """Login user"""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    refresh_token = auth_service.create_refresh_token(user.id)
    
    # Update last login
    auth_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    auth_service = AuthService(db)
    
    user = auth_service.verify_refresh_token(refresh_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    new_refresh_token = auth_service.create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email"""
    auth_service = AuthService(db)
    
    success = auth_service.verify_email_token(token)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    auth_service = AuthService(db)
    email_service = EmailService()
    
    user = auth_service.get_user_by_email(email)
    if user:
        reset_token = auth_service.create_password_reset_token(email)
        background_tasks.add_task(
            email_service.send_password_reset_email,
            email,
            reset_token
        )
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Reset password"""
    auth_service = AuthService(db)
    
    success = auth_service.reset_password(token, new_password)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}