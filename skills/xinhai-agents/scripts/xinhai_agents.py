#!/usr/bin/env python3
"""
XinHaiAgents OpenClaw Skill
心海多智能体框架的OpenClaw封装

提供：
- 场景模拟
- 动态编排
- 可视化
- 评估
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Optional, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SimulationMode(Enum):
    """模拟模式"""
    COLLABORATIVE = "collaborative"  # 协作模式
    ADVERSARIAL = "adversarial"      # 对抗模式
    HYBRID = "hybrid"                # 混合模式


class TopologyType(Enum):
    """拓扑类型"""
    STAR = "star"                    # 星型：中心节点
    CHAIN = "chain"                  # 链型：顺序传递
    CIRCLE = "circle"                # 环形：循环讨论
    FULLY_CONNECTED = "fully_connected"  # 全连接
    CUSTOM = "custom"                # 自定义


@dataclass
class Agent:
    """智能体配置"""
    name: str
    role: str
    system_prompt: str = ""
    model: str = "default"
    capabilities: List[str] = field(default_factory=list)
    memory_config: Dict = field(default_factory=dict)


@dataclass
class Message:
    """消息数据类"""
    agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent": self.agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Session:
    """会话数据类"""
    id: str
    scenario: str
    agents: List[Agent]
    messages: List[Message] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    status: str = "running"
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: Message):
        self.messages.append(message)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "scenario": self.scenario,
            "agents": [{"name": a.name, "role": a.role} for a in self.agents],
            "messages": [m.to_dict() for m in self.messages],
            "metrics": self.metrics,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class Orchestrator:
    """编排器基类"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def next_speaker(self, context: Dict) -> str:
        """
        决定下一个发言者
        
        Args:
            context: 当前上下文，包含messages、agents、round等信息
            
        Returns:
            下一个发言者的name
        """
        raise NotImplementedError
    
    def should_stop(self, context: Dict) -> bool:
        """
        判断是否结束模拟
        """
        max_rounds = self.config.get("max_rounds", 10)
        return context.get("round", 0) >= max_rounds


