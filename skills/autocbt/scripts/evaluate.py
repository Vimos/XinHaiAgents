#!/usr/bin/env python3
"""
AutoCBT 评估脚本
基于论文中的6维度自动评估体系
"""

import json
import argparse
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class EvaluationResult:
    """评估结果数据类"""
    empathy: float
    identification: float
    reflection: float
    strategy: float
    encouragement: float
    relevance: float
    total: float
    comments: str = ""

class AutoCBTEvaluator:
    """
    AutoCBT 自动评估器
    
    使用LLM作为评估器，从6个维度评估咨询回应质量
    """
    
    def __init__(self, model="gpt-4o-mini", num_rounds=3):
        self.model = model
        self.num_rounds = num_rounds
        
    def evaluate(self, user_message: str, counsellor_response: str) -> EvaluationResult:
        """
        评估单个回应
        
        Args:
            user_message: 用户原始消息
            counsellor_response: 咨询师生成的回应
            
        Returns:
            EvaluationResult: 包含6个维度评分的结果
        """
        scores = []
        
        for _ in range(self.num_rounds):
            round_scores = self._evaluate_single_round(
                user_message, 
                counsellor_response
            )
            scores.append(round_scores)
        
        # 取多次评估的平均值
        avg_scores = self._average_scores(scores)
        
        return EvaluationResult(
            empathy=avg_scores['empathy'],
            identification=avg_scores['identification'],
            reflection=avg_scores['reflection'],
            strategy=avg_scores['strategy'],
            encouragement=avg_scores['encouragement'],
            relevance=avg_scores['relevance'],
            total=sum(avg_scores.values()),
            comments=avg_scores.get('comments', '')
        )
    
    def _evaluate_single_round(self, user_msg: str, response: str) -> Dict:
        """单次评估"""
        prompt = f"""基于CBT核心原则，评估以下咨询回应的质量。

【用户消息】
{user_msg}

【咨询师回应】
{response}

请从以下6个维度分别评分（1-7分，7分为最佳）：

1. Empathy (共情)
   - 1.1 是否正确理解了用户的意图？
   - 1.2 是否展示了尊重、理解和共情？
   - 1.3 是否创造了安全的表达环境？

2. Identification (识别)
   - 2.1 是否识别出用户的认知扭曲？
   - 2.2 是否深入挖掘了用户的扭曲信念？
   - 2.3 是否帮助用户意识到这些扭曲？

3. Reflection (反思)
   - 3.1 是否提出了与用户初始想法相关的问题？
   - 3.2 是否提出了促进深度思考的问题？
   - 3.3 是否提出了反映用户扭曲信念的问题？

4. Strategy (策略)
   - 4.1 提供的策略或见解是否实用？
   - 4.2 策略是否能解决用户当前问题？
   - 4.3 策略是否基于专业心理方法？

5. Encouragement (鼓励)
   - 5.1 是否鼓励用户采取行动？
   - 5.2 是否预见了用户可能遇到的困难？
   - 5.3 是否对挫折和挑战提供了安慰和鼓励？

6. Relevance (相关性)
   - 6.1 回应是否与用户问题高度相关？
   - 6.2 回应是否自然流畅？
   - 6.3 回应是否涵盖了用户的主要问题或担忧？

每个维度的3个子问题，每个子问题1-7分，然后取平均作为该维度得分。

请以JSON格式输出结果：
{{
    "empathy": 分数,
    "identification": 分数,
    "reflection": 分数,
    "strategy": 分数,
    "encouragement": 分数,
    "relevance": 分数,
    "comments": "简要评价"
}}"""

        # 这里应该调用LLM API，示例用模拟数据
        # 实际使用时替换为真实的LLM调用
        return self._mock_evaluate(prompt)
    
    def _mock_evaluate(self, prompt: str) -> Dict:
        """模拟评估（实际使用时替换为真实LLM调用）"""
        # 这里应该调用实际的LLM API
        # 示例返回一个合理的评分
        return {
            'empathy': 6.0,
            'identification': 5.5,
            'reflection': 5.0,
            'strategy': 6.0,
            'encouragement': 5.5,
            'relevance': 6.5,
            'comments': '回应整体良好，共情充分，策略实用'
        }
    
    def _average_scores(self, scores_list: List[Dict]) -> Dict:
        """计算多次评估的平均分"""
        result = {}
        keys = ['empathy', 'identification', 'reflection', 
                'strategy', 'encouragement', 'relevance']
        
        for key in keys:
            values = [s[key] for s in scores_list if key in s]
            result[key] = round(sum(values) / len(values), 2)
        
        # 合并comments
        comments = [s.get('comments', '') for s in scores_list]
        result['comments'] = ' | '.join(set(comments))
        
        return result
    
    def evaluate_batch(self, test_cases: List[Dict]) -> List[EvaluationResult]:
        """
        批量评估
        
        Args:
            test_cases: 测试用例列表，每个用例包含user_message和response
            
        Returns:
            List[EvaluationResult]: 评估结果列表
        """
        results = []
        for case in test_cases:
            result = self.evaluate(
                case['user_message'],
                case['response']
            )
            results.append(result)
        return results
    
    def compare_methods(self, user_msg: str, responses: Dict[str, str]) -> Dict:
        """
        对比不同方法的回应质量
        
        Args:
            user_msg: 用户消息
            responses: 各方法的回应，如 {'AutoCBT': '...', 'PromptCBT': '...'}
            
        Returns:
            对比结果
        """
        comparison = {}
        
        for method_name, response in responses.items():
            result = self.evaluate(user_msg, response)
            comparison[method_name] = {
                'scores': {
                    'empathy': result.empathy,
                    'identification': result.identification,
                    'reflection': result.reflection,
                    'strategy': result.strategy,
                    'encouragement': result.encouragement,
                    'relevance': result.relevance,
                    'total': result.total
                },
                'comments': result.comments
            }
        
        # 找出最佳方法
        best_method = max(comparison.keys(), 
                         key=lambda x: comparison[x]['scores']['total'])
        comparison['best_method'] = best_method
        
        return comparison


