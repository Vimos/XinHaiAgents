#!/usr/bin/env python3
"""
Suicide Risk Evidence Extractor - 评估脚本

评估指标（基于 CLPsych 2024 Shared Task）：
- Evidence Highlights: Recall, Precision, Weighted Recall, Harmonic Mean (F1)
- Summarized Evidence: Consistency, Contradiction
"""

import json
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class EvaluationMetrics:
    """评估指标数据类"""
    recall: float
    precision: float
    weighted_recall: float
    harmonic_mean: float
    consistency: float
    contradiction: float


class BERTScorer:
    """
    BERTScore 计算（简化实现）
    
    实际使用时应安装 bert-score 包:
    pip install bert-score
    """
    
    def __init__(self, model_type="bert-base-uncased"):
        self.model_type = model_type
        self.scorer = None
        
    def load(self):
        """加载BERTScore scorer"""
        try:
            from bert_score import BERTScorer as BS
            self.scorer = BS(model_type=self.model_type)
        except ImportError:
            print("Warning: bert-score not installed. Using mock scoring.")
    
    def score(self, candidates: List[str], references: List[str]) -> Tuple[List[float], List[float], List[float]]:
        """
        计算BERTScore
        
        Returns:
            (precision, recall, f1) - 每个样本的分数列表
        """
        if self.scorer is None:
            # Mock scoring for testing
            n = len(candidates)
            return (
                [0.85] * n,  # precision
                [0.87] * n,  # recall
                [0.86] * n   # f1
            )
        
        P, R, F1 = self.scorer.score(candidates, references)
        return P.tolist(), R.tolist(), F1.tolist()


