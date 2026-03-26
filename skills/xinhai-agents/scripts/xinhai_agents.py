#!/usr/bin/env python3
"""
XinHaiAgents OpenClaw Skill

This skill provides an interface to the XinHaiAgents multi-agent simulation framework.
It imports core functionality from the backend/src/xinhai package.

Usage:
    from skills.xinhai_agents.scripts.xinhai_agents import XinHaiSkill, ScenarioBuilder
    
    xinhai = XinHaiSkill(config)
    session = xinhai.simulate("therapy_session", agents, rounds=10)
"""

import sys
import os
from pathlib import Path

# Add backend/src to path for imports
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import from backend
try:
    from xinhai.skills import (
        XinHaiSkill as BaseSkill,
        Scenario,
        Agent,
        Session,
        Message,
        Context,
        Orchestrator,
        RoundRobinOrchestrator,
        DynamicOrchestrator,
        Topology,
        StarTopology,
        ChainTopology,
        CircleTopology,
        FullyConnectedTopology,
    )
    from xinhai.skills.evaluator import (
        Evaluator,
        CoherenceEvaluator,
        DiversityEvaluator,
        GoalAchievementEvaluator,
    )
    from xinhai.skills.visualizer import (
        Visualizer,
        NetworkVisualizer,
        ConversationFlowVisualizer,
    )
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import from backend: {e}")
    print("Falling back to standalone implementation")
    BACKEND_AVAILABLE = False
    # Import standalone implementations as fallback
    from dataclasses import dataclass, field
    from datetime import datetime
    from typing import List, Dict, Optional, AsyncGenerator, Callable
    from enum import Enum
    import json
    import asyncio
    import aiohttp
    
    # Fallback implementations would go here
    # For now, raise error if backend not available
    raise ImportError(
        "Backend not available. Please ensure backend/src/xinhai is properly set up."
    )


class ScenarioBuilder:
    """Builder for creating scenarios"""
    
    def __init__(self, skill: "XinHaiSkill", config: Dict):
        self.skill = skill
        self.config = config
        self.agents = []
        self.custom_config = {}
    
    def add_agent(self, name: str, role: str = None, **kwargs):
        """Add an agent to the scenario"""
        agent = {"name": name}
        if role:
            agent["role"] = role
        agent.update(kwargs)
        self.agents.append(agent)
        return self
    
    def set_topology(self, topology: str):
        """Set the communication topology"""
        self.custom_config["topology"] = topology
        return self
    
    def set_orchestrator(self, orchestrator: str):
        """Set the orchestrator type"""
        self.custom_config["orchestrator"] = orchestrator
        return self
    
    def run(self, rounds: int = 10) -> Session:
        """Run the scenario"""
        agents = self.agents or self.config.get("agents", [])
        config = {**self.config, **self.custom_config}
        
        return self.skill.simulate(
            scenario=self.config.get("name", "custom"),
            agents=agents,
            rounds=rounds,
            config=config
        )


class WorkflowBuilder:
    """Builder for creating multi-stage workflows"""
    
    def __init__(self, skill: "XinHaiSkill", name: str):
        self.skill = skill
        self.name = name
        self.stages = []
    
    def add_stage(self, name: str, **kwargs):
        """Add a stage to the workflow"""
        self.stages.append({"name": name, **kwargs})
        return self
    
    def run(self) -> Session:
        """Run the workflow"""
        # Implementation would go here
        raise NotImplementedError("Workflow execution not yet implemented")


class XinHaiSkill(BaseSkill if BACKEND_AVAILABLE else object):
    """
    XinHaiAgents Skill for OpenClaw integration
    
    Provides multi-agent simulation capabilities with support for:
    - Various scenarios (therapy, debate, negotiation, etc.)
    - Dynamic agent orchestration
    - Multiple communication topologies
    - Session evaluation and visualization
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # Load built-in scenarios from JSON
        self._load_scenarios_from_file()
    
    def _load_scenarios_from_file(self):
        """Load scenarios from builtin_scenarios.json"""
        scenarios_path = Path(__file__).parent.parent / "assets" / "scenarios" / "builtin_scenarios.json"
        
        if scenarios_path.exists():
            with open(scenarios_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, config in data.get("scenarios", {}).items():
                    self.scenarios[name] = Scenario.from_dict(config)
    
    def load_scenario(self, scenario_name: str) -> ScenarioBuilder:
        """
        Load a built-in scenario
        
        Args:
            scenario_name: Name of the scenario to load
            
        Returns:
            ScenarioBuilder for customizing and running the scenario
            
        Raises:
            ValueError: If scenario not found
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(self.scenarios.keys())}")
        
        scenario_config = self.scenarios[scenario_name]
        return ScenarioBuilder(self, scenario_config.to_dict())
    
    def create_scenario(self, scenario_config: Dict) -> ScenarioBuilder:
        """
        Create a custom scenario
        
        Args:
            scenario_config: Configuration for the custom scenario
            
        Returns:
            ScenarioBuilder for the custom scenario
        """
        return ScenarioBuilder(self, scenario_config)
    
    def create_workflow(self, name: str) -> WorkflowBuilder:
        """
        Create a multi-stage workflow
        
        Args:
            name: Name of the workflow
            
        Returns:
            WorkflowBuilder for constructing the workflow
        """
        return WorkflowBuilder(self, name)
    
    def register_scenario(self, name: str, config: Dict):
        """
        Register a new scenario
        
        Args:
            name: Name for the scenario
            config: Scenario configuration
        """
        self.scenarios[name] = Scenario.from_dict(config)
    
    def list_scenarios(self) -> List[str]:
        """List available scenario names"""
        return list(self.scenarios.keys())
    
    def get_scenario_info(self, name: str) -> Optional[Dict]:
        """Get information about a scenario"""
        if name in self.scenarios:
            return self.scenarios[name].to_dict()
        return None