def load_test_data(filepath: str) -> List[Dict]:
    """加载测试数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_cases = []
    for sample in data.get('samples', []):
        test_cases.append({
            'id': sample['id'],
            'user_message': sample['question'],
            'reference_response': sample.get('answer', '')
        })
    
    return test_cases


def main():
    parser = argparse.ArgumentParser(description='AutoCBT 评估工具')
    parser.add_argument('--input', '-i', type=str, required=True,
                       help='测试数据文件路径')
    parser.add_argument('--method', '-m', type=str, default='autocbt',
                       help='评估的方法名称')
    parser.add_argument('--output', '-o', type=str, default='evaluation_results.json',
                       help='输出结果文件路径')
    parser.add_argument('--rounds', '-r', type=int, default=3,
                       help='每个样本的评估轮数')
    
    args = parser.parse_args()
    
    # 加载测试数据
    test_cases = load_test_data(args.input)
    print(f"加载了 {len(test_cases)} 个测试用例")
    
    # 初始化评估器
    evaluator = AutoCBTEvaluator(num_rounds=args.rounds)
    
    # 批量评估
    results = []
    for i, case in enumerate(test_cases):
        print(f"评估进度: {i+1}/{len(test_cases)}")
        
        # 这里应该调用实际的生成方法获取回应
        # 示例中假设回应已存在于case中
        response = case.get('generated_response', '')
        
        if response:
            result = evaluator.evaluate(case['user_message'], response)
            results.append({
                'id': case['id'],
                'method': args.method,
                'scores': {
                    'empathy': result.empathy,
                    'identification': result.identification,
                    'reflection': result.reflection,
                    'strategy': result.strategy,
                    'encouragement': result.encouragement,
                    'relevance': result.relevance,
                    'total': result.total
                },
                'comments': result.comments
            })
    
    # 计算平均分
    if results:
        avg_total = sum(r['scores']['total'] for r in results) / len(results)
        print(f"\n平均总分: {avg_total:.2f}")
        print(f"详细结果已保存至: {args.output}")
        
        # 保存结果
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                'method': args.method,
                'num_samples': len(results),
                'average_total': avg_total,
                'results': results
            }, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
