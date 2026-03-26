# XinHaiAgents 架构设计

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OpenClaw Platform                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Discord Bot     │  │  Telegram Bot    │  │  Web Interface   │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                     │                     │                     │
│           └─────────────────────┼─────────────────────┘                     │
│                                 │                                           │
│                    ┌────────────▼────────────┐                              │
│                    │   XinHaiAgents Skill    │                              │
│                    │   (Orchestration Layer) │                              │
│                    └────────────┬────────────┘                              │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │ API / WebSocket
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                      XinHaiAgents Backend                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         API Gateway (Bridge)                         │   │
│  │  - REST API / WebSocket / gRPC                                      │   │
│  │  - Authentication & Rate Limiting                                   │   │
│  │  - Request Routing                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                        Controller (编排中心)                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │  │
│  │  │ Scenario    │  │ Workflow    │  │ Topology    │  │ Memory     │ │  │
│  │  │ Manager     │  │ Engine      │  │ Manager     │  │ Manager    │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                        Agent Services                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │  │
│  │  │ Agent 1     │  │ Agent 2     │  │ Agent 3     │  │ Agent N    │ │  │
│  │  │ (LLM +      │  │ (LLM +      │  │ (LLM +      │  │ (LLM +     │ │  │
│  │  │  Memory)    │  │  Memory)    │  │  Memory)    │  │  Memory)   │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────▼────────────────────────────────────┐  │
│  │                        Infrastructure                                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │  │
│  │  │ LLM Service │  │ Vector DB   │  │ Cache       │  │ Message    │ │  │
│  │  │ ( XinHai )  │  │ (ChromaDB)  │  │ (Redis)     │  │ Queue      │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                         Visualization Layer                                  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Vue 3 + Phaser  │  │  React + D3      │  │  Real-time       │          │
│  │  (Game View)     │  │  (Data Viz)      │  │  Dashboard       │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Controller (编排中心)

负责多智能体协作的核心调度。

```python
class Controller:
    """
    编排中心 - 多智能体协作的"大脑"
    """
    
    def __init__(self):
        self.scenario_manager = ScenarioManager()
        self.workflow_engine = WorkflowEngine()
        self.topology_manager = TopologyManager()
        self.memory_manager = MemoryManager()
    
    async def run_simulation(self, scenario: Scenario) -> Session:
        """
        运行模拟
        
        流程:
        1. 初始化场景
        2. 设置拓扑结构
        3. 启动工作流
        4. 循环执行直到结束条件
        """
        # 初始化
        session = Session(scenario)
        topology = self.topology_manager.create(scenario.topology)
        
        # 主循环
        while not self.should_stop(session):
            # 选择下一个发言者
            next_agent = self.select_next_agent(session, topology)
            
            # 获取上下文
            context = self.build_context(session, next_agent)
            
            # 生成回复
            message = await next_agent.generate(context)
            
            # 存储消息
            session.add_message(message)
            
            # 更新记忆
            self.memory_manager.update(next_agent, message)
            
            # 通知观察者
            await self.notify_observers(session, message)
        
        return session
    
    def select_next_agent(self, session: Session, topology: Topology) -> Agent:
        """
        选择下一个发言者
        
        策略:
        - Round Robin: 轮询
        - Dynamic: 基于内容动态选择
        - Role-based: 基于角色分配
        - Random: 随机选择
        """
        orchestrator = self.get_orchestrator(session.config)
        return orchestrator.select(session, topology)
```

### 2. Agent Service

单个智能体的服务封装。

