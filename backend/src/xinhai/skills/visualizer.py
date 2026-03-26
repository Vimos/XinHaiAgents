"""
Visualizers for session data
"""

from abc import ABC, abstractmethod
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Session, Agent, Message


class Visualizer(ABC):
    """Base visualizer"""
    
    @abstractmethod
    def visualize(self, session: "Session") -> Dict:
        """
        Generate visualization data
        
        Args:
            session: The session to visualize
            
        Returns:
            Visualization data dictionary
        """
        pass


class NetworkVisualizer(Visualizer):
    """Visualize agent communication network"""
    
    def visualize(self, session: "Session") -> Dict:
        nodes = []
        edges = []
        
        # Create nodes
        for agent in session.agents:
            nodes.append({
                "id": agent.name,
                "label": agent.name,
                "role": agent.role,
                "group": agent.role,
                "size": 30,
            })
        
        # Create edges based on interactions
        interactions = self._count_interactions(session.messages)
        for (source, target), weight in interactions.items():
            edges.append({
                "source": source,
                "target": target,
                "weight": weight,
            })
        
        return {
            "type": "network",
            "nodes": nodes,
            "edges": edges,
        }
    
    def _count_interactions(self, messages: List["Message"]) -> Dict:
        """Count interactions between agents"""
        interactions = {}
        last_speaker = None
        
        for msg in messages:
            if last_speaker and msg.agent != last_speaker:
                key = (last_speaker, msg.agent)
                interactions[key] = interactions.get(key, 0) + 1
            last_speaker = msg.agent
        
        return interactions


class ConversationFlowVisualizer(Visualizer):
    """Visualize conversation flow over time"""
    
    def visualize(self, session: "Session") -> Dict:
        timeline = []
        
        for i, msg in enumerate(session.messages):
            timeline.append({
                "turn": i,
                "agent": msg.agent,
                "content_preview": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            })
        
        # Calculate speaker statistics
        speaker_stats = {}
        for msg in session.messages:
            if msg.agent not in speaker_stats:
                speaker_stats[msg.agent] = {"count": 0, "total_length": 0}
            speaker_stats[msg.agent]["count"] += 1
            speaker_stats[msg.agent]["total_length"] += len(msg.content)
        
        return {
            "type": "conversation_flow",
            "timeline": timeline,
            "speaker_stats": speaker_stats,
            "total_turns": len(session.messages),
        }


class EmotionTrajectoryVisualizer(Visualizer):
    """Visualize emotional trajectory (placeholder)"""
    
    def visualize(self, session: "Session") -> Dict:
        # Placeholder - would use sentiment analysis
        emotions = []
        
        for i, msg in enumerate(session.messages):
            # Mock emotion detection
            emotion = self._detect_emotion(msg.content)
            emotions.append({
                "turn": i,
                "agent": msg.agent,
                "emotion": emotion,
            })
        
        return {
            "type": "emotion_trajectory",
            "emotions": emotions,
        }
    
    def _detect_emotion(self, text: str) -> str:
        """Detect emotion from text (placeholder)"""
        # In practice, this would use a sentiment analysis model
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["sad", "depressed", "hopeless"]):
            return "sadness"
        elif any(word in text_lower for word in ["happy", "joy", "excited"]):
            return "joy"
        elif any(word in text_lower for word in ["angry", "frustrated", "mad"]):
            return "anger"
        elif any(word in text_lower for word in ["anxious", "worried", "nervous"]):
            return "anxiety"
        else:
            return "neutral"
