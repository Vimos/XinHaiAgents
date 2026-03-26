# XinHaiAgents 与 OpenClaw 集成指南

## 概述

本指南介绍如何将 XinHaiAgents 集成到 OpenClaw 平台，实现：
- Discord/Telegram Bot 交互
- Session 管理和状态同步
- 实时消息推送
- 可视化展示

## 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                         │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Discord Bot     │  │  Telegram Bot    │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                           │
│           └──────────┬──────────┘                           │
│                      │                                      │
│           ┌──────────▼──────────┐                          │
│           │  OpenClaw Skill     │                          │
│           │  (xinhai-agents)    │                          │
│           └──────────┬──────────┘                          │
└──────────────────────┼──────────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                  XinHaiAgents Backend                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Controller │  │   Agents    │  │   Memory    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 快速集成

### 1. 配置 XinHaiAgents Backend

```bash
# 克隆仓库
git clone https://github.com/Vimos/XinHaiAgents.git
cd XinHaiAgents

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置后端地址、API密钥等

# 启动服务
docker-compose up -d
```

### 2. 配置 OpenClaw Skill

```python
# config.yaml
xinhai_agents:
  backend_url: "http://localhost:8000"
  api_key: "your_api_key"
  timeout: 300
  
  # Discord Bot 配置
  discord:
    enabled: true
    command_prefix: "/"
    
  # Telegram Bot 配置
  telegram:
    enabled: false
    
  # 可视化配置
  visualization:
    enabled: true
    update_interval: 1.0
```

### 3. 创建 Bot 命令

```python
# bot_commands.py
from openclaw import Bot
from xinhai_agents import XinHaiSkill, DiscordIntegration

bot = Bot()
xinhai = XinHaiSkill(config)
integration = DiscordIntegration(xinhai, bot)

@bot.command(name="simulate")
async def simulate(ctx, scenario: str, *agent_names):
    """启动多智能体模拟
    
    用法: /simulate <场景名> [智能体1] [智能体2] ...
    示例: /simulate therapy_session therapist patient
    """
    await integration.handle_simulate_command(ctx, scenario, *agent_names)

@bot.command(name="status")
async def status(ctx, session_id: str = None):
    """查看模拟状态
    
    用法: /status [会话ID]
    不指定ID则查看当前频道活动会话
    """
    await integration.handle_status_command(ctx, session_id)

@bot.command(name="visualize")
async def visualize(ctx, session_id: str = None):
    """生成可视化
    
    用法: /visualize [会话ID]
    """
    await integration.handle_visualize_command(ctx, session_id)

@bot.command(name="evaluate")
async def evaluate(ctx, session_id: str, *metrics):
    """评估模拟效果
    
    用法: /evaluate <会话ID> [指标1] [指标2] ...
    示例: /evaluate xhs_abc123 coherence diversity
    """
    session = xinhai.get_session(session_id)
    if not session:
        await ctx.send(f"❌ 会话不存在: {session_id}")
        return
    
    results = xinhai.evaluate(session_id, metrics if metrics else None)
    
    embed = {
        "title": f"评估结果: {session_id}",
        "fields": [
            {"name": k, "value": f"{v:.2f}", "inline": True}
            for k, v in results.items()
        ]
    }
    await ctx.send(embed=embed)

@bot.command(name="scenarios")
async def list_scenarios(ctx):
    """列出可用场景"""
    scenarios = xinhai.scenarios
    
    embed = {
        "title": "可用场景",
        "description": "使用 /simulate <场景名> 启动模拟",
        "fields": [
            {
                "name": name,
                "value": f"{info['description']}\nAgents: {', '.join(a['role'] for a in info['agents'])}",
                "inline": False
            }
            for name, info in scenarios.items()
        ]
    }
    await ctx.send(embed=embed)
```

## 高级集成

### 实时消息流

```python
# 使用 WebSocket 实时接收消息
import websockets
import json

async def stream_messages(session_id: str, callback):
    """实时流式接收消息"""
    uri = f"ws://localhost:8000/ws/{session_id}"
    
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            await callback(data)

# 在 Discord 中实现
@bot.command(name="stream")
async def stream_simulation(ctx, session_id: str):
    """实时流式查看模拟"""
    await ctx.send(f"🔴 开始实时流: {session_id}")
    
    async def on_message(data):
        agent = data.get('agent')
        content = data.get('content')
        await ctx.send(f"**{agent}**: {content}")
    
    await stream_messages(session_id, on_message)
```

### Session 状态同步

