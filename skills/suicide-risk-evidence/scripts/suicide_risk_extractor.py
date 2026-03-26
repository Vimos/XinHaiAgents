#!/usr/bin/env python3
"""
Suicide Risk Evidence Extractor
CLPsych 2024 Shared Task 实现

基于 XinHai Healthcare-oriented LLM 的自杀风险证据提取与摘要生成
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RiskEvidence:
    """风险证据数据类"""
    text: str
    start_char: int
    end_char: int
    dimension: str
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class RiskAssessment:
    """风险评估结果数据类"""
    level: str  # "Low Risk", "Moderate Risk", "High Risk"
    confidence: float
    primary_concerns: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """完整分析结果数据类"""
    user_id: str
    risk_assessment: RiskAssessment
    evidence_highlights: List[RiskEvidence]
    summary: str
    metadata: Dict = field(default_factory=dict)


class XinHaiInference:
    """
    XinHai-6B 模型推理封装
    
    基于 ChatGLM3-6B 医疗/心理健康领域微调
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_path = config.get('model_path', 'XinHai-6B')
        self.device = config.get('device', 'cuda')
        self.temperature = config.get('temperature', 0.3)
        self.max_length = config.get('max_length', 4096)
        self.granularity = config.get('granularity', 'phrase')
        
        self.tokenizer = None
        self.model = None
        self.prompt_template = self._load_prompt_template()
        
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        try:
            with open('assets/prompts/cot_gpt4_optimized.json', 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                language = self.config.get('language', 'en')
                if language == 'zh':
                    return template_data.get('chinese_prompt_template', '')
                return template_data.get('prompt_template', '')
        except FileNotFoundError:
            # 返回默认提示词
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """默认提示词模板"""
        return """You are an expert clinical psychologist. Analyze the post for suicide risk evidence across six dimensions: Emotions, Cognitions, Behaviour, Interpersonal, Mental Health, and Context.

Extract exact text spans indicating risk and provide JSON output with evidence highlights and risk assessment.

Post: {post_text}

Output JSON:"""
    
    def load_model(self):
        """加载模型（如果尚未加载）"""
        if self.model is not None:
            return
        
        try:
            from transformers import AutoTokenizer, AutoModel
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device_map='auto'
            ).eval()
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Warning: Could not load model: {e}")
            print("Running in mock mode for testing")
    
    def extract_evidence(self, post_text: str) -> Dict:
        """
        从帖子中提取风险证据
        
        Returns:
            {
                "evidence": [RiskEvidence, ...],
                "risk_level": str,
                "confidence": float,
                "summary": str
            }
        """
        prompt = self._build_prompt(post_text)
        
        if self.model is None:
            # Mock mode for testing
            return self._mock_extract(post_text)
        
        # 实际模型推理
        response = self._generate(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, post_text: str) -> str:
        """构建完整提示词"""
        granularity_instruction = ""
        if self.granularity == 'phrase':
            granularity_instruction = "Extract concise phrases that indicate suicide risk."
        else:
            granularity_instruction = "Extract complete sentences that indicate suicide risk."
        
        return self.prompt_template.format(
            post_text=post_text,
            granularity_instruction=granularity_instruction
        )
    
    def _generate(self, prompt: str) -> str:
        """调用模型生成"""
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True, max_length=self.max_length)
        inputs = inputs.to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=self.max_length,
                temperature=self.temperature,
                do_sample=True,
                num_return_sequences=1
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # 移除prompt部分
        response = response[len(prompt):].strip()
        return response
    
    def _parse_response(self, response: str) -> Dict:
        """解析模型输出的JSON"""
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {response[:200]}")
        
        return {
            "evidence": [],
            "risk_level": "Unknown",
            "confidence": 0.0,
            "summary": ""
        }
    
    def _mock_extract(self, post_text: str) -> Dict:
        """Mock提取（用于测试）"""
        # 简单的关键词匹配模拟
        risk_keywords = {
            "suicide": ("Cognitions", 0.9),
            "kill myself": ("Cognitions", 0.95),
            "end it all": ("Cognitions", 0.9),
            "hopeless": ("Emotions", 0.85),
            "burden": ("Cognitions", 0.8),
            "pain": ("Emotions", 0.75),
            "depression": ("Mental Health", 0.8),
            "alone": ("Interpersonal", 0.7),
        }
        
        evidence = []
        post_lower = post_text.lower()
        
        for keyword, (dimension, confidence) in risk_keywords.items():
            if keyword in post_lower:
                start = post_lower.find(keyword)
                end = start + len(keyword)
                evidence.append({
                    "text": post_text[start:end],
                    "start_position": start,
                    "end_position": end,
                    "dimension": dimension,
                    "confidence": confidence,
                    "reasoning": f"Keyword '{keyword}' indicates {dimension.lower()} risk"
                })
        
        # 简单风险等级判定
        risk_level = "Low Risk"
        if len(evidence) >= 3:
            risk_level = "High Risk"
        elif len(evidence) >= 1:
            risk_level = "Moderate Risk"
        
        return {
            "evidence": evidence,
            "risk_level": risk_level,
            "confidence": min(0.5 + len(evidence) * 0.1, 0.95),
            "summary": f"Detected {len(evidence)} risk indicators. Risk level: {risk_level}"
        }


