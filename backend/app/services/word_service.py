from typing import List, Optional, Tuple
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
        """Get word pairs with optional search and user progress"""
        
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

    def get_random_word_pairs_simple(
            self,
            limit: int,
            user_id: Optional[str] = None
    ) -> List[WordPairWithUserProgress]:
        """Get random active word pairs with user progress, no filters"""

        query = self.db.query(WordPair).filter(WordPair.is_active == True)
        query = query.order_by(func.random())
        word_pairs = query.limit(limit).all()

        if not user_id:
            return [WordPairWithUserProgress.from_orm(wp) for wp in word_pairs]

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

        return enriched_pairs

    def get_word_pair(self, word_pair_id: int) -> WordPair:
        """Get single word pair by ID"""
        
        word_pair = self.db.query(WordPair).filter(
            WordPair.id == word_pair_id,
            WordPair.is_active == True
        ).first()
        
        if not word_pair:
            raise NotFoundException(f"Word pair {word_pair_id} not found")
        
        return word_pair
    
    def create_word_pair(self, word_data: WordPairCreate) -> WordPair:
        """Create a new word pair"""
        
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
        """Create multiple word pairs in batch"""
        
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
        """Update existing word pair"""
        
        word_pair = self.get_word_pair(word_pair_id)
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(word_pair, field, value)
        
        self.db.commit()
        self.db.refresh(word_pair)
        
        return word_pair
    
    def delete_word_pair(self, word_pair_id: int) -> bool:
        """Soft delete word pair"""
        
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
        """Get random word pairs for exercises"""
        
        query = self.db.query(WordPair).filter(WordPair.is_active == True)
        
        if cefr_level:
            query = query.filter(WordPair.cefr_level == cefr_level)
        
        if exclude_ids:
            query = query.filter(~WordPair.id.in_(exclude_ids))
        
        # PostgreSQL random order
        query = query.order_by(func.random())
        
        return query.limit(limit).all()
