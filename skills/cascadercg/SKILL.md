---
name: cascadercg
description: CascadeRCG - 基于双库交叉迭代检索的咨询回复质量提升框架。通过分离专业知识库与通用知识库、Three Ws查询重写、两阶段交叉检索、聚类总结等创新技术，显著提升心理健康咨询回复的专业性和知识性。当用户需要：1) 提升咨询回复的专业度 2) 减少LLM幻觉 3) 平衡专业知识与生活经验 4) 多轮对话场景下的知识增强 5) 构建专业心理健康知识库时触发。
---

# CascadeRCG Skill

**论文**: CascadeRCG: Retrieval-Augmented Generation for Enhancing Professionalism and Knowledgeability in Online Mental Health Support (WWW Companion 2025)  
**作者**: Di Yang, Jingwei Zhu, Haihong Wu, Minghuan Tan, Chengming Li, Min Yang  
**代码**: https://github.com/CAS-SIAT-XinHai/CascadeRCG

## 核心创新

### 1. 双库知识管理

传统RAG使用统一知识库导致专业/通用知识不平衡。CascadeRCG分离两者：

| 知识库 | 内容 | 作用 |
|-------|------|------|
| **Professional DB** | 经典心理学书籍、理论框架、实证研究 | 提供专业性 |
| **General DB** | 生活经验、文化理解、社会知识 | 提供知识性 |

**分离优势**: 避免通用知识淹没专业知识，确保检索平衡

### 2. Three Ws 查询重写

将复杂咨询问题分解为三个维度：

```
Original Question: "我在办公室空调太冷，不敢提意见，很困扰"

Three Ws Decomposition:
├── What: 群体思维现象、从众心理
├── Why: 社会心理学中的多元无知效应、对自我价值的怀疑
└── How: 沟通技巧、自信表达方法
```

### 3. 两阶段交叉迭代检索

```
┌─────────────────────────────────────────────────────────────┐
│                    CascadeRCG Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Stage 1: First Retrieval                                    │
│  ├── 从 Professional DB 检索 → 过滤总结                      │
│  └── 从 General DB 检索 → 过滤总结                           │
│                           ↓                                  │
│  Stage 2: Cross Retrieval                                    │
│  ├── Professional结果 → 查询General DB（补充生活视角）        │
│  └── General结果 → 查询Professional DB（补充理论支撑）        │
│                           ↓                                  │
│  Clustering & Summarizing                                    │
│  ├── 聚类（J=4个簇）                                         │
│  └── 每簇总结                                                │
│                           ↓                                  │
│  Final Generation                                            │
│  └── 生成专业且富有知识性的回复                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4. 聚类-总结策略

减少生成提示长度，提高信息密度：
- 使用 query-retrieval pairs 的 embedding 进行聚类
- 每簇内文档进一步总结
- 将聚类级总结输入LLM生成最终回复

## 完整流程

```python
# 1. Three Ws 查询重写
sub_queries = three_ws_rewrite(user_question)
# Output: [what_query, why_query, how_query]

# 2. 第一阶段检索
prof_results = retrieve_and_summarize(sub_queries, professional_db, K=2)
gen_results = retrieve_and_summarize(sub_queries, general_db, K=2)

# 3. 第二阶段交叉检索
cross_prof = retrieve_and_summarize(prof_results, general_db, M=1)
cross_gen = retrieve_and_summarize(gen_results, professional_db, M=1)

# 4. 聚类与总结
all_results = prof_results + gen_results + cross_prof + cross_gen
clusters = cluster(all_results, J=4)
cluster_summaries = [summarize(c) for c in clusters]

# 5. 最终生成
response = generate(original_question, cluster_summaries)
```

## 使用方式

### 基础用法

```python
from cascadercg import CascadeRCG

# 初始化
cascadercg = CascadeRCG(
    professional_db_path="path/to/professional_db",
    general_db_path="path/to/general_db",
    embedding_model="bge-large-zh-v1.5",
    llm_model="qwen1.5-14b"
)

# 生成专业咨询回复
response = cascadercg.generate(
    query="我22岁实习生，办公室空调太冷不敢提意见，很困扰",
    conversation_history=None  # 支持多轮
)

print(response)
```

### 多轮对话支持

```python
# 多轮对话场景
history = [
    {"role": "user", "content": "我最近总是失眠..."},
    {"role": "assistant", "content": "失眠确实很难受..."},
    {"role": "user", "content": "试过很多方法都没用"}
]

response = cascadercg.generate_multi_turn(
    current_query="试过很多方法都没用",
    history=history
)
```

### 知识库构建

```python
# 构建专业知识库
from cascadercg.database import KnowledgeBaseBuilder

