# Создаем модели базы данных

# Models __init__.py
models_init = """from app.models.user import User
from app.models.word_pair import WordPair
from app.models.user_card import UserCard
from app.models.review import Review
from app.models.session import StudySession
from app.models.achievement import Achievement, UserAchievement

__all__ = [
    "User",
    "WordPair", 
    "UserCard",
    "Review",
    "StudySession",
    "Achievement",
    "UserAchievement"
]
"""

# User model
user_model = """import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

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
    
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    settings = Column(Text, default="{}")  # JSON settings
    
    # Study preferences
    daily_goal = Column(String(20), default="10")  # cards per day
    difficulty_preference = Column(String(10), default="adaptive")
    notification_enabled = Column(Boolean, default=True)
    
    # Relationships  
    user = relationship("User", back_populates="profile")
"""

# WordPair model
word_pair_model = """import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY
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
"""

# UserCard model - ключевая для SM-2 алгоритма
user_card_model = """from datetime import datetime, timedelta
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
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
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
        \"\"\"Check if card is due for review\"\"\"
        if self.due_date is None:
            return True
        return func.now() >= self.due_date
    
    @property
    def days_overdue(self) -> int:
        \"\"\"Days card is overdue (negative if not due)\"\"\"
        if self.due_date is None:
            return 0
        delta = func.now() - self.due_date
        return delta.days
    
    def schedule_next_review(self, quality: int) -> None:
        \"\"\"Schedule next review using SM-2 algorithm\"\"\"
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
        self.due_date = func.now() + timedelta(days=result.interval_days)
        self.last_quality = quality
        self.last_reviewed_at = func.now()
        self.updated_at = func.now()
"""

# Review model
review_model = """from datetime import datetime
from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey
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
    def is_correct(self) -> bool:
        \"\"\"Quality >= 3 is considered correct in SM-2\"\"\"
        return self.quality >= 3
"""

# Session model
session_model = """import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Current state
    active_pair_ids = Column(ARRAY(Integer), default=list)  # Currently active word_pair_ids
    
    # Session metadata
    session_data = Column(JSONB, default=dict)  # Additional session info
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)  # Session expiry
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    @property
    def is_expired(self) -> bool:
        \"\"\"Check if session has expired\"\"\"
        if self.expires_at is None:
            return False
        return func.now() > self.expires_at
"""

# Achievement models
achievement_model = """from datetime import datetime
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
    
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    
    # When earned
    earned_at = Column(DateTime, default=func.now())
    
    # Context when earned
    context_data = Column(Text)  # JSON with context info
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")
    
    __table_args__ = (
        Index('ix_user_achievement_unique', 'user_id', 'achievement_id', unique=True),
        Index('ix_user_achievement_earned', 'user_id', 'earned_at'),
    )
"""

# Blacklisted tokens model
token_blacklist_model = """import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TokenBlacklist(Base):
    __tablename__ = "tokens_blacklist"

    jti = Column(UUID(as_uuid=True), primary_key=True)  # JWT ID
    user_id = Column(UUID(as_uuid=True), nullable=True)
    token_type = Column(String(20), default="access")  # access or refresh
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    reason = Column(String(100), default="logout")  # logout, revoked, etc.
"""

# Записываем модели
with open("pairlingua/backend/app/models/__init__.py", "w") as f:
    f.write(models_init)

with open("pairlingua/backend/app/models/user.py", "w") as f:
    f.write(user_model)

with open("pairlingua/backend/app/models/word_pair.py", "w") as f:
    f.write(word_pair_model)

with open("pairlingua/backend/app/models/user_card.py", "w") as f:
    f.write(user_card_model)

with open("pairlingua/backend/app/models/review.py", "w") as f:
    f.write(review_model)

with open("pairlingua/backend/app/models/session.py", "w") as f:
    f.write(session_model)

with open("pairlingua/backend/app/models/achievement.py", "w") as f:
    f.write(achievement_model)

# Добавляем токен blacklist в user.py
with open("pairlingua/backend/app/models/user.py", "a") as f:
    f.write("\n\n" + token_blacklist_model)

print("✅ Database модели созданы")
print("📊 User, WordPair, UserCard (SM-2), Review, Session")  
print("🏆 Achievement система")
print("🔒 TokenBlacklist для безопасности")