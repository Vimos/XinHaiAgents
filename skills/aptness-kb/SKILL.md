---
name: aptness-kb
description: APTNESS知识库 - 结合评估理论(Appraisal Theory)和情感支持策略的共情回复生成方法。包含情感调色板(7大类23小类)、APT数据库构建、两阶段RAG生成框架、策略预测模块等完整技术细节。当用户需要：1) 基于评估理论的共情回复生成 2) 情感支持策略整合 3) 认知共情与情感共情的技术实现 4) APTNESS框架应用 5) 共情对话数据集构建时触发。
---

# APTNESS 知识库

**论文**: APTNESS: Incorporating Appraisal Theory and Emotion Support Strategies for Empathetic Response Generation  
**会议**: CIKM 2024  
**作者**: Yuxuan Hu, Minghuan Tan, Chenwei Zhang, et al.  
**代码**: https://github.com/CAS-SIAT-XinHai/APTNESS

## 核心贡献

APTNESS 是一个结合**评估理论(Appraisal Theory)**和**情感支持策略**的共情回复生成框架，通过两阶段生成机制同时提升认知共情和情感共情能力。

## 理论框架

### 共情的两个维度

| 维度 | 定义 | 技术实现 |
|-----|------|---------|
| **认知共情** | 识别和理解他人情绪，无需亲身体验 | 评估理论分解 + RAG检索增强 |
| **情感共情** | 与他人情绪形成深度共鸣，通过安慰回应 | 情感支持策略整合 |

### 评估理论(Appraisal Theory)

人类共情的三步过程：
1. **识别情绪** → 理解对方情绪状态
2. **分析因素** → 考虑影响情绪的因素
3. **理解情境** → 结合具体情境生成回应

对应到技术实现：
```
情绪(E) → 影响因素(F) → 情境(S) → 共情回复(R)
```

## APTNESS 框架架构

```
┌─────────────────────────────────────────────────────────────┐
│                    APTNESS Framework                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Phase 1: 检索增强 (RAG)                   │  │
│  │  • LLM生成初稿 G₁                                     │  │
│  │  • Nomic Embed编码                                    │  │
│  │  • Top-K语义检索 (K=2)                                 │  │
│  │  • 获取相似回复 R₁, R₂...                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Phase 2: 策略整合                           │  │
│  │  • LoRA策略预测模块                                    │  │
│  │  • 策略去重                                           │  │
│  │  • 融合生成最终回复                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│                    最终共情回复 R_final                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 情感调色板 (Emotional Palette)

### 7大类23小类

| 大类 | 小类 | 共情场景 |
|-----|------|---------|
| **喜悦 Joy** | 快乐、兴奋、满足、自豪、爱 | 庆祝、分享喜悦 |
| **愤怒 Anger** | 愤怒、厌恶、嫉妒 | 不公对待、挫折 |
| **悲伤 Sadness** | 悲伤、失望、孤独、绝望 | 失落、分离、失败 |
| **恐惧 Fear** | 恐惧、焦虑、担忧、紧张 | 不确定性、危险 |
| **惊讶 Surprise** | 惊讶、困惑 | 意外事件 |
| **厌恶 Disgust** | 厌恶、鄙视 | 道德不适 |
| **信任 Trust** | 信任、期待 | 人际关系、依赖 |

## APT数据库

### 构建流程

```python
# Step 1: 生成影响因素
Factors = GenerateFactors(Emotion)  # 230个

# Step 2: 生成情境
Situations = GenerateSituations(Emotion, Factors)  # 2,415个

# Step 3: 生成对话首句
FirstUtterance = GenerateFirstSentence(Situation)

# Step 4: 延续生成完整对话
Dialogue = ContinueDialogue(FirstUtterance)

# Step 5: 反思重生成
FinalResponse = ReflectAndRegenerate(Dialogue, E, F, S)
```

### 数据库统计

| 项目 | 数量 |
|-----|------|
| 主要情绪类别 | 7 |
| 情绪子类别 | 23 |
| 影响因素 | 230 |
| 情境 | 2,415 |
| 对话 | 9,663 |
| 回复条目 | 19,896 |

## 两阶段生成详解

### Phase 1: 检索增强生成

```python
# 输入: 对话历史 C
# 输出: 初稿 + 相似回复

G_1 = LLM(C)  # 生成初稿
E_G1 = NomicEmbed(G_1)  # 编码

# Top-K检索
R = TopK_CosineSimilarity(E_G1, APT_Database, K=2)
H = [C] + [History(r) for r in R]  # 对应历史
```

**检索器**: Nomic Embed 1.5 (稠密检索)

### Phase 2: 策略整合

```python
# LoRA微调策略预测
S_LoRA = LoRA_Strategy_Predictor(H)  # 预测策略
S_unique = Deduplicate(S_LoRA)  # 去重
S_def = [Definition(s) for s in S_unique]  # 获取定义

