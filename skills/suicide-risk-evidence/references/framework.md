# Suicide Risk Evidence Extractor - 框架实现

## 核心类设计

### 1. SuicideRiskExtractor (主类)

```python
class SuicideRiskExtractor:
    """
    自杀风险证据提取器主类
    
    整合三个核心模块：
    1. XinHaiInference - LLM推理
    2. EvidenceAligner - 证据对齐
    3. SummaryGenerator - 摘要生成
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.inference = XinHaiInference(config)
        self.aligner = EvidenceAligner(config)
        self.summary_gen = SummaryGenerator(config)
        
    def analyze_post(self, title: str, body: str) -> Dict:
        """
        分析单条帖子
        
        Returns:
            {
                "risk_level": str,
                "evidence_highlights": List[Dict],
                "summary": str,
                "confidence": float
            }
        """
        # 1. 构建完整帖子文本
        full_text = f"{title}\n\n{body}" if title else body
        
        # 2. LLM提取候选证据
        raw_evidence = self.inference.extract_evidence(full_text)
        
        # 3. 证据对齐（匹配原文）
        aligned_evidence = []
        for ev in raw_evidence:
            match = self.aligner.match(ev['text'], full_text)
            if match:
                aligned_evidence.append({
                    "text": match['matched_text'],
                    "start_char": match['start'],
                    "end_char": match['end'],
                    "criteria": ev['criteria'],
                    "confidence": ev['confidence']
                })
        
        # 4. 生成摘要
        summary = self.summary_gen.generate(
            post_text=full_text,
            evidence_list=aligned_evidence
        )
        
        # 5. 判定风险等级
        risk_level = self._assess_risk_level(aligned_evidence)
        
        return {
            "risk_level": risk_level,
            "evidence_highlights": aligned_evidence,
            "summary": summary,
            "confidence": self._calculate_confidence(aligned_evidence)
        }
    
    def analyze_user_posts(self, user_id: str, posts: List[Dict]) -> Dict:
        """
        分析同一用户的多条帖子
        
        每条帖子单独提取证据，但生成单一综合摘要
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
        combined_summary = self.summary_gen.generate_combined(
            evidence_list=all_evidence,
            num_posts=len(posts)
        )
        
        return {
            "user_id": user_id,
            "risk_level": self._assess_risk_level(all_evidence),
            "posts": post_results,
            "combined_summary": combined_summary
        }
```

### 2. XinHaiInference (LLM推理模块)

```python
class XinHaiInference:
    """
    XinHai-6B 模型推理封装
    
    基于 ChatGLM3-6B 医疗/心理健康领域微调
    """
    
    def __init__(self, config: Dict):
        self.model_path = config['model_path']
        self.device = config.get('device', 'cuda')
        self.temperature = config.get('temperature', 0.3)
        self.max_length = config.get('max_length', 4096)
        
        # 加载模型
        self._load_model()
        
        # 加载提示词模板
        self.prompt_template = self._load_prompt_template()
        
    def _load_model(self):
        """加载 XinHai-6B 模型"""
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
    
    def _load_prompt_template(self) -> str:
        """加载 CoT + GPT-4优化提示词"""
        import json
        with open('assets/prompts/cot_gpt4_optimized.json', 'r') as f:
            template = json.load(f)
        return template['prompt']
    
    def extract_evidence(self, post_text: str) -> List[Dict]:
        """
        从帖子中提取风险证据
        
        Returns:
            [
                {
                    "text": "提取的文本片段",
                    "criteria": ["Emotions", "Cognitions"],
                    "confidence": 0.95
                }
            ]
        """
        # 构建提示词
        prompt = self._build_prompt(post_text)
        
        # LLM生成
        response = self._generate(prompt)
        
        # 解析JSON输出
        evidence_list = self._parse_response(response)
        
        return evidence_list
    
    def _build_prompt(self, post_text: str) -> str:
        """
        构建完整提示词
        
        包含：
        1. CoT 指令（6维度分析）
        2. GPT-4 优化结构
        3. One-shot JSON 示例
        """
        return f"""{self.prompt_template}

【用户帖子】
{post_text}

请分析上述帖子，识别与自杀风险相关的证据片段，以JSON格式输出：
{{
    "evidence": [
        {{
            "text": "提取的文本片段",
            "criteria": ["Emotions"],
            "reasoning": "为什么这是风险证据"
        }}
    ],
    "risk_assessment": "Low/Moderate/High Risk",
    "confidence": 0.85
}}"""
    
    def _generate(self, prompt: str) -> str:
        """调用模型生成"""
        inputs = self.tokenizer(prompt, return_tensors='pt')
        inputs = inputs.to(self.device)
        
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            temperature=self.temperature,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def _parse_response(self, response: str) -> List[Dict]:
        """解析模型输出的JSON"""
        import json
        import re
        
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data.get('evidence', [])
            except json.JSONDecodeError:
                # 解析失败时返回空列表
                return []
        return []
```

