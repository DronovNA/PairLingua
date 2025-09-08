from datetime import datetime, timedelta
from sqlalchemy import (
    Column, Integer, DateTime, Numeric, ForeignKey, 
    SmallInteger, Boolean, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserCard(Base):
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    word_pair_id = Column(Integer, ForeignKey("word_pairs.id"), nullable=False)
    
    # SM-2 Algorithm fields
    ease_factor = Column(Numeric(4, 2), default=2.50)  # Starting ease factor
    repetition_count = Column(Integer, default=0)      # Number of successful reviews
    interval_days = Column(Integer, default=0)         # Days until next review
    due_date = Column(DateTime, nullable=True)          # When card is due for review
    
    # Review tracking
    last_quality = Column(SmallInteger, nullable=True)  # Last quality score (0-5)
    last_reviewed_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_reviews = Column(Integer, default=0)
    correct_reviews = Column(Integer, default=0)
    accuracy = Column(Numeric(4, 2), default=0.0)      # % correct
    average_response_time = Column(Integer, nullable=True)  # milliseconds
    
    # State
    is_learning = Column(Boolean, default=True)         # vs graduated
    is_suspended = Column(Boolean, default=False)       # User suspended card
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cards")
    word_pair = relationship("WordPair", back_populates="user_cards")
    reviews = relationship("Review", back_populates="user_card", lazy="dynamic")
    
    # Constraints
    __table_args__ = (
        Index('ix_user_cards_due', 'user_id', 'due_date'),
        Index('ix_user_cards_user_word', 'user_id', 'word_pair_id', unique=True),
        CheckConstraint('ease_factor >= 1.3', name='ck_ease_factor_min'),
        CheckConstraint('ease_factor <= 5.0', name='ck_ease_factor_max'),
        CheckConstraint('last_quality >= 0', name='ck_quality_min'),
        CheckConstraint('last_quality <= 5', name='ck_quality_max'),
        CheckConstraint('accuracy >= 0.0', name='ck_accuracy_min'),
        CheckConstraint('accuracy <= 1.0', name='ck_accuracy_max'),
    )
    
    @property
    def is_due(self) -> bool:
        """Check if card is due for review"""
        if self.due_date is None:
            return True
        return datetime.utcnow() >= self.due_date
    
    @property
    def days_overdue(self) -> int:
        """Days card is overdue (negative if not due)"""
        if self.due_date is None:
            return 0
        delta = datetime.utcnow() - self.due_date
        return delta.days
    
    def schedule_next_review(self, quality: int) -> None:
        """Schedule next review using SM-2 algorithm"""
        from app.services.sm2_service import SM2Service
        sm2 = SM2Service()
        
        result = sm2.calculate_next_interval(
            quality=quality,
            ease_factor=float(self.ease_factor),
            interval_days=self.interval_days,
            repetition_count=self.repetition_count
        )
        
        self.ease_factor = result.ease_factor
        self.interval_days = result.interval_days
        self.repetition_count = result.repetition_count
        self.due_date = datetime.utcnow() + timedelta(days=result.interval_days)
        self.last_quality = quality
        self.last_reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
