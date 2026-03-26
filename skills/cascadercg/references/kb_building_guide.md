# CascadeRCG 知识库构建指南

## 概述

CascadeRCG 使用**双库分离**策略：
- **Professional DB**: 专业心理学知识（理论、研究、临床指南）
- **General DB**: 通用知识（生活经验、社会文化、实用技能）

## 推荐知识库构成

### 1. Professional Knowledge Database (16本经典)

| 类别 | 推荐书籍 | 作用 |
|-----|---------|------|
| **心理咨询理论** | 《心理咨询与治疗的理论与实践》(Corey) | 提供主要流派 overview |
| **认知行为** | 《认知疗法：基础与应用》(Beck) | CBT核心技术 |
| **人本主义** | 《个人形成论》(Rogers) | 共情和无条件积极关注 |
| **精神分析** | 《精神分析导论》(Freud) | 深层心理动力 |
| **家庭治疗** | 《家庭治疗：概念与方法》(Nichols) | 系统视角 |
| **危机干预** | 《危机干预策略》(James) | 自杀/危机处理 |
| **发展心理学** | 《发展心理学》(Santrock) | 生命周期视角 |
| **社会心理学** | 《社会心理学》(Myers/David) | 群体/人际现象 |
| **异常心理学** | 《异常心理学》(Barlow) | 诊断和理解障碍 |
| **正念/接纳** | 《接纳承诺疗法》(Hayes) | ACT技术 |
| **积极心理学** | 《真实的幸福》(Seligman) | 优势和韧性 |
| **创伤治疗** | 《身体从未忘记》(van der Kolk) | 创伤知情护理 |
| **情绪调节** | 《情绪调节手册》(Gross) | 情绪管理策略 |
| **人际关系** | 《亲密关系》(Miller) | 关系动力学 |
| **职业咨询** | 《职业心理学》(Brown) | 职场心理问题 |
| **伦理准则** | 《中国心理学会临床与咨询心理学工作伦理守则》| 专业伦理 |

### 2. General Knowledge Database (979本/文章)

| 类别 | 内容示例 | 作用 |
|-----|---------|------|
| **生活技能** | 沟通技巧、时间管理、压力管理 | 实用建议 |
| **社会文化** | 文化习俗、代际差异、社会趋势 | 文化敏感性 |
| **职场经验** | 职场心理学、领导力、团队协作 | 职场问题 |
| **情感关系** | 恋爱心理学、婚姻指导、亲子教育 | 关系问题 |
| **自我成长** | 习惯养成、目标设定、自我认知 | 个人发展 |
| **健康科普** | 睡眠、营养、运动心理健康 | 身心整合 |
| **文学艺术** | 心理学相关的文学、电影、艺术 | 隐喻和表达 |
| **哲学思考** | 人生意义、价值观、存在主义 | 深层探索 |

## 构建步骤

### Step 1: 准备数据

```bash
# 创建目录结构
mkdir -p knowledge_base/{professional,general}/{raw,processed,vectors}

# 收集PDF书籍
# professional/raw/ - 放入16本专业书籍PDF
general/raw/ - 放入979本通用知识PDF/TXT
```

### Step 2: 文本提取与清洗

```python
from PyPDF2 import PdfReader
import re

def extract_text_from_pdf(pdf_path):
    """从PDF提取文本"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_text(text):
    """清洗文本"""
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 去除页码和页眉
    text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
    return text.strip()
```

### Step 3: 文本分块

```python
def chunk_text(text, chunk_size=300, chunk_overlap=30):
    """
    将文本分块
    
    Args:
        text: 原始文本
        chunk_size: 每块字数
        chunk_overlap: 重叠字数
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks
```

### Step 4: 生成 Embeddings

```python
from sentence_transformers import SentenceTransformer

# 加载模型
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

def generate_embeddings(chunks):
    """生成向量表示"""
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings
```

### Step 5: 构建向量索引

```python
import faiss
import numpy as np

def build_faiss_index(embeddings, save_path):
    """构建FAISS索引"""
    dimension = embeddings.shape[1]
    
    # 使用内积（余弦相似度）
    index = faiss.IndexFlatIP(dimension)
    
    # 添加向量
    index.add(embeddings.astype('float32'))
    
    # 保存索引
    faiss.write_index(index, save_path)
    
    return index
```

### Step 6: 完整构建脚本

```python
# build_kb.py
import os
import json
import pickle
from pathlib import Path

class KnowledgeBaseBuilder:
    def __init__(self, config):
        self.config = config
        self.model = SentenceTransformer(config['embedding_model'])
    
    def build_kb(self, source_dir, output_dir, kb_type):
        """构建知识库"""
        print(f"Building {kb_type} knowledge base...")
        
        # 1. 提取所有文档
        all_chunks = []
        chunk_metadata = []
        
        for file_path in Path(source_dir).glob('*'):
            print(f"Processing {file_path.name}...")
            
            # 提取文本
            if file_path.suffix == '.pdf':
                text = extract_text_from_pdf(file_path)
            elif file_path.suffix in ['.txt', '.md']:
                text = file_path.read_text(encoding='utf-8')
            
            # 清洗
            text = clean_text(text)
            
            # 分块
            chunks = chunk_text(
                text,
                self.config['chunk_size'],
                self.config['chunk_overlap']
            )
            
            # 记录元数据
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata.append({
                    'source': file_path.name,
                    'chunk_id': i,
                    'kb_type': kb_type
                })
        
        # 2. 生成embeddings
        print("Generating embeddings...")
        embeddings = self.model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        )
        
        # 3. 构建索引
        print("Building index...")
        index = build_faiss_index(embeddings, f"{output_dir}/index.faiss")
        
        # 4. 保存数据
        with open(f"{output_dir}/chunks.pkl", 'wb') as f:
            pickle.dump(all_chunks, f)
        
        with open(f"{output_dir}/metadata.json", 'w') as f:
            json.dump(chunk_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"{kb_type} KB built: {len(all_chunks)} chunks")

# 使用
config = {
    'embedding_model': 'BAAI/bge-large-zh-v1.5',
    'chunk_size': 300,
    'chunk_overlap': 30
}

builder = KnowledgeBaseBuilder(config)

# 构建专业知识库
builder.build_kb(
    'knowledge_base/professional/raw',
    'knowledge_base/professional/processed',
    'professional'
)

# 构建通用知识库
builder.build_kb(
    'knowledge_base/general/raw',
    'knowledge_base/general/processed',
    'general'
)
```

