# XinHaiAgents Skill - Quick Start

## 安装

```bash
# 1. 安装依赖
pip install aiohttp websockets

# 2. 启动 XinHaiAgents 后端
# 参见: https://github.com/Vimos/XinHaiAgents

# 3. 加载 Skill
openclaw skill install xinhai-agents.skill
```

## 快速开始

### 基础用法

```python
from xinhai_agents import XinHaiSkill

# 初始化
xinhai = XinHaiSkill({
    'backend_url': 'http://localhost:8000',
    'api_key': 'your_key'
})

# 创建模拟
session = xinhai.simulate(
    scenario='therapy_session',
    agents=[
        {'name': 'therapist', 'role': 'CBT_counselor'},
        {'name': 'patient', 'role': 'anxious_patient'}
    ],
    rounds=10
)

print(f'Session: {session.id}')
print(f'Messages: {len(session.messages)}')
```

### 使用场景模板

```python
# 加载预置场景
scenario = xinhai.load_scenario('suicide_intervention')
scenario.add_agent('counselor', 'crisis_counselor')
scenario.add_agent('individual', 'at_risk_individual')
session = scenario.run(rounds=5)

# 查看评估
metrics = xinhai.evaluate(session.id)
print(metrics)
```

### Discord Bot 集成

```python
from xinhai_agents import XinHaiSkill, DiscordIntegration

xinhai = XinHaiSkill(config)
integration = DiscordIntegration(xinhai, bot)

# 命令: /simulate therapy_session therapist patient
@bot.command()
async def simulate(ctx, scenario, *agents):
    await integration.handle_simulate_command(ctx, scenario, *agents)
```

## 内置场景

| 场景 | 描述 | 智能体 |
|-----|------|--------|
| therapy_session | 一对一心理咨询 | therapist, patient |
| group_therapy | 团体治疗 | therapist, patients (3) |
| suicide_intervention | 危机干预 | counselor, individual |
| peer_counseling | 朋辈咨询 | peer_counselor, seeker |
| family_therapy | 家庭治疗 | therapist, father, mother, teenager |
| debate | 结构化辩论 | affirmative, negative, moderator |
| negotiation | 多方谈判 | party_a, party_b, mediator |

## API 参考

```python
# 核心方法
xinhai.simulate(scenario, agents, rounds, config)
xinhai.load_scenario(name) -> ScenarioBuilder
xinhai.create_scenario(config) -> ScenarioBuilder
xinhai.visualize(session_id, config) -> dict
xinhai.evaluate(session_id, metrics) -> dict

# 会话管理
xinhai.get_session(session_id) -> Session
xinhai.list_sessions() -> list

# 扩展
xinhai.register_scenario(name, config)
xinhai.register_orchestrator(name, class)
xinhai.register_metric(name, config)
```

## 配置选项

```python
config = {
    'backend_url': 'http://localhost:8000',
    'api_key': '',
    'timeout': 300,
    'max_rounds': 20,
    'default_topology': 'star',
    'default_orchestrator': 'dynamic',
    'enable_visualization': True,
    'enable_evaluation': True
}
```

## 参考文档

- [架构设计](references/architecture.md)
- [集成指南](references/integration.md)
- [场景模板](assets/scenarios/builtin_scenarios.json)

## 引用

```bibtex
@software{xinhai_agents,
  title={XinHaiAgents: Sea of Minds Framework},
  author={Xu, Ancheng and Zhu, Jingwei and Tan, Minghuan and Yang, Min},
  year={2024},
  url={https://github.com/Vimos/XinHaiAgents}
}
```
