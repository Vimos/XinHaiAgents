#!/usr/bin/env python3
"""
CascadeRCG - Retrieval-Augmented Generation for Enhancing 
Professionalism and Knowledgeability in Online Mental Health Support

Based on: WWW Companion 2025
Authors: Di Yang, Jingwei Zhu, Haihong Wu, Minghuan Tan, et al.
"""

import os
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans

# Optional imports - will use mock if not available
try:
    from sentence_transformers import SentenceTransformer
    from langchain.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("Warning: Optional dependencies not installed. Using mock mode.")


@dataclass
class RetrievalResult:
    """检索结果数据类"""
    query: str
    documents: List[str]
    filtered_documents: List[str]
    summary: str


@dataclass
class CascadeRCGConfig:
    """CascadeRCG配置"""
    chunk_size: int = 300
    chunk_overlap: int = 30
    first_stage_k: int = 2
    second_stage_m: int = 1
    num_clusters: int = 4
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    
    # Prompts
    three_ws_prompt: str = """请将以下咨询问题按照"What-Why-How"框架分解：

问题：{question}

要求：
- What: 识别关键心理学概念或现象
- Why: 分析可能的心理学原因
- How: 提供可行的解决建议

输出格式：
What: ...
Why: ...
How: ..."""
    
    filter_prompt: str = """判断以下检索到的文档是否与查询相关。

查询: {query}
文档: {document}

如果文档包含对查询有用的信息，回答"相关"。
否则回答"不相关"。

回答:"""
    
    summarize_prompt: str = """请总结以下与查询相关的文档内容。

查询: {query}
文档: {documents}

要求：
1. 提取与查询直接相关的信息
2. 去除冗余内容
3. 保持关键概念和观点
4. 控制在100字以内

总结:"""
    
    generation_prompt: str = """基于以下检索到的专业知识，回答用户的咨询问题。

原始问题: {question}

相关知识:
{summaries}

要求：
1. 准确应用心理学专业知识
2. 引用相关理论和研究
3. 结合生活经验和实际建议
4. 语言温和、支持性
5. 避免有害或不确定的建议

请生成专业且富有知识性的回复:"""


class MockLLM:
    """Mock LLM for testing"""
    def generate(self, prompt: str) -> str:
        """模拟生成"""
        if "Three Ws" in prompt or "What-Why-How" in prompt:
            return self._mock_three_ws(prompt)
        elif "filter" in prompt.lower() or "相关" in prompt:
            return "相关"
        elif "summarize" in prompt.lower() or "总结" in prompt:
            return "这是相关内容的总结..."
        else:
            return "这是一个专业且富有知识性的回复..."
    
    def _mock_three_ws(self, prompt: str) -> str:
        """模拟Three Ws分解"""
        return """What: 群体思维现象、人际冲突、舒适度问题
Why: 多元无知效应、对自我价值的不确定、担心被视为麻烦制造者
How: 沟通技巧、自信表达、寻求折中方案"""


