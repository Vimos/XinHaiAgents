"""
Base classes for XinHaiAgents Skills
"""

import uuid
import json
from typing import List, Dict, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SimulationMode(Enum):
    """Simulation mode"""
    COLLABORATIVE = "collaborative"
    ADVERSARIAL = "adversarial"
    HYBRID = "hybrid"


class RiskLevel(Enum):
    """Risk level for mental health applications"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    IMMINENT = "imminent"


@dataclass
class Message:
    """Message in a conversation"""
    agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent": self.agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(
            agent=data["agent"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Context:
    """Context for agent decision making"""
    messages: List[Message]
    round: int
    stage: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def last_message(self) -> Optional[Message]:
        return self.messages[-1] if self.messages else None


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    level: RiskLevel
    confidence: float
    primary_concerns: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    evidence: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "level": self.level.value,
            "confidence": self.confidence,
            "primary_concerns": self.primary_concerns,
            "protective_factors": self.protective_factors,
            "evidence": self.evidence,
        }


@dataclass
class EvaluationMetrics:
    """Evaluation metrics for a session"""
    coherence: float = 0.0
    diversity: float = 0.0
    goal_achievement: float = 0.0
    turn_efficiency: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "coherence": self.coherence,
            "diversity": self.diversity,
            "goal_achievement": self.goal_achievement,
            "turn_efficiency": self.turn_efficiency,
            **self.custom_metrics,
        }


@dataclass
class Agent:
    """Agent configuration"""
    name: str
    role: str
    system_prompt: str = ""
    model: str = "default"
    capabilities: List[str] = field(default_factory=list)
    memory_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "capabilities": self.capabilities,
            "memory_config": self.memory_config,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Agent":
        return cls(
            name=data["name"],
            role=data["role"],
            system_prompt=data.get("system_prompt", ""),
            model=data.get("model", "default"),
            capabilities=data.get("capabilities", []),
            memory_config=data.get("memory_config", {}),
        )


@dataclass
class Session:
    """Simulation session"""
    id: str
    scenario: str
    agents: List[Agent]
    messages: List[Message] = field(default_factory=list)
    metrics: EvaluationMetrics = field(default_factory=EvaluationMetrics)
    status: str = "running"
    created_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message):
        """Add a message to the session"""
        self.messages.append(message)
    
    def end(self):
        """Mark session as ended"""
        self.status = "completed"
        self.ended_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "scenario": self.scenario,
            "agents": [a.to_dict() for a in self.agents],
            "messages": [m.to_dict() for m in self.messages],
            "metrics": self.metrics.to_dict(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        return cls(
            id=data["id"],
            scenario=data["scenario"],
            agents=[Agent.from_dict(a) for a in data.get("agents", [])],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            metrics=EvaluationMetrics(**data.get("metrics", {})),
            status=data.get("status", "running"),
            created_at=datetime.fromisoformat(data["created_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class Scenario:
    """Scenario configuration"""
    name: str
    description: str
    category: str
    agents: List[Agent]
    topology: str = "star"
    orchestrator: str = "dynamic"
    stages: List[Dict] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "agents": [a.to_dict() for a in self.agents],
            "topology": self.topology,
            "orchestrator": self.orchestrator,
            "stages": self.stages,
            "rules": self.rules,
            "evaluation_metrics": self.evaluation_metrics,
            "config": self.config,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Scenario":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "general"),
            agents=[Agent.from_dict(a) for a in data.get("agents", [])],
            topology=data.get("topology", "star"),
            orchestrator=data.get("orchestrator", "dynamic"),
            stages=data.get("stages", []),
            rules=data.get("rules", {}),
            evaluation_metrics=data.get("evaluation_metrics", []),
            config=data.get("config", {}),
        )


class XinHaiSkill:
    """
    Main skill class for XinHaiAgents
    
    This is the primary interface for OpenClaw integration.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.backend_url = self.config.get("backend_url", "http://localhost:8000")
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 300)
        
        # Load scenarios
        self.scenarios: Dict[str, Scenario] = {}
        self._load_builtin_scenarios()
        
        # Session storage
        self.sessions: Dict[str, Session] = {}
    
    def _load_builtin_scenarios(self):
        """Load built-in scenarios"""
        # This will be populated from scenario files
        pass
    
    def simulate(
        self,
        scenario: str,
        agents: List[Dict],
        rounds: int = 10,
        config: Optional[Dict] = None
    ) -> Session:
        """
        Run a simulation
        
        Args:
            scenario: Scenario name or config
            agents: List of agent configurations
            rounds: Number of rounds
            config: Additional configuration
            
        Returns:
            Session object
        """
        raise NotImplementedError("Subclasses must implement simulate()")
    
    async def simulate_async(
        self,
        scenario: str,
        agents: List[Dict],
        rounds: int = 10,
        config: Optional[Dict] = None
    ) -> AsyncGenerator[Message, None]:
        """
        Run simulation asynchronously with streaming
        
        Yields:
            Message objects as they are generated
        """
        raise NotImplementedError("Subclasses must implement simulate_async()")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Session]:
        """List all sessions"""
        return list(self.sessions.values())
    
    def evaluate(self, session_id: str, metrics: Optional[List[str]] = None) -> Dict:
        """
        Evaluate a session
        
        Args:
            session_id: Session ID
            metrics: List of metrics to compute (None for all)
            
        Returns:
            Evaluation results
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
    
    def visualize(self, session_id: str, config: Optional[Dict] = None) -> Dict:
        """
        Generate visualization data
        
        Args:
            session_id: Session ID
            config: Visualization configuration
            
        Returns:
            Visualization data
        """
        raise NotImplementedError("Subclasses must implement visualize()")
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID"""
        return f"xhs_{uuid.uuid4().hex[:12]}"
