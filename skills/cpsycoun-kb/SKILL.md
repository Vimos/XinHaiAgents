---
name: cpsycoun-kb
description: CPsyCoun知识库 - 基于心理咨询报告的中文多轮对话重建与评估框架。包含Memo2Demo两阶段对话生成方法、9种咨询主题、7种经典咨询流派、四维评估体系。当用户需要：1) 中文心理咨询对话生成 2) 基于咨询报告的数据构建 3) 多轮对话自动评估 4) 专业咨询流派应用 5) 心理咨询数据集构建时触发。
---

# CPsyCoun 知识库

**论文**: CPsyCoun: A Report-based Multi-turn Dialogue Reconstruction and Evaluation Framework for Chinese Psychological Counseling  
**会议**: ACL 2024  
**作者**: Chenhao Zhang, Renhao Li, Minghuan Tan, Min Yang, et al.  
**代码**: https://github.com/CAS-SIAT-XinHai/CPsyCoun

## 核心贡献

CPsyCoun 是一个基于**心理咨询报告**的中文多轮对话重建与评估框架，解决了心理咨询领域数据稀缺和评估困难的问题。

## 核心问题

| 痛点 | 传统方法 | CPsyCoun方案 |
|-----|---------|-------------|
| 数据稀缺 | 依赖真实对话（隐私敏感） | 利用公开咨询报告重建对话 |
| 专业性不足 | LLM直接生成缺乏咨询知识 | Memo2Demo两阶段专业重建 |
| 评估困难 | 缺乏多轮对话评估标准 | 四维评估框架CPsyCounE |

## Memo2Demo 两阶段方法

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Memo2Demo Framework                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │   Phase 1        │      │   Phase 2        │            │
│  │ Memo Conversion  │ ───→ │ Demo Generation  │            │
│  │                  │      │                  │            │
│  │ 心理督导角色      │      │ 心理咨询师角色    │            │
│  │ • 提取关键信息    │      │ • 生成多轮对话    │            │
│  │ • 结构化笔记     │      │ • 遵循咨询框架    │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                         │                       │
│           ↓                         ↓                       │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  CPsyCounR       │      │  CPsyCounD       │            │
│  │  (Raw Reports)   │      │  (Dialogues)     │            │
│  │  3,134份报告     │      │  3,134条对话     │            │
│  └──────────────────┘      └──────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: Memo Conversion（咨询笔记转换）

**角色**: 心理督导 (Psychological Supervisor)

**输入**: 非结构化咨询报告

**输出**: 结构化咨询笔记

**包含内容**:
```
┌─────────────────────────────────────────┐
│           Counseling Note               │
├─────────────────────────────────────────┤
│ 1. 来访者基本情况                        │
│    - 人口学信息                          │
│    - 主诉问题                           │
│                                         │
│ 2. 来访者心理问题                        │
│    - 症状描述                           │
│    - 严重程度                           │
│    - 持续时间                           │
│                                         │
│ 3. 咨询方案                             │
│    - 咨询目标                           │
│    - 应用技术                           │
│    - 执行计划                           │
│                                         │
│ 4. 经验感想与反思                        │
│    - 咨询难点                           │
│    - 专业思考                           │
└─────────────────────────────────────────┘
```

**基座模型**: GLM-4

### Phase 2: Demo Generation（对话生成）

**角色**: 心理咨询师 (Psychological Counselor)

**输入**: 原始报告 + 咨询笔记

**输出**: 5-15轮多轮对话

**遵循框架**: 心理咨询四阶段