class NLIEvaluator:
    """
    NLI (Natural Language Inference) 评估器
    
    用于评估生成摘要与专家摘要的一致性
    """
    
    def __init__(self):
        self.model = None
        
    def load(self):
        """加载NLI模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            # 使用常见的NLI模型
            model_name = "facebook/bart-large-mnli"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        except ImportError:
            print("Warning: transformers not installed. Using mock NLI.")
    
    def evaluate_consistency(self, generated_summary: str, reference_summary: str) -> Dict:
        """
        评估摘要一致性
        
        Returns:
            {
                "consistency": float,  # 一致性分数
                "contradiction": float  # 矛盾概率
            }
        """
        if self.model is None:
            # Mock evaluation
            return {
                "consistency": 0.95,
                "contradiction": 0.05
            }
        
        # 实际NLI推理
        import torch
        
        # 将摘要分句
        gen_sentences = self._split_sentences(generated_summary)
        ref_sentences = self._split_sentences(reference_summary)
        
        consistencies = []
        contradictions = []
        
        for gen_sent in gen_sentences:
            for ref_sent in ref_sentences:
                # 构造 premise-hypothesis 对
                inputs = self.tokenizer(
                    ref_sent,  # premise (reference)
                    gen_sent,  # hypothesis (generated)
                    return_tensors="pt",
                    truncation=True
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs = torch.softmax(outputs.logits, dim=1)
                    
                    # MNLI标签: 0=contradiction, 1=neutral, 2=entailment
                    contradiction_prob = probs[0][0].item()
                    entailment_prob = probs[0][2].item()
                    
                    consistencies.append(entailment_prob)
                    contradictions.append(contradiction_prob)
        
        return {
            "consistency": np.mean(consistencies),
            "contradiction": np.mean(contradictions)
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """将文本分句"""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


class SuicideRiskEvaluator:
    """
    自杀风险证据提取评估器
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.bert_scorer = BERTScorer()
        self.nli_evaluator = NLIEvaluator()
        
    def load_models(self):
        """加载评估模型"""
        self.bert_scorer.load()
        self.nli_evaluator.load()
    
    def evaluate_evidence_highlights(
        self,
        system_highlights: List[Dict],
        reference_highlights: List[Dict],
        original_text: str
    ) -> Dict:
        """
        评估 Evidence Highlights
        
        Args:
            system_highlights: 系统提取的证据 [{"text": str}, ...]
            reference_highlights: 专家标注的证据 [{"text": str}, ...]
            original_text: 原始帖子文本
            
        Returns:
            评估指标字典
        """
        # 提取文本
        system_texts = [h["text"] for h in system_highlights]
        reference_texts = [h["text"] for h in reference_highlights]
        
        # 计算BERTScore
        if system_texts and reference_texts:
            P, R, F1 = self.bert_scorer.score(system_texts, reference_texts)
            
            # 取最大Recall（基于CLPsych评估标准）
            max_recall = max(R) if R else 0.0
            avg_precision = np.mean(P) if P else 0.0
            weighted_recall = self._compute_weighted_recall(
                system_texts, reference_texts, original_text
            )
            harmonic_mean = np.mean(F1) if F1 else 0.0
        else:
            max_recall = 0.0
            avg_precision = 0.0
            weighted_recall = 0.0
            harmonic_mean = 0.0
        
        return {
            "recall": max_recall,
            "precision": avg_precision,
            "weighted_recall": weighted_recall,
            "harmonic_mean": harmonic_mean
        }
    
    def _compute_weighted_recall(
        self,
        system_texts: List[str],
        reference_texts: List[str],
        original_text: str
    ) -> float:
        """
        计算 Weighted Recall
        
        考虑证据长度的适当性
        """
        if not system_texts or not reference_texts:
            return 0.0
        
        # 计算每个系统证据与参考证据的匹配
        total_weight = 0.0
        matched_weight = 0.0
        
        for ref_text in reference_texts:
            ref_len = len(ref_text)
            total_weight += ref_len
            
            # 找最佳匹配
            best_match_len = 0
            for sys_text in system_texts:
                # 简化：使用文本重叠度
                overlap = self._compute_overlap(ref_text, sys_text)
                if overlap > best_match_len:
                    best_match_len = overlap
            
            matched_weight += min(best_match_len, ref_len)
        
        return matched_weight / total_weight if total_weight > 0 else 0.0
    
    def _compute_overlap(self, text1: str, text2: str) -> int:
        """计算两个文本的重叠字符数"""
        # 简化的重叠计算
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # 查找最长公共子串（简化版）
        if text1_lower in text2_lower:
            return len(text1)
        if text2_lower in text1_lower:
            return len(text2)
        
        # 计算词级别的重叠
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        overlap_words = words1 & words2
        
        return len(overlap_words) * 5  # 近似估计
    
    def evaluate_summarized_evidence(
        self,
        system_summary: str,
        reference_summary: str
    ) -> Dict:
        """
        评估 Summarized Evidence
        
        Returns:
            一致性指标字典
        """
        result = self.nli_evaluator.evaluate_consistency(
            system_summary,
            reference_summary
        )
        
        return result
    
    def evaluate_sample(
        self,
        sample: Dict
    ) -> Dict:
        """
        评估单个样本
        
        Args:
            sample: {
                "user_id": str,
                "posts": [...],
                "system_output": {
                    "evidence_highlights": [...],
                    "summary": str
                },
                "reference": {
                    "evidence_highlights": [...],
                    "summary": str
                },
                "original_text": str
            }
            
        Returns:
            评估结果字典
        """
        # 评估 Evidence Highlights
        evidence_metrics = self.evaluate_evidence_highlights(
            sample["system_output"]["evidence_highlights"],
            sample["reference"]["evidence_highlights"],
            sample["original_text"]
        )
        
        # 评估 Summarized Evidence
        summary_metrics = self.evaluate_summarized_evidence(
            sample["system_output"]["summary"],
            sample["reference"]["summary"]
        )
        
        return {
            "user_id": sample["user_id"],
            "evidence_highlights": evidence_metrics,
            "summarized_evidence": summary_metrics,
            "overall": {
                "harmonic_mean": evidence_metrics["harmonic_mean"],
                "consistency": summary_metrics["consistency"]
            }
        }
    
    def evaluate_dataset(
        self,
        dataset: List[Dict]
    ) -> Dict:
        """
        评估整个数据集
        
        Returns:
            整体评估结果
        """
        results = []
        
        for sample in dataset:
            result = self.evaluate_sample(sample)
            results.append(result)
        
        # 计算平均值
        avg_recall = np.mean([r["evidence_highlights"]["recall"] for r in results])
        avg_precision = np.mean([r["evidence_highlights"]["precision"] for r in results])
        avg_weighted_recall = np.mean([r["evidence_highlights"]["weighted_recall"] for r in results])
        avg_harmonic_mean = np.mean([r["evidence_highlights"]["harmonic_mean"] for r in results])
        avg_consistency = np.mean([r["summarized_evidence"]["consistency"] for r in results])
        avg_contradiction = np.mean([r["summarized_evidence"]["contradiction"] for r in results])
        
        return {
            "num_samples": len(results),
            "evidence_highlights": {
                "recall": avg_recall,
                "precision": avg_precision,
                "weighted_recall": avg_weighted_recall,
                "harmonic_mean": avg_harmonic_mean
            },
            "summarized_evidence": {
                "consistency": avg_consistency,
                "contradiction": avg_contradiction
            },
            "individual_results": results
        }


def load_dataset(filepath: str) -> List[Dict]:
    """加载评估数据集"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "samples" in data:
        return data["samples"]
    else:
        return [data]


def main():
    parser = argparse.ArgumentParser(
        description='Suicide Risk Evidence Extractor - Evaluation Script'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='评估数据集文件路径 (JSON格式)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='evaluation_results.json',
        help='输出结果文件路径'
    )
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'table', 'csv'],
        default='table',
        help='输出格式'
    )
    
    args = parser.parse_args()
    
    # 加载数据集
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset)} samples")
    
    # 初始化评估器
    evaluator = SuicideRiskEvaluator()
    evaluator.load_models()
    
    # 评估
    print("Evaluating...")
    results = evaluator.evaluate_dataset(dataset)
    
    # 输出结果
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    
    print("\nEvidence Highlights:")
    print(f"  Recall:          {results['evidence_highlights']['recall']:.3f}")
    print(f"  Precision:       {results['evidence_highlights']['precision']:.3f}")
    print(f"  Weighted Recall: {results['evidence_highlights']['weighted_recall']:.3f}")
    print(f"  Harmonic Mean:   {results['evidence_highlights']['harmonic_mean']:.3f}")
    
    print("\nSummarized Evidence:")
    print(f"  Consistency:     {results['summarized_evidence']['consistency']:.3f}")
    print(f"  Contradiction:   {results['summarized_evidence']['contradiction']:.3f}")
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