# 最终生成
R_final = Generate(C, R, S_unique, S_def)
```

### 情感支持策略 (17类)

| 策略 | 定义 | 示例 |
|-----|------|------|
| **反思性陈述** | 反映对方感受 | "听起来你很沮丧" |
| **澄清** | 确认理解正确 | "你是说...对吗?" |
| **情绪验证** | 认可情绪合理性 | "有这种感觉很正常" |
| **共情陈述** | 表达理解 | "我能理解你的痛苦" |
| **肯定** | 认可对方能力 | "你已经做得很好了" |
| **给予希望** | 提供积极展望 | "事情会好起来的" |
| **避免评判** | 保持中立态度 | "我不会评判你的选择" |
| **建议选项** | 提供解决方案 | "也许你可以尝试..." |
| **自我披露** | 分享类似经历 | "我也有过类似经历" |
| **信息提供** | 给予相关知识 | "研究表明..." |
| ... | ... | ... |

## 完整生成算法

```python
def APTNESS_Generate(C, APT_Database, Strategy_Data):
    """
    Args:
        C: 对话历史
        APT_Database: 共情回复数据库
        Strategy_Data: 策略训练数据
    
    Returns:
        R_final: 最终共情回复
    """
    # === Phase 1: 检索增强 ===
    G_1 = LLM(C)  # 初稿
    R = [G_1] + Retriever(G_1, APT_Database, K=2)  # 检索
    H = [C] + [GetHistory(r) for r in R]  # 历史
    
    # === Phase 2: 策略整合 ===
    LLM_LoRA = LoadLoRA(Strategy_Data)  # 加载策略模型
    S = []
    for h in H:
        S_i = LLM_LoRA.predict(h)  # 预测策略
        S.append(S_i)
    
    S = Deduplicate(S)  # 去重
    S_def = GetDefinitions(S)  # 获取策略定义
    
    # === 最终生成 ===
    R_final = GenerateWithPrompt(C, R, S, S_def)
    
    return R_final
```

## 实验结果

### 主实验 (GPT-4自动评估)

**ED数据集** (短对话):
| 方法 | 共情 | 识别 | 安慰 |
|-----|------|------|------|
| Llama3-8B GEN | 5.72 | 4.69 | 5.02 |
| + RAG | 6.22 | 5.02 | 5.03 |
| + APTNESS | **6.28** | **5.23** | **5.23** |

**ET数据集** (长对话):
| 方法 | 共情 | 识别 | 安慰 |
|-----|------|------|------|
| Llama3-8B GEN | 5.99 | 5.10 | 5.73 |
| + RAG | 6.17 | 5.25 | 5.58 |
| + APTNESS | **6.44** | **5.48** | **5.93** |

### 关键发现

1. **共情 ≈ 认知共情** (Pearson 0.92)
   - 识别能力是共情的基础

2. **情感共情独立贡献** (Pearson 0.62)
   - 安慰性与识别性中等相关
   - 需要单独优化

3. **策略模块必要性**
   - 直接LLM生成策略在长对话中失效
   - 专用LoRA模块稳定提升

## 数据集

### ED (EmpatheticDialogues)
- 30段对话 × 4轮 = 120轮
- 短对话场景
- 明确情绪标签

### ET (ExTES)
- 10段对话 × 12轮 = 120轮
- 长对话深度支持
- 17种细粒度策略

### 评估维度
- 共情(Empathy)
- 识别(Identification) 
- 安慰(Comforting)
- 建议(Suggestion)
- 信息性(Informativity)
- 一致性(Coherence)

## 使用示例

```python
# 加载APTNESS
from aptness import APTNESSGenerator

generator = APTNESSGenerator(
    llm_model="llama3-8b",
    apt_database_path="apt_db.json",
    strategy_model_path="strategy_lora"
)

# 生成共情回复
dialogue_history = [
    {"speaker": "user", "text": "我最近工作压力大，总是很焦虑..."}
]

response = generator.generate(dialogue_history)
print(response)
# "我能感受到你现在的压力。面对工作焦虑，记得你并不孤单...
#  或许我们可以一起探讨一些缓解方法？"
```

## 参考文件

- **框架实现**: `references/framework.md`
- **情感调色板**: `references/emotional_palette.md`
- **策略详解**: `references/strategies.md`
- **数据库格式**: `references/database_format.md`
- **评估方法**: `references/evaluation.md`

## 引用

```bibtex
@inproceedings{hu2024aptness,
  title={APTNESS: Incorporating Appraisal Theory and Emotion Support Strategies for Empathetic Response Generation},
  author={Hu, Yuxuan and Tan, Minghuan and Zhang, Chenwei and Li, Zixuan and Liang, Xiaodan and Yang, Min and Li, Chengming and Hu, Xiping},
  booktitle={Proceedings of the 33rd ACM International Conference on Information and Knowledge Management (CIKM)},
  year={2024}
}
```
