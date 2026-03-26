# AutoCBT 数据集格式

## 1. 双语咨询数据集结构

### 1.1 中文数据集 (PsyQA格式)

```json
{
  "dataset_name": "AutoCBT-Chinese",
  "source": "PsyQA",
  "language": "zh",
  "samples": [
    {
      "id": "zh_001",
      "category": "人际关系",
      "cognitive_distortion": "labeling",
      "question": "总是要考虑很多问题，我感觉我活在世界上就没有意义？",
      "question_description": "我感觉我自己在交朋友的这条路上总是很不顺，初一初二的时候跟别人抢，我总是抢不过...",
      "answer": "抱抱～看到发生在你身上的事就像往事重现。请允许我以姐姐的口吻与你讲下我的故事...",
      "metadata": {
        "question_length": 245,
        "answer_length": 580,
        "has_distortion": true,
        "distortion_types": ["labeling", "overgeneralization"]
      }
    }
  ]
}
```

### 1.2 英文数据集 (TherapistQA格式)

```json
{
  "dataset_name": "AutoCBT-English",
  "source": "TherapistQA",
  "language": "en",
  "samples": [
    {
      "id": "en_001",
      "category": "family_relationships",
      "cognitive_distortion": "catastrophizing",
      "question": "Me and my sister in law are both pregnant right now...",
      "question_description": "This situation really has me depressed, and unsure what to do...",
      "answer": "Thank you for explaining this situation. How unfortunate that this share joyous event is turning into a competition...",
      "metadata": {
        "question_length": 312,
        "answer_length": 445,
        "has_distortion": true,
        "distortion_types": ["catastrophizing", "mind_reading"]
      }
    }
  ]
}
```

## 2. 认知扭曲标注格式

### 2.1 标注字段

```json
{
  "annotation": {
    "annotator": "Qwen-72B",
    "annotation_date": "2024-01-15",
    "distortions": [
      {
        "type": "labeling",
        "text": "我总觉得自己一无是处",
        "start_pos": 15,
        "end_pos": 25,
        "confidence": 0.92,
        "explanation": "用户给自己贴上全面否定的标签"
      },
      {
        "type": "overgeneralization",
        "text": "从来没有人喜欢我",
        "start_pos": 30,
        "end_pos": 40,
        "confidence": 0.88,
        "explanation": "从有限经验推断普遍规律"
      }
    ]
  }
}
```

### 2.2 10类认知扭曲定义

```json
{
  "cognitive_distortions": {
    "catastrophizing": {
      "name_cn": "灾难化",
      "name_en": "Catastrophizing",
      "definition": "想象最坏的情况会发生",
      "examples": ["这次失败意味着我的人生完了", "如果失去这份工作，我就完了"],
      "keywords": ["完了", "彻底", "永远", "不可能"]
    },
    "labeling": {
      "name_cn": "贴标签",
      "name_en": "Labeling",
      "definition": "给自己或他人贴上负面的全局性标签",
      "examples": ["我是个失败者", "他就是个混蛋"],
      "keywords": ["我是个", "他就是", "总是", "永远"]
    },
    "minimizing": {
      "name_cn": "最小化",
      "name_en": "Minimizing",
      "definition": "贬低自己的成就或积极方面",
      "examples": ["这没什么大不了", "任何人都能做到"],
      "keywords": ["没什么", "小事", "不值得一提"]
    },
    "all_or_nothing": {
      "name_cn": "全或无思维",
      "name_en": "All-or-Nothing Thinking",
      "definition": "非黑即白的极端思维",
      "examples": ["如果不能做到最好，那就是失败", "要么完美，要么放弃"],
      "keywords": ["要么", "或者", "完美", "彻底"]
    },
    "overgeneralization": {
      "name_cn": "过度概括",
      "name_en": "Overgeneralization",
      "definition": "从单一负面事件推断普遍规律",
      "examples": ["这次失败了，我总是失败", "从来没有人喜欢我"],
      "keywords": ["总是", "永远", "每次", "从来"]
    },
    "mind_reading": {
      "name_cn": "读心术",
      "name_en": "Mind Reading",
      "definition": "假设知道他人的想法，通常是负面的",
      "examples": ["他们一定觉得我很蠢", "他肯定不喜欢我"],
      "keywords": ["一定", "肯定", "觉得", "认为"]
    },
    "emotional_reasoning": {
      "name_cn": "情绪推理",
      "name_en": "Emotional Reasoning",
      "definition": "把感受当作事实的证据",
      "examples": ["我感觉自己很失败，所以我一定是个失败者", "我觉得没人爱我，所以这是真的"],
      "keywords": ["感觉", "觉得", "所以"]
    },
    "should_statements": {
      "name_cn": "应该陈述",
      "name_en": "Should Statements",
      "definition": "用"应该"、"必须"对自己或他人有不切实际的期望",
      "examples": ["我应该做得更好", "他们应该理解我"],
      "keywords": ["应该", "必须", "一定要"]
    },
    "personalization": {
      "name_cn": "个人化",
      "name_en": "Personalization",
      "definition": "把无关的外部事件归咎于自己",
      "examples": ["妈妈不高兴，一定是因为我", "项目失败是我的错"],
      "keywords": ["因为我", "我的错", "怪我"]
    },
    "discounting_positives": {
      "name_cn": "否定积极",
      "name_en": "Discounting Positives",
      "definition": "拒绝接受正面的经验或赞美",
      "examples": ["他们只是客气", "那只是运气"],
      "keywords": ["只是", "碰巧", "运气", "客气"]
    }
  }
}
```

