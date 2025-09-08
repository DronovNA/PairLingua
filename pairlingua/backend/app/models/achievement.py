from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    icon = Column(String(100))  # Icon identifier
    
    # Requirements
    requirement_type = Column(String(50))  # streak, total_reviews, accuracy, etc.
    requirement_value = Column(Integer)    # Target value
    
    # Metadata
    category = Column(String(50), default="general")
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    points = Column(Integer, default=0)    # Points awarded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    
    # When earned
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Context when earned
    context_data = Column(Text)  # JSON with context info
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")
    
    __table_args__ = (
        Index('ix_user_achievement_unique', 'user_id', 'achievement_id', unique=True),
        Index('ix_user_achievement_earned', 'user_id', 'earned_at'),
    )
