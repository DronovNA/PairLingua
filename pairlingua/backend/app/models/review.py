from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey, ColumnElement
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    word_pair_id = Column(Integer, ForeignKey("word_pairs.id"), nullable=False)
    user_card_id = Column(Integer, ForeignKey("user_cards.id"), nullable=False)
    
    # Review data
    quality = Column(SmallInteger, nullable=False)      # 0-5 quality score
    response_time_ms = Column(Integer, nullable=True)   # Response time in milliseconds
    source = Column(String(50), default="web")          # matching, multiple_choice, typing, etc.
    
    # Context
    session_id = Column(UUID(as_uuid=True), nullable=True)  # Optional session grouping
    
    # Before/after state for analysis
    ease_factor_before = Column(Integer, nullable=True)
    ease_factor_after = Column(Integer, nullable=True)
    interval_before = Column(Integer, nullable=True)
    interval_after = Column(Integer, nullable=True)
    
    # Timestamp
    reviewed_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    word_pair = relationship("WordPair", back_populates="reviews")
    user_card = relationship("UserCard", back_populates="reviews")

    @property
    def is_correct(self) -> ColumnElement[bool]:
        """Quality >= 3 is considered correct in SM-2
        (свойство пока не используется — оставить для будущих расширений)
        """
        return self.quality >= 3

