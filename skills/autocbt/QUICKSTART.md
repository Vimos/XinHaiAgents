# AutoCBT Skill 快速开始

## 安装

```bash
# 克隆或使用 skill 文件
openclaw skill install autocbt.skill
```

## 基础使用

```python
from autocbt import AutoCBTFramework

# 初始化框架
autocbt = AutoCBTFramework(
    model="gpt-4",  # 或 Qwen-2.5-72B, Llama-3.1-70B
    language="zh",  # "zh" 或 "en"
    temperature=0.98
)

# 进行咨询
response = autocbt.consult("我最近总是很焦虑...")
print(response)
```

## 带认知扭曲识别

```python
result = autocbt.consult_with_cd_detection(
    "我总觉得自己一无是处...",
    return_cd=True
)

print(result['response'])
print(f"识别的认知扭曲: {result['cognitive_distortion']}")
```

## 自定义配置

```python
# 启用特定监督者
autocbt.configure_supervisors([
    "empathy",
    "identify",
    "strategy"
])

# 获取路由历史
history = autocbt.get_routing_history()
for h in history:
    print(f"路由 {h['count']}: {h['strategy']} -> {h['targets']}")
```

## 评估

```bash
# 评估模型性能
python scripts/evaluate.py \
    --input test_data.json \
    --method autocbt \
    --output results.json \
    --rounds 3
```

## 参考文献

- Xu et al. "AutoCBT: An Autonomous Multi-agent Framework for Cognitive Behavioral Therapy in Psychological Counseling" (2025)
- Beck, J.S. "Cognitive Behavior Therapy: Basics and Beyond" (2020)
