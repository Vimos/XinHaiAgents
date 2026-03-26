---
name: xinhai-agents
description: XinHaiAgents - "心海"多智能体模拟与进化框架的OpenClaw封装。支持多模态多智能体场景模拟、动态拓扑编排、可视化交互。当用户需要：1) 创建多智能体模拟场景（辩论、谈判、心理咨询等）2) 编排多智能体协作工作流 3) 可视化展示智能体交互过程 4) 评估智能体对话质量 5) 快速原型验证多智能体应用时触发。保留与XinHaiAgents后端的无缝集成能力，支持场景模板扩展、自定义编排策略、多模态输入输出。
---

# XinHaiAgents Skill - 心海多智能体框架

XinHai (心海): Sea of Minds Framework for Multimodal Multi-agent Simulation and Evolution

## 核心能力

### 1. 多智能体场景模拟

```python
# 快速启动一个心理咨询模拟
scenario = xinhai.create_scenario("therapy_session")
scenario.add_agent("therapist", role="CBT_therapist")
scenario.add_agent("patient", role="anxious_patient")
result = scenario.run(rounds=10)
```

### 2. 动态编排工作流

```python
# 创建复杂的辩论流程
workflow = xinhai.create_workflow("debate")
workflow.add_stage("opening", duration=3)
workflow.add_stage("cross_examination", agents=["agent_a", "agent_b"])
workflow.add_stage("closing", parallel=False)
```

### 3. 可视化交互

```python
# 生成可视化数据
viz_data = xinhai.visualize(session_id)
# 返回网络图、对话流、情感变化等数据
```

### 4. 评估与优化

```python
# 评估模拟效果
metrics = xinhai.evaluate(session_id)
# 对话连贯性、目标达成度、多样性等
```

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenClaw Platform                            │
│  ├─ Discord/Telegram Bot Interface                              │
│  ├─ Session Management                                          │
│  └─ Skill Orchestration                                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ API / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                  XinHaiAgents Backend                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ Controller  │ │   Bridge    │ │    LLM      │ │  Storage   │ │
│  │  (编排中心)  │ │  (API网关)  │ │ (模型服务)  │ │ (向量存储)  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     Frontend (可选)                              │
│  ├─ Vue 3 + Phaser (游戏化可视化)                                │
│  ├─ React + D3 (数据可视化)                                      │
│  └─ Real-time Dashboard (实时监控)                               │
└─────────────────────────────────────────────────────────────────┘
```

## 快速开始

### 基础用法

```python
from xinhai_agents import XinHaiSkill

# 初始化
xinhai = XinHaiSkill(
    backend_url="http://localhost:8000",
    api_key="your_api_key"
)

# 创建模拟场景
session = xinhai.simulate(
    scenario="group_therapy",
    agents=[
        {"name": "therapist", "role": "CBT_counselor"},
        {"name": "patient1", "role": "depressed_patient"},
        {"name": "patient2", "role": "anxious_patient"}
    ],
    rounds=5,
    config={
        "topology": "star",  # star, chain, fully_connected
        "memory_type": "chromadb",
        "enable_visualization": True
    }
)

# 获取结果
print(f"Session ID: {session.id}")
print(f"Messages: {len(session.messages)}")
print(f"Metrics: {session.metrics}")
```

### 场景模板

```python
# 使用预置场景
session = xinhai.load_scenario("suicide_intervention")
# 内置场景：心理咨询、自杀干预、认知行为治疗、群体讨论等

# 自定义场景
custom = xinhai.create_scenario({
    "name": "family_therapy",
    "description": "家庭治疗模拟",
    "agents": ["father", "mother", "teenager", "therapist"],
    "topology": "circle",
    "rules": [...]
})
```

### 与 Discord Bot 集成

```python
# 在 Discord 中启动模拟
@bot.command()
async def simulate(ctx, scenario: str, *agent_names):
    """启动多智能体模拟"""
    session = xinhai.simulate(
        scenario=scenario,
        agents=[{"name": name} for name in agent_names]
    )
    
    # 实时推送结果
    for msg in session.stream():
        await ctx.send(f"**{msg.agent}**: {msg.content}")
```

## 扩展点设计

### 1. 场景模板扩展

```python
# 添加自定义场景
xinhai.register_scenario({
    "name": "peer_counseling",
    "description": "朋辈心理咨询",
    "agents": [
        {"role": "peer_counselor", "system_prompt": "..."},
        {"role": "seeker", "system_prompt": "..."}
    ],
    "topology": "one_to_one",
    "evaluation_metrics": ["empathy", "helpfulness"]
})
```

### 2. 编排策略扩展

```python
# 自定义编排策略
class TherapyOrchestrator(xinhai.Orchestrator):
    def next_speaker(self, context):
        # 根据治疗阶段决定下一个发言者
        if context.stage == "assessment":
            return "therapist"
        elif context.stage == "intervention":
            return context.last_speaker
