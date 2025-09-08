from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.services.study_service import StudyService
from app.schemas.study import (
    StudyCardsRequest, StudyCardsResponse, 
    ReviewBatch, ReviewBatchResponse,
    SessionReplaceRequest, SessionReplaceResponse,
    StudySessionStats, LeaderboardResponse
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/cards/due",
    response_model=StudyCardsResponse,
    summary="Get cards due for review",
    description="Get cards that are due for review using spaced repetition algorithm"
)
async def get_due_cards(
    limit: int = Query(20, ge=1, le=50, description="Number of cards to return"),
    include_new: bool = Query(True, description="Include new cards"),
    exercise_types: Optional[List[str]] = Query(None, description="Filter by exercise types"),
    cefr_levels: Optional[List[str]] = Query(None, description="Filter by CEFR levels"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cards due for review with SM-2 spaced repetition"""
    try:
        study_service = StudyService(db)
        
        request = StudyCardsRequest(
            limit=limit,
            include_new=include_new,
            exercise_types=exercise_types,
            cefr_levels=cefr_levels
        )
        
        return await study_service.get_due_cards(str(current_user.id), request)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/cards/review",
    response_model=ReviewBatchResponse,
    summary="Submit review results",
    description="Submit batch of review results and update SM-2 intervals"
)
async def submit_reviews(
    review_batch: ReviewBatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit review results and update spaced repetition schedule"""
    try:
        study_service = StudyService(db)
        return await study_service.submit_review_batch(str(current_user.id), review_batch)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/session/replace",
    response_model=SessionReplaceResponse,
    summary="Replace card in session",
    description="Replace a completed card with a new one in the current session"
)
async def replace_session_card(
    replace_request: SessionReplaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Replace a completed card in the current study session"""
    try:
        study_service = StudyService(db)
        return await study_service.replace_session_card(str(current_user.id), replace_request)
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/session/{session_id}/stats",
    response_model=StudySessionStats,
    summary="Get session statistics",
    description="Get statistics for a specific study session"
)
async def get_session_stats(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a study session"""
    try:
        # Implementation would fetch session stats
        # For now, return placeholder
        return StudySessionStats(
            session_id=session_id,
            started_at=datetime.utcnow(),
            cards_studied=0,
            cards_correct=0,
            average_response_time=None,
            accuracy=0.0,
            points_earned=0,
            time_spent_minutes=0
        )
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/leaderboard/weekly",
    response_model=LeaderboardResponse,
    summary="Get weekly leaderboard",
    description="Get weekly leaderboard rankings"
)
async def get_weekly_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly leaderboard"""
    try:
        # Implementation would fetch leaderboard data
        # For now, return placeholder
        return LeaderboardResponse(
            entries=[],
            current_user_rank=None,
            period="weekly",
            last_updated=datetime.utcnow()
        )
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/progress/overview",
    summary="Get learning progress overview",
    description="Get overview of learning progress and upcoming reviews"
)
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning progress overview"""
    try:
        study_service = StudyService(db)
        
        # Get basic stats for overview
        from app.services.user_service import UserService
        user_service = UserService(db)
        stats = user_service.get_user_stats(str(current_user.id))
        
        return {
            "cards_due": stats.cards_due,
            "cards_learned": stats.cards_learned,
            "current_streak": stats.current_streak,
            "accuracy": stats.accuracy,
            "next_review_hours": 1,  # Simplified
            "study_goal_progress": min(100, (stats.cards_learned / 50) * 100)  # 50 cards goal
        }
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