### 3. EvidenceAligner (证据对齐模块)

```python
class EvidenceAligner:
    """
    证据对齐模块
    
    将LLM生成的证据片段与原始文本对齐，
    解决LLM输出可能与原文表述不一致的问题
    """
    
    def __init__(self, config: Dict):
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        self.max_span_length = config.get('max_span_length', 500)
        
        # 加载Spacy模型
        import spacy
        self.nlp = spacy.load(config.get('spacy_model', 'en_core_web_md'))
        
    def match(self, generated_phrase: str, original_text: str) -> Dict:
        """
        将LLM生成的短语匹配到原始文本
        
        Args:
            generated_phrase: LLM生成的证据片段
            original_text: 原始帖子文本
            
        Returns:
            {
                "matched_text": "匹配到的原文片段",
                "start": 起始位置,
                "end": 结束位置,
                "similarity": 相似度分数
            }
        """
        # 阶段1：Spacy语义向量匹配
        best_match = self._semantic_match(generated_phrase, original_text)
        
        # 阶段2：正则修复
        if best_match and best_match['similarity'] < 1.0:
            best_match = self._regex_repair(best_match, original_text)
        
        # 验证相似度阈值
        if best_match and best_match['similarity'] >= self.similarity_threshold:
            return best_match
        
        return None
    
    def _semantic_match(self, phrase: str, text: str) -> Dict:
        """
        使用Spacy向量进行语义匹配
        
        流程：
        1. 将原文分句
        2. 计算每句与候选短语的向量相似度
        3. 返回最相似的句子
        """
        # 分句
        doc = self.nlp(text)
        sentences = list(doc.sents)
        
        # 计算候选短语向量
        phrase_doc = self.nlp(phrase)
        phrase_vector = phrase_doc.vector
        
        # 找最相似的句子
        best_similarity = 0
        best_sentence = None
        
        for sent in sentences:
            similarity = sent.similarity(phrase_doc)
            if similarity > best_similarity:
                best_similarity = similarity
                best_sentence = sent
        
        if best_sentence:
            return {
                "matched_text": best_sentence.text,
                "start": best_sentence.start_char,
                "end": best_sentence.end_char,
                "similarity": best_similarity
            }
        
        return None
    
    def _regex_repair(self, match: Dict, text: str) -> Dict:
        """
        使用正则表达式修复匹配结果
        
        处理：
        1. 不完整的词
        2. 标点符号边界
        3. 语义一致性检查
        """
        import re
        
        matched = match['matched_text']
        
        # 处理截断的词
        # 查找完整词边界
        pattern = re.escape(matched[:20]) + r'\w*'  # 使用前20字符作为锚点
        full_match = re.search(pattern, text)
        
        if full_match:
            # 扩展匹配到完整句子或合理边界
            start = max(0, full_match.start() - 20)
            end = min(len(text), full_match.end() + 20)
            
            # 调整到词边界
            while start > 0 and text[start].isalnum():
                start -= 1
            while end < len(text) and text[end-1].isalnum():
                end += 1
            
            match['matched_text'] = text[start:end].strip()
            match['start'] = start
            match['end'] = end
        
        return match
    
    def batch_match(self, phrases: List[str], text: str) -> List[Dict]:
        """批量匹配多个短语"""
        results = []
        for phrase in phrases:
            match = self.match(phrase, text)
            if match:
                results.append(match)
        return results
```

### 4. SummaryGenerator (摘要生成模块)

