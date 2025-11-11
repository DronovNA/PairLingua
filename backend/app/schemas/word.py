from datetime import datetime
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
    """Word pair enriched with user's learning progress"""
    user_accuracy: Optional[float] = None
    last_reviewed: Optional[datetime] = None
    ease_factor: Optional[float] = None
    due_date: Optional[datetime] = None
    is_due: bool = False
    review_count: int = 0

    class Config:
        from_attributes = True
