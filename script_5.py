# Создаем сервисы

# Services __init__.py
services_init = """from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.word_service import WordService
from app.services.study_service import StudyService
from app.services.sm2_service import SM2Service

__all__ = [
    "AuthService",
    "UserService", 
    "WordService",
    "StudyService",
    "SM2Service"
]
"""

# SM-2 Algorithm Service - ключевой для spaced repetition
sm2_service = """from datetime import datetime, timedelta
from typing import NamedTuple
import math


class SM2Result(NamedTuple):
    ease_factor: float
    interval_days: int
    repetition_count: int


class SM2Service:
    \"\"\"
    SuperMemo-2 (SM-2) spaced repetition algorithm implementation.
    
    Quality scale:
    0 - complete blackout
    1 - incorrect response; the correct one remembered
    2 - incorrect response; where the correct one seemed easy to recall
    3 - correct response recalled with serious difficulty
    4 - correct response after a hesitation
    5 - perfect response
    \"\"\"
    
    MIN_EASE_FACTOR = 1.3
    INITIAL_EASE_FACTOR = 2.5
    
    def calculate_next_interval(
        self,
        quality: int,
        ease_factor: float = INITIAL_EASE_FACTOR,
        interval_days: int = 0,
        repetition_count: int = 0
    ) -> SM2Result:
        \"\"\"
        Calculate next review interval based on SM-2 algorithm.
        
        Args:
            quality: Response quality (0-5)
            ease_factor: Current ease factor
            interval_days: Current interval in days  
            repetition_count: Number of consecutive correct reviews
            
        Returns:
            SM2Result with new ease_factor, interval_days, repetition_count
        \"\"\"
        
        # Validate inputs
        quality = max(0, min(5, quality))
        ease_factor = max(self.MIN_EASE_FACTOR, ease_factor)
        
        # Update ease factor based on quality
        new_ease_factor = self._update_ease_factor(ease_factor, quality)
        
        # If quality < 3, reset repetition count and set short interval
        if quality < 3:
            new_repetition_count = 0
            new_interval_days = 1
        else:
            # Correct response (quality >= 3)
            new_repetition_count = repetition_count + 1
            
            if new_repetition_count == 1:
                new_interval_days = 1
            elif new_repetition_count == 2:
                new_interval_days = 6
            else:
                # For subsequent reviews, multiply previous interval by ease factor
                new_interval_days = max(1, round(interval_days * new_ease_factor))
        
        # Cap maximum interval at 365 days
        new_interval_days = min(new_interval_days, 365)
        
        return SM2Result(
            ease_factor=new_ease_factor,
            interval_days=new_interval_days,
            repetition_count=new_repetition_count
        )
    
    def _update_ease_factor(self, current_ef: float, quality: int) -> float:
        \"\"\"Update ease factor based on response quality\"\"\"
        
        # SM-2 formula: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Ensure ease factor doesn't go below minimum
        return max(self.MIN_EASE_FACTOR, new_ef)
    
    def calculate_retention_probability(
        self, 
        days_since_review: int, 
        ease_factor: float,
        interval_days: int
    ) -> float:
        \"\"\"
        Estimate probability that user still remembers the card.
        This is a heuristic, not part of original SM-2.
        \"\"\"
        if interval_days == 0:
            return 1.0
        
        # Simple exponential decay model
        decay_rate = 1 / (ease_factor * interval_days)
        retention = math.exp(-decay_rate * days_since_review)
        
        return max(0.0, min(1.0, retention))
    
    def adjust_for_overdue(
        self,
        base_interval: int,
        days_overdue: int,
        ease_factor: float
    ) -> int:
        \"\"\"
        Adjust interval for overdue cards.
        If card is significantly overdue, reduce next interval.
        \"\"\"
        if days_overdue <= 0:
            return base_interval
        
        # Reduce interval based on how overdue the card is
        overdue_factor = min(1.0, days_overdue / base_interval)
        adjustment = 1.0 - (overdue_factor * 0.2)  # Max 20% reduction
        
        adjusted_interval = max(1, round(base_interval * adjustment))
        return adjusted_interval
    
    def quality_from_response_time(
        self,
        response_time_ms: int,
        is_correct: bool,
        average_time_ms: int = 3000
    ) -> int:
        \"\"\"
        Estimate quality score from response time and correctness.
        This is a helper function, not part of SM-2.
        \"\"\"
        if not is_correct:
            return 1 if response_time_ms < average_time_ms * 2 else 0
        
        # For correct responses, map response time to quality 3-5
        if response_time_ms <= average_time_ms * 0.5:
            return 5  # Very fast = perfect response
        elif response_time_ms <= average_time_ms:
            return 4  # Fast = good response
        else:
            return 3  # Slow = correct but difficult
"""

