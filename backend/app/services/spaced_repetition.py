"""
Spaced repetition algorithm implementation.
Based on the SM-2 algorithm with modifications.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import math


class SpacedRepetitionScheduler:
    """
    Implements adaptive spaced repetition scheduling.
    Uses modified SM-2 algorithm.
    """
    
    # Intervals in days for different quality ratings
    INITIAL_INTERVAL = 1  # First review after 1 day
    SECOND_INTERVAL = 3   # Second review after 3 days
    
    # Easiness factor bounds
    MIN_EASINESS = 1.3
    MAX_EASINESS = 2.5
    
    @staticmethod
    def calculate_next_review(
        quality: int,  # 0-5, where 5 is perfect recall
        review_count: int,
        easiness_factor: float = 2.5,
        interval: int = 0
    ) -> Tuple[datetime, float, int]:
        """
        Calculate next review date and update parameters.
        
        Args:
            quality: Quality of recall (0-5)
            review_count: Number of times reviewed
            easiness_factor: Current easiness factor
            interval: Current interval in days
            
        Returns:
            Tuple of (next_review_date, new_easiness_factor, new_interval)
        """
        # Update easiness factor based on quality
        new_easiness = max(
            SpacedRepetitionScheduler.MIN_EASINESS,
            min(
                SpacedRepetitionScheduler.MAX_EASINESS,
                easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            )
        )
        
        # Calculate new interval
        if quality < 3:  # Forgotten
            new_interval = 1
            new_easiness = SpacedRepetitionScheduler.MIN_EASINESS
        elif review_count == 0:
            new_interval = SpacedRepetitionScheduler.INITIAL_INTERVAL
        elif review_count == 1:
            new_interval = SpacedRepetitionScheduler.SECOND_INTERVAL
        else:
            new_interval = max(1, int(interval * new_easiness))
        
        # Add some randomization to avoid clustering
        randomized_interval = int(new_interval * (0.9 + 0.2 * (quality / 5)))
        
        next_review = datetime.utcnow() + timedelta(days=randomized_interval)
        
        return next_review, new_easiness, randomized_interval
    
    @staticmethod
    def get_difficulty_level(difficulty_score: float) -> str:
        """Get difficulty level from score"""
        if difficulty_score < 0.3:
            return "easy"
        elif difficulty_score < 0.7:
            return "medium"
        else:
            return "hard"
    
    @staticmethod
    def update_difficulty_score(
        current_score: float,
        is_correct: bool,
        response_time_seconds: int,
        average_response_time: float = 30.0
    ) -> float:
        """
        Update difficulty score based on answer correctness and response time.
        Higher score means harder question.
        """
        base_adjustment = 0.1 if is_correct else -0.15
        
        # Adjust based on response time (faster = harder)
        time_ratio = response_time_seconds / average_response_time
        time_adjustment = max(-0.1, min(0.1, (1 - time_ratio) * 0.05))
        
        new_score = max(0.0, min(1.0, current_score + base_adjustment + time_adjustment))
        return new_score
    
    @staticmethod
    def select_next_cards(
        user_cards: List,
        limit: int = 10,
        preferred_difficulty: Optional[str] = None
    ) -> List:
        """
        Select next cards to study using spaced repetition algorithm.
        
        Prioritizes:
        1. Cards due for review
        2. Cards matching preferred difficulty
        3. Cards with higher difficulty scores
        """
        now = datetime.utcnow()
        
        # Cards due for review (last_reviewed is None or past next_review)
        due_cards = []
        new_cards = []
        review_cards = []
        
        for card in user_cards:
            if card.last_reviewed is None:
                new_cards.append(card)
            elif card.last_reviewed < now:
                due_cards.append(card)
            else:
                review_cards.append(card)
        
        # Sort by difficulty if preferred
        if preferred_difficulty:
            def difficulty_priority(card):
                if card.difficulty == preferred_difficulty:
                    return 0
                elif card.difficulty == "medium":
                    return 1
                else:
                    return 2
            
            due_cards.sort(key=difficulty_priority)
            new_cards.sort(key=difficulty_priority)
        
        # Combine and limit
        selected = due_cards + new_cards
        return selected[:limit]