```

### 3. 评估指标扩展

```python
# 添加自定义评估
xinhai.register_metric("therapeutic_alliance", {
    "description": "治疗联盟强度",
    "compute": lambda messages: compute_alliance(messages),
    "threshold": 0.7
})
```

### 4. 可视化扩展

```python
# 自定义可视化
viz_config = {
    "type": "network_graph",
    "layout": "force_directed",
    "node_color_by": "agent_role",
    "edge_weight_by": "interaction_frequency",
    "animations": True
}
xinhai.visualize(session_id, config=viz_config)
```

## 高级功能

### 多模态支持

```python
# 支持图像、音频输入
session = xinhai.simulate(
    scenario="art_therapy",
    agents=["therapist", "patient"],
    multimodal=True,  # 启用多模态
    inputs=[
        {"type": "image", "content": "drawing.png"},
        {"type": "text", "content": "描述你的画作..."}
    ]
)
```

### 长期记忆与进化

```python
# 启用长期记忆
session = xinhai.simulate(
    scenario="long_term_therapy",
    memory_config={
        "type": "chromadb",
        "collection": "patient_history",
        "retrieval_k": 5
    }
)

# 智能体进化
xinhai.evolve(
    agent_id="therapist_001",
    feedback="positive",
    learning_rate=0.01
)
```

### 对抗与协作

```python
# 对抗场景
debate = xinhai.simulate(
    scenario="debate",
    agents=[
        {"name": "affirmative", "stance": "pro"},
        {"name": "negative", "stance": "con"}
    ],
    mode="adversarial"
)

# 协作场景
team = xinhai.simulate(
    scenario="problem_solving",
    agents=["planner", "executor", "critic"],
    mode="collaborative"
)
```

## 应用场景

### 情感支持对话研究

```python
# 评估不同咨询策略
strategies = ["CBT", "psychodynamic", "humanistic"]
results = {}

for strategy in strategies:
    session = xinhai.simulate(
        scenario="therapy",
        agent_config={"therapist": {"approach": strategy}},
        test_cases=load_test_cases()
    )
    results[strategy] = xinhai.evaluate(session)

# 对比分析
compare_strategies(results)
```

### 自杀风险干预训练

```python
# 模拟危机干预
crisis = xinhai.load_scenario("suicide_intervention")
crisis.set_risk_level("high")
crisis.set_patient_profile({
    "age": 25,
    "history": "previous_attempt",
    "triggers": ["relationship_loss"]
})

# 训练干预技能
for i in range(100):
    result = crisis.run()
    if result.safety_outcome == "positive":
        crisis.reward()
```

### 多智能体评估基准

```python
# 创建评估基准
benchmark = xinhai.create_benchmark({
    "name": "therapy_quality",
    "metrics": ["empathy", "safety", "effectiveness"],
    "test_cases": load_therapy_cases(),
    "baseline": "human_therapist"
})

# 运行评估
scores = benchmark.run(agent_config={...})
benchmark.report()
```

## API 参考

### 核心类

- `XinHaiSkill` - 主入口类
- `Scenario` - 场景定义
- `Agent` - 智能体配置
- `Session` - 模拟会话
- `Orchestrator` - 编排器
- `Evaluator` - 评估器

### 配置选项

```python
config = {
    # 后端连接
    "backend_url": "http://localhost:8000",
    "api_key": "...",
    "timeout": 300,
    
    # 模型配置
    "llm_model": "xinhai-6b",
    "embedding_model": "bge-large",
    "device": "cuda",
    
    # 存储配置
    "vector_store": "chromadb",
    "persist_directory": "./chroma_db",
    
    # 可视化配置
    "enable_viz": True,
    "viz_update_interval": 1.0,
    
    # 评估配置
    "auto_evaluate": True,
    "evaluation_metrics": ["coherence", "diversity", "goal_achievement"]
}
```

## 参考文档

- **架构设计**: `references/architecture.md`
- **场景模板**: `assets/scenarios/`
- **API文档**: `references/api.md`
- **集成指南**: `references/integration.md`
- **扩展开发**: `references/extension.md`

## 依赖

```bash
# 基础依赖
pip install fastapi uvicorn langchain chromadb

# 多模态支持
pip install transformers pillow torch

# 可视化
pip install vue-cli-service phaser

# 评估工具
pip install bert-score nltk
```

## 开源协议

Apache 2.0 - 参考了 AgentVerse, LLaMA-Factory, MGM, FlashRAG

## 引用

```bibtex
@software{xinhai_agents,
  title={XinHaiAgents: Sea of Minds Framework},
  author={Xu, Ancheng and Zhu, Jingwei and Tan, Minghuan and Yang, Min},
  year={2024},
  url={https://github.com/Vimos/XinHaiAgents}
}
```