```python
class Agent:
    """
    智能体 - 独立的LLM + 记忆 + 能力
    """
    
    def __init__(self, config: AgentConfig):
        self.name = config.name
        self.role = config.role
        self.system_prompt = config.system_prompt
        self.model = config.model
        
        # 记忆系统
        self.short_term_memory = []
        self.long_term_memory = ChromaDB(config.memory_config)
        
        # 能力
        self.capabilities = config.capabilities
    
    async def generate(self, context: Context) -> Message:
        """
        生成回复
        
        Args:
            context: 包含对话历史、相关记忆、环境信息等
            
        Returns:
            Message: 生成的消息
        """
        # 构建提示词
        prompt = self.build_prompt(context)
        
        # 调用LLM
        response = await self.model.generate(prompt)
        
        # 后处理
        content = self.post_process(response)
        
        return Message(
            agent=self.name,
            content=content,
            metadata={
                "model": self.model.name,
                "temperature": self.model.temperature
            }
        )
    
    def build_prompt(self, context: Context) -> str:
        """构建提示词"""
        parts = [
            f"You are {self.name}, a {self.role}.",
            self.system_prompt,
            "\n=== Relevant Memories ===",
            self.retrieve_memories(context),
            "\n=== Conversation History ===",
            format_history(context.messages),
            "\n=== Your Turn ===",
            "Respond as your character:"
        ]
        return "\n\n".join(parts)
    
    def retrieve_memories(self, context: Context) -> str:
        """检索相关记忆"""
        query = context.last_message.content
        memories = self.long_term_memory.search(query, k=5)
        return "\n".join(m.content for m in memories)
```

### 3. Topology Manager (拓扑管理)

管理智能体之间的通信拓扑。

```python
class TopologyManager:
    """拓扑管理器"""
    
    def create(self, topology_type: str, agents: List[Agent]) -> Topology:
        """创建拓扑"""
        if topology_type == "star":
            return StarTopology(agents)
        elif topology_type == "chain":
            return ChainTopology(agents)
        elif topology_type == "circle":
            return CircleTopology(agents)
        elif topology_type == "fully_connected":
            return FullyConnectedTopology(agents)
        else:
            return CustomTopology(agents, topology_type)
    
    def get_neighbors(self, agent: Agent, topology: Topology) -> List[Agent]:
        """获取相邻智能体"""
        return topology.get_neighbors(agent)


class StarTopology(Topology):
    """星型拓扑 - 中心节点协调"""
    
    def __init__(self, agents: List[Agent]):
        # 第一个agent作为中心
        self.center = agents[0]
        self.peripherals = agents[1:]
    
    def get_neighbors(self, agent: Agent) -> List[Agent]:
        if agent == self.center:
            return self.peripherals
        else:
            return [self.center]
    
    def get_next_speaker(self, current: Agent, round_robin: bool = True) -> Agent:
        if current == self.center:
            # 中心节点发言后，轮到外围节点
            idx = self.peripherals.index(self.last_peripheral) if hasattr(self, 'last_peripheral') else -1
            next_idx = (idx + 1) % len(self.peripherals)
            self.last_peripheral = self.peripherals[next_idx]
            return self.last_peripheral
        else:
            # 外围节点发言后，回到中心
            return self.center
```

### 4. Memory Manager (记忆管理)

管理智能体的短期和长期记忆。

```python
class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, vector_db: ChromaDB):
        self.vector_db = vector_db
        self.short_term_limit = 10
    
    def add_to_short_term(self, agent: Agent, message: Message):
        """添加到短期记忆"""
        agent.short_term_memory.append(message)
        
        # 限制容量
        if len(agent.short_term_memory) > self.short_term_limit:
            # 将旧记忆转移到长期记忆
            old_memories = agent.short_term_memory[:-self.short_term_limit]
            agent.short_term_memory = agent.short_term_memory[-self.short_term_limit:]
            
            for mem in old_memories:
                self.add_to_long_term(agent, mem)
    
    def add_to_long_term(self, agent: Agent, message: Message):
        """添加到长期记忆"""
        # 生成embedding
        embedding = embed(message.content)
        
        # 存储到向量数据库
        self.vector_db.add(
            collection=agent.name,
            documents=[message.content],
            embeddings=[embedding],
            metadatas=[{
                "timestamp": message.timestamp,
                "agent": message.agent
            }]
        )
    
    def retrieve(self, agent: Agent, query: str, k: int = 5) -> List[str]:
        """检索相关记忆"""
        query_embedding = embed(query)
        
        results = self.vector_db.search(
            collection=agent.name,
            query_embedding=query_embedding,
            n_results=k
        )
        
        return [r.document for r in results]
```