class EvidenceAligner:
    """
    证据对齐模块
    
    将LLM生成的证据片段与原始文本对齐
    """
    
    def __init__(self, config: Dict):
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        self.max_span_length = config.get('max_span_length', 500)
        self.nlp = None
        
    def load_spacy(self):
        """加载Spacy模型"""
        if self.nlp is not None:
            return
        
        try:
            import spacy
            spacy_model = self.config.get('spacy_model', 'en_core_web_md')
            self.nlp = spacy.load(spacy_model)
        except Exception as e:
            print(f"Warning: Could not load Spacy model: {e}")
    
    def match(self, generated_text: str, original_text: str) -> Optional[Dict]:
        """
        将LLM生成的文本匹配到原始文本
        
        Returns:
            {
                "matched_text": str,
                "start": int,
                "end": int,
                "similarity": float
            }
        """
        if not generated_text or not original_text:
            return None
        
        if self.nlp is None:
            # 简单的字符串匹配回退
            return self._simple_match(generated_text, original_text)
        
        # Spacy语义匹配
        best_match = self._semantic_match(generated_text, original_text)
        
        if best_match and best_match['similarity'] >= self.similarity_threshold:
            return best_match
        
        return None
    
    def _simple_match(self, generated: str, original: str) -> Optional[Dict]:
        """简单的字符串匹配（无Spacy时的回退）"""
        generated_lower = generated.lower().strip()
        original_lower = original.lower()
        
        if generated_lower in original_lower:
            start = original_lower.find(generated_lower)
            end = start + len(generated)
            return {
                "matched_text": original[start:end],
                "start": start,
                "end": end,
                "similarity": 1.0
            }
        
        # 尝试模糊匹配
        words = generated_lower.split()
        if len(words) >= 2:
            # 查找前两个词的位置
            search_pattern = ' '.join(words[:2])
            if search_pattern in original_lower:
                start = original_lower.find(search_pattern)
                # 扩展匹配到合理长度
                end = min(start + len(generated) + 20, len(original))
                return {
                    "matched_text": original[start:end],
                    "start": start,
                    "end": end,
                    "similarity": 0.8
                }
        
        return None
    
    def _semantic_match(self, phrase: str, text: str) -> Optional[Dict]:
        """使用Spacy进行语义匹配"""
        doc = self.nlp(text)
        phrase_doc = self.nlp(phrase)
        
        # 分句
        sentences = list(doc.sents)
        
        best_similarity = 0
        best_match = None
        
        for sent in sentences:
            similarity = sent.similarity(phrase_doc)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    "matched_text": sent.text,
                    "start": sent.start_char,
                    "end": sent.end_char,
                    "similarity": similarity
                }
        
        return best_match


