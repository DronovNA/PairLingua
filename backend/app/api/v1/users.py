from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    User, UserUpdate, UserStats, UserStatsDetailed
)
from app.api.v1.auth import get_current_user
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/me",
    response_model=User,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        user_service = UserService(db)
        return user_service.get_user_profile(str(current_user.id))
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/me",
    response_model=User,
    summary="Update user profile",
    description="Update the profile of the currently authenticated user"
)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    try:
        user_service = UserService(db)
        return user_service.update_user_profile(str(current_user.id), update_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/me/stats",
    response_model=UserStats,
    summary="Get user statistics",
    description="Get learning statistics for the current user"
)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user learning statistics"""
    try:
        user_service = UserService(db)
        return user_service.get_user_stats(str(current_user.id))
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/me/stats/detailed",
    response_model=UserStatsDetailed,
    summary="Get detailed user statistics",
    description="Get detailed learning statistics with date range"
)
async def get_my_detailed_stats(
    date_range: str = "30days",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user statistics for specified period"""
    try:
        if date_range not in ["7days", "30days", "all"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date range. Use: 7days, 30days, or all"
            )
        
        user_service = UserService(db)
        return user_service.get_user_detailed_stats(str(current_user.id), date_range)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user password"
)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        user_service = UserService(db)
        success = user_service.change_password(
            str(current_user.id), 
            current_password, 
            new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
    description="Soft delete the current user account"
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account (soft delete)"""
    try:
        user_service = UserService(db)
        success = user_service.delete_user_account(str(current_user.id))
        
        if success:
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete account"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