### 5. Workflow Engine (工作流引擎)

支持复杂的多阶段工作流。

```python
class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self):
        self.stages = []
    
    def add_stage(self, stage: Stage):
        """添加阶段"""
        self.stages.append(stage)
    
    async def execute(self, session: Session) -> Session:
        """执行工作流"""
        for stage in self.stages:
            # 执行阶段
            await stage.execute(session)
            
            # 检查阶段完成条件
            if not stage.is_complete(session):
                # 重试或等待
                await stage.wait_for_completion(session)
        
        return session


class Stage:
    """工作流阶段"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.agents = config.get("agents", [])
        self.duration = config.get("duration")
        self.parallel = config.get("parallel", False)
    
    async def execute(self, session: Session):
        """执行阶段"""
        if self.parallel:
            # 并行执行
            tasks = [agent.generate(session.context) for agent in self.agents]
            messages = await asyncio.gather(*tasks)
        else:
            # 顺序执行
            messages = []
            for agent in self.agents:
                msg = await agent.generate(session.context)
                messages.append(msg)
                session.add_message(msg)
    
    def is_complete(self, session: Session) -> bool:
        """检查是否完成"""
        if self.duration:
            return session.current_round >= self.duration
        return True
```

## 数据流

```
User Request
    │
    ▼
┌─────────────┐
│ API Gateway │  ← 认证、限流、路由
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Controller │  ← 创建Session，初始化Scenario
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Session   │  ← 维护对话状态
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Topology  │  ← 确定通信拓扑
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Orchestrator│  ← 选择下一个Agent
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Agent    │  ← 生成回复
│   (LLM)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Memory    │  ← 更新记忆
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Storage   │  ← 持久化
└──────┬──────┘
       │
       ▼
    Response
```

## 扩展点

### 1. 自定义编排器

```python
class CustomOrchestrator(Orchestrator):
    """自定义编排策略"""
    
    def select_next_agent(self, session: Session, topology: Topology) -> Agent:
        # 实现自定义选择逻辑
        pass
```

### 2. 自定义拓扑

```python
class CustomTopology(Topology):
    """自定义拓扑结构"""
    
    def get_neighbors(self, agent: Agent) -> List[Agent]:
        # 实现自定义邻居关系
        pass
```

### 3. 自定义Agent能力

```python
class ToolUsingAgent(Agent):
    """支持工具使用的Agent"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tools = config.tools
    
    async def generate(self, context: Context) -> Message:
        # 分析是否需要使用工具
        if self.should_use_tool(context):
            tool_result = await self.execute_tool(context)
            context.add_tool_result(tool_result)
        
        return await super().generate(context)
```

## 部署架构

```
Production Deployment

┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
│                    (Nginx / Traefik)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌───────┐     ┌───────┐     ┌───────┐
│API 1  │     │API 2  │     │API 3  │
│(FastAPI)│    │(FastAPI)│    │(FastAPI)│
└───┬───┘     └───┬───┘     └───┬───┘
    │             │             │
    └─────────────┼─────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐    ┌───────┐    ┌───────┐
│Worker 1│    │Worker 2│    │Worker 3│
└───┬───┘    └───┬───┘    └───┬───┘
    │            │            │
    └────────────┼────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌───────┐   ┌───────┐   ┌───────┐
│ChromaDB│   │ Redis │   │ PostgreSQL│
└───────┘   └───────┘   └───────┘
```

## 性能考虑

1. **并发处理**: 使用 asyncio 处理多个会话
2. **缓存**: Redis 缓存频繁访问的数据
3. **向量检索**: ChromaDB 支持快速相似度搜索
4. **流式响应**: WebSocket / SSE 支持实时推送
5. **水平扩展**: 无状态设计支持多实例部署