# Auth Service
auth_service = """from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.core.security import (
    verify_password, create_password_hash, 
    create_access_token, create_refresh_token, decode_token
)
from app.core.exceptions import AuthenticationException, ConflictException
from app.models.user import User, TokenBlacklist
from app.schemas.auth import UserRegister, UserLogin, Token
from app.core.redis import redis_service


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> User:
        \"\"\"Register a new user\"\"\"
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ConflictException("User with this email already exists")
        
        # Check nickname uniqueness
        if user_data.nickname:
            existing_nickname = self.db.query(User).filter(
                User.nickname == user_data.nickname
            ).first()
            if existing_nickname:
                raise ConflictException("Nickname already taken")
        
        # Create new user
        user = User(
            email=user_data.email,
            password_hash=create_password_hash(user_data.password),
            nickname=user_data.nickname,
            locale=user_data.locale
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, credentials: UserLogin) -> Token:
        \"\"\"Authenticate user and return tokens\"\"\"
        
        user = self.db.query(User).filter(
            User.email == credentials.email,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60  # 15 minutes
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        \"\"\"Refresh access token using refresh token\"\"\"
        
        try:
            payload = decode_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            if not user_id or not jti:
                raise AuthenticationException("Invalid refresh token")
            
            # Check if token is blacklisted
            blacklisted = self.db.query(TokenBlacklist).filter(
                TokenBlacklist.jti == jti
            ).first()
            
            if blacklisted:
                raise AuthenticationException("Token has been revoked")
            
            # Verify user exists
            user = self.db.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if not user:
                raise AuthenticationException("User not found")
            
            # Blacklist old refresh token
            old_token = TokenBlacklist(
                jti=jti,
                user_id=user_id,
                token_type="refresh",
                expires_at=datetime.utcfromtimestamp(payload.get("exp")),
                reason="refresh"
            )
            self.db.add(old_token)
            
            # Create new tokens
            new_access_token = create_access_token(str(user.id))
            new_refresh_token = create_refresh_token(str(user.id))
            
            self.db.commit()
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=15 * 60
            )
            
        except Exception as e:
            if isinstance(e, AuthenticationException):
                raise e
            raise AuthenticationException("Could not refresh token")
    
    async def logout_user(self, access_token: str, refresh_token: Optional[str] = None):
        \"\"\"Logout user by blacklisting tokens\"\"\"
        
        try:
            # Blacklist access token
            access_payload = decode_token(access_token, "access")
            access_jti = access_payload.get("jti")
            user_id = access_payload.get("sub")
            
            if access_jti:
                blacklist_entry = TokenBlacklist(
                    jti=access_jti,
                    user_id=user_id,
                    token_type="access",
                    expires_at=datetime.utcfromtimestamp(access_payload.get("exp")),
                    reason="logout"
                )
                self.db.add(blacklist_entry)
            
            # Blacklist refresh token if provided
            if refresh_token:
                try:
                    refresh_payload = decode_token(refresh_token, "refresh")
                    refresh_jti = refresh_payload.get("jti")
                    
                    if refresh_jti:
                        blacklist_entry = TokenBlacklist(
                            jti=refresh_jti,
                            user_id=user_id,
                            token_type="refresh",
                            expires_at=datetime.utcfromtimestamp(refresh_payload.get("exp")),
                            reason="logout"
                        )
                        self.db.add(blacklist_entry)
                except:
                    pass  # Ignore errors with refresh token
            
            self.db.commit()
            
        except Exception:
            raise AuthenticationException("Could not logout user")
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        \"\"\"Check if token is blacklisted\"\"\"
        
        # First check Redis cache
        cache_key = f"blacklist:{jti}"
        cached = await redis_service.get(cache_key)
        
        if cached == "1":
            return True
        elif cached == "0":
            return False
        
        # Check database
        blacklisted = self.db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti,
            TokenBlacklist.expires_at > datetime.utcnow()
        ).first()
        
        # Cache result
        is_blacklisted = blacklisted is not None
        await redis_service.set(cache_key, "1" if is_blacklisted else "0", ex=3600)
        
        return is_blacklisted
    
    async def get_current_user(self, token: str) -> User:
        \"\"\"Get current user from access token\"\"\"
        
        payload = decode_token(token, "access")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        
        if not user_id or not jti:
            raise AuthenticationException("Invalid token")
        
        # Check if token is blacklisted
        if await self.is_token_blacklisted(jti):
            raise AuthenticationException("Token has been revoked")
        
        user = self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            raise AuthenticationException("User not found")
        
        return user
"""

