from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.word_service import WordService
from app.schemas.word import (
    WordPair, WordPairCreate, WordPairUpdate, WordPairSearch,
    WordPairBatchCreate, WordPairWithUserProgress
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/pairs",
    response_model=List[WordPairWithUserProgress],
    summary="Search word pairs",
    description="Search word pairs with optional filters and user progress"
)
async def search_word_pairs(
    query: Optional[str] = Query(None, description="Search term"),
    cefr_level: Optional[str] = Query(None, description="CEFR level filter"),
    tags: Optional[List[str]] = Query(None, description="Tags filter"),
    limit: int = Query(20, ge=1, le=100, description="Results limit"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search word pairs with user progress"""
    try:
        search_params = WordPairSearch(
            query=query,
            cefr_level=cefr_level,
            tags=tags or [],
            limit=limit,
            cursor=cursor
        )
        
        word_service = WordService(db)
        word_pairs, next_cursor = word_service.get_word_pairs(
            search_params, 
            user_id=str(current_user.id)
        )
        if not word_pairs:
            # Вернуть пустой список с описанием в заголовке (например)
            # Или просто пустой список: FastAPI сериализует его в []
            return []
        
        # Add pagination header
        # In real implementation, you'd add Link header with next_cursor
        return word_pairs
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/pairs/random_simple",
    response_model=List[WordPairWithUserProgress],
    summary="Get random word pairs, no filters"
)
async def get_random_word_pairs_simple_route(
        limit: int = Query(5, ge=1, le=100, description="Number of random words"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        word_service = WordService(db)
        word_pairs = word_service.get_random_word_pairs_simple(limit, user_id=str(current_user.id))

        if not word_pairs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No word pairs found")

        return word_pairs

    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except HTTPException:
        raise  # Пробрасываем уже сформированные HTTP ошибки

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")




@router.get(
    "/pairs/{word_pair_id}",
    response_model=WordPair,
    summary="Get word pair",
    description="Get a specific word pair by ID"
)
async def get_word_pair(
    word_pair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get word pair by ID"""
    try:
        word_service = WordService(db)
        return word_service.get_word_pair(word_pair_id)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/pairs",
    response_model=WordPair,
    status_code=status.HTTP_201_CREATED,
    summary="Create word pair",
    description="Create a new word pair (admin only)"
)
async def create_word_pair(
    word_data: WordPairCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new word pair (admin only)"""
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.create_word_pair(word_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/pairs/batch",
    response_model=List[WordPair],
    status_code=status.HTTP_201_CREATED,
    summary="Create word pairs in batch",
    description="Create multiple word pairs at once (admin only)"
)
async def create_word_pairs_batch(
    batch_data: WordPairBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple word pairs in batch"""
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.create_word_pairs_batch(batch_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/pairs/{word_pair_id}",
    response_model=WordPair,
    summary="Update word pair",
    description="Update an existing word pair (admin only)"
)
async def update_word_pair(
    word_pair_id: int,
    update_data: WordPairUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update word pair"""
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.update_word_pair(word_pair_id, update_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/pairs/{word_pair_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete word pair",
    description="Soft delete a word pair (admin only)"
)
async def delete_word_pair(
    word_pair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete word pair (soft delete)"""
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        success = word_service.delete_word_pair(word_pair_id)
        
        if success:
            return {"message": f"Word pair {word_pair_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete word pair"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
