from datetime import datetime, timedelta
from typing import NamedTuple
import math


class SM2Result(NamedTuple):
    ease_factor: float
    interval_days: int
    repetition_count: int


class SM2Service:
    """
    SuperMemo-2 (SM-2) spaced repetition algorithm implementation.
    
    Quality scale:
    0 - complete blackout
    1 - incorrect response; the correct one remembered
    2 - incorrect response; where the correct one seemed easy to recall
    3 - correct response recalled with serious difficulty
    4 - correct response after a hesitation
    5 - perfect response
    """
    
    MIN_EASE_FACTOR = 1.3
    INITIAL_EASE_FACTOR = 2.5
    
    def calculate_next_interval(
        self,
        quality: int,
        ease_factor: float = INITIAL_EASE_FACTOR,
        interval_days: int = 0,
        repetition_count: int = 0
    ) -> SM2Result:
        """
        Calculate next review interval based on SM-2 algorithm.
        
        Args:
            quality: Response quality (0-5)
            ease_factor: Current ease factor
            interval_days: Current interval in days  
            repetition_count: Number of consecutive correct reviews
            
        Returns:
            SM2Result with new ease_factor, interval_days, repetition_count
        """
        
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
        """Update ease factor based on response quality"""
        
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
        """
        Estimate probability that user still remembers the card.
        This is a heuristic, not part of original SM-2.
        """
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
        """
        Adjust interval for overdue cards.
        If card is significantly overdue, reduce next interval.
        """
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
        """
        Estimate quality score from response time and correctness.
        This is a helper function, not part of SM-2.
        """
        if not is_correct:
            return 1 if response_time_ms < average_time_ms * 2 else 0
        
        # For correct responses, map response time to quality 3-5
        if response_time_ms <= average_time_ms * 0.5:
            return 5  # Very fast = perfect response
        elif response_time_ms <= average_time_ms:
            return 4  # Fast = good response
        else:
            return 3  # Slow = correct but difficult
