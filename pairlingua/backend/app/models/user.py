import uuid
from sqlalchemy import Boolean, Text, func, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), unique=True, index=True)
    
    # Localization
    locale = Column(String(10), default="ru")
    timezone = Column(String(50), default="UTC")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    cards = relationship("UserCard", back_populates="user", lazy="dynamic")
    reviews = relationship("Review", back_populates="user", lazy="dynamic")
    sessions = relationship("StudySession", back_populates="user", lazy="dynamic")
    achievements = relationship("UserAchievement", back_populates="user", lazy="dynamic")
    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    settings = Column(Text, default="{}")  # JSON settings
    
    # Study preferences
    daily_goal = Column(String(20), default="10")  # cards per day
    difficulty_preference = Column(String(10), default="adaptive")
    notification_enabled = Column(Boolean, default=True)
    
    # Relationships  
    user = relationship("User", back_populates="profile")




class TokenBlacklist(Base):
    __tablename__ = "tokens_blacklist"

    jti = Column(UUID(as_uuid=True), primary_key=True)  # JWT ID
    user_id = Column(UUID(as_uuid=True), nullable=True)
    token_type = Column(String(20), default="access")  # access or refresh
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    reason = Column(String(100), default="logout")  # logout, revoked, etc.