class RoundRobinOrchestrator(Orchestrator):
    """轮询编排器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.current_index = 0
    
    def next_speaker(self, context: Dict) -> str:
        agents = context.get("agents", [])
        if not agents:
            return None
        
        speaker = agents[self.current_index % len(agents)]
        self.current_index += 1
        return speaker["name"]


class DynamicOrchestrator(Orchestrator):
    """动态编排器 - 基于内容选择发言者"""
    
    def next_speaker(self, context: Dict) -> str:
        messages = context.get("messages", [])
        agents = context.get("agents", [])
        
        if not messages:
            # 第一个消息：选择指定的开场者或随机
            return self.config.get("starter", agents[0]["name"] if agents else None)
        
        last_message = messages[-1]
        last_agent = last_message.get("agent")
        
        # 简单的逻辑：如果有人提问，让therapist回答
        content = last_message.get("content", "").lower()
        if "?" in content or "how" in content or "what" in content:
            for agent in agents:
                if "therapist" in agent.get("role", "").lower():
                    return agent["name"]
        
        # 否则轮询
        agent_names = [a["name"] for a in agents]
        last_idx = agent_names.index(last_agent) if last_agent in agent_names else -1
        next_idx = (last_idx + 1) % len(agent_names)
        return agent_names[next_idx]


class XinHaiSkill:
    """
    XinHaiAgents Skill 主类
    
    提供多智能体模拟的完整功能
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.backend_url = self.config.get("backend_url", "http://localhost:8000")
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 300)
        
        # 注册的场景模板
        self.scenarios = self._load_scenarios()
        
        # 注册的编排器
        self.orchestrators = {
            "round_robin": RoundRobinOrchestrator,
            "dynamic": DynamicOrchestrator,
        }
        
        # 会话缓存
        self.sessions: Dict[str, Session] = {}
    
    def _load_scenarios(self) -> Dict:
        """加载内置场景模板"""
        return {
            "therapy_session": {
                "name": "心理咨询",
                "description": "一对一心理咨询模拟",
                "agents": [
                    {"role": "therapist", "name": "therapist"},
                    {"role": "patient", "name": "patient"}
                ],
                "topology": "star",
                "orchestrator": "dynamic"
            },
            "group_therapy": {
                "name": "团体治疗",
                "description": "多患者团体治疗模拟",
                "agents": [
                    {"role": "therapist", "name": "therapist"},
                    {"role": "patient", "name": "patient1"},
                    {"role": "patient", "name": "patient2"},
                    {"role": "patient", "name": "patient3"}
                ],
                "topology": "circle",
                "orchestrator": "round_robin"
            },
            "suicide_intervention": {
                "name": "自杀干预",
                "description": "危机干预模拟",
                "agents": [
                    {"role": "crisis_counselor", "name": "counselor"},
                    {"role": "at_risk_individual", "name": "individual"}
                ],
                "topology": "star",
                "orchestrator": "dynamic",
                "safety_checks": True
            },
            "debate": {
                "name": "辩论",
                "description": "正反方辩论模拟",
                "agents": [
                    {"role": "affirmative", "name": "affirmative"},
                    {"role": "negative", "name": "negative"},
                    {"role": "moderator", "name": "moderator"}
                ],
                "topology": "chain",
                "orchestrator": "round_robin",
                "mode": "adversarial"
            },
            "negotiation": {
                "name": "谈判",
                "description": "双方谈判模拟",
                "agents": [
                    {"role": "party_a", "name": "party_a"},
                    {"role": "party_b", "name": "party_b"},
                    {"role": "mediator", "name": "mediator"}
                ],
                "topology": "star",
                "orchestrator": "dynamic"
            },
            "peer_counseling": {
                "name": "朋辈咨询",
                "description": "朋辈互助咨询模拟",
                "agents": [
                    {"role": "peer_counselor", "name": "counselor"},
                    {"role": "seeker", "name": "seeker"}
                ],
                "topology": "star",
                "orchestrator": "dynamic"
            }
        }
    
    # ==================== 核心 API ====================
    
    def simulate(
        self,
        scenario: str,
        agents: List[Dict],
        rounds: int = 10,
        config: Dict = None
    ) -> Session:
        """
        创建并运行模拟
        
        Args:
            scenario: 场景名称或自定义场景定义
            agents: 智能体配置列表
            rounds: 对话轮数
            config: 额外配置
            
        Returns:
            Session 对象
        """
        config = config or {}
        
        # 创建会话
        session_id = self._generate_session_id()
        agent_objects = [Agent(**a) for a in agents]
        
        session = Session(
            id=session_id,
            scenario=scenario,
            agents=agent_objects
        )
        
        # 选择编排器
        orchestrator_type = config.get("orchestrator", "dynamic")
        orchestrator_class = self.orchestrators.get(
            orchestrator_type, 
            DynamicOrchestrator
        )
        orchestrator = orchestrator_class(config)
        
        # 运行模拟（简化版，实际应调用后端API）
        # TODO: 实现与XinHaiAgents后端的实际通信
        
        self.sessions[session_id] = session
        return session
    
    async def simulate_async(
        self,
        scenario: str,
        agents: List[Dict],
        rounds: int = 10,
        config: Dict = None
    ) -> AsyncGenerator[Message, None]:
        """
        异步运行模拟，实时返回消息
        
        Yields:
            Message 对象
        """
        config = config or {}
        session_id = self._generate_session_id()
        
        # 连接到后端WebSocket或SSE
        async with aiohttp.ClientSession() as session:
            # TODO: 实现与后端的流式通信
            pass
    
    def load_scenario(self, scenario_name: str) -> "ScenarioBuilder":
        """
        加载预置场景
        
        Args:
            scenario_name: 场景名称
            
        Returns:
            ScenarioBuilder 对象
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario_config = self.scenarios[scenario_name]
        return ScenarioBuilder(self, scenario_config)
    
    def create_scenario(self, scenario_config: Dict) -> "ScenarioBuilder":
        """
        创建自定义场景
        
        Args:
            scenario_config: 场景配置
            
        Returns:
            ScenarioBuilder 对象
        """
        return ScenarioBuilder(self, scenario_config)
    
    def register_scenario(self, name: str, config: Dict):
        """
        注册新场景
        
        Args:
            name: 场景名称
            config: 场景配置
        """
        self.scenarios[name] = config
    
    def create_workflow(self, name: str) -> "WorkflowBuilder":
        """
        创建工作流
        
        Args:
            name: 工作流名称
            
        Returns:
            WorkflowBuilder 对象
        """
        return WorkflowBuilder(self, name)
    
    def visualize(self, session_id: str, config: Dict = None) -> Dict:
        """
        获取可视化数据
        
        Args:
            session_id: 会话ID
            config: 可视化配置
            
        Returns:
            可视化数据字典
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # 生成可视化数据
        viz_data = {
            "network_graph": self._generate_network_graph(session),
            "conversation_flow": self._generate_conversation_flow(session),
            "agent_statistics": self._generate_agent_stats(session),
            "emotional_trajectory": self._generate_emotional_trajectory(session)
        }
        
        return viz_data
    
    def evaluate(self, session_id: str, metrics: List[str] = None) -> Dict:
        """
        评估会话
        
        Args:
            session_id: 会话ID
            metrics: 评估指标列表，None表示全部
            
        Returns:
            评估结果
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # 计算指标
        results = {}
        
        if metrics is None or "coherence" in metrics:
            results["coherence"] = self._calc_coherence(session)
        
        if metrics is None or "diversity" in metrics:
            results["diversity"] = self._calc_diversity(session)
        
        if metrics is None or "goal_achievement" in metrics:
            results["goal_achievement"] = self._calc_goal_achievement(session)
        
        session.metrics = results
        return results
    
    def register_metric(self, name: str, config: Dict):
        """
        注册自定义评估指标
        
        Args:
            name: 指标名称
            config: 指标配置
        """
        # TODO: 实现自定义指标注册
        pass
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Session]:
        """列出所有会话"""
        return list(self.sessions.values())
    
    # ==================== 内部方法 ====================
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return f"xhs_{uuid.uuid4().hex[:12]}"
    
    def _generate_network_graph(self, session: Session) -> Dict:
        """生成网络图数据"""
        nodes = []
        edges = []
        
        for agent in session.agents:
            nodes.append({
                "id": agent.name,
                "label": agent.name,
                "role": agent.role,
                "group": agent.role
            })
        
        # 统计交互
        interactions = {}
        for msg in session.messages:
            agent = msg.agent
            if agent not in interactions:
                interactions[agent] = {}
        
        return {"nodes": nodes, "edges": edges}
    
    def _generate_conversation_flow(self, session: Session) -> List[Dict]:
        """生成对话流程数据"""
        return [msg.to_dict() for msg in session.messages]
    
    def _generate_agent_stats(self, session: Session) -> Dict:
        """生成智能体统计"""
        stats = {}
        for agent in session.agents:
            agent_messages = [m for m in session.messages if m.agent == agent.name]
            stats[agent.name] = {
                "message_count": len(agent_messages),
                "avg_message_length": sum(len(m.content) for m in agent_messages) / max(len(agent_messages), 1)
            }
        return stats
    
    def _generate_emotional_trajectory(self, session: Session) -> List[Dict]:
        """生成情感轨迹"""
        # TODO: 实现情感分析
        return []
    
    def _calc_coherence(self, session: Session) -> float:
        """计算连贯性"""
        # TODO: 实现连贯性计算
        return 0.85
    
    def _calc_diversity(self, session: Session) -> float:
        """计算多样性"""
        # TODO: 实现多样性计算
        return 0.75
    
    def _calc_goal_achievement(self, session: Session) -> float:
        """计算目标达成度"""
        # TODO: 实现目标达成度计算
        return 0.80


class ScenarioBuilder:
    """场景构建器"""
    
    def __init__(self, skill: XinHaiSkill, config: Dict):
        self.skill = skill
        self.config = config
        self.agents = []
        self.custom_config = {}
    
    def add_agent(self, name: str, role: str = None, **kwargs):
        """添加智能体"""
        agent = {"name": name}
        if role:
            agent["role"] = role
        agent.update(kwargs)
        self.agents.append(agent)
        return self
    
    def set_topology(self, topology: str):
        """设置拓扑"""
        self.custom_config["topology"] = topology
        return self
    
    def set_orchestrator(self, orchestrator: str):
        """设置编排器"""
        self.custom_config["orchestrator"] = orchestrator
        return self
    
    def run(self, rounds: int = 10) -> Session:
        """运行场景"""
        agents = self.agents or self.config.get("agents", [])
        config = {**self.config, **self.custom_config}
        
        return self.skill.simulate(
            scenario=self.config.get("name", "custom"),
            agents=agents,
            rounds=rounds,
            config=config
        )


class WorkflowBuilder:
    """工作流构建器"""
    
    def __init__(self, skill: XinHaiSkill, name: str):
        self.skill = skill
        self.name = name
        self.stages = []
    
    def add_stage(self, name: str, **kwargs):
        """添加阶段"""
        self.stages.append({"name": name, **kwargs})
        return self
    
    def run(self) -> Session:
        """运行工作流"""
        # TODO: 实现工作流执行
        pass


# ==================== Discord Bot 集成 ====================

class DiscordIntegration:
    """Discord Bot 集成"""
    
    def __init__(self, skill: XinHaiSkill, bot):
        self.skill = skill
        self.bot = bot
        self.active_sessions: Dict[str, str] = {}  # channel_id -> session_id
    
    async def handle_simulate_command(self, ctx, scenario: str, *agent_names):
        """处理 /simulate 命令"""
        await ctx.send(f"🎭 启动模拟: **{scenario}**")
        
        # 创建智能体配置
        agents = [{"name": name} for name in agent_names]
        if not agents:
            agents = [{"name": "agent1"}, {"name": "agent2"}]
        
        try:
            # 创建会话
            session = self.skill.simulate(
                scenario=scenario,
                agents=agents,
                rounds=5
            )
            
            self.active_sessions[str(ctx.channel.id)] = session.id
            
            await ctx.send(f"✅ 会话已创建: `{session.id}`")
            
            # 模拟实时输出
            for i, msg in enumerate(session.messages):
                await ctx.send(f"**{msg.agent}**: {msg.content}")
                await asyncio.sleep(1)
            
        except Exception as e:
            await ctx.send(f"❌ 错误: {e}")
    
    async def handle_status_command(self, ctx, session_id: str = None):
        """处理 /status 命令"""
        if not session_id:
            session_id = self.active_sessions.get(str(ctx.channel.id))
        
        if not session_id:
            await ctx.send("❌ 没有活动的会话")
            return
        
        session = self.skill.get_session(session_id)
        if not session:
            await ctx.send(f"❌ 会话不存在: {session_id}")
            return
        
        embed = {
            "title": f"Session Status: {session_id}",
            "fields": [
                {"name": "Status", "value": session.status, "inline": True},
                {"name": "Messages", "value": str(len(session.messages)), "inline": True},
                {"name": "Agents", "value": ", ".join(a.name for a in session.agents), "inline": False}
            ]
        }
        
        await ctx.send(embed=embed)
    
    async def handle_visualize_command(self, ctx, session_id: str = None):
        """处理 /visualize 命令"""
        if not session_id:
            session_id = self.active_sessions.get(str(ctx.channel.id))
        
        if not session_id:
            await ctx.send("❌ 没有活动的会话")
            return
        
        try:
            viz_data = self.skill.visualize(session_id)
            await ctx.send(f"📊 可视化数据已生成: `{session_id}`")
            # TODO: 发送可视化图片或链接
        except Exception as e:
            await ctx.send(f"❌ 错误: {e}")


# 使用示例
if __name__ == "__main__":
    # 初始化
    xinhai = XinHaiSkill({
        "backend_url": "http://localhost:8000"
    })
    
    # 示例1: 快速启动心理咨询模拟
    session = xinhai.simulate(
        scenario="therapy_session",
        agents=[
            {"name": "therapist", "role": "CBT_counselor"},
            {"name": "patient", "role": "anxious_patient"}
        ],
        rounds=5
    )
    
    print(f"Session created: {session.id}")
    
    # 示例2: 使用场景构建器
    scenario = xinhai.load_scenario("group_therapy")
    scenario.add_agent("therapist", "CBT_therapist")
    scenario.add_agent("patient1", "depressed_patient")
    scenario.add_agent("patient2", "anxious_patient")
    session = scenario.run(rounds=10)
    
    # 示例3: 评估
    metrics = xinhai.evaluate(session.id)
    print(f"Metrics: {metrics}")
    
    # 示例4: 可视化
    viz = xinhai.visualize(session.id)
    print(f"Visualization data ready")
