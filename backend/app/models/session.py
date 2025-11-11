import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ARRAY, ForeignKey, func
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
        """Check if session has expired"""
        if self.expires_at is None:
            return False
        return func.now() > self.expires_at