```python
class SummaryGenerator:
    """
    风险证据摘要生成器
    """
    
    def __init__(self, config: Dict):
        self.model = None  # 复用XinHaiInference
        self.language = config.get('output_language', 'en')
        
    def generate(self, post_text: str, evidence_list: List[Dict]) -> str:
        """
        为单条帖子生成风险证据摘要
        
        Args:
            post_text: 原始帖子文本
            evidence_list: 提取的证据列表
            
        Returns:
            风险摘要文本
        """
        # 构建提示词
        prompt = self._build_summary_prompt(post_text, evidence_list)
        
        # 生成摘要
        summary = self.model.generate(prompt)
        
        return summary
    
    def generate_combined(self, evidence_list: List[Dict], num_posts: int) -> str:
        """
        为多帖用户生成综合摘要
        
        Args:
            evidence_list: 所有帖子的证据汇总
            num_posts: 帖子数量
        """
        # 按维度聚合证据
        aggregated = self._aggregate_by_criteria(evidence_list)
        
        # 构建综合摘要提示词
        prompt = self._build_combined_prompt(aggregated, num_posts)
        
        summary = self.model.generate(prompt)
        
        return summary
    
    def _aggregate_by_criteria(self, evidence_list: List[Dict]) -> Dict:
        """按评估维度聚合证据"""
        aggregated = {
            "Emotions": [],
            "Cognitions": [],
            "Behaviour": [],
            "Interpersonal": [],
            "Mental Health": [],
            "Context": []
        }
        
        for ev in evidence_list:
            for criterion in ev.get('criteria', []):
                if criterion in aggregated:
                    aggregated[criterion].append(ev['text'])
        
        return aggregated
    
    def _build_summary_prompt(self, post_text: str, evidence_list: List[Dict]) -> str:
        """构建单帖摘要提示词"""
        evidence_text = "\n".join([
            f"- {ev['text']} [{', '.join(ev['criteria'])}]"
            for ev in evidence_list
        ])
        
        return f"""基于以下帖子和提取的风险证据，生成一段简洁的风险评估摘要。

【帖子内容】
{post_text}

【提取的风险证据】
{evidence_text}

请生成一段2-3句话的摘要，说明：
1. 用户的主要风险因素
2. 关键证据支持
3. 建议的风险等级判定依据

摘要："""
    
    def _build_combined_prompt(self, aggregated: Dict, num_posts: int) -> str:
        """构建多帖综合摘要提示词"""
        evidence_by_criteria = "\n\n".join([
            f"【{criterion}】\n" + "\n".join([f"- {text}" for text in texts])
            for criterion, texts in aggregated.items() if texts
        ])
        
        return f"""基于用户的{num_posts}条帖子，生成综合风险评估摘要。

【按维度聚合的风险证据】
{evidence_by_criteria}

请生成一段综合摘要，涵盖：
1. 整体风险态势
2. 主要风险维度
3. 风险变化趋势（如有多帖时间信息）
4. 建议的风险等级

综合摘要："""
```

## 数据处理流程

### 完整Pipeline

```python
def process_pipeline(post: Dict, config: Dict) -> Dict:
    """
    完整的处理流程
    """
    # 1. 初始化
    extractor = SuicideRiskExtractor(config)
    
    # 2. 证据提取
    result = extractor.analyze_post(
        title=post.get('title', ''),
        body=post['body']
    )
    
    # 3. 后处理
    # - 去重
    # - 合并重叠片段
    # - 排序
    result = post_process(result)
    
    return result

def post_process(result: Dict) -> Dict:
    """后处理：去重、合并、排序"""
    evidence = result['evidence_highlights']
    
    # 去重
    seen = set()
    unique = []
    for ev in evidence:
        key = ev['text'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(ev)
    
    # 合并重叠片段
    merged = merge_overlapping_spans(unique)
    
    # 按位置排序
    merged.sort(key=lambda x: x['start_char'])
    
    result['evidence_highlights'] = merged
    return result

def merge_overlapping_spans(spans: List[Dict]) -> List[Dict]:
    """合并重叠的文本片段"""
    if not spans:
        return []
    
    # 按起始位置排序
    sorted_spans = sorted(spans, key=lambda x: x['start_char'])
    
    merged = [sorted_spans[0]]
    
    for current in sorted_spans[1:]:
        last = merged[-1]
        
        # 检查是否重叠
        if current['start_char'] <= last['end_char']:
            # 合并
            last['end_char'] = max(last['end_char'], current['end_char'])
            last['text'] = last['text'] + current['text'][last['end_char']-current['start_char']:]
            # 合并criteria
            last['criteria'] = list(set(last['criteria'] + current['criteria']))
        else:
            merged.append(current)
    
    return merged
```

## 批处理优化

```python
class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config: Dict):
        self.extractor = SuicideRiskExtractor(config)
        self.batch_size = config.get('batch_size', 4)
        
    def process_dataset(self, dataset: List[Dict], output_file: str):
        """
        批量处理数据集
        
        Args:
            dataset: 用户帖子列表
            output_file: 输出文件路径
        """
        results = []
        
        for i in range(0, len(dataset), self.batch_size):
            batch = dataset[i:i+self.batch_size]
            
            for item in batch:
                result = self.extractor.analyze_user_posts(
                    user_id=item['user_id'],
                    posts=item['posts']
                )
                results.append(result)
            
            # 定期保存
            if i % 100 == 0:
                self._save_checkpoint(results, output_file)
        
        # 最终保存
        self._save_results(results, output_file)
        
    def _save_checkpoint(self, results: List[Dict], output_file: str):
        """保存检查点"""
        import json
        checkpoint_file = output_file + '.checkpoint'
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def _save_results(self, results: List[Dict], output_file: str):
        """保存最终结果"""
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
```
