# Создаем оставшиеся сервисы

# Study Service - основной сервис для обучения
study_service = """from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid
import random

from app.models.user import User
from app.models.word_pair import WordPair
from app.models.user_card import UserCard
from app.models.review import Review
from app.models.session import StudySession
from app.models.achievement import Achievement, UserAchievement
from app.services.sm2_service import SM2Service
from app.services.word_service import WordService
from app.schemas.study import (
    StudyCardsRequest, StudyCardsResponse, StudyCard,
    ReviewBatch, ReviewBatchResponse, ReviewResult,
    SessionReplaceRequest, SessionReplaceResponse
)
from app.core.redis import redis_service
from app.core.exceptions import NotFoundException, ValidationException


class StudyService:
    def __init__(self, db: Session):
        self.db = db
        self.sm2_service = SM2Service()
        self.word_service = WordService(db)
    
    async def get_due_cards(
        self, 
        user_id: str, 
        request: StudyCardsRequest
    ) -> StudyCardsResponse:
        \"\"\"Get cards due for review using spaced repetition\"\"\"
        
        # Check cache first
        cache_key = f"due_cards:{user_id}:{request.limit}"
        cached_data = await redis_service.get(cache_key)
        
        if cached_data:
            # Return cached data if available
            import json
            data = json.loads(cached_data)
            return StudyCardsResponse(**data)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        
        # Get existing session or create new one
        session = await self._get_or_create_session(user_id)
        
        due_cards = []
        
        # 1. Get overdue cards (highest priority)
        overdue_query = self.db.query(UserCard).join(WordPair).filter(
            UserCard.user_id == user_id,
            UserCard.due_date < func.now(),
            UserCard.is_suspended == False,
            WordPair.is_active == True,
            ~UserCard.word_pair_id.in_(session.active_pair_ids or [])
        ).order_by(UserCard.due_date)
        
        if request.cefr_levels:
            overdue_query = overdue_query.filter(WordPair.cefr_level.in_(request.cefr_levels))
        
        overdue_cards = overdue_query.limit(request.limit // 2).all()
        due_cards.extend(overdue_cards)
        
        # 2. Get new cards if requested
        remaining_slots = request.limit - len(due_cards)
        if request.include_new and remaining_slots > 0:
            new_cards_query = self.db.query(WordPair).filter(
                WordPair.is_active == True,
                ~WordPair.id.in_(
                    self.db.query(UserCard.word_pair_id).filter(
                        UserCard.user_id == user_id
                    )
                ),
                ~WordPair.id.in_(session.active_pair_ids or [])
            ).order_by(
                WordPair.frequency_rank.nulls_last(),
                func.random()
            )
            
            if request.cefr_levels:
                new_cards_query = new_cards_query.filter(
                    WordPair.cefr_level.in_(request.cefr_levels)
                )
            
            new_word_pairs = new_cards_query.limit(remaining_slots).all()
            
            # Create UserCard entries for new words
            for word_pair in new_word_pairs:
                user_card = UserCard(
                    user_id=user_id,
                    word_pair_id=word_pair.id,
                    due_date=func.now()  # Available immediately
                )
                self.db.add(user_card)
                due_cards.append(user_card)
        
        self.db.commit()
        
        # Convert to StudyCard format
        study_cards = []
        for user_card in due_cards:
            word_pair = user_card.word_pair if hasattr(user_card, 'word_pair') else \\
                       self.db.query(WordPair).filter(WordPair.id == user_card.word_pair_id).first()
            
            # Determine exercise type
            exercise_type = self._determine_exercise_type(user_card, request.exercise_types)
            
            study_card = StudyCard(
                id=word_pair.id,
                spanish_word=word_pair.spanish_word,
                russian_word=word_pair.russian_word if exercise_type != "typing" else None,
                audio_url=word_pair.audio_url,
                cefr_level=word_pair.cefr_level,
                type=exercise_type,
                distractors=self._generate_distractors(word_pair) if exercise_type == "multiple_choice" else [],
                ease_factor=float(user_card.ease_factor),
                due_date=user_card.due_date,
                is_new=user_card.total_reviews == 0,
                review_count=user_card.total_reviews
            )
            study_cards.append(study_card)
        
        # Update session with active pairs
        active_ids = [card.id for card in study_cards]
        session.active_pair_ids = active_ids
        session.updated_at = func.now()
        self.db.commit()
        
        # Count total due cards
        total_due = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.due_date <= func.now(),
            UserCard.is_suspended == False
        ).count()
        
        response = StudyCardsResponse(
            cards=study_cards,
            total_due=total_due,
            session_id=session.id,
            estimated_time_minutes=len(study_cards) * 2  # 2 minutes per card estimate
        )
        
        # Cache response for 60 seconds
        await redis_service.set(
            cache_key, 
            response.json(), 
            ex=60
        )
        
        return response
    
    async def submit_review_batch(
        self,
        user_id: str,
        review_batch: ReviewBatch
    ) -> ReviewBatchResponse:
        \"\"\"Process a batch of reviews and update SM-2 intervals\"\"\"
        
        results = []
        total_points = 0
        correct_count = 0
        
        for review_item in review_batch.items:
            # Get user card
            user_card = self.db.query(UserCard).filter(
                UserCard.user_id == user_id,
                UserCard.word_pair_id == review_item.word_pair_id
            ).first()
            
            if not user_card:
                # Create new user card if it doesn't exist
                user_card = UserCard(
                    user_id=user_id,
                    word_pair_id=review_item.word_pair_id
                )
                self.db.add(user_card)
                self.db.flush()  # Get ID
            
            # Store previous state for review record
            prev_ease_factor = float(user_card.ease_factor)
            prev_interval = user_card.interval_days
            
            # Update SM-2 parameters
            user_card.schedule_next_review(review_item.quality)
            
            # Update statistics
            user_card.total_reviews += 1
            if review_item.quality >= 3:
                user_card.correct_reviews += 1
                correct_count += 1
            
            user_card.accuracy = (user_card.correct_reviews / user_card.total_reviews) * 100
            
            if review_item.response_time_ms:
                # Update average response time (exponential moving average)
                if user_card.average_response_time:
                    user_card.average_response_time = int(
                        0.8 * user_card.average_response_time + 0.2 * review_item.response_time_ms
                    )
                else:
                    user_card.average_response_time = review_item.response_time_ms
            
            # Create review record
            review_record = Review(
                user_id=user_id,
                word_pair_id=review_item.word_pair_id,
                user_card_id=user_card.id,
                quality=review_item.quality,
                response_time_ms=review_item.response_time_ms,
                source=review_item.source,
                session_id=review_batch.session_id,
                ease_factor_before=int(prev_ease_factor * 100),
                ease_factor_after=int(user_card.ease_factor * 100),
                interval_before=prev_interval,
                interval_after=user_card.interval_days
            )
            self.db.add(review_record)
            
            # Calculate points earned
            points = self._calculate_points(review_item.quality, user_card.ease_factor)
            total_points += points
            
            results.append(ReviewResult(
                word_pair_id=review_item.word_pair_id,
                correct=review_item.quality >= 3,
                new_ease_factor=float(user_card.ease_factor),
                new_interval_days=user_card.interval_days,
                next_review_date=user_card.due_date,
                points_earned=points
            ))
        
        # Update user streak
        streak_updated = await self._update_user_streak(user_id, correct_count > 0)
        
        # Check for achievements
        achievements = await self._check_achievements(user_id, review_batch.items)
        
        self.db.commit()
        
        # Clear cache
        await redis_service.delete(f"due_cards:{user_id}*")
        
        accuracy = (correct_count / len(review_batch.items)) * 100 if review_batch.items else 0
        
        return ReviewBatchResponse(
            results=results,
            total_points_earned=total_points,
            accuracy=accuracy,
            streak_updated=streak_updated,
            achievements_unlocked=[a.code for a in achievements]
        )
    
    async def replace_session_card(
        self,
        user_id: str,
        request: SessionReplaceRequest
    ) -> SessionReplaceResponse:
        \"\"\"Replace a completed card in the current session\"\"\"
        
        session = self.db.query(StudySession).filter(
            StudySession.id == request.session_id,
            StudySession.user_id == user_id
        ).first()
        
        if not session:
            raise NotFoundException("Study session not found")
        
        # Remove completed card from active pairs
        if request.completed_word_pair_id in (session.active_pair_ids or []):
            session.active_pair_ids.remove(request.completed_word_pair_id)
        
        # Get a new card
        new_cards = await self.get_due_cards(
            user_id, 
            StudyCardsRequest(limit=1, include_new=True)
        )
        
        if not new_cards.cards:
            raise NotFoundException("No more cards available")
        
        new_card = new_cards.cards[0]
        
        # Add to session
        if session.active_pair_ids is None:
            session.active_pair_ids = []
        session.active_pair_ids.append(new_card.id)
        session.updated_at = func.now()
        
        self.db.commit()
        
        return SessionReplaceResponse(
            new_card=new_card,
            session_id=session.id
        )
    
    # Helper methods
    
    async def _get_or_create_session(self, user_id: str) -> StudySession:
        \"\"\"Get existing session or create new one\"\"\"
        
        # Look for active session (not expired)
        session = self.db.query(StudySession).filter(
            StudySession.user_id == user_id,
            or_(
                StudySession.expires_at.is_(None),
                StudySession.expires_at > func.now()
            )
        ).order_by(StudySession.created_at.desc()).first()
        
        if not session:
            session = StudySession(
                user_id=user_id,
                expires_at=func.now() + timedelta(hours=2)  # 2 hour session
            )
            self.db.add(session)
            self.db.flush()
        
        return session
    
    def _determine_exercise_type(
        self, 
        user_card: UserCard, 
        preferred_types: Optional[List[str]] = None
    ) -> str:
        \"\"\"Determine best exercise type based on card progress\"\"\"
        
        if preferred_types:
            return random.choice(preferred_types)
        
        # Adaptive exercise selection based on review count and accuracy
        if user_card.total_reviews == 0:
            return "matching"  # Start with matching for new cards
        elif user_card.total_reviews < 3:
            return random.choice(["matching", "multiple_choice"])
        elif user_card.accuracy > 80:
            return random.choice(["typing", "multiple_choice"])  # Harder exercises
        else:
            return "matching"  # Easier exercise for struggling cards
    
    def _generate_distractors(self, word_pair: WordPair) -> List[str]:
        \"\"\"Generate distractor options for multiple choice\"\"\"
        
        # Get similar words (same CEFR level or similar frequency)
        similar_words = self.db.query(WordPair).filter(
            WordPair.id != word_pair.id,
            WordPair.is_active == True,
            or_(
                WordPair.cefr_level == word_pair.cefr_level,
                WordPair.frequency_rank.between(
                    (word_pair.frequency_rank or 1000) - 100,
                    (word_pair.frequency_rank or 1000) + 100
                )
            )
        ).order_by(func.random()).limit(3).all()
        
        distractors = [w.russian_word for w in similar_words]
        
        # If not enough similar words, get random ones
        if len(distractors) < 3:
            random_words = self.db.query(WordPair).filter(
                WordPair.id != word_pair.id,
                WordPair.is_active == True
            ).order_by(func.random()).limit(3 - len(distractors)).all()
            
            distractors.extend([w.russian_word for w in random_words])
        
        return distractors[:3]
    
    def _calculate_points(self, quality: int, ease_factor: float) -> int:
        \"\"\"Calculate points earned for a review\"\"\"
        
        base_points = [0, 1, 2, 5, 10, 15][quality]  # Points by quality
        
        # Bonus for difficult cards (low ease factor)
        difficulty_bonus = max(0, (3.0 - ease_factor) * 5)
        
        return int(base_points + difficulty_bonus)
    
    async def _update_user_streak(self, user_id: str, had_correct: bool) -> bool:
        \"\"\"Update user's daily streak\"\"\"
        
        cache_key = f"streak:{user_id}"
        today = func.now().date()
        
        # Implementation would track daily streaks
        # For now, simplified version
        if had_correct:
            await redis_service.set(f"study_date:{user_id}", str(today), ex=86400 * 7)
            return True
        
        return False
    
    async def _check_achievements(
        self, 
        user_id: str, 
        reviews: List
    ) -> List[Achievement]:
        \"\"\"Check and award achievements\"\"\"
        
        achievements_unlocked = []
        
        # Example: Check for "Perfect Day" achievement (all reviews correct)
        all_correct = all(r.quality >= 3 for r in reviews)
        if all_correct and len(reviews) >= 5:
            achievement = self.db.query(Achievement).filter(
                Achievement.code == "perfect_day"
            ).first()
            
            if achievement:
                # Check if user already has this achievement
                existing = self.db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == achievement.id
                ).first()
                
                if not existing:
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        context_data=f"Earned with {len(reviews)} perfect reviews"
                    )
                    self.db.add(user_achievement)
                    achievements_unlocked.append(achievement)
        
        return achievements_unlocked
"""