class SuicideRiskExtractor:
    """
    自杀风险证据提取器主类
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 初始化模块
        self.inference = XinHaiInference(self.config)
        self.aligner = EvidenceAligner(self.config)
        
        # 加载模型
        if self.config.get('load_model', True):
            self.inference.load_model()
            self.aligner.load_spacy()
    
    def analyze_post(self, title: str = "", body: str = "") -> Dict:
        """
        分析单条帖子
        
        Args:
            title: 帖子标题（可选）
            body: 帖子正文
            
        Returns:
            分析结果字典
        """
        # 构建完整文本
        full_text = f"{title}\n\n{body}" if title else body
        
        # 1. LLM提取候选证据
        raw_result = self.inference.extract_evidence(full_text)
        
        # 2. 证据对齐
        aligned_evidence = []
        for ev in raw_result.get('evidence', []):
            match = self.aligner.match(ev.get('text', ''), full_text)
            if match:
                aligned_evidence.append(RiskEvidence(
                    text=match['matched_text'],
                    start_char=match['start'],
                    end_char=match['end'],
                    dimension=ev.get('dimension', 'Unknown'),
                    confidence=ev.get('confidence', 0.5),
                    reasoning=ev.get('reasoning', '')
                ))
        
        # 3. 后处理（去重、合并、排序）
        aligned_evidence = self._post_process_evidence(aligned_evidence)
        
        # 4. 构建结果
        risk_assessment = RiskAssessment(
            level=raw_result.get('risk_level', 'Unknown'),
            confidence=raw_result.get('confidence', 0.0),
            primary_concerns=raw_result.get('primary_concerns', []),
            protective_factors=raw_result.get('protective_factors', [])
        )
        
        result = {
            "risk_level": risk_assessment.level,
            "confidence": risk_assessment.confidence,
            "evidence_highlights": [
                {
                    "text": ev.text,
                    "start_char": ev.start_char,
                    "end_char": ev.end_char,
                    "dimension": ev.dimension,
                    "confidence": ev.confidence
                }
                for ev in aligned_evidence
            ],
            "summary": raw_result.get('summary', ''),
            "primary_concerns": risk_assessment.primary_concerns,
            "protective_factors": risk_assessment.protective_factors,
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "model": self.config.get('model_path', 'XinHai-6B'),
                "granularity": self.config.get('granularity', 'phrase')
            }
        }
        
        return result
    
    def analyze_user_posts(self, user_id: str, posts: List[Dict]) -> Dict:
        """
        分析同一用户的多条帖子
        
        Args:
            user_id: 用户ID
            posts: 帖子列表，每个帖子包含title, body, post_id等
            
        Returns:
            综合分析结果
        """
        all_evidence = []
        post_results = []
        
        for post in posts:
            result = self.analyze_post(
                title=post.get('title', ''),
                body=post['body']
            )
            post_results.append({
                "post_id": post.get('post_id'),
                "evidence": result['evidence_highlights']
            })
            all_evidence.extend(result['evidence_highlights'])
        
        # 生成综合摘要
        combined_summary = self._generate_combined_summary(all_evidence, len(posts))
        
        # 判定整体风险等级
        overall_risk = self._assess_overall_risk(all_evidence)
        
        return {
            "user_id": user_id,
            "num_posts": len(posts),
            "overall_risk_level": overall_risk,
            "posts": post_results,
            "all_evidence": all_evidence,
            "combined_summary": combined_summary,
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "model": self.config.get('model_path', 'XinHai-6B')
            }
        }
    
    def _post_process_evidence(self, evidence: List[RiskEvidence]) -> List[RiskEvidence]:
        """后处理：去重、合并、排序"""
        if not evidence:
            return []
        
        # 去重
        seen = set()
        unique = []
        for ev in evidence:
            key = ev.text.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(ev)
        
        # 按位置排序
        unique.sort(key=lambda x: x.start_char)
        
        # 合并重叠片段
        merged = self._merge_overlapping_spans(unique)
        
        return merged
    
    def _merge_overlapping_spans(self, spans: List[RiskEvidence]) -> List[RiskEvidence]:
        """合并重叠的文本片段"""
        if not spans:
            return []
        
        merged = [spans[0]]
        
        for current in spans[1:]:
            last = merged[-1]
            
            # 检查是否重叠
            if current.start_char <= last.end_char:
                # 合并
                last.end_char = max(last.end_char, current.end_char)
                last.text = last.text + current.text[last.end_char - current.start_char:]
                # 合并维度
                if current.dimension != last.dimension:
                    last.dimension = f"{last.dimension}, {current.dimension}"
                last.confidence = max(last.confidence, current.confidence)
            else:
                merged.append(current)
        
        return merged
    
    def _generate_combined_summary(self, evidence: List[Dict], num_posts: int) -> str:
        """生成多帖综合摘要"""
        if not evidence:
            return "No significant risk evidence detected."
        
        # 按维度统计
        dimension_counts = {}
        for ev in evidence:
            dim = ev.get('dimension', 'Unknown')
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1
        
        # 生成摘要
        summary_parts = [f"Analysis of {num_posts} posts identified {len(evidence)} risk indicators."]
        
        # 添加主要风险维度
        top_dimensions = sorted(dimension_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_dimensions:
            dim_str = ", ".join([f"{dim} ({count})" for dim, count in top_dimensions])
            summary_parts.append(f"Primary risk dimensions: {dim_str}.")
        
        return " ".join(summary_parts)
    
    def _assess_overall_risk(self, evidence: List[Dict]) -> str:
        """判定整体风险等级"""
        if not evidence:
            return "Low Risk"
        
        # 统计高置信度证据数量
        high_confidence = sum(1 for ev in evidence if ev.get('confidence', 0) >= 0.8)
        
        # 检查是否有行为维度证据（更严重）
        behaviour_evidence = sum(1 for ev in evidence if ev.get('dimension') == 'Behaviour')
        
        if high_confidence >= 3 or behaviour_evidence >= 1:
            return "High Risk"
        elif high_confidence >= 1:
            return "Moderate Risk"
        
        return "Low Risk"
    
    def batch_analyze(self, dataset: List[Dict], output_file: str = None) -> List[Dict]:
        """
        批量分析数据集
        
        Args:
            dataset: 用户帖子数据集
            output_file: 可选的输出文件路径
            
        Returns:
            分析结果列表
        """
        results = []
        
        for i, item in enumerate(dataset):
            print(f"Processing {i+1}/{len(dataset)}: {item.get('user_id', 'unknown')}")
            
            result = self.analyze_user_posts(
                user_id=item['user_id'],
                posts=item['posts']
            )
            results.append(result)
        
        # 保存结果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {output_file}")
        
        return results


# 使用示例
if __name__ == "__main__":
    # 配置
    config = {
        "model_path": "XinHai-6B",  # 实际模型路径
        "granularity": "phrase",  # "phrase" 或 "sentence"
        "language": "en",
        "load_model": False  # 测试时设为False使用mock模式
    }
    
    # 初始化提取器
    extractor = SuicideRiskExtractor(config)
    
    # 测试示例
    test_post = {
        "title": "I can't do this anymore",
        "body": "I've been struggling with depression for years. Nothing seems to help, not therapy, not medication. I feel like a burden to everyone around me. I just want the pain to stop."
    }
    
    result = extractor.analyze_post(
        title=test_post['title'],
        body=test_post['body']
    )
    
    print("\n=== Analysis Result ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
