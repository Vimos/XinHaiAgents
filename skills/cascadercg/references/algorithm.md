# CascadeRCG 算法详解

## 完整算法流程 (Algorithm 1)

```
输入: 问题Q, 专业知识库P, 通用知识库G, 
     重写提示pr, 过滤提示pf, 总结提示ps, 生成提示pg,
     第一阶段检索数K, 第二阶段检索数M, 聚类数J

输出: 答案Ans

1. Qs ← Rewrite(Q, pr) = {q1, q2, ..., qL}  // Three Ws重写
   RES ← ∅

2. 定义函数C(Query, Database, pf, ps, K):
3.   Rdocs ← ∅, RdocsE ← ∅
4.   for q ∈ Query do:
5.     for k ∈ [1, K] do:
6.       rqk ← Retrieve(Database, q)  // 检索
7.       if ¬filter((q, rqk), pf) then:  // 过滤
8.         Rdocs ← Rdocs ∪ {(q, rqk)}
9.   RdocsE ← RdocsE ∪ {(qe, re) | (qe, re) = S(q, (Rdocs(q)), ps)}  // 总结
10.  return RdocE

11. RPE ← C(Qs, P, pf, ps, K)   // 从专业知识库检索
    RGE ← C(Qs, G, pf, ps, K)   // 从通用知识库检索

12. R2PE ← C(RGE, P, pf, ps, M)  // 交叉：通用→专业
    R2GE ← C(RPE, G, pf, ps, M)  // 交叉：专业→通用

13. RE ← RPE ∪ RGE ∪ R2PE ∪ R2GE  // 合并所有结果

14. C ← Cluster(RE, J) = {C1, C2, ..., CJ}  // 聚类

15. for j ∈ [1, J] do:
16.   RES ← RES ∪ S(Cj, ps)  // 每簇总结

17. Ans ← Generation(RES, Q, pg)  // 最终生成

18. return Ans
```

## 关键步骤详解

### 1. Three Ws 查询重写

**目的**: 将复杂咨询问题分解为更简单的子问题

**三个维度**:
- **What**: 关键心理概念或现象是什么？
- **Why**: 背后的原因或理论依据是什么？
- **How**: 对应的解决方法或应对策略是什么？

**示例**:
```
原始问题: "我22岁实习生，办公室空调太冷不敢提意见，很困扰"

Three Ws分解:
- What: 群体思维现象、人际冲突、舒适度问题
- Why: 多元无知效应、对自我价值的不确定、担心被视为麻烦制造者
- How: 沟通技巧、自信表达、寻求折中方案
```

**提示模板**:
```
请将以下咨询问题按照"What-Why-How"框架分解：

问题：{question}

要求：
- What: 识别关键心理学概念或现象
- Why: 分析可能的心理学原因
- How: 提供可行的解决建议

输出格式：
What: ...
Why: ...
How: ...
```

### 2. 检索-过滤-总结 (函数C)

```python
def retrieve_filter_summarize(queries, database, K, filter_prompt, summarize_prompt):
    """
    对每个查询进行检索、过滤和总结
    
    Args:
        queries: 查询列表 [q1, q2, ...]
        database: 知识库
        K: 每查询检索文档数
        filter_prompt: 过滤提示
        summarize_prompt: 总结提示
    
    Returns:
        总结后的(query, summary)对列表
    """
    results = []
    
    for query in queries:
        # 检索Top-K
        retrieved_docs = retrieve(query, database, top_k=K)
        
        # 过滤相关文档
        filtered_docs = []
        for doc in retrieved_docs:
            if llm_filter(query, doc, filter_prompt):
                filtered_docs.append(doc)
        
        # 总结过滤后的文档
        if filtered_docs:
            summary = llm_summarize(query, filtered_docs, summarize_prompt)
            results.append((query, summary))
    
    return results
```

**过滤提示**:
```
判断以下检索到的文档是否与查询相关。

查询: {query}
文档: {document}

如果文档包含对查询有用的信息，回答"相关"。
否则回答"不相关"。

回答: [相关/不相关]
```

**总结提示**:
```
请总结以下与查询相关的文档内容。

查询: {query}
文档: {documents}

要求：
1. 提取与查询直接相关的信息
2. 去除冗余内容
3. 保持关键概念和观点
4. 控制在100字以内

总结:
```

