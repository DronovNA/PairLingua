from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/available",
    response_model=List[dict],
    summary="Get all achievements",
    description="Get list of all available achievements"
)
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available achievements"""
    try:
        achievements = db.query(Achievement).filter(
            Achievement.is_active == True
        ).all()
        
        return [
            {
                "id": achievement.id,
                "code": achievement.code,
                "title": achievement.title,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "difficulty": achievement.difficulty,
                "points": achievement.points
            }
            for achievement in achievements
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievements"
        )


@router.get(
    "/available/me",
    response_model=List[dict],
    summary="Get user achieavailablevements",
    description="Get achievements earned by current user"
)
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get achievements earned by current user"""
    try:
        user_achievements = db.query(UserAchievement).join(Achievement).filter(
            UserAchievement.user_id == current_user.id,
            Achievement.is_active == True
        ).all()
        
        return [
            {
                "id": ua.achievement.id,
                "code": ua.achievement.code,
                "title": ua.achievement.title,
                "description": ua.achievement.description,
                "icon": ua.achievement.icon,
                "category": ua.achievement.category,
                "difficulty": ua.achievement.difficulty,
                "points": ua.achievement.points,
                "earned_at": ua.earned_at.isoformat(),
                "context_data": ua.context_data
            }
            for ua in user_achievements
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user achievements"
        )


@router.get(
    "/available/progress",
    summary="Get achievement progress",
    description="Get progress towards unearned achievements"
)
async def get_achievement_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress towards achievements"""
    try:
        # This would calculate progress towards each achievement
        # For now, return placeholder data
        return {
            "in_progress": [
                {
                    "code": "streak_7",
                    "title": "Week Warrior",
                    "description": "Study 7 days in a row",
                    "progress": 3,
                    "target": 7,
                    "percentage": 42.8
                },
                {
                    "code": "accuracy_90",
                    "title": "Precision Master",
                    "description": "Achieve 90% accuracy over 100 reviews",
                    "progress": 67,
                    "target": 100,
                    "percentage": 67.0
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievement progress"
        )