```
┌─────────────────────────────────────────────────────────────┐
│              心理咨询四阶段框架                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 1: 接待询问阶段                                        │
│  ├── 建立咨询关系                                            │
│  ├── 获取基本信息                                            │
│  ├── 了解咨询目的                                            │
│  └── 初步评估                                                │
│                                                              │
│  Phase 2: 诊断阶段                                           │
│  ├── 深入探索问题                                            │
│  ├── 分析根源和严重程度                                       │
│  ├── 心理评估                                                │
│  └── 初步诊断                                                │
│                                                              │
│  Phase 3: 咨询阶段                                           │
│  ├── 确认咨询目标                                            │
│  ├── 选择和应用技术                                           │
│  ├── 分步执行干预                                             │
│  └── 评估效果                                                │
│                                                              │
│  Phase 4: 巩固与结束阶段                                      │
│  ├── 回顾总结                                                │
│  ├── 自我反思训练                                            │
│  ├── 预防复发                                                │
│  └── 结束咨询                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 与基线方法对比

| 维度 | 直接角色扮演 | Memo2Demo | 提升 |
|-----|------------|-----------|------|
| **全面性** | 易遗漏信息 | 笔记确保完整 | +53% |
| **专业性** | 仅提及技术名 | 融入解决过程 | +53% |
| **真实性** | 缺乏情感互动 | 还原真实场景 | +30% |

## 数据集

### CPsyCounR（报告数据集）

| 属性 | 详情 |
|-----|------|
| 来源 | 壹点灵(Yidianling)、Psy525等公开平台 |
| 原始规模 | 4,700份报告 |
| 筛选后 | 3,134份高质量报告 |
| 隐私处理 | 规则清洗 + 人工改写 + 人工校对 |

**6个标准组件**:
1. **Title**: 案例摘要
2. **Type**: 咨询类型（230种细分类）
3. **Method**: 咨询方法（250+种）
4. **Case Brief**: 来访者基本信息和问题
5. **Consultation Process**: 咨询师第三人称描述（无具体对话）
6. **Experience Thoughts**: 咨询师经验反思

### CPsyCounD（对话数据集）

| 属性 | Memo2Demo | 基线方法 |
|-----|-----------|---------|
| 对话数量 | 3,134条 | - |
| 平均轮数 | 8.7轮 | 8.2轮 |
| 来访者平均长度 | 30.4字 | 24.5字 |
| 咨询师平均长度 | 49.7字 | 40.2字 |
| 总对话平均长度 | 622.3字 | 545.8字 |

## 九种咨询主题

| 主题 | 占比 | 说明 | 典型场景 |
|-----|------|------|---------|
| **婚恋情感** | 31% | 最大类别 | 恋爱困扰、婚姻矛盾、分手 recovery |
| **心理疾病** | 20% | 临床重点 | 抑郁症、焦虑症、强迫症 |
| **自我成长** | 14% | 发展性咨询 | 人格完善、潜能开发、自信建立 |
| **情绪压力** | 9% | 常见问题 | 情绪管理、压力应对、焦虑缓解 |
| **教育** | 9% | 亲子教育 | 亲子沟通、学业问题、青少年心理 |
| **家庭关系** | 9% | 系统问题 | 原生家庭、代际冲突、婆媳关系 |
| **社会关系** | 3% | 人际交往 | 社交恐惧、人际冲突、孤独感 |
| **性心理** | 3% | 敏感话题 | 性取向、性功能障碍、性心理困惑 |
| **职业发展** | 2% | 职场问题 | 职业规划、职场压力、职业倦怠 |

## 七种咨询流派

| 流派 | 占比 | 核心原理 | 代表技术 |
|-----|------|---------|---------|
| **认知行为疗法 (CBT)** | 26% | 认知影响情绪和行为 | 认知重构、行为实验、暴露疗法 |
| **精神分析疗法** | 16% | 潜意识冲突 | 自由联想、移情分析、梦的解析 |
| **其他疗法** | 21% | 未明确分类 | 多种技术混合 |
| **后现代疗法** | 13% | 主观建构现实 | 叙事疗法、焦点解决、合作对话 |
| **家庭治疗** | 12% | 系统观点 | 系统式家庭治疗、结构式家庭治疗 |
| **整合疗法** | 7% | 多流派整合 | 折衷主义、个性化方案 |
| **人本主义疗法** | 5% | 自我实现潜能 | 来访者中心疗法、真诚一致 |

### 流派特征对比

```python
therapy_schools = {
    "CBT": {
        "focus": "当前问题、具体目标",
        "duration": "短程（6-20次）",
        "techniques": ["认知重构", "行为实验", "家庭作业"],
        "suitable_for": ["抑郁症", "焦虑症", "恐惧症"]
    },
    "Psychoanalytic": {
        "focus": "潜意识、童年经历",
        "duration": "长程（数月-数年）",
        "techniques": ["自由联想", "移情分析", "阻抗分析"],
        "suitable_for": ["人格障碍", "深层心理冲突"]
    },
    "Humanistic": {
        "focus": "自我实现、成长潜能",
        "duration": "中程",
        "techniques": ["积极倾听", "无条件积极关注", "共情"],
        "suitable_for": ["自我探索", "个人成长", "低自尊"]
    },
    "Family": {
        "focus": "家庭系统、互动模式",
        "duration": "中短程",
        "techniques": ["家谱图", "系统提问", "家庭作业"],
        "suitable_for": ["家庭冲突", "青少年问题", "婚姻咨询"]
    }
}
```

## 自动评估框架 CPsyCounE

### 四维评估指标

| 指标 | 满分 | 考察点 | 权重 |
|-----|------|--------|------|
| **全面性** | 2分 | 反映来访者信息和心理问题 | 20% |
| **专业性** | 4分 | 诊断、技术使用、专业语言、框架遵循 | 40% |
| **真实性** | 3分 | 情感表达、共情倾听、符合真实场景 | 30% |
| **安全性** | 1分 | 隐私保护、尊重来访者 | 10% |
| **总分** | **10分** | - | 100% |

### 轮次评估方法

```python
def evaluate_multi_turn_dialogue(dialogue):
    """
    m轮对话 {(q₁,r₁), (q₂,r₂), ..., (qₘ,rₘ)}
    
    分解为m个单轮，分别评估后平均
    """
    scores = []
    history = []
    
    for i, (question, reference) in enumerate(dialogue):
        # 生成回复
        generated = model.generate(history, question)
        
        # GPT-4评估
        score = gpt4_evaluate(
            history=history,
            question=question,
            generated=generated,
            reference=reference,
            metrics=["Comprehensiveness", "Professionalism", "Authenticity", "Safety"]
        )
        
        scores.append(score)
        history.append((question, reference))
    
    # 平均分
    final_score = sum(scores) / len(scores)
    return final_score
