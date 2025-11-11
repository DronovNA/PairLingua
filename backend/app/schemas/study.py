from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, validator
from uuid import UUID


class StudyCardBase(BaseModel):
    id: int
    spanish_word: str
    russian_word: Optional[str] = None  # Hidden for some exercise types
    audio_url: Optional[str] = None
    cefr_level: Optional[str] = None
    type: Literal["matching", "multiple_choice", "typing", "audio"] = "matching"
    distractors: List[str] = []  # For multiple choice
    
    class Config:
        from_attributes = True


class StudyCard(StudyCardBase):
    """Study card with all information for frontend"""
    ease_factor: float
    due_date: Optional[datetime]
    is_new: bool
    review_count: int


class StudyCardsRequest(BaseModel):
    limit: int = 20
    include_new: bool = True
    exercise_types: Optional[List[str]] = None  # Filter by exercise type
    cefr_levels: Optional[List[str]] = None     # Filter by CEFR level
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Limit must be between 1 and 50')
        return v


class StudyCardsResponse(BaseModel):
    cards: List[StudyCard]
    total_due: int
    session_id: UUID
    estimated_time_minutes: int


class ReviewItem(BaseModel):
    word_pair_id: int
    quality: int  # 0-5 SM-2 quality score
    response_time_ms: Optional[int] = None
    source: str = "web"  # matching, multiple_choice, typing, etc.
    
    @validator('quality')
    def validate_quality(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Quality must be between 0 and 5')
        return v


class ReviewBatch(BaseModel):
    items: List[ReviewItem]
    session_id: Optional[UUID] = None
    
    @validator('items')
    def validate_items(cls, v):
        if len(v) > 50:
            raise ValueError('Cannot review more than 50 items at once')
        if len(v) == 0:
            raise ValueError('Must review at least one item')
        return v


class ReviewResult(BaseModel):
    word_pair_id: int
    correct: bool
    new_ease_factor: float
    new_interval_days: int
    next_review_date: datetime
    points_earned: int


class ReviewBatchResponse(BaseModel):
    results: List[ReviewResult]
    total_points_earned: int
    accuracy: float
    streak_updated: bool
    achievements_unlocked: List[str] = []


class SessionReplaceRequest(BaseModel):
    session_id: UUID
    completed_word_pair_id: int


class SessionReplaceResponse(BaseModel):
    new_card: StudyCard
    session_id: UUID


class StudySessionStats(BaseModel):
    session_id: UUID
    started_at: datetime
    cards_studied: int
    cards_correct: int
    average_response_time: Optional[float]
    accuracy: float
    points_earned: int
    time_spent_minutes: int

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    nickname: str
    points: int
    accuracy: float
    streak: int
    is_current_user: bool = False


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    current_user_rank: Optional[int] = None
    period: str  # weekly, monthly, all_time
    last_updated: datetime
