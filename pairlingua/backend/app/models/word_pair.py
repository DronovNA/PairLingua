import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class WordPair(Base):
    __tablename__ = "word_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core content
    spanish_word = Column(String(200), nullable=False, index=True)
    russian_word = Column(String(200), nullable=False, index=True)
    
    # Audio
    audio_url = Column(Text, nullable=True)
    
    # Metadata
    cefr_level = Column(String(2), index=True)  # A1, A2, B1, B2, C1, C2
    frequency_rank = Column(Integer, index=True, nullable=True)
    tags = Column(ARRAY(String), default=list)
    
    # Examples and context
    examples = Column(JSONB, default=list)  # [{"es": "...", "ru": "..."}]
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user_cards = relationship("UserCard", back_populates="word_pair", lazy="dynamic")
    reviews = relationship("Review", back_populates="word_pair", lazy="dynamic")
