---
name: autocbt
description: AutoCBT - 认知行为疗法导向的自主多智能体心理咨询框架。基于论文《AutoCBT: An Autonomous Multi-agent Framework for Cognitive Behavioral Therapy in Psychological Counseling》实现。支持动态路由、监督机制、CBT核心原则指导的回应生成。当用户需要：1) 构建AI心理咨询系统 2) 实现CBT技术自动化 3) 多智能体情感支持对话 4) 认知扭曲识别与干预 5) 双语心理咨询回复生成时触发。
---

# AutoCBT Skill

基于论文的自主多智能体CBT心理咨询框架。

## 核心架构

### 四元组定义
AutoCBT = (a₀, S, T, Σ)

| 组件 | 说明 |
|-----|------|
| a₀ | 咨询师智能体（Counsellor Agent） |
| S | 监督智能体集合 {a₁, a₂, ..., aₙ} |
| T | 智能体通信拓扑 |
| Σ | 路由策略集合 |

### 5大CBT核心原则（监督者）

| 编号 | 原则 | 监督者职责 |
|-----|------|-----------|
| 1 | Validation and Empathy | 验证与共情：理解用户情绪，创造安全感 |
| 2 | Identify Key Thought | 识别关键想法：发现用户认知扭曲 |
| 3 | Pose Challenge | 提出挑战：用开放性问题促反思 |
| 4 | Provide Strategy | 提供策略：给出实用解决方案 |
| 5 | Encouragement | 鼓励与预见：鼓励行动并预见困难 |

### 5种路由策略

- **LOOPBACK**: 回环，继续当前处理
- **UNICAST**: 单播，发送给特定监督者
- **MULTICAST**: 组播，发送给多个监督者
- **BROADCAST**: 广播，发送给所有监督者
- **ENDCAST**: 终止，结束咨询返回最终回应

## 工作流程

```
用户输入
    ↓
咨询师 Agent → 动态路由决策
    ├──→ 直接回应 → ENDCAST → 最终回应
    └──→ 咨询监督者
            ↓
        起草回应 → 发送给监督者
            ↓
        接收建议 → 学习改进
            ↓
        重新进入路由决策
```

## 使用方式

### 基础用法：单次咨询

```python
from autocbt import AutoCBTFramework

# 初始化框架
autocbt = AutoCBTFramework(
    model="gpt-4",  # 或 Qwen-2.5-72B, Llama-3.1-70B
    language="zh",  # "zh" 或 "en"
    temperature=0.98
)

# 进行咨询
response = autocbt.consult(
    user_query="我最近总是很焦虑，工作上压力很大..."
)
print(response)
```

### 带认知扭曲识别的咨询

```python
# 自动识别认知扭曲类型
response = autocbt.consult_with_cd_detection(
    user_query="我总觉得自己一无是处...",
    return_cd_type=True  # 返回识别的认知扭曲类型
)

# 输出: {"response": "...", "cognitive_distortion": "labeling"}
```

### 自定义监督者配置

```python
# 启用/禁用特定监督者
autocbt.configure_supervisors([
    "empathy",      # 必须
    "identify",     # 可选
    # "challenge",  # 禁用
    "strategy",
    "encouragement"
])

# 调整路由策略
autocbt.set_routing_strategy("adaptive")  # adaptive, aggressive, conservative
```

## 认知扭曲类型（基于Beck理论）

1. **Catastrophizing** (灾难化)：想象最坏情况
2. **Labeling** (贴标签)：给自己/他人贴负面标签
3. **Minimizing** (最小化)：忽视积极方面
4. **All-or-Nothing** (全或无)：非黑即白的思维
5. **Overgeneralization** (过度概括)：从单一事件推断普遍规律
6. **Mind Reading** (读心术)：假设知道他人想法
7. **Emotional Reasoning** (情绪推理)：把感受当事实
8. **Should Statements** (应该陈述）：对自己/他人有不切实际的期望
9. **Personalization** (个人化)：把无关事件归咎于自己
10. **Discounting Positives** (否定积极)：拒绝接受正面经验

## 评估指标

自动评估6个维度（1-7分）：

| 维度 | 评估内容 |
|-----|---------|
| Empathy | 共情理解 |
| Identification | 认知扭曲识别 |
| Reflection | 反思提问 |
| Strategy | 策略实用性 |
| Encouragement | 鼓励行动 |
| Relevance | 相关性 |

## 参考文件

- **框架实现**: 见 `references/framework.md`
- **提示词模板**: 见 `references/prompts.md`
- **评估工具**: 见 `scripts/evaluate.py`
- **数据集格式**: 见 `references/dataset.md`

## 示例

```python
# 完整示例：中英双语CBT咨询
from autocbt import AutoCBTFramework

# 中文咨询
autocbt_zh = AutoCBTFramework(language="zh")
response_zh = autocbt_zh.consult("我感觉自己活着没有意义...")

# 英文咨询
autocbt_en = AutoCBTFramework(language="en")
response_en = autocbt_en.consult(
    "I've been feeling really down lately and can't find joy in anything..."
)

# 评估回应质量
from autocbt.evaluation import AutoEvaluator
evaluator = AutoCBTFramework()
scores = evaluator.evaluate(response_zh, dimension="all")
```

## 注意事项

1. **模型选择**: Qwen 更适合中文场景（无过度保护问题）
2. **温度设置**: 建议 0.98 保持创造性同时避免重复
3. **伦理安全**: 涉及自杀/自伤/未成年人性问题时需人工介入
4. **不替代专业治疗**: 明确告知用户这是辅助工具