### 3. 两阶段交叉检索

**第一阶段 (First Retrieval)**:
- 从专业知识库检索 → 过滤总结
- 从通用知识库检索 → 过滤总结

**第二阶段 (Cross Retrieval)**:
- 用通用知识库的总结 → 查询专业知识库（补充理论支撑）
- 用专业知识库的总结 → 查询通用知识库（补充生活视角）

**交叉优势**:
1. **互补性**: 专业知识+生活经验=更全面的回复
2. **平衡性**: 避免通用知识淹没专业知识
3. **深度性**: 理论+实践=更有说服力的建议

### 4. 聚类-总结策略

**目的**: 减少生成提示长度，提高信息密度

**流程**:
```python
def cluster_then_summarize(query_retrieval_pairs, J):
    """
    聚类然后总结
    
    Args:
        query_retrieval_pairs: [(query1, summary1), (query2, summary2), ...]
        J: 聚类数量
    
    Returns:
        聚类级总结列表
    """
    # 1. 计算embedding
    embeddings = [get_embedding(f"{q} {s}") for q, s in query_retrieval_pairs]
    
    # 2. 聚类 (K-means, J=4)
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=J, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    
    # 3. 每簇总结
    cluster_summaries = []
    for j in range(J):
        cluster_pairs = [query_retrieval_pairs[i] for i in range(len(labels)) if labels[i] == j]
        cluster_content = "\n".join([f"Q: {q}\nS: {s}" for q, s in cluster_pairs])
        
        summary = llm_summarize_cluster(cluster_content)
        cluster_summaries.append(summary)
    
    return cluster_summaries
```

**聚类总结提示**:
```
请总结以下聚类内的所有查询-检索对。

聚类内容: {cluster_content}

要求：
1. 识别共同主题
2. 综合关键信息
3. 去除重复内容
4. 生成连贯的段落

聚类总结:
```

### 5. 最终生成

**输入**:
- 原始问题
- 聚类级总结列表

**提示模板**:
```
基于以下检索到的专业知识，回答用户的咨询问题。

原始问题: {question}

相关知识:
{cluster_summaries}

要求：
1. 准确应用心理学专业知识
2. 引用相关理论和研究
3. 结合生活经验和实际建议
4. 语言温和、支持性
5. 避免有害或不确定的建议

请生成专业且富有知识性的回复:
```

## 超参数调优指南

| 参数 | 推荐值 | 说明 |
|-----|-------|------|
| **chunk_size** | 300 | 文档分块大小 |
| **chunk_overlap** | 30 | 分块重叠，保持上下文 |
| **first_stage_K** | 2 | 第一阶段每查询检索数 |
| **second_stage_M** | 1 | 第二阶段交叉检索数 |
| **clusters_J** | 4 | 聚类数量 |

**调优建议**:
- K增大 → 召回率↑，但噪声↑
- M增大 → 交叉效果↑，但延迟↑
- J增大 → 粒度更细，但总结成本↑

## 性能优化

### 1. 向量索引

使用 FAISS 或 Milvus 加速向量检索:
```python
import faiss

# 构建索引
index = faiss.IndexFlatIP(dimension)  # 内积（余弦相似度）
index.add(embeddings)

# 检索
distances, indices = index.search(query_embedding, k=K)
```

### 2. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_retrieve(query_hash, database_name, k):
    """缓存频繁查询的结果"""
    return retrieve(query_hash, database_name, k)
```

### 3. 异步处理

```python
import asyncio

async def parallel_retrieval(queries, databases):
    """并行检索多个查询和数据库"""
    tasks = []
    for query in queries:
        for db in databases:
            tasks.append(asyncio.create_task(retrieve_async(query, db)))
    
    results = await asyncio.gather(*tasks)
    return results
```

## 错误处理

### 常见问题

1. **检索结果为空**
   - 检查知识库覆盖度
   - 降低过滤阈值
   - 增加K值

2. **幻觉仍然存在**
   - 加强过滤提示
   - 增加总结约束
   - 添加事实核查步骤

3. **回复过于学术化**
   - 调整生成提示，强调通俗性
   - 增加通用知识权重
   - 添加语言风格示例

4. **响应时间过长**
   - 使用向量索引
   - 减少K和M
   - 启用缓存