builder = KnowledgeBaseBuilder(
    chunk_size=300,
    chunk_overlap=30,
    embedding_model="bge-large-zh-v1.5"
)

# 添加专业书籍
professional_kb = builder.build_from_books(
    book_paths=["psychology_classics/*.pdf"],
    db_name="professional_psychology"
)

# 添加通用知识
general_kb = builder.build_from_sources(
    sources=["life_experience.json", "social_knowledge.txt"],
    db_name="general_knowledge"
)
```

## 评估指标

CascadeRCG 使用 5 维度评估：

| 指标 | 满分 | 评估内容 |
|-----|------|---------|
| **Professionalism** | 5分 | 心理学专业知识应用、理论引用、相关性 |
| **Knowledgeability** | 5分 | 社会知识、生活经验、准确性 |
| **Empathy** | 3分 | 情感支持、语言温和、鼓励性 |
| **Safety** | 3分 | 避免有害建议、安全资源、隐私保护 |
| **No-Hallucination** | 3分 | 无幻觉知识、逻辑一致 |

## 实验结果

### PsyQA 数据集（单轮对话）

| 方法 | Qwen1.5-14B Pro | Qwen1.5-14B Kno | Qwen1.5-72B Pro | Qwen1.5-72B Kno |
|-----|----------------|----------------|----------------|----------------|
| Generation | 2.80 | 4.12 | 2.95 | 4.16 |
| CoT w/o retrieval | 3.06 | 4.33 | 3.26 | 4.35 |
| Naive RAG | 2.94 | 4.21 | 3.43 | 4.38 |
| **CascadeRCG** | **4.08** | **4.40** | **4.30** | **4.62** |

**提升**: Professionalism +38%~+47%, Knowledgeability +5%~+11%

### SmileChat 数据集（多轮对话）

CascadeRCG 在多轮对话场景同样优于基线方法。

## 配置参数

```python
config = {
    # 知识库配置
    "professional_db": {
        "books": 16,  # 经典心理学书籍
        "chunk_size": 300,
        "chunk_overlap": 30
    },
    "general_db": {
        "books_and_articles": 979,
        "chunk_size": 300,
        "chunk_overlap": 30
    },
    
    # 检索配置
    "retrieval": {
        "embedding_model": "bge-large-zh-v1.5",
        "reranker": "Cross-Encoder",
        "first_stage_K": 2,      # 第一阶段每查询检索数
        "second_stage_M": 1,     # 第二阶段交叉检索数
        "clusters_J": 4          # 聚类数量
    },
    
    # 生成配置
    "generation": {
        "model": "qwen1.5-14b",  # 或其他LLM
        "temperature": 0.7,
        "max_tokens": 1024
    }
}
```

## 与现有Skill的整合

### 1. 与 AutoCBT 结合

```python
# 先使用 CascadeRCG 生成专业回复
crg_response = cascadercg.generate(user_query)

# 再使用 AutoCBT 进行多智能体优化
from autocbt import AutoCBTFramework

autocbt = AutoCBTFramework()
final_response = autocbt.refine_with_supervisors(crg_response)
```

### 2. 与 CPsyCoun 结合

```python
# CascadeRCG 提供专业知识支撑
from cpsycoun_kb import CounselingScenarios

scenario = CounselingScenarios.load(topic="anxiety")
crg_response = cascadercg.generate(
    query=user_query,
    context=scenario.techniques  # 注入特定流派技术
)
```

### 3. 与 APTNESS 结合

```python
# CascadeRCG 提供专业知识
# APTNESS 提供共情策略

professional_response = cascadercg.generate(query)
empathetic_response = aptness_kb.enhance_with_empathy(
    professional_response,
    emotion_detected="anxiety"
)
```

## 参考文件

- **算法实现**: `references/algorithm.md`
- **Three Ws提示**: `assets/prompts/three_ws_prompts.json`
- **过滤与总结提示**: `assets/prompts/filtering_summarization_prompts.md`
- **评估标准**: `references/evaluation_criteria.md`
- **知识库构建指南**: `references/kb_building_guide.md`

## 引用

```bibtex
@inproceedings{yang2025cascadercg,
  title={CascadeRCG: Retrieval-Augmented Generation for Enhancing Professionalism and Knowledgeability in Online Mental Health Support},
  author={Yang, Di and Zhu, Jingwei and Wu, Haihong and Tan, Minghuan and Li, Chengming and Yang, Min},
  booktitle={Companion of the 16th ACM/SPEC International Conference on Performance Engineering (WWW Companion)},
  year={2025}
}
```
