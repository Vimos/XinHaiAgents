---
name: suicide-risk-evidence
description: Suicide Risk Evidence Extractor - CLPsych 2024 Shared Task 实现。基于 XinHai Healthcare-oriented LLM (ChatGLM3-6B医疗微调)，从社交媒体/论坛帖子中自动提取自杀风险证据（Evidence Highlights）并生成风险摘要。支持6维度评估（情绪、认知、行为动机、社会支持、精神健康问题、情境风险因素），提供phrase-level和sentence-level两种提取粒度。当用户需要：1) 自动识别社交媒体帖子中的自杀风险信号 2) 从文本中提取自杀相关证据片段 3) 生成风险等级判定摘要 4) 心理健康监测和预警 5) Reddit r/SuicideWatch类帖子分析时触发。
---

# Suicide Risk Evidence Extractor

CLPsych 2024 Shared Task 实现：基于 XinHai-6B 的自杀风险证据提取与摘要生成。

## 核心功能

### 1. 风险证据提取 (Evidence Highlights)

从用户帖子中提取与自杀风险相关的原文片段(text spans)，支持：
- **Phrase-level**: 精准定位关键短语（Weighted Recall更高）
- **Sentence-level**: 捕获完整上下文（F1更高）

### 2. 风险摘要生成 (Summarized Evidence)

基于提取的证据生成风险判定解释，包含：
- 风险等级判定依据
- 6维度风险评估总结
- 关键证据综合描述

### 3. 六维度风险识别

| 维度 | 识别内容 |
|------|---------|
| **Emotions** | 悲伤、绝望、难以忍受的心理痛苦 |
| **Cognitions** | 自杀想法频率、意图、计划 |
| **Behaviour** | 自杀相关行为、应对能力、动机变化 |
| **Interpersonal** | 社会支持、关系稳定性 |
| **Mental Health** | 精神疾病史、自伤/自杀未遂史 |
| **Context** | 社会经济因素、创伤暴露史、慢性病 |

## 系统架构

```
用户输入帖子
    ↓
┌─────────────────────────────────────────────┐
│  Module 1: 风险证据提取 (XinHai-6B LLM)      │
│  • CoT Prompt (6维度分析)                    │
│  • GPT-4优化提示词                          │
│  • One-shot JSON格式约束                    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Module 2: 证据匹配对齐 (Evidence Aligner)   │
│  • Spacy语义向量匹配                        │
│  • 余弦相似度计算                           │
│  • 正则修复截断/变形文本                     │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│  Module 3: 摘要生成 (XinHai-6B LLM)          │
│  • 整合多帖证据                              │
│  • 生成风险判定摘要                          │
└─────────────────────────────────────────────┘
    ↓
结构化输出 (Evidence Highlights + Summary)
```

## 快速开始

### 基础用法

```python
from suicide_risk_evidence import SuicideRiskExtractor

# 初始化提取器
extractor = SuicideRiskExtractor(
    model_path="XinHai-6B",
    granularity="phrase",  # "phrase" 或 "sentence"
    language="en"
)

# 分析单条帖子
result = extractor.analyze_post(
    title="I can't do this anymore",
    body="I've been struggling for years. Nothing seems to help. I feel like a burden to everyone around me..."
)

print(result)
```

输出示例：
```json
{
  "risk_level": "High Risk",
  "evidence_highlights": [
    {
      "text": "I can't do this anymore",
      "start_char": 0,
      "end_char": 24,
      "criteria": ["Emotions", "Cognitions"]
    },
    {
      "text": "I feel like a burden to everyone",
      "start_char": 89,
      "end_char": 121,
      "criteria": ["Cognitions", "Interpersonal"]
    }
  ],
  "summary": "User expresses severe emotional distress with feelings of hopelessness and burden. Evidence indicates high suicide risk due to persistent negative cognitions and perceived lack of social support.",
  "confidence": 0.92
}
```

### 多帖用户分析

```python
# 分析同一用户的多条帖子
posts = [
    {"post_id": "p1", "title": "First post", "body": "..."},
    {"post_id": "p2", "title": "Update", "body": "..."}
]

result = extractor.analyze_user_posts(
    user_id="u12345",
    posts=posts
)

# 每条帖子单独高亮证据，但生成单一综合摘要
```

### 批量处理

```python
# 批量分析多个用户
dataset = [
    {"user_id": "u1", "posts": [...]},
    {"user_id": "u2", "posts": [...]}
]

results = extractor.batch_analyze(
    dataset,
    batch_size=4,
    output_file="results.json"
)
```

## 评估指标

| 指标 | 说明 | 论文结果 (v4-phrase) |
|-----|------|---------------------|
| **Recall** | 专家证据捕获程度 | 0.868 |
| **Precision** | 提取证据准确性 | 0.884 |
| **Weighted Recall** | 证据长度适当性 | 0.807 |
| **Harmonic Mean (F1)** | P/R平衡 | 0.876 |
| **Consistency** | 摘要与专家一致性 | 0.956 |
| **Contradiction** | 摘要矛盾程度 | 0.132 |

## 配置选项

```python
config = {
    # 模型配置
    "model_path": "XinHai-6B",  # 本地模型路径
    "device": "cuda",  # cuda 或 cpu
    "max_length": 4096,
    "temperature": 0.3,  # 低温度确保稳定输出
    
    # 提取配置
    "granularity": "phrase",  # "phrase" 或 "sentence"
    "similarity_threshold": 0.85,  # 语义匹配阈值
    "max_span_length": 500,  # 最大片段长度
    
    # Spacy配置
    "spacy_model": "en_core_web_md",  # 英文
    # "spacy_model": "zh_core_web_md",  # 中文
    
    # 输出配置
    "include_summary": True,
    "output_language": "en"
}

extractor = SuicideRiskExtractor(config=config)
```

## 参考文件

- **框架实现**: `references/framework.md`
- **提示词模板**: `assets/prompts/cot_gpt4_optimized.json`
- **6维度评估标准**: `references/criteria.md`
- **评估脚本**: `scripts/evaluate.py`
- **批量处理**: `scripts/batch_process.py`

## 数据来源

- **CLPsych 2024 Shared Task**: UMD Suicidality Dataset v2 (Reddit r/SuicideWatch)
- **风险等级**: Low Risk / Moderate Risk / High Risk (专家标注)
- **论文**: XinHai@CLPsych 2024 - "Prompting Healthcare-oriented LLMs for Evidence Highlighting in Posts with Suicide Risk"

## 伦理与隐私

⚠️ **重要提示**:
- 本系统仅用于研究和辅助筛查，**不能替代专业心理健康评估**
- 涉及敏感心理健康数据，请确保符合数据使用规范
- 建议人工审核系统输出，避免误判
- 如发现高自杀风险用户，请遵循当地危机干预流程

## 引用

```bibtex
@inproceedings{zhu2024xinhai,
  title={XinHai@CLPsych 2024 Shared Task: Prompting Healthcare-oriented LLMs for Evidence Highlighting in Posts with Suicide Risk},
  author={Zhu, Jingwei and Xu, Ancheng and Tan, Minghuan and Yang, Min},
  booktitle={Proceedings of the 9th Workshop on Computational Linguistics and Clinical Psychology (CLPsych 2024)},
  pages={238--246},
  year={2024}
}
```
