from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.user import User
from app.models.user_card import UserCard
from app.models.review import Review
from app.schemas.user import (
    UserUpdate, UserStats, UserStatsDetailed,
)
from app.core.exceptions import NotFoundException, ValidationException
from app.core.security import create_password_hash, verify_password
from app.schemas.word import WordPair


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: str) -> User:
        """Get user profile with all related data"""
        
        user = self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            raise NotFoundException("User not found")
        
        return user
    
    def update_user_profile(self, user_id: str, update_data: UserUpdate) -> User:
        """Update user profile"""
        
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
    
    async def get_user_stats(self, user_id: str) -> UserStats:
        """Get user's learning statistics"""
        
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
    
    async def get_user_detailed_stats(
        self, 
        user_id: str, 
        date_range: str = "30days"
    ) -> UserStatsDetailed:
        """Get detailed user statistics for a specific period"""
        
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
        """Change user password"""
        
        user = self.get_user_profile(user_id)
        
        if not verify_password(current_password, user.password_hash):
            raise ValidationException("Current password is incorrect")
        
        user.password_hash = create_password_hash(new_password)
        user.updated_at = func.now()
        
        self.db.commit()
        return True
    
    def delete_user_account(self, user_id: str) -> bool:
        """Soft delete user account"""
        
        user = self.get_user_profile(user_id)
        user.deleted_at = func.now()
        user.is_active = False
        
        self.db.commit()
        return True
    
    # Helper methods
    
    async def _calculate_current_streak(self, user_id: str) -> int:
        """Calculate current daily study streak"""
        
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
        """Get last 7 days of study statistics"""
        
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