```python
# 在 OpenClaw 中维护 Session 状态
class SessionManager:
    """Session 管理器"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> Session
        self.channel_sessions = {}  # channel_id -> session_id
    
    def create_session(self, channel_id: str, scenario: str, agents: list) -> Session:
        """创建新会话"""
        session = xinhai.simulate(scenario, agents)
        self.sessions[session.id] = session
        self.channel_sessions[channel_id] = session.id
        return session
    
    def get_channel_session(self, channel_id: str) -> Optional[Session]:
        """获取频道当前会话"""
        session_id = self.channel_sessions.get(channel_id)
        return self.sessions.get(session_id) if session_id else None
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            # 清理 channel_sessions
            for ch_id, sid in list(self.channel_sessions.items()):
                if sid == session_id:
                    del self.channel_sessions[ch_id]

session_manager = SessionManager()
```

### 可视化集成

```python
# 生成可视化并发送到 Discord
@bot.command(name="viz")
async def visualize_command(ctx, session_id: str = None, viz_type: str = "network"):
    """生成并发送可视化
    
    viz_type: network, flow, timeline, emotion
    """
    if not session_id:
        session = session_manager.get_channel_session(str(ctx.channel.id))
        if not session:
            await ctx.send("❌ 当前频道没有活动会话")
            return
        session_id = session.id
    
    # 生成可视化数据
    viz_data = xinhai.visualize(session_id, {"type": viz_type})
    
    # 使用 matplotlib 生成图片
    import matplotlib.pyplot as plt
    import networkx as nx
    
    if viz_type == "network":
        G = nx.Graph()
        for node in viz_data["network_graph"]["nodes"]:
            G.add_node(node["id"], role=node["role"])
        for edge in viz_data["network_graph"]["edges"]:
            G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=1500, font_size=10, font_weight='bold')
        
        # 保存并发送
        plt.savefig(f"/tmp/viz_{session_id}.png")
        await ctx.send(file=discord.File(f"/tmp/viz_{session_id}.png"))
```

### 多模态支持

```python
# 支持图像输入
@bot.command(name="multimodal")
async def multimodal_simulate(ctx, scenario: str, *, description: str):
    """多模态模拟 - 支持图片
    
    用法: 上传图片并发送命令
    /multimodal art_therapy 描述你的画作
    """
    if not ctx.message.attachments:
        await ctx.send("❌ 请上传图片")
        return
    
    # 下载图片
    attachment = ctx.message.attachments[0]
    image_path = f"/tmp/{attachment.filename}"
    await attachment.save(image_path)
    
    # 创建多模态会话
    session = xinhai.simulate(
        scenario=scenario,
        agents=[{"name": "therapist"}, {"name": "patient"}],
        multimodal=True,
        inputs=[
            {"type": "image", "path": image_path},
            {"type": "text", "content": description}
        ]
    )
    
    await ctx.send(f"✅ 多模态会话已创建: {session.id}")
```

## 自定义扩展

### 添加自定义场景

```python
# 在 bot 启动时注册自定义场景
@bot.event
async def on_ready():
    # 注册自定义场景
    xinhai.register_scenario("custom_therapy", {
        "name": "自定义治疗",
        "description": "针对特定问题的治疗模拟",
        "agents": [
            {
                "role": "specialist",
                "system_prompt": "You are a specialist in..."
            },
            {
                "role": "client",
                "system_prompt": "You are seeking help for..."
            }
        ],
        "topology": "star",
        "evaluation_metrics": ["custom_metric"]
    })
    
    # 注册自定义编排器
    xinhai.register_orchestrator("my_orchestrator", MyCustomOrchestrator)
```

### 自定义评估指标

```python
# 添加治疗联盟评估
xinhai.register_metric("therapeutic_alliance", {
    "description": "治疗联盟强度",
    "compute": lambda messages: calculate_alliance(messages),
    "threshold": 0.7,
    "categories": ["poor", "fair", "good", "excellent"]
})

def calculate_alliance(messages):
    """计算治疗联盟强度"""
    # 基于消息内容分析
    # - 共情表达
    # - 合作意愿
    # - 目标一致性
    # ...
    return 0.75  # 示例返回值
```

## 故障排查

### 常见问题

1. **连接失败**
   ```bash
   # 检查后端服务
   curl http://localhost:8000/health
   
   # 检查防火墙
   sudo ufw allow 8000/tcp
   ```

2. **消息延迟**
   - 增加 WebSocket 连接数
   - 使用消息队列缓冲

3. **内存溢出**
   - 限制 Session 数量
   - 启用消息清理

### 日志监控

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xinhai_agents")

# 在关键位置添加日志
@bot.command(name="simulate")
async def simulate(ctx, *args):
    logger.info(f"Creating simulation: {args}")
    try:
        session = xinhai.simulate(*args)
        logger.info(f"Session created: {session.id}")
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise
```

## 最佳实践

1. **安全性**
   - 使用 API Key 认证
   - 限制请求频率
   - 过滤敏感内容

2. **性能优化**
   - 使用连接池
   - 启用缓存
   - 异步处理

3. **用户体验**
   - 提供进度反馈
   - 支持命令简化
   - 优雅处理错误

4. **监控告警**
   - 监控 Session 数量
   - 设置超时告警
   - 记录关键指标