class CascadeRCG:
    """
    CascadeRCG主类
    
    双库交叉迭代检索框架，提升咨询回复的专业性和知识性
    """
    
    def __init__(
        self,
        professional_db_path: Optional[str] = None,
        general_db_path: Optional[str] = None,
        embedding_model: str = "BAAI/bge-large-zh-v1.5",
        llm_model: Optional[str] = None,
        config: Optional[CascadeRCGConfig] = None
    ):
        """
        初始化CascadeRCG
        
        Args:
            professional_db_path: 专业知识库路径
            general_db_path: 通用知识库路径
            embedding_model: Embedding模型名称
            llm_model: LLM模型名称
            config: 配置对象
        """
        self.config = config or CascadeRCGConfig()
        self.config.embedding_model = embedding_model
        
        # 初始化LLM（实际应接入真实LLM）
        self.llm = MockLLM()
        
        # 初始化Embedding模型
        self.embedding_model = self._init_embedding_model()
        
        # 加载知识库
        self.professional_db = self._load_database(professional_db_path, "professional")
        self.general_db = self._load_database(general_db_path, "general")
    
    def _init_embedding_model(self):
        """初始化embedding模型"""
        if HAS_DEPS:
            try:
                return SentenceTransformer(self.config.embedding_model)
            except:
                return None
        return None
    
    def _load_database(self, db_path: Optional[str], db_type: str):
        """加载知识库"""
        if db_path and os.path.exists(db_path):
            # 实际应加载向量数据库
            return {"path": db_path, "type": db_type, "loaded": True}
        return {"path": db_path, "type": db_type, "loaded": False}
    
    def generate(self, query: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        生成专业咨询回复
        
        Args:
            query: 用户查询
            conversation_history: 对话历史（可选）
            
        Returns:
            生成的回复
        """
        # Step 1: Three Ws 查询重写
        print(f"[CascadeRCG] Step 1: Three Ws rewriting for query: {query[:50]}...")
        sub_queries = self._three_ws_rewrite(query)
        
        # Step 2: 第一阶段检索
        print(f"[CascadeRCG] Step 2: First stage retrieval (K={self.config.first_stage_k})")
        prof_results = self._retrieve_filter_summarize(
            sub_queries, self.professional_db, self.config.first_stage_k
        )
        gen_results = self._retrieve_filter_summarize(
            sub_queries, self.general_db, self.config.first_stage_k
        )
        
        # Step 3: 第二阶段交叉检索
        print(f"[CascadeRCG] Step 3: Cross retrieval (M={self.config.second_stage_m})")
        cross_prof = self._cross_retrieve(
            gen_results, self.professional_db, self.config.second_stage_m
        )
        cross_gen = self._cross_retrieve(
            prof_results, self.general_db, self.config.second_stage_m
        )
        
        # Step 4: 聚类与总结
        print(f"[CascadeRCG] Step 4: Clustering (J={self.config.num_clusters}) and summarizing")
        all_results = prof_results + gen_results + cross_prof + cross_gen
        cluster_summaries = self._cluster_and_summarize(
            all_results, self.config.num_clusters
        )
        
        # Step 5: 最终生成
        print("[CascadeRCG] Step 5: Final generation")
        response = self._generate_final_response(query, cluster_summaries)
        
        return response
    
    def _three_ws_rewrite(self, query: str) -> List[str]:
        """
        Three Ws查询重写
        
        Args:
            query: 原始查询
            
        Returns:
            分解后的子查询列表
        """
        prompt = self.config.three_ws_prompt.format(question=query)
        result = self.llm.generate(prompt)
        
        # 解析结果
        sub_queries = []
        lines = result.strip().split('\n')
        
        for line in lines:
            if line.startswith('What:') or line.startswith('Why:') or line.startswith('How:'):
                sub_query = line.split(':', 1)[1].strip()
                if sub_query:
                    sub_queries.append(sub_query)
        
        # 如果解析失败，返回原始查询
        if not sub_queries:
            sub_queries = [query]
        
        return sub_queries
    
    def _retrieve_filter_summarize(
        self,
        queries: List[str],
        database: Dict,
        k: int
    ) -> List[RetrievalResult]:
        """
        检索-过滤-总结（函数C）
        
        Args:
            queries: 查询列表
            database: 知识库
            k: 检索数量
            
        Returns:
            检索结果列表
        """
        results = []
        
        for query in queries:
            # 检索Top-K（模拟）
            retrieved_docs = self._mock_retrieve(query, database, k)
            
            # 过滤
            filtered_docs = []
            for doc in retrieved_docs:
                is_relevant = self._filter(query, doc)
                if is_relevant:
                    filtered_docs.append(doc)
            
            # 总结
            if filtered_docs:
                summary = self._summarize(query, filtered_docs)
                results.append(RetrievalResult(
                    query=query,
                    documents=retrieved_docs,
                    filtered_documents=filtered_docs,
                    summary=summary
                ))
        
        return results
    
    def _mock_retrieve(self, query: str, database: Dict, k: int) -> List[str]:
        """模拟检索"""
        # 实际应调用向量数据库
        return [f"相关文档{i}: 关于{query}的内容..." for i in range(k)]
    
    def _filter(self, query: str, document: str) -> bool:
        """
        过滤文档
        
        Args:
            query: 查询
            document: 文档
            
        Returns:
            是否相关
        """
        prompt = self.config.filter_prompt.format(
            query=query,
            document=document
        )
        result = self.llm.generate(prompt).strip()
        
        return "相关" in result or "relevant" in result.lower()
    
    def _summarize(self, query: str, documents: List[str]) -> str:
        """
        总结文档
        
        Args:
            query: 查询
            documents: 文档列表
            
        Returns:
            总结
        """
        docs_text = "\n".join(documents)
        prompt = self.config.summarize_prompt.format(
            query=query,
            documents=docs_text
        )
        summary = self.llm.generate(prompt).strip()
        
        return summary
    
    def _cross_retrieve(
        self,
        source_results: List[RetrievalResult],
        target_database: Dict,
        m: int
    ) -> List[RetrievalResult]:
        """
        交叉检索
        
        Args:
            source_results: 源结果列表
            target_database: 目标知识库
            m: 检索数量
            
        Returns:
            交叉检索结果
        """
        # 提取源结果中的总结作为查询
        cross_queries = [r.summary for r in source_results if r.summary]
        
        # 在目标库中检索
        return self._retrieve_filter_summarize(cross_queries, target_database, m)
    
    def _cluster_and_summarize(
        self,
        results: List[RetrievalResult],
        j: int
    ) -> List[str]:
        """
        聚类并总结
        
        Args:
            results: 检索结果列表
            j: 聚类数量
            
        Returns:
            聚类总结列表
        """
        if not results:
            return []
        
        # 准备聚类数据
        texts = [f"{r.query} {r.summary}" for r in results]
        
        if self.embedding_model:
            # 真实聚类
            embeddings = self.embedding_model.encode(texts)
            
            # K-means聚类
            kmeans = KMeans(n_clusters=min(j, len(results)), random_state=42)
            labels = kmeans.fit_predict(embeddings)
        else:
            # 模拟聚类
            labels = list(range(len(results)) % j)
        
        # 每簇总结
        cluster_summaries = []
        for cluster_id in range(min(j, len(results))):
            cluster_results = [
                results[i] for i in range(len(results)) 
                if labels[i] == cluster_id
            ]
            
            if cluster_results:
                cluster_text = "\n".join([
                    f"Q: {r.query}\nS: {r.summary}" 
                    for r in cluster_results
                ])
                
                summary = self._summarize_cluster(cluster_text)
                cluster_summaries.append(summary)
        
        return cluster_summaries
    
    def _summarize_cluster(self, cluster_text: str) -> str:
        """总结聚类内容"""
        prompt = f"""请总结以下聚类内的所有查询-检索对。

聚类内容: {cluster_text}

要求：
1. 识别共同主题
2. 综合关键信息
3. 去除重复内容
4. 生成连贯的段落

聚类总结:"""
        
        return self.llm.generate(prompt).strip()
    
    def _generate_final_response(self, query: str, summaries: List[str]) -> str:
        """
        生成最终回复
        
        Args:
            query: 原始查询
            summaries: 聚类总结列表
            
        Returns:
            最终回复
        """
        summaries_text = "\n\n".join([f"[{i+1}] {s}" for i, s in enumerate(summaries)])
        
        prompt = self.config.generation_prompt.format(
            question=query,
            summaries=summaries_text
        )
        
        response = self.llm.generate(prompt).strip()
        
        return response
    
    def generate_multi_turn(
        self,
        current_query: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        多轮对话生成
        
        Args:
            current_query: 当前查询
            history: 对话历史 [{"role": "user"/"assistant", "content": ...}]
            
        Returns:
            生成的回复
        """
        # 构建上下文
        context = self._build_context(history)
        
        # 结合上下文和当前查询
        enriched_query = f"{context}\n当前问题: {current_query}"
        
        return self.generate(enriched_query)
    
    def _build_context(self, history: List[Dict[str, str]]) -> str:
        """构建对话上下文"""
        context_parts = []
        
        for turn in history[-5:]:  # 最近5轮
            role = "来访者" if turn["role"] == "user" else "咨询师"
            context_parts.append(f"{role}: {turn['content']}")
        
        return "\n".join(context_parts)


class KnowledgeBaseBuilder:
    """知识库构建器"""
    
    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 30,
        embedding_model: str = "BAAI/bge-large-zh-v1.5"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
    
    def build_from_books(
        self,
        book_paths: List[str],
        db_name: str,
        db_type: str = "professional"
    ) -> str:
        """
        从书籍构建知识库
        
        Args:
            book_paths: 书籍路径列表
            db_name: 知识库名称
            db_type: 知识库类型 (professional/general)
            
        Returns:
            知识库路径
        """
        print(f"[KB Builder] Building {db_type} knowledge base: {db_name}")
        print(f"[KB Builder] Processing {len(book_paths)} books...")
        
        # 实际应实现PDF解析、分块、向量化
        db_path = f"knowledge_bases/{db_name}"
        
        print(f"[KB Builder] Knowledge base saved to: {db_path}")
        return db_path
    
    def build_from_sources(
        self,
        sources: List[str],
        db_name: str,
        db_type: str = "general"
    ) -> str:
        """
        从多种来源构建知识库
        
        Args:
            sources: 来源路径列表
            db_name: 知识库名称
            db_type: 知识库类型
            
        Returns:
            知识库路径
        """
        print(f"[KB Builder] Building {db_type} knowledge base from sources: {db_name}")
        
        db_path = f"knowledge_bases/{db_name}"
        
        print(f"[KB Builder] Knowledge base saved to: {db_path}")
        return db_path


# 使用示例
if __name__ == "__main__":
    # 初始化CascadeRCG
    cascadercg = CascadeRCG(
        professional_db_path="path/to/professional_db",
        general_db_path="path/to/general_db"
    )
    
    # 测试查询
    test_query = "我22岁实习生，办公室空调太冷不敢提意见，很困扰"
    
    print(f"\n用户问题: {test_query}\n")
    print("=" * 60)
    
    response = cascadercg.generate(test_query)
    
    print("\n生成的回复:")
    print(response)
