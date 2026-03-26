"""
Topologies for agent communication
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Agent


class Topology(ABC):
    """Base topology for agent communication"""
    
    def __init__(self, agents: List["Agent"], config: Dict = None):
        self.agents = agents
        self.config = config or {}
        self.agent_map = {a.name: a for a in agents}
    
    @abstractmethod
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        """Get neighboring agents that can communicate with the given agent"""
        pass
    
    @abstractmethod
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        """Check if two agents can communicate"""
        pass
    
    def get_next_speaker(self, current: "Agent", last_speaker: "Agent" = None) -> "Agent":
        """Get the next speaker based on topology"""
        # Default: round-robin through all agents
        idx = self.agents.index(current)
        return self.agents[(idx + 1) % len(self.agents)]


class StarTopology(Topology):
    """Star topology - one central agent connected to all others"""
    
    def __init__(self, agents: List["Agent"], config: Dict = None):
        super().__init__(agents, config)
        if not agents:
            raise ValueError("Star topology requires at least one agent")
        self.center = agents[0]  # First agent is center
        self.peripherals = agents[1:]
    
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        if agent.name == self.center.name:
            return self.peripherals
        else:
            return [self.center]
    
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        # Only center can communicate with peripherals, peripherals communicate through center
        return (
            agent_a.name == self.center.name or 
            agent_b.name == self.center.name
        )
    
    def get_next_speaker(self, current: "Agent", last_speaker: "Agent" = None) -> "Agent":
        if current.name == self.center.name:
            # Center spoke, now a peripheral speaks
            if self.peripherals:
                idx = self.peripherals.index(last_speaker) + 1 if last_speaker in self.peripherals else 0
                return self.peripherals[idx % len(self.peripherals)]
            return self.center
        else:
            # Peripheral spoke, now center speaks
            return self.center


class ChainTopology(Topology):
    """Chain topology - agents connected in a line"""
    
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        idx = self.agents.index(agent)
        neighbors = []
        if idx > 0:
            neighbors.append(self.agents[idx - 1])
        if idx < len(self.agents) - 1:
            neighbors.append(self.agents[idx + 1])
        return neighbors
    
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        idx_a = self.agents.index(agent_a)
        idx_b = self.agents.index(agent_b)
        return abs(idx_a - idx_b) == 1
    
    def get_next_speaker(self, current: "Agent", last_speaker: "Agent" = None) -> "Agent":
        idx = self.agents.index(current)
        # Alternate direction
        if last_speaker:
            last_idx = self.agents.index(last_speaker)
            if last_idx < idx:
                # Going forward
                if idx < len(self.agents) - 1:
                    return self.agents[idx + 1]
                else:
                    return self.agents[idx - 1]  # Turn around
            else:
                # Going backward
                if idx > 0:
                    return self.agents[idx - 1]
                else:
                    return self.agents[idx + 1]  # Turn around
        return self.agents[(idx + 1) % len(self.agents)]


class CircleTopology(Topology):
    """Circle topology - agents connected in a circle"""
    
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        idx = self.agents.index(agent)
        n = len(self.agents)
        return [
            self.agents[(idx - 1) % n],
            self.agents[(idx + 1) % n]
        ]
    
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        idx_a = self.agents.index(agent_a)
        idx_b = self.agents.index(agent_b)
        n = len(self.agents)
        return abs(idx_a - idx_b) == 1 or abs(idx_a - idx_b) == n - 1
    
    def get_next_speaker(self, current: "Agent", last_speaker: "Agent" = None) -> "Agent":
        idx = self.agents.index(current)
        # Continue in same direction if possible
        if last_speaker:
            last_idx = self.agents.index(last_speaker)
            if (last_idx + 1) % len(self.agents) == idx:
                # Going clockwise
                return self.agents[(idx + 1) % len(self.agents)]
            else:
                # Going counter-clockwise
                return self.agents[(idx - 1) % len(self.agents)]
        return self.agents[(idx + 1) % len(self.agents)]


class FullyConnectedTopology(Topology):
    """Fully connected topology - all agents can communicate with each other"""
    
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        return [a for a in self.agents if a.name != agent.name]
    
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        return agent_a.name != agent_b.name
    
    def get_next_speaker(self, current: "Agent", last_speaker: "Agent" = None) -> "Agent":
        # Round-robin
        idx = self.agents.index(current)
        return self.agents[(idx + 1) % len(self.agents)]


class CustomTopology(Topology):
    """Custom topology defined by adjacency matrix or edge list"""
    
    def __init__(self, agents: List["Agent"], config: Dict = None):
        super().__init__(agents, config)
        self.edges: Dict[str, Set[str]] = {}
        
        # Build edges from config
        if config and "edges" in config:
            for edge in config["edges"]:
                a, b = edge["from"], edge["to"]
                if a not in self.edges:
                    self.edges[a] = set()
                if b not in self.edges:
                    self.edges[b] = set()
                self.edges[a].add(b)
                self.edges[b].add(a)
    
    def get_neighbors(self, agent: "Agent") -> List["Agent"]:
        neighbor_names = self.edges.get(agent.name, set())
        return [self.agent_map[name] for name in neighbor_names if name in self.agent_map]
    
    def can_communicate(self, agent_a: "Agent", agent_b: "Agent") -> bool:
        return agent_b.name in self.edges.get(agent_a.name, set())
