from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None
    locale: str = "ru"
    timezone: str = "UTC"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    
    @validator('nickname')
    def validate_nickname(cls, v):
        if v and len(v) < 3:
            raise ValueError('Nickname must be at least 3 characters')
        return v


class UserProfile(BaseModel):
    user_id: UUID
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    daily_goal: str = "10"
    difficulty_preference: str = "adaptive"
    notification_enabled: bool = True
    settings: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_cards: int
    cards_due: int
    cards_learned: int
    accuracy: float
    current_streak: int
    longest_streak: int
    total_study_time_minutes: int
    last_study_date: Optional[datetime] = None
    level_progress: Dict[str, int]  # A1: 45, A2: 23, etc.
    weekly_stats: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class User(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[UserProfile] = None

    class Config:
        from_attributes = True


class UserStatsDetailed(BaseModel):
    user_id: UUID
    date_range: str  # "7days", "30days", "all"
    
    # Overall stats
    total_reviews: int
    correct_reviews: int
    accuracy: float
    
    # Time-based stats
    daily_stats: List[Dict[str, Any]]
    streak_data: Dict[str, Any]
    
    # Learning progress
    cards_by_level: Dict[str, int]
    cards_by_status: Dict[str, int]  # learning, graduated, suspended
    
    # Performance metrics
    average_response_time: float
    best_accuracy_day: Dict[str, Any]
    most_studied_words: List[Dict[str, Any]]

    class Config:
        from_attributes = True
