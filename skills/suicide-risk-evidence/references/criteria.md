# Suicide Risk Evidence Extractor - 6维度评估标准

## 评估维度详解

基于 CLPsych 2024 Shared Task 的六维度风险评估框架。

---

## 维度1：Emotions (情绪状态)

### 识别内容
- 深度悲伤、绝望感
- 心理痛苦难以忍受
- 空虚感、无意义感
- 焦虑、恐惧
- 愤怒、怨恨

### 典型表达
```
"I feel completely hopeless"
"The pain is unbearable"
"I feel empty inside"
"Nothing brings me joy anymore"
"我感到彻底的绝望"
"痛苦难以忍受"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 情绪低落，但还能感受到一些积极情绪 |
| Moderate | 持续悲伤，难以感受到快乐 |
| High | 深度绝望，情感麻木或极度痛苦 |

---

## 维度2：Cognitions (自杀相关认知)

### 识别内容
- 自杀想法的频率和强度
- 自杀意图明确性
- 自杀计划的具体程度
- 死亡欲望 (wish to die)
- 认为自己是负担
- 未来无望感

### 典型表达
```
"I think about ending it all every day"
"I have a plan"
"Everyone would be better off without me"
"There's no point in continuing"
"I'm a burden to my family"
"我每天都在想结束这一切"
"没有我大家会过得更好"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 偶尔出现自杀念头，无明确意图 |
| Moderate | 频繁自杀想法，有模糊意图 |
| High | 明确自杀计划，强烈死亡欲望 |

---

## 维度3：Behaviour and Motivation (行为与动机)

### 识别内容
- 自杀相关行为（准备、尝试）
- 应对能力下降
- 动机丧失
- 自我照顾能力下降
- 冒险行为增加
- 社会退缩

### 典型表达
```
"I've been researching methods"
"I've started giving away my belongings"
"I can't take care of myself anymore"
"I've stopped eating"
"I don't care what happens to me"
"我一直在查相关资料"
"我开始把东西送人"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 应对能力轻度下降，仍有日常功能 |
| Moderate | 明显应对困难，社会功能受损 |
| High | 严重自我忽视，准备自杀行为 |

---

## 维度4：Interpersonal and Social Support (社会支持)

### 识别内容
- 人际关系质量
- 社会隔离程度
- 感受到的支持
- 冲突和丧失
- 被拒绝感

### 典型表达
```
"I have no one to talk to"
"Everyone has abandoned me"
"I push everyone away"
"My friends don't understand"
"I feel so alone"
"我没有人可以倾诉"
"所有人都抛弃了我"
"我感到如此孤独"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 有基本支持网络，偶感孤独 |
| Moderate | 支持网络薄弱，明显孤立感 |
| High | 完全孤立，缺乏任何支持 |

---

## 维度5：Mental Health-related Issues (精神健康问题)

### 识别内容
- 精神疾病史（抑郁、焦虑、PTSD等）
- 既往自伤史
- 既往自杀未遂史
- 物质滥用
- 当前治疗状态

### 典型表达
```
"I've been depressed for years"
"I used to cut myself"
"I attempted suicide before"
"I've stopped taking my medication"
"I'm drinking more than usual"
"我抑郁多年了"
"我以前自残过"
"我停掉了我的药"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 有精神健康问题史，目前在接受治疗 |
| Moderate | 活跃的精神健康症状，治疗不充分 |
| High | 严重精神健康问题，无治疗或治疗无效 |

---

## 维度6：Context/Additional Risk Factors (情境/额外风险因素)

### 识别内容
- 近期重大生活事件
- 丧失（工作、关系、亲人）
- 创伤暴露史
- 慢性疾病或疼痛
- 经济困难
- 法律问题

### 典型表达
```
"I lost my job last month"
"My partner just left me"
"I was diagnosed with cancer"
"I can't pay my bills"
"I'm facing legal charges"
"我上个月失业了"
"我刚被诊断出重病"
"我付不起账单"
```

### 风险信号
| 等级 | 特征 |
|-----|------|
| Low | 轻度压力，可控的生活变化 |
| Moderate | 重大压力事件，应对困难 |
| High | 多重危机同时发生，压倒性压力 |

---

## 综合风险等级判定

### 判定标准

| 风险等级 | 定义 | 主要特征 |
|---------|------|---------|
| **Low Risk** | 低风险 | 1-2个维度有轻度风险信号，有保护因素 |
| **Moderate Risk** | 中度风险 | 3-4个维度有中度风险信号，支持网络薄弱 |
| **High Risk** | 高风险 | 5-6个维度有显著风险信号，有自杀计划或行为 |

### 保护因素 (Protective Factors)

在评估风险时，也需要识别保护因素：

- 强烈的生存意愿
- 对未来的希望
- 宗教信仰或精神寄托
- 家庭责任（子女等）
- 有效的应对策略
- 良好的社会支持
- 寻求帮助的意愿
- 之前成功克服危机的经历

---

## CoT 评估提示词模板

```
请从以下六个维度分析用户帖子中的自杀风险证据：

【评估维度】

1. Emotions (情绪状态)
   - 用户表达了什么情绪？
   - 情绪的强度和持续性如何？
   - 是否有绝望或无法忍受的痛苦？

2. Cognitions (自杀相关认知)
   - 是否有自杀想法？频率如何？
   - 是否有明确的自杀意图？
   - 是否制定了自杀计划？
   - 是否认为自己是负担？

3. Behaviour and Motivation (行为与动机)
   - 是否有自杀相关行为？
   - 应对能力是否下降？
   - 动机和兴趣是否丧失？
   - 是否有自我照顾能力下降？

4. Interpersonal and Social Support (社会支持)
   - 用户的支持网络状况如何？
   - 是否感到孤立或被抛弃？
   - 人际关系质量如何？

5. Mental Health-related Issues (精神健康问题)
   - 是否有精神疾病史？
   - 是否有自伤或自杀未遂史？
   - 是否在接受治疗？
   - 是否有物质滥用？

6. Context/Additional Risk Factors (情境因素)
   - 是否有近期重大生活事件？
   - 是否有丧失或创伤？
   - 是否有经济或法律问题？
   - 是否有慢性疾病或疼痛？

【分析要求】
对于每个维度：
1. 识别相关的文本证据
2. 评估风险程度（None/Low/Moderate/High）
3. 提供推理依据

【输出格式】
{
    "dimension_analysis": {
        "Emotions": {
            "evidence": ["文本片段1", "文本片段2"],
            "risk_level": "Moderate",
            "reasoning": "用户表达了持续的悲伤和绝望感..."
        },
        ...其他维度...
    },
    "overall_risk": "Moderate Risk",
    "key_concerns": ["主要关注点1", "主要关注点2"],
    "protective_factors": ["保护因素1", "保护因素2"]
}
```

---

## 提示词优化建议

### 1. Chain-of-Thought (CoT)
强制模型按步骤推理，提高识别准确性。

### 2. GPT-4 优化
使用 GPT-4 优化提示词结构，提高清晰度。

### 3. One-shot 示例
提供 JSON 格式示例，确保输出一致性。

### 4. 双语适配
- 英文：使用英文维度和标准
- 中文：翻译成中文维度和标准，保持评估逻辑一致