# User Service
user_service = """from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models.user import User, Profile
from app.models.user_card import UserCard
from app.models.review import Review
from app.models.achievement import UserAchievement
from app.schemas.user import (
    UserUpdate, UserStats, UserStatsDetailed, 
    UserProfile as UserProfileSchema
)
from app.core.exceptions import NotFoundException, ValidationException
from app.core.security import create_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: str) -> User:
        \"\"\"Get user profile with all related data\"\"\"
        
        user = self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            raise NotFoundException("User not found")
        
        return user
    
    def update_user_profile(self, user_id: str, update_data: UserUpdate) -> User:
        \"\"\"Update user profile\"\"\"
        
        user = self.get_user_profile(user_id)
        
        # Handle email change (requires verification in production)
        update_dict = update_data.dict(exclude_unset=True)
        
        # Check nickname uniqueness if being updated
        if 'nickname' in update_dict and update_dict['nickname']:
            existing_nickname = self.db.query(User).filter(
                User.nickname == update_dict['nickname'],
                User.id != user_id
            ).first()
            
            if existing_nickname:
                raise ValidationException("Nickname already taken")
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        user.updated_at = func.now()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_stats(self, user_id: str) -> UserStats:
        \"\"\"Get user's learning statistics\"\"\"
        
        user = self.get_user_profile(user_id)
        
        # Total cards created for user
        total_cards = self.db.query(UserCard).filter(
            UserCard.user_id == user_id
        ).count()
        
        # Cards due for review
        cards_due = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.due_date <= func.now(),
            UserCard.is_suspended == False
        ).count()
        
        # Cards considered "learned" (reviewed 3+ times with good accuracy)
        cards_learned = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.total_reviews >= 3,
            UserCard.accuracy >= 70.0
        ).count()
        
        # Overall accuracy
        accuracy_result = self.db.query(
            func.avg(UserCard.accuracy)
        ).filter(UserCard.user_id == user_id).scalar()
        
        accuracy = float(accuracy_result or 0.0)
        
        # Current streak (simplified - days with study activity)
        current_streak = await self._calculate_current_streak(user_id)
        
        # Total study time from reviews
        total_time_result = self.db.query(
            func.sum(Review.response_time_ms)
        ).filter(Review.user_id == user_id).scalar()
        
        total_study_time_minutes = int((total_time_result or 0) / 60000)  # ms to minutes
        
        # Last study date
        last_study = self.db.query(Review).filter(
            Review.user_id == user_id
        ).order_by(desc(Review.reviewed_at)).first()
        
        # Level progress (cards by CEFR level)
        level_progress = {}
        level_stats = self.db.query(
            WordPair.cefr_level,
            func.count(UserCard.id)
        ).join(UserCard).filter(
            UserCard.user_id == user_id
        ).group_by(WordPair.cefr_level).all()
        
        for level, count in level_stats:
            level_progress[level or "Unknown"] = count
        
        # Weekly stats (last 7 days)
        weekly_stats = await self._get_weekly_stats(user_id)
        
        return UserStats(
            total_cards=total_cards,
            cards_due=cards_due,
            cards_learned=cards_learned,
            accuracy=accuracy,
            current_streak=current_streak,
            longest_streak=current_streak,  # Simplified
            total_study_time_minutes=total_study_time_minutes,
            last_study_date=last_study.reviewed_at if last_study else None,
            level_progress=level_progress,
            weekly_stats=weekly_stats
        )
    
    def get_user_detailed_stats(
        self, 
        user_id: str, 
        date_range: str = "30days"
    ) -> UserStatsDetailed:
        \"\"\"Get detailed user statistics for a specific period\"\"\"
        
        # Calculate date range
        end_date = func.now()
        if date_range == "7days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "30days":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime(2020, 1, 1)  # All time
        
        # Reviews in date range
        reviews = self.db.query(Review).filter(
            Review.user_id == user_id,
            Review.reviewed_at >= start_date,
            Review.reviewed_at <= end_date
        ).all()
        
        total_reviews = len(reviews)
        correct_reviews = sum(1 for r in reviews if r.quality >= 3)
        accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        # Daily breakdown
        daily_stats = []
        for i in range((end_date.date() - start_date.date()).days + 1):
            date = start_date.date() + timedelta(days=i)
            date_reviews = [r for r in reviews if r.reviewed_at.date() == date]
            
            daily_stats.append({
                "date": date.isoformat(),
                "reviews": len(date_reviews),
                "correct": sum(1 for r in date_reviews if r.quality >= 3),
                "accuracy": (sum(1 for r in date_reviews if r.quality >= 3) / len(date_reviews) * 100) if date_reviews else 0,
                "time_minutes": sum(r.response_time_ms or 0 for r in date_reviews) / 60000
            })
        
        # Cards by level
        cards_by_level = {}
        level_query = self.db.query(
            WordPair.cefr_level,
            func.count(UserCard.id)
        ).select_from(UserCard).join(WordPair).filter(
            UserCard.user_id == user_id
        ).group_by(WordPair.cefr_level).all()
        
        for level, count in level_query:
            cards_by_level[level or "Unknown"] = count
        
        # Cards by status
        learning_cards = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.is_learning == True
        ).count()
        
        graduated_cards = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.is_learning == False
        ).count()
        
        suspended_cards = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.is_suspended == True
        ).count()
        
        cards_by_status = {
            "learning": learning_cards,
            "graduated": graduated_cards,
            "suspended": suspended_cards
        }
        
        # Performance metrics
        avg_response_time = sum(r.response_time_ms or 0 for r in reviews) / len(reviews) if reviews else 0
        
        best_day = max(daily_stats, key=lambda x: x["accuracy"]) if daily_stats else {"date": "", "accuracy": 0}
        
        # Most studied words
        most_studied = self.db.query(
            WordPair.spanish_word,
            WordPair.russian_word,
            func.count(Review.id).label("review_count")
        ).select_from(Review).join(WordPair).filter(
            Review.user_id == user_id,
            Review.reviewed_at >= start_date
        ).group_by(
            WordPair.id, WordPair.spanish_word, WordPair.russian_word
        ).order_by(
            desc("review_count")
        ).limit(10).all()
        
        most_studied_words = [
            {
                "spanish": word.spanish_word,
                "russian": word.russian_word, 
                "reviews": word.review_count
            }
            for word in most_studied
        ]
        
        return UserStatsDetailed(
            user_id=user_id,
            date_range=date_range,
            total_reviews=total_reviews,
            correct_reviews=correct_reviews,
            accuracy=accuracy,
            daily_stats=daily_stats,
            streak_data={"current": await self._calculate_current_streak(user_id)},
            cards_by_level=cards_by_level,
            cards_by_status=cards_by_status,
            average_response_time=avg_response_time,
            best_accuracy_day=best_day,
            most_studied_words=most_studied_words
        )
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        \"\"\"Change user password\"\"\"
        
        user = self.get_user_profile(user_id)
        
        if not verify_password(current_password, user.password_hash):
            raise ValidationException("Current password is incorrect")
        
        user.password_hash = create_password_hash(new_password)
        user.updated_at = func.now()
        
        self.db.commit()
        return True
    
    def delete_user_account(self, user_id: str) -> bool:
        \"\"\"Soft delete user account\"\"\"
        
        user = self.get_user_profile(user_id)
        user.deleted_at = func.now()
        user.is_active = False
        
        self.db.commit()
        return True
    
    # Helper methods
    
    async def _calculate_current_streak(self, user_id: str) -> int:
        \"\"\"Calculate current daily study streak\"\"\"
        
        # Get dates with reviews, ordered descending
        review_dates = self.db.query(
            func.date(Review.reviewed_at)
        ).filter(
            Review.user_id == user_id
        ).distinct().order_by(
            desc(func.date(Review.reviewed_at))
        ).limit(365).all()  # Check last year
        
        if not review_dates:
            return 0
        
        streak = 0
        current_date = func.now().date()
        
        for (review_date,) in review_dates:
            if review_date == current_date or review_date == current_date - timedelta(days=1):
                streak += 1
                current_date = review_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    async def _get_weekly_stats(self, user_id: str) -> List[Dict[str, Any]]:
        \"\"\"Get last 7 days of study statistics\"\"\"
        
        weekly_stats = []
        today = func.now().date()
        
        for i in range(7):
            date = today - timedelta(days=i)
            
            day_reviews = self.db.query(Review).filter(
                Review.user_id == user_id,
                func.date(Review.reviewed_at) == date
            ).all()
            
            correct_count = sum(1 for r in day_reviews if r.quality >= 3)
            
            weekly_stats.append({
                "date": date.isoformat(),
                "reviews": len(day_reviews),
                "correct": correct_count,
                "accuracy": (correct_count / len(day_reviews) * 100) if day_reviews else 0
            })
        
        return list(reversed(weekly_stats))  # Chronological order
"""

# Записываем оставшиеся сервисы
with open("pairlingua/backend/app/services/study_service.py", "w") as f:
    f.write(study_service)

with open("pairlingua/backend/app/services/user_service.py", "w") as f:
    f.write(user_service)

print("✅ StudyService и UserService созданы")
print("🎯 StudyService: due cards, SM-2 reviews, сессии")  
print("👤 UserService: профиль, статистика, стрики")
print("🏆 Интеграция с достижениями и геймификацией")