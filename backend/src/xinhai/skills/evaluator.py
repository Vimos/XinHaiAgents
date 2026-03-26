"""
Evaluators for session quality assessment
"""

from abc import ABC, abstractmethod
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Session, Message


class Evaluator(ABC):
    """Base evaluator"""
    
    @abstractmethod
    def evaluate(self, session: "Session") -> float:
        """
        Evaluate session and return score
        
        Args:
            session: The session to evaluate
            
        Returns:
            Score between 0 and 1
        """
        pass


class CoherenceEvaluator(Evaluator):
    """Evaluate conversation coherence"""
    
    def evaluate(self, session: "Session") -> float:
        if len(session.messages) < 2:
            return 1.0
        
        # Simple heuristic: check for topic consistency
        # In practice, this would use embeddings or LLM-based evaluation
        scores = []
        for i in range(1, len(session.messages)):
            prev_msg = session.messages[i - 1]
            curr_msg = session.messages[i]
            
            # Check if current message references previous
            coherence = self._calculate_coherence(prev_msg, curr_msg)
            scores.append(coherence)
        
        return sum(scores) / len(scores) if scores else 1.0
    
    def _calculate_coherence(self, msg_a: "Message", msg_b: "Message") -> float:
        """Calculate coherence between two messages"""
        # Placeholder - would use semantic similarity in practice
        content_a = msg_a.content.lower()
        content_b = msg_b.content.lower()
        
        # Simple word overlap
        words_a = set(content_a.split())
        words_b = set(content_b.split())
        
        if not words_a:
            return 0.0
        
        overlap = len(words_a & words_b)
        return min(overlap / 3, 1.0)  # Normalize


class DiversityEvaluator(Evaluator):
    """Evaluate conversation diversity"""
    
    def evaluate(self, session: "Session") -> float:
        if len(session.messages) < 2:
            return 0.5
        
        # Calculate lexical diversity
        all_words = []
        for msg in session.messages:
            all_words.extend(msg.content.lower().split())
        
        if not all_words:
            return 0.0
        
        unique_words = set(all_words)
        diversity = len(unique_words) / len(all_words)
        
        return min(diversity * 2, 1.0)  # Scale to 0-1


class GoalAchievementEvaluator(Evaluator):
    """Evaluate goal achievement (for task-oriented sessions)"""
    
    def __init__(self, goals: List[str] = None):
        self.goals = goals or []
    
    def evaluate(self, session: "Session") -> float:
        if not self.goals:
            return 0.5
        
        # Check how many goals are mentioned/achieved
        achieved = 0
        all_text = " ".join(m.content.lower() for m in session.messages)
        
        for goal in self.goals:
            if goal.lower() in all_text:
                achieved += 1
        
        return achieved / len(self.goals)
    
    def set_goals(self, goals: List[str]):
        """Set goals for evaluation"""
        self.goals = goals