# Word Service
word_service = """from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.word_pair import WordPair
from app.models.user_card import UserCard
from app.schemas.word import (
    WordPairCreate, WordPairUpdate, WordPairSearch, 
    WordPairBatchCreate, WordPairWithUserProgress
)
from app.core.exceptions import NotFoundException, ConflictException


class WordService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_word_pairs(
        self, 
        search: WordPairSearch,
        user_id: Optional[str] = None
    ) -> Tuple[List[WordPairWithUserProgress], Optional[str]]:
        \"\"\"Get word pairs with optional search and user progress\"\"\"
        
        query = self.db.query(WordPair).filter(WordPair.is_active == True)
        
        # Apply filters
        if search.query:
            search_term = f"%{search.query.lower()}%"
            query = query.filter(
                or_(
                    func.lower(WordPair.spanish_word).contains(search_term),
                    func.lower(WordPair.russian_word).contains(search_term)
                )
            )
        
        if search.cefr_level:
            query = query.filter(WordPair.cefr_level == search.cefr_level)
        
        if search.tags:
            # PostgreSQL array overlap operator
            query = query.filter(WordPair.tags.op('&&')(search.tags))
        
        # Cursor-based pagination
        if search.cursor:
            try:
                cursor_id = int(search.cursor)
                query = query.filter(WordPair.id > cursor_id)
            except ValueError:
                pass  # Ignore invalid cursor
        
        # Order by frequency rank (most common first) then by ID
        query = query.order_by(
            WordPair.frequency_rank.nulls_last(),
            WordPair.id
        )
        
        # Fetch one extra to determine if there are more results
        word_pairs = query.limit(search.limit + 1).all()
        
        # Check if there are more results
        next_cursor = None
        if len(word_pairs) > search.limit:
            word_pairs = word_pairs[:-1]
            next_cursor = str(word_pairs[-1].id) if word_pairs else None
        
        # Enrich with user progress if user_id provided
        if user_id:
            enriched_pairs = []
            for word_pair in word_pairs:
                user_card = self.db.query(UserCard).filter(
                    UserCard.user_id == user_id,
                    UserCard.word_pair_id == word_pair.id
                ).first()
                
                word_with_progress = WordPairWithUserProgress.from_orm(word_pair)
                if user_card:
                    word_with_progress.user_accuracy = float(user_card.accuracy)
                    word_with_progress.last_reviewed = user_card.last_reviewed_at
                    word_with_progress.ease_factor = float(user_card.ease_factor)
                    word_with_progress.due_date = user_card.due_date
                    word_with_progress.is_due = user_card.is_due
                    word_with_progress.review_count = user_card.total_reviews
                
                enriched_pairs.append(word_with_progress)
            
            return enriched_pairs, next_cursor
        
        return word_pairs, next_cursor
    
    def get_word_pair(self, word_pair_id: int) -> WordPair:
        \"\"\"Get single word pair by ID\"\"\"
        
        word_pair = self.db.query(WordPair).filter(
            WordPair.id == word_pair_id,
            WordPair.is_active == True
        ).first()
        
        if not word_pair:
            raise NotFoundException(f"Word pair {word_pair_id} not found")
        
        return word_pair
    
    def create_word_pair(self, word_data: WordPairCreate) -> WordPair:
        \"\"\"Create a new word pair\"\"\"
        
        # Check for duplicates
        existing = self.db.query(WordPair).filter(
            WordPair.spanish_word == word_data.spanish_word,
            WordPair.russian_word == word_data.russian_word
        ).first()
        
        if existing:
            raise ConflictException(
                f"Word pair '{word_data.spanish_word}' -> '{word_data.russian_word}' already exists"
            )
        
        word_pair = WordPair(**word_data.dict())
        self.db.add(word_pair)
        self.db.commit()
        self.db.refresh(word_pair)
        
        return word_pair
    
    def create_word_pairs_batch(self, batch_data: WordPairBatchCreate) -> List[WordPair]:
        \"\"\"Create multiple word pairs in batch\"\"\"
        
        created_pairs = []
        for word_data in batch_data.word_pairs:
            try:
                word_pair = WordPair(**word_data.dict())
                self.db.add(word_pair)
                created_pairs.append(word_pair)
            except Exception:
                # Skip duplicates or invalid pairs
                continue
        
        self.db.commit()
        
        # Refresh all created pairs
        for pair in created_pairs:
            self.db.refresh(pair)
        
        return created_pairs
    
    def update_word_pair(self, word_pair_id: int, update_data: WordPairUpdate) -> WordPair:
        \"\"\"Update existing word pair\"\"\"
        
        word_pair = self.get_word_pair(word_pair_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(word_pair, field, value)
        
        self.db.commit()
        self.db.refresh(word_pair)
        
        return word_pair
    
    def delete_word_pair(self, word_pair_id: int) -> bool:
        \"\"\"Soft delete word pair\"\"\"
        
        word_pair = self.get_word_pair(word_pair_id)
        word_pair.is_active = False
        
        self.db.commit()
        return True
    
    def get_random_word_pairs(
        self, 
        limit: int = 20,
        cefr_level: Optional[str] = None,
        exclude_ids: Optional[List[int]] = None
    ) -> List[WordPair]:
        \"\"\"Get random word pairs for exercises\"\"\"
        
        query = self.db.query(WordPair).filter(WordPair.is_active == True)
        
        if cefr_level:
            query = query.filter(WordPair.cefr_level == cefr_level)
        
        if exclude_ids:
            query = query.filter(~WordPair.id.in_(exclude_ids))
        
        # PostgreSQL random order
        query = query.order_by(func.random())
        
        return query.limit(limit).all()
"""

# Записываем сервисы
with open("pairlingua/backend/app/services/__init__.py", "w") as f:
    f.write(services_init)

with open("pairlingua/backend/app/services/sm2_service.py", "w") as f:
    f.write(sm2_service)

with open("pairlingua/backend/app/services/auth_service.py", "w") as f:
    f.write(auth_service)

with open("pairlingua/backend/app/services/word_service.py", "w") as f:
    f.write(word_service)

print("✅ Сервисы созданы")
print("🧠 SM-2 алгоритм для spaced repetition")  
print("🔐 AuthService с JWT и blacklist")
print("📚 WordService с поиском и batch операциями")