## 数据库配置

### 目录结构

```
knowledge_base/
├── professional/
│   ├── raw/                    # 原始PDF
│   ├── processed/
│   │   ├── index.faiss        # FAISS索引
│   │   ├── chunks.pkl         # 文本块
│   │   └── metadata.json      # 元数据
│   └── vectors/               # 可选：原始向量
├── general/
│   ├── raw/
│   ├── processed/
│   │   ├── index.faiss
│   │   ├── chunks.pkl
│   │   └── metadata.json
│   └── vectors/
└── config.json                # 配置文件
```

### 配置文件

```json
{
  "professional": {
    "index_path": "knowledge_base/professional/processed/index.faiss",
    "chunks_path": "knowledge_base/professional/processed/chunks.pkl",
    "metadata_path": "knowledge_base/professional/processed/metadata.json",
    "num_books": 16,
    "description": "专业心理学知识库"
  },
  "general": {
    "index_path": "knowledge_base/general/processed/index.faiss",
    "chunks_path": "knowledge_base/general/processed/chunks.pkl",
    "metadata_path": "knowledge_base/general/processed/metadata.json",
    "num_books": 979,
    "description": "通用生活知识库"
  },
  "embedding_model": "BAAI/bge-large-zh-v1.5",
  "chunk_size": 300,
  "chunk_overlap": 30,
  "dimension": 1024
}
```

## 检索配置

### 重排序 (Cross-Encoder)

```python
from sentence_transformers import CrossEncoder

# 加载重排序模型
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, retrieved_docs, top_k=5):
    """重排序检索结果"""
    pairs = [(query, doc) for doc in retrieved_docs]
    scores = reranker.predict(pairs)
    
    # 按分数排序
    ranked = sorted(
        zip(retrieved_docs, scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [doc for doc, score in ranked[:top_k]]
```

### 混合检索

```python
def hybrid_search(query, index, chunks, alpha=0.7):
    """
    混合检索：向量检索 + 关键词检索
    
    Args:
        alpha: 向量检索权重
    """
    # 向量检索
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, k=20)
    
    # 关键词检索 (BM25)
    from rank_bm25 import BM25Okapi
    tokenized_chunks = [c.split() for c in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # 融合
    final_scores = alpha * vector_scores + (1-alpha) * bm25_scores
    
    return final_scores
```

## 性能优化

### 1. 索引优化

```python
# 使用IVF索引加速大规模检索
nlist = 100  # 聚类中心数
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# 训练索引
index.train(embeddings.astype('float32'))
index.add(embeddings.astype('float32'))

# 设置搜索参数
index.nprobe = 10  # 搜索的聚类数
```

### 2. 缓存策略

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_search(query_hash, k):
    """缓存频繁查询"""
    return search(query_hash, k)
```

### 3. 异步加载

```python
import asyncio

async def load_kb_async(config):
    """异步加载知识库"""
    loop = asyncio.get_event_loop()
    
    # 并行加载两个知识库
    prof_task = loop.run_in_executor(None, load_kb, config['professional'])
    gen_task = loop.run_in_executor(None, load_kb, config['general'])
    
    prof_kb, gen_kb = await asyncio.gather(prof_task, gen_task)
    
    return prof_kb, gen_kb
```

## 维护与更新

### 增量更新

```python
def incremental_update(kb_path, new_documents):
    """增量更新知识库"""
    # 加载现有索引
    index = faiss.read_index(f"{kb_path}/index.faiss")
    
    # 处理新文档
    new_chunks = []
    for doc in new_documents:
        chunks = chunk_text(extract_text(doc))
        new_chunks.extend(chunks)
    
    # 生成新embeddings
    new_embeddings = model.encode(new_chunks)
    
    # 添加到索引
    index.add(new_embeddings.astype('float32'))
    
    # 保存更新后的索引
    faiss.write_index(index, f"{kb_path}/index.faiss")
```

### 版本控制

```
knowledge_base/
├── v1.0/          # 初始版本
├── v1.1/          # 新增3本书
├── v2.0/          # 更换embedding模型
└── current -> v2.0  # 符号链接
```

## 资源需求

| 知识库 | 存储 | 内存 | 构建时间 |
|-------|------|------|---------|
| Professional (16本) | ~500MB | ~1GB | ~5分钟 |
| General (979本) | ~20GB | ~8GB | ~2小时 |
| 总计 | ~20.5GB | ~16GB | ~2.5小时 |

## 推荐工具

- **PDF解析**: PyPDF2, pdfplumber, marker
- **文本分块**: LangChain TextSplitter
- **向量库**: FAISS, Milvus, Chroma
- **Embedding**: BGE, M3E, OpenAI
- **重排序**: Cross-Encoder

## 注意事项

1. **版权问题**: 确保使用的书籍有合法授权
2. **隐私保护**: 不要包含真实案例的个人信息
3. **内容审核**: 定期审查知识库内容准确性
4. **备份策略**: 定期备份索引和元数据
