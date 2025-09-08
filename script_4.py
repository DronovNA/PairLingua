# Создаем Pydantic схемы

# Schemas __init__.py
schemas_init = """from app.schemas.auth import *
from app.schemas.user import *
from app.schemas.word import *
from app.schemas.study import *
"""

# Auth schemas
auth_schemas = """from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    locale: str = "ru"
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter') 
        if not re.search(r'\\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('nickname')
    def validate_nickname(cls, v):
        if v and len(v) < 3:
            raise ValueError('Nickname must be at least 3 characters long')
        if v and len(v) > 50:
            raise ValueError('Nickname must be less than 50 characters')
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Nickname can only contain letters, numbers, underscore and dash')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
"""

# User schemas
user_schemas = """from datetime import datetime
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
"""

# Word schemas
word_schemas = """from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator


class WordPairBase(BaseModel):
    spanish_word: str
    russian_word: str
    cefr_level: Optional[str] = None
    frequency_rank: Optional[int] = None
    tags: List[str] = []
    audio_url: Optional[str] = None
    examples: List[Dict[str, str]] = []
    
    @validator('cefr_level')
    def validate_cefr_level(cls, v):
        if v and v not in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            raise ValueError('CEFR level must be one of: A1, A2, B1, B2, C1, C2')
        return v
    
    @validator('spanish_word', 'russian_word')
    def validate_words(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Word cannot be empty')
        return v.strip()


class WordPairCreate(WordPairBase):
    pass


class WordPairUpdate(BaseModel):
    spanish_word: Optional[str] = None
    russian_word: Optional[str] = None
    cefr_level: Optional[str] = None
    frequency_rank: Optional[int] = None
    tags: Optional[List[str]] = None
    audio_url: Optional[str] = None
    examples: Optional[List[Dict[str, str]]] = None
    is_active: Optional[bool] = None


class WordPair(WordPairBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordPairSearch(BaseModel):
    query: Optional[str] = None
    cefr_level: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20
    cursor: Optional[str] = None  # For cursor-based pagination
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v


class WordPairBatchCreate(BaseModel):
    word_pairs: List[WordPairCreate]
    
    @validator('word_pairs')
    def validate_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError('Cannot create more than 1000 word pairs at once')
        return v


class WordPairWithUserProgress(WordPair):
    \"\"\"Word pair enriched with user's learning progress\"\"\"
    user_accuracy: Optional[float] = None
    last_reviewed: Optional[datetime] = None
    ease_factor: Optional[float] = None
    due_date: Optional[datetime] = None
    is_due: bool = False
    review_count: int = 0

    class Config:
        from_attributes = True
"""

# Study schemas
study_schemas = """from datetime import datetime
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
    \"\"\"Study card with all information for frontend\"\"\"
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
"""

# Записываем схемы
with open("pairlingua/backend/app/schemas/__init__.py", "w") as f:
    f.write(schemas_init)

with open("pairlingua/backend/app/schemas/auth.py", "w") as f:
    f.write(auth_schemas)

with open("pairlingua/backend/app/schemas/user.py", "w") as f:
    f.write(user_schemas)

with open("pairlingua/backend/app/schemas/word.py", "w") as f:
    f.write(word_schemas)

with open("pairlingua/backend/app/schemas/study.py", "w") as f:
    f.write(study_schemas)

print("✅ Pydantic схемы созданы")
print("🔐 Auth: регистрация, логин, токены")  
print("👤 User: профиль, статистика, настройки")
print("📚 Word: пары слов, поиск, batch операции")
print("🎯 Study: карточки, обзоры, сессии, лидерборд")