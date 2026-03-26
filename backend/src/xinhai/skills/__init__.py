"""
Skills module for XinHaiAgents

This module provides the skill interface for OpenClaw integration.
It exposes the core multi-agent simulation capabilities as reusable components.
"""

from .base import (
    XinHaiSkill,
    Scenario,
    Agent,
    Session,
    Message,
    Context,
    RiskAssessment,
    EvaluationMetrics,
)

from .orchestrator import (
    Orchestrator,
    RoundRobinOrchestrator,
    DynamicOrchestrator,
    RoleBasedOrchestrator,
)

from .topology import (
    Topology,
    StarTopology,
    ChainTopology,
    CircleTopology,
    FullyConnectedTopology,
    CustomTopology,
)

from .evaluator import (
    Evaluator,
    CoherenceEvaluator,
    DiversityEvaluator,
    GoalAchievementEvaluator,
)

from .visualizer import (
    Visualizer,
    NetworkVisualizer,
    ConversationFlowVisualizer,
)

__all__ = [
    # Base classes
    "XinHaiSkill",
    "Scenario",
    "Agent",
    "Session",
    "Message",
    "Context",
    "RiskAssessment",
    "EvaluationMetrics",
    # Orchestrators
    "Orchestrator",
    "RoundRobinOrchestrator",
    "DynamicOrchestrator",
    "RoleBasedOrchestrator",
    # Topologies
    "Topology",
    "StarTopology",
    "ChainTopology",
    "CircleTopology",
    "FullyConnectedTopology",
    "CustomTopology",
    # Evaluators
    "Evaluator",
    "CoherenceEvaluator",
    "DiversityEvaluator",
    "GoalAchievementEvaluator",
    # Visualizers
    "Visualizer",
    "NetworkVisualizer",
    "ConversationFlowVisualizer",
]
