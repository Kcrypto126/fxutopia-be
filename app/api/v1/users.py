from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import UserInDB, UserUpdate, UserPublic
from app.models.user import User
from app.core.deps import get_current_active_user, get_current_admin_user
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user"""
    user_service = UserService(db)
    return user_service.update_user(current_user.id, user_update)

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    user_service = UserService(db)
    avatar_url = await user_service.upload_avatar(current_user.id, file)
    return {"avatar_url": avatar_url}

@router.get("/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserPublic])
async def read_users(
    skip: int = 0,
    limit: int = 20,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get users list (admin only)"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)