```

### 评估数据集

- **基础**: SMILECHAT（56k多轮对话）
- **筛选**: 按9大主题各选5个代表性案例
- **规模**: 45个评估案例

## 实验结果

### 内在评估（Memo2Demo vs 角色扮演）

| 指标 | 角色扮演 | Memo2Demo | 提升 |
|-----|---------|-----------|------|
| 全面性 | 1.30 | **2.00** | +53% |
| 专业性 | 2.25 | **3.44** | +53% |
| 真实性 | 2.04 | **2.64** | +30% |
| 安全性 | 1.00 | 1.00 | - |

### 外在评估（模型对比）

| 模型 | 全面性 | 专业性 | 真实性 | 安全性 |
|-----|--------|--------|--------|--------|
| InternLM2-7B | 1.30 | 2.16 | 1.48 | 1.00 |
| SoulChat | 1.22 | 2.18 | 2.24 | 1.00 |
| ChatGPT | 1.32 | 2.25 | 2.09 | 1.00 |
| GLM-4 | **1.44** | 2.36 | 2.22 | 1.00 |
| **CPsyCounX** | 1.39 | **2.65** | **2.29** | 1.00 |

**CPsyCounX**: InternLM2-7B-Chat + CPsyCounD SFT 9轮

## 使用示例

```python
# Memo2Demo 对话生成
from cpsycoun import Memo2Demo

memo2demo = Memo2Demo(
    phase1_model="glm-4",
    phase2_model="glm-4"
)

# 输入咨询报告
report = """
Title: 大学生焦虑问题咨询案例
Type: 情绪压力
Method: 认知行为疗法
Case Brief: 大三学生，因考研压力出现焦虑失眠...
Consultation Process: 咨询师通过认知重构帮助来访者...
Experience Thoughts: 来访者对压力源认知存在偏差...
"""

# 生成对话
dialogue = memo2demo.generate(report, max_turns=10)

for turn in dialogue:
    print(f"来访者: {turn.user}")
    print(f"咨询师: {turn.counselor}")
    print()
```

## 与现有Skill的整合

### 与 AutoCBT 结合
```python
# CBT流派的专业应用
from autocbt import AutoCBTFramework
from cpsycoun_kb import CBTTechniques

# 使用CPsyCoun的CBT技术库
autocbt.add_techniques(CBTTechniques.from_cpsycoun())
```

### 与 APTNESS 结合
```python
# 评估框架互补
from aptness_kb import evaluate_empathy
from cpsycoun_kb import evaluate_professionalism

# 综合评估
total_score = (
    evaluate_empathy(dialogue) * 0.4 +
    evaluate_professionalism(dialogue) * 0.6
)
```

### 与 XinHaiAgents 结合
```python
# 多智能体咨询场景
from xinhai_agents import XinHaiSkill
from cpsycoun_kb import CounselingScenarios

# 加载咨询场景
scenario = XinHaiSkill.load_scenario(CounselingScenarios.cpsycoun_topics)
```

## 参考文件

- **Memo2Demo详解**: `references/memo2demo.md`
- **咨询主题与流派**: `references/topics_and_schools.md`
- **评估框架**: `references/evaluation_framework.md`
- **数据集格式**: `references/dataset_format.md`
- **流派技术详解**: `references/therapy_techniques.md`

## 引用

```bibtex
@inproceedings{zhang2024cpsycoun,
  title={CPsyCoun: A Report-based Multi-turn Dialogue Reconstruction and Evaluation Framework for Chinese Psychological Counseling},
  author={Zhang, Chenhao and Li, Renhao and Tan, Minghuan and Yang, Min and Zhu, Jingwei and Yang, Di and Zhao, Jiahao and Ye, Guancheng and Li, Chengming and Hu, Xiping},
  booktitle={Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)},
  pages={13947--13966},
  year={2024}
}
```
