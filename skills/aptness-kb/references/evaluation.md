# APTNESS 评估方法

## 评估维度详解

### 1. 共情 (Empathy)

**定义**: 回复整体展现的共情程度

**评分标准 (1-7分)**:
- 1-2分: 机械、缺乏共情
- 3-4分: 有一定理解但不深入
- 5-6分: 较好的共情表达
- 7分: 深刻、真挚的共情

**评估要点**:
- 是否理解对方情绪
- 是否恰当回应
- 是否建立情感连接

---

### 2. 识别 (Identification)

**定义**: 认知共情能力 - 准确理解对方情绪

**评分标准**:
- 是否准确识别情绪类型
- 是否理解情绪强度
- 是否把握情绪原因

**与认知共情的关系**:
- Pearson相关系数: 0.92 (ED), 0.97 (ET)
- 结论: 识别能力是认知共情的核心

---

### 3. 安慰 (Comforting)

**定义**: 情感共情能力 - 提供情感支持

**评分标准**:
- 是否表达关怀
- 是否提供情感支持
- 是否让对方感到被理解

**与情感共情的关系**:
- Pearson相关系数: 0.62 (ED), 0.73 (ET)
- 结论: 安慰是独立的情感共情维度

---

### 4. 建议 (Suggestion)

**定义**: 提供解决方案的恰当性

**评分标准**:
- 1-2分: 不恰当或过多建议
- 3-4分: 建议适中但不够精准
- 5-6分: 恰当且有帮助的建议
- 7分: 精准、可行的建议

**平衡原则**:
- 避免过度建议化
- 建议应建立在共情基础上

---

### 5. 信息性 (Informativity)

**定义**: 回复的信息价值和实用性

**评分标准**:
- 是否提供有价值信息
- 信息是否准确
- 是否增加对话深度

---

### 6. 一致性 (Coherence)

**定义**: 回复与对话上下文的连贯性

**评分标准**:
- 是否承接上文
- 是否自然流畅
- 是否有逻辑跳跃

---

## GPT-4自动评估

### 提示模板

```
You are an expert evaluator of empathetic responses.

Task: Evaluate the following empathetic response based on 6 dimensions.

Dialogue History:
{history}

Response to Evaluate:
{response}

Please rate each dimension from 1-7 (1=very poor, 7=excellent):

1. Empathy: How empathetic is the response overall?
2. Identification: How well does it identify and understand the emotions?
3. Comforting: How comforting and supportive is it?
4. Suggestion: How appropriate are the suggestions (if any)?
5. Informativity: How informative and valuable is the content?
6. Coherence: How coherent is it with the dialogue context?

Provide ratings and brief justification for each.

Format:
Empathy: [score] - [justification]
Identification: [score] - [justification]
...
```

### 评估流程

```python
def evaluate_with_gpt4(dialogue_history, response):
    """
    1. 构建评估提示
    2. 调用GPT-4
    3. 解析评分
    4. 计算平均分
    """
    prompt = build_evaluation_prompt(dialogue_history, response)
    result = gpt4.generate(prompt)
    scores = parse_scores(result)
    return scores
```

### 评估协议

1. **逐轮评估**: 每轮对话单独评分
2. **对话平均**: 同一段对话的分数平均
3. **全局平均**: 所有对话的平均

---

## 实验结果分析

### 主实验对比

| 方法 | ED共情 | ED识别 | ED安慰 | ET共情 | ET识别 | ET安慰 |
|-----|-------|-------|-------|-------|-------|-------|
| GEN | 5.72 | 4.69 | 5.02 | 5.99 | 5.10 | 5.73 |
| RAG | 6.22 | 5.02 | 5.03 | 6.17 | 5.25 | 5.58 |
| APTNESS | **6.28** | **5.23** | **5.23** | **6.44** | **5.48** | **5.93** |

### 关键发现

1. **RAG显著提升认知共情**
   - 识别度: 4.69 → 5.02 (+0.33)
   - 验证: 外部知识库增强理解能力

2. **APTNESS进一步提升情感共情**
   - 安慰性: 5.03 → 5.23 (+0.20)
   - 验证: 策略整合的必要性

3. **长对话挑战**
   - ET数据集比ED更难
   - Llama3-8B在长对话中出现退化
   - 策略模块在ET中更重要

---

## 消融实验

### 策略数据来源对比

| 训练数据 | ED共情 | ED识别 | ED安慰 |
|---------|-------|-------|-------|
| ESConv (粗粒度) | 6.23 | 5.07 | 5.09 |
| ExTES (细粒度) | **6.28** | **5.23** | **5.23** |

**结论**: 细粒度、单一策略标注更优

### 策略模块必要性

| 数据集 | 方法 | 共情 | 安慰 |
|-------|-----|------|------|
| ED | RAG | 5.94 | 5.07 |
| | APTNESS(直接) | **6.19** | **5.20** |
| ET | RAG | 6.08 | **5.73** |
| | APTNESS(直接) | 5.85 | 5.39 |

**结论**: 
- 短对话: LLM直接生成策略有效
- 长对话: 需要专用策略预测模块

---

## 人工评估 vs 自动评估

### 一致性

| 维度 | 人机一致性 |
|-----|-----------|
| 共情 | 0.78 |
| 识别 | 0.82 |
| 安慰 | 0.75 |
| 建议 | 0.71 |
| 一致性 | 0.80 |

**结论**: GPT-4自动评估与人工评估具有较高一致性

### 评估成本

| 方法 | 时间/样本 | 成本 |
|-----|----------|------|
| 人工评估 | 5-10分钟 | 高 |
| GPT-4 | 5-10秒 | 中 |
| 规则基线 | <1秒 | 低 |

---

## 评估代码示例

```python
import openai

def evaluate_response(dialogue_history, response):
    prompt = f"""
    Evaluate the empathetic response on 6 dimensions (1-7 scale).
    
    Dialogue History:
    {format_history(dialogue_history)}
    
    Response:
    {response}
    
    Rate: Empathy, Identification, Comforting, Suggestion, Informativity, Coherence
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert evaluator."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return parse_evaluation(response.choices[0].message.content)
```

## 引用

```bibtex
@inproceedings{hu2024aptness,
  title={APTNESS: Incorporating Appraisal Theory and Emotion Support Strategies for Empathetic Response Generation},
  author={Hu, Yuxuan and Tan, Minghuan and Zhang, Chenwei and others},
  booktitle={CIKM},
  year={2024}
}
```