## 3. 评估数据集格式

### 3.1 自动评估数据

```json
{
  "evaluation_data": {
    "sample_id": "eval_001",
    "user_message": "我最近工作压力很大，感觉自己什么都做不好...",
    "ground_truth_response": "...",
    "generated_response": "...",
    "auto_scores": {
      "empathy": 6.5,
      "identification": 6.0,
      "reflection": 5.5,
      "strategy": 6.0,
      "encouragement": 5.5,
      "relevance": 6.5,
      "total": 36.0
    },
    "evaluation_model": "GPT-4o-mini",
    "evaluation_rounds": 3
  }
}
```

### 3.2 人工评估数据

```json
{
  "human_evaluation": {
    "sample_id": "heval_001",
    "evaluator_id": "psychologist_001",
    "evaluator_background": "临床心理学博士，5年CBT经验",
    "preference_ranking": {
      "best": "AutoCBT",
      "second": "PromptCBT",
      "third": "Generation"
    },
    "detailed_scores": {
      "AutoCBT": {
        "empathy": 6,
        "identify_cd": 7,
        "challenge_cd": 6,
        "reflection": 5,
        "strategy": 6,
        "encouragement": 5,
        "presentation": 6,
        "comments": "..."
      }
    }
  }
}
```

## 4. 训练数据格式

### 4.1 SFT (Supervised Fine-Tuning) 数据

```json
{
  "sft_data": {
    "conversations": [
      {
        "role": "system",
        "content": "你是一位专业的CBT心理咨询师..."
      },
      {
        "role": "user",
        "content": "我总是觉得自己很失败..."
      },
      {
        "role": "assistant",
        "content": "我能感受到你现在的低落情绪..."
      }
    ],
    "metadata": {
      "cognitive_distortion": "labeling",
      "language": "zh",
      "quality_score": 7.0
    }
  }
}
```

### 4.2 DPO (Direct Preference Optimization) 数据

```json
{
  "dpo_data": {
    "prompt": "用户：我总是搞砸一切，觉得自己一无是处。\n咨询师：",
    "chosen": "我能感受到你现在很难过。当我们说"总是"和"一无是处"时，可能是在用非黑即白的方式看待自己...",
    "rejected": "你应该多想想积极的事情，不要太消极。",
    "rationale": "chosen回应更共情且识别了认知扭曲，rejected过于简单且缺乏共情"
  }
}
```

## 5. 多轮对话数据

```json
{
  "multi_turn_conversation": {
    "session_id": "session_001",
    "user_id": "user_anonymous_001",
    "turns": [
      {
        "turn_id": 1,
        "role": "user",
        "content": "我最近很焦虑...",
        "timestamp": "2024-01-15T09:00:00Z"
      },
      {
        "turn_id": 2,
        "role": "assistant",
        "content": "我能理解你的焦虑...",
        "routing_history": ["BROADCAST", "ENDCAST"],
        "supervisors_consulted": ["empathy", "identify", "strategy"]
      },
      {
        "turn_id": 3,
        "role": "user",
        "content": "但是我试过那些方法，都没有用...",
        "timestamp": "2024-01-15T09:05:00Z"
      },
      {
        "turn_id": 4,
        "role": "assistant",
        "content": "听起来你已经尝试了很多方法...",
        "routing_history": ["UNICAST:encouragement", "ENDCAST"],
        "supervisors_consulted": ["encouragement"]
      }
    ],
    "session_summary": {
      "main_issue": "工作焦虑",
      "cognitive_distortions_identified": ["overgeneralization", "all_or_nothing"],
      "strategies_suggested": ["认知重构", "行为激活"],
      "session_outcome": "用户表示有帮助，愿意尝试新策略"
    }
  }
}
```

## 6. 数据使用示例

### 6.1 加载数据集

```python
import json

def load_dataset(filepath):
    """加载AutoCBT数据集"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 加载中文数据集
zh_data = load_dataset('autocbt_chinese.json')

# 按认知扭曲类型筛选
labeling_samples = [
    s for s in zh_data['samples']
    if s['cognitive_distortion'] == 'labeling'
]

# 加载英文数据集
en_data = load_dataset('autocbt_english.json')
```

### 6.2 数据预处理

```python
def preprocess_for_training(data):
    """将数据转换为训练格式"""
    sft_data = []
    
    for sample in data['samples']:
        conversation = [
            {"role": "system", "content": "你是一位专业的CBT心理咨询师..."},
            {"role": "user", "content": sample['question']},
            {"role": "assistant", "content": sample['answer']}
        ]
        
        sft_data.append({
            "conversations": conversation,
            "metadata": {
                "cognitive_distortion": sample['cognitive_distortion'],
                "language": data['language']
            }
        })
    
    return sft_data
```

## 7. 数据集统计

```json
{
  "dataset_statistics": {
    "total_samples": 200,
    "language_distribution": {
      "zh": 100,
      "en": 100
    },
    "cognitive_distortion_distribution": {
      "catastrophizing": 20,
      "labeling": 20,
      "minimizing": 20,
      "all_or_nothing": 20,
      "overgeneralization": 20,
      "mind_reading": 20,
      "emotional_reasoning": 20,
      "should_statements": 20,
      "personalization": 20,
      "discounting_positives": 20
    },
    "average_question_length": {
      "zh": 156,
      "en": 189
    },
    "average_answer_length": {
      "zh": 412,
      "en": 398
    }
  }
}
```
