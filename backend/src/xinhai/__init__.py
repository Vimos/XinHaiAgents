"""
XinHaiAgents - Sea of Minds Framework

A framework for multimodal multi-agent simulation and evolution.
"""

__version__ = "0.1.0"
__author__ = "XinHai Team"

# Core exports for skills
from .controller import Controller
from .memory_storage import MemoryStorage
from .utils import build_logger
from .config import LOG_DIR, CONTROLLER_HEART_BEAT_EXPIRATION

# Types
from .types.message import (
    XinHaiMMRequest,
    XinHaiMMResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    XinHaiChatCompletionRequest,
)

# Skills support (new)
try:
    from .skills import (
        XinHaiSkill,
        Scenario,
        Agent,
        Session,
        Orchestrator,
        RoundRobinOrchestrator,
        DynamicOrchestrator,
        Topology,
        StarTopology,
        ChainTopology,
        CircleTopology,
        FullyConnectedTopology,
    )
except ImportError:
    # Skills module may not be available if dependencies are missing
    pass

__all__ = [
    "Controller",
    "MemoryStorage",
    "build_logger",
    "LOG_DIR",
    "CONTROLLER_HEART_BEAT_EXPIRATION",
    "XinHaiMMRequest",
    "XinHaiMMResponse",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "XinHaiChatCompletionRequest",
    # Skills
    "XinHaiSkill",
    "Scenario",
    "Agent",
    "Session",
    "Orchestrator",
    "RoundRobinOrchestrator",
    "DynamicOrchestrator",
    "Topology",
    "StarTopology",
    "ChainTopology",
    "CircleTopology",
    "FullyConnectedTopology",
]
