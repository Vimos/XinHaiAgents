"""
Orchestrators for agent coordination
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Context, Agent, Session


class Orchestrator(ABC):
    """Base orchestrator for agent coordination"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    @abstractmethod
    def select_next_agent(self, context: "Context", agents: List["Agent"]) -> str:
        """
        Select the next agent to speak
        
        Args:
            context: Current conversation context
            agents: List of available agents
            
        Returns:
            Name of the selected agent
        """
        pass
    
    def should_stop(self, context: "Context", max_rounds: int = 10) -> bool:
        """
        Determine if the simulation should stop
        
        Args:
            context: Current context
            max_rounds: Maximum number of rounds
            
        Returns:
            True if simulation should stop
        """
        return context.round >= max_rounds


class RoundRobinOrchestrator(Orchestrator):
    """Round-robin orchestrator - agents take turns in order"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.current_index = 0
    
    def select_next_agent(self, context: "Context", agents: List["Agent"]) -> str:
        if not agents:
            raise ValueError("No agents available")
        
        agent = agents[self.current_index % len(agents)]
        self.current_index += 1
        return agent.name


class DynamicOrchestrator(Orchestrator):
    """Dynamic orchestrator - selects based on content"""
    
    def select_next_agent(self, context: "Context", agents: List["Agent"]) -> str:
        if not agents:
            raise ValueError("No agents available")
        
        if not context.messages:
            # First message - use starter agent or first agent
            starter = self.config.get("starter")
            if starter:
                return starter
            return agents[0].name
        
        last_message = context.last_message
        last_agent = last_message.agent if last_message else None
        
        # Simple logic: if someone asks a question, let therapist/responder answer
        content = last_message.content.lower() if last_message else ""
        question_words = ["?", "how", "what", "why", "when", "where", "who"]
        
        if any(word in content for word in question_words):
            # Look for therapist/counselor/responder role
            for agent in agents:
                role_lower = agent.role.lower()
                if any(r in role_lower for r in ["therapist", "counselor", "responder", "moderator"]):
                    return agent.name
        
        # Otherwise, round-robin
        agent_names = [a.name for a in agents]
        if last_agent and last_agent in agent_names:
            last_idx = agent_names.index(last_agent)
            next_idx = (last_idx + 1) % len(agent_names)
            return agent_names[next_idx]
        
        return agents[0].name


class RoleBasedOrchestrator(Orchestrator):
    """Role-based orchestrator - assigns turns based on roles"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.role_order = config.get("role_order", []) if config else []
        self.current_role_index = 0
    
    def select_next_agent(self, context: "Context", agents: List["Agent"]) -> str:
        if not agents:
            raise ValueError("No agents available")
        
        if not self.role_order:
            # Fallback to round-robin
            return agents[self.current_role_index % len(agents)].name
        
        # Find next role in sequence
        for _ in range(len(self.role_order)):
            expected_role = self.role_order[self.current_role_index % len(self.role_order)]
            self.current_role_index += 1
            
            # Find agent with this role
            for agent in agents:
                if agent.role == expected_role:
                    return agent.name
        
        # Fallback to first agent
        return agents[0].name