# Discord Bot Integration
class DiscordIntegration:
    """Integration with Discord Bot for XinHaiAgents"""
    
    def __init__(self, skill: XinHaiSkill, bot):
        self.skill = skill
        self.bot = bot
        self.active_sessions: Dict[str, str] = {}  # channel_id -> session_id
    
    async def handle_simulate_command(self, ctx, scenario: str, *agent_names):
        """Handle /simulate command"""
        import discord
        
        await ctx.send(f"🎭 Starting simulation: **{scenario}**")
        
        # Create agent configs
        agents = [{"name": name} for name in agent_names] if agent_names else [
            {"name": "agent1"},
            {"name": "agent2"}
        ]
        
        try:
            session = self.skill.simulate(
                scenario=scenario,
                agents=agents,
                rounds=5
            )
            
            self.active_sessions[str(ctx.channel.id)] = session.id
            
            await ctx.send(f"✅ Session created: `{session.id}`")
            
            # Stream messages
            for msg in session.messages:
                await ctx.send(f"**{msg.agent}**: {msg.content}")
                await asyncio.sleep(1)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
    
    async def handle_status_command(self, ctx, session_id: str = None):
        """Handle /status command"""
        import discord
        
        if not session_id:
            session_id = self.active_sessions.get(str(ctx.channel.id))
        
        if not session_id:
            await ctx.send("❌ No active session in this channel")
            return
        
        session = self.skill.get_session(session_id)
        if not session:
            await ctx.send(f"❌ Session not found: {session_id}")
            return
        
        embed = discord.Embed(
            title=f"Session Status: {session_id}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value=session.status, inline=True)
        embed.add_field(name="Messages", value=str(len(session.messages)), inline=True)
        embed.add_field(
            name="Agents",
            value=", ".join(a.name for a in session.agents),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_visualize_command(self, ctx, session_id: str = None):
        """Handle /visualize command"""
        if not session_id:
            session_id = self.active_sessions.get(str(ctx.channel.id))
        
        if not session_id:
            await ctx.send("❌ No active session")
            return
        
        try:
            viz_data = self.skill.visualize(session_id)
            await ctx.send(f"📊 Visualization data generated for: `{session_id}`")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")


# Export main classes
__all__ = [
    "XinHaiSkill",
    "ScenarioBuilder",
    "WorkflowBuilder",
    "DiscordIntegration",
    # Re-export from backend
    "Scenario",
    "Agent",
    "Session",
    "Message",
    "Context",
    "Orchestrator",
    "RoundRobinOrchestrator",
    "DynamicOrchestrator",
    "Topology",
    "StarTopology",
    "ChainTopology",
    "CircleTopology",
    "FullyConnectedTopology",
    "Evaluator",
    "CoherenceEvaluator",
    "DiversityEvaluator",
    "GoalAchievementEvaluator",
    "Visualizer",
    "NetworkVisualizer",
    "ConversationFlowVisualizer",
]


# Example usage
if __name__ == "__main__":
    # Example: Quick start
    xinhai = XinHaiSkill({
        "backend_url": "http://localhost:8000",
        "api_key": ""
    })
    
    # List available scenarios
    print("Available scenarios:", xinhai.list_scenarios())
    
    # Load and run a scenario
    scenario = xinhai.load_scenario("therapy_session")
    scenario.add_agent("therapist", "CBT_counselor")
    scenario.add_agent("patient", "anxious_patient")
    session = scenario.run(rounds=5)
    
    print(f"Session: {session.id}")
    print(f"Messages: {len(session.messages)}")
