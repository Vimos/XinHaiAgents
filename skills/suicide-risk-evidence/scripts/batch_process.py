#!/usr/bin/env python3
"""
Suicide Risk Evidence Extractor - 批量处理脚本

支持从文件批量处理用户帖子，支持进度保存和恢复
"""

import json
import argparse
import os
from typing import List, Dict
from datetime import datetime
from pathlib import Path

from suicide_risk_extractor import SuicideRiskExtractor


class BatchProcessor:
    """
    批量处理器
    
    支持：
    - 批量处理数据集
    - 进度保存和恢复
    - 断点续传
    - 并行处理（可选）
    """
    
    def __init__(self, config: Dict, checkpoint_interval: int = 10):
        self.config = config
        self.checkpoint_interval = checkpoint_interval
        self.extractor = SuicideRiskExtractor(config)
        
    def process_file(
        self,
        input_file: str,
        output_file: str,
        resume: bool = True
    ) -> Dict:
        """
        处理整个文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            resume: 是否从检查点恢复
            
        Returns:
            处理统计信息
        """
        # 加载数据
        print(f"Loading data from {input_file}...")
        dataset = self._load_dataset(input_file)
        total = len(dataset)
        print(f"Total samples: {total}")
        
        # 检查是否有检查点
        checkpoint_file = f"{output_file}.checkpoint"
        processed_ids = set()
        results = []
        
        if resume and os.path.exists(checkpoint_file):
            print(f"Resuming from checkpoint: {checkpoint_file}")
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
                results = checkpoint_data.get('results', [])
                processed_ids = set(r['user_id'] for r in results)
                print(f"Already processed: {len(results)}/{total}")
        
        # 处理未完成的样本
        start_time = datetime.now()
        processed_count = len(results)
        
        for i, sample in enumerate(dataset):
            user_id = sample.get('user_id', f'unknown_{i}')
            
            # 跳过已处理的
            if user_id in processed_ids:
                continue
            
            print(f"\n[{processed_count+1}/{total}] Processing: {user_id}")
            
            try:
                # 处理样本
                result = self.extractor.analyze_user_posts(
                    user_id=user_id,
                    posts=sample.get('posts', [])
                )
                
                # 添加原始信息（可选）
                if self.config.get('include_original', False):
                    result['original'] = sample
                
                results.append(result)
                processed_count += 1
                
                # 保存检查点
                if processed_count % self.checkpoint_interval == 0:
                    self._save_checkpoint(checkpoint_file, results, processed_count, total)
                    
            except Exception as e:
                print(f"Error processing {user_id}: {e}")
                # 记录错误但继续处理
                results.append({
                    'user_id': user_id,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # 保存最终结果
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        final_output = {
            'metadata': {
                'input_file': input_file,
                'output_file': output_file,
                'total_samples': total,
                'processed_samples': processed_count,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'config': self.config
            },
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        # 删除检查点文件
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
        
        print(f"\n{'='*60}")
        print(f"Processing completed!")
        print(f"  Total: {total}")
        print(f"  Processed: {processed_count}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Avg: {duration/max(processed_count, 1):.2f}s/sample")
        print(f"  Output: {output_file}")
        print(f"{'='*60}")
        
        return final_output['metadata']
    
    def _load_dataset(self, filepath: str) -> List[Dict]:
        """加载数据集"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持多种格式
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'samples' in data:
                return data['samples']
            elif 'data' in data:
                return data['data']
            else:
                return [data]
        else:
            raise ValueError(f"Unsupported data format in {filepath}")
    
    def _save_checkpoint(self, checkpoint_file: str, results: List[Dict], processed: int, total: int):
        """保存检查点"""
        checkpoint = {
            'results': results,
            'processed': processed,
            'total': total,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        print(f"  Checkpoint saved: {processed}/{total}")
    
    def process_single_post(self, title: str, body: str, output_file: str = None) -> Dict:
        """
        处理单个帖子（用于快速测试）
        
        Args:
            title: 帖子标题
            body: 帖子正文
            output_file: 可选的输出文件
            
        Returns:
            分析结果
        """
        print("Analyzing post...")
        result = self.extractor.analyze_post(title=title, body=body)
        
        print("\n" + "="*60)
        print("ANALYSIS RESULT")
        print("="*60)
        print(f"Risk Level: {result['risk_level']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"\nEvidence Highlights ({len(result['evidence_highlights'])}):")
        
        for i, ev in enumerate(result['evidence_highlights'], 1):
            print(f"\n{i}. [{ev['dimension']}] {ev['text']}")
            print(f"   Position: {ev['start_char']}-{ev['end_char']}")
        
        print(f"\nSummary:\n{result['summary']}")
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nResult saved to: {output_file}")
        
        return result


def create_sample_dataset(output_file: str, num_samples: int = 5):
    """
    创建示例数据集（用于测试）
    
    Args:
        output_file: 输出文件路径
        num_samples: 样本数量
    """
    samples = [
        {
            "user_id": "user_001",
            "posts": [
                {
                    "post_id": "p001",
                    "title": "I can't do this anymore",
                    "body": "I've been struggling with depression for years. Nothing seems to help, not therapy, not medication. I feel like a burden to everyone around me. I just want the pain to stop."
                }
            ]
        },
        {
            "user_id": "user_002",
            "posts": [
                {
                    "post_id": "p002",
                    "title": "Feeling lost",
                    "body": "I don't know what to do with my life. I lost my job last month and my relationship just ended. I feel so alone and worthless."
                }
            ]
        },
        {
            "user_id": "user_003",
            "posts": [
                {
                    "post_id": "p003",
                    "title": "Just venting",
                    "body": "Things have been tough lately but I'm trying to stay positive. I have support from my family and I'm seeing a therapist. It's hard but I'm not giving up."
                }
            ]
        },
        {
            "user_id": "user_004",
            "posts": [
                {
                    "post_id": "p004",
                    "title": "Update",
                    "body": "I've been having thoughts about ending it all. I've started researching methods and I think I have a plan. Nobody would miss me anyway."
                }
            ]
        },
        {
            "user_id": "user_005",
            "posts": [
                {
                    "post_id": "p005a",
                    "title": "First post",
                    "body": "I'm not sure if I should post this, but I need to talk to someone. I've been feeling really down lately."
                },
                {
                    "post_id": "p005b",
                    "title": "Update: Things got worse",
                    "body": "I don't think I can keep going. I've lost hope that things will get better. I'm so tired of fighting."
                }
            ]
        }
    ]
    
    dataset = samples[:num_samples]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Sample dataset created: {output_file}")
    print(f"Total samples: {len(dataset)}")


def main():
    parser = argparse.ArgumentParser(
        description='Suicide Risk Evidence Extractor - Batch Processing'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 批量处理命令
    process_parser = subparsers.add_parser('process', help='Process dataset file')
    process_parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input dataset file (JSON)'
    )
    process_parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output file path'
    )
    process_parser.add_argument(
        '--model', '-m',
        type=str,
        default='XinHai-6B',
        help='Model path'
    )
    process_parser.add_argument(
        '--granularity', '-g',
        type=str,
        choices=['phrase', 'sentence'],
        default='phrase',
        help='Evidence extraction granularity'
    )
    process_parser.add_argument(
        '--checkpoint-interval', '-c',
        type=int,
        default=10,
        help='Checkpoint save interval'
    )
    process_parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Do not resume from checkpoint'
    )
    
    # 单帖处理命令
    single_parser = subparsers.add_parser('analyze', help='Analyze single post')
    single_parser.add_argument(
        '--title', '-t',
        type=str,
        default='',
        help='Post title'
    )
    single_parser.add_argument(
        '--body', '-b',
        type=str,
        required=True,
        help='Post body'
    )
    single_parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (optional)'
    )
    single_parser.add_argument(
        '--model', '-m',
        type=str,
        default='XinHai-6B',
        help='Model path'
    )
    
    # 创建示例数据集命令
    sample_parser = subparsers.add_parser('create-sample', help='Create sample dataset')
    sample_parser.add_argument(
        '--output', '-o',
        type=str,
        default='sample_dataset.json',
        help='Output file path'
    )
    sample_parser.add_argument(
        '--num-samples', '-n',
        type=int,
        default=5,
        help='Number of samples'
    )
    
    args = parser.parse_args()
    
    if args.command == 'process':
        # 批量处理
        config = {
            'model_path': args.model,
            'granularity': args.granularity,
            'load_model': False  # 实际使用时设为True
        }
        
        processor = BatchProcessor(config, checkpoint_interval=args.checkpoint_interval)
        processor.process_file(
            input_file=args.input,
            output_file=args.output,
            resume=not args.no_resume
        )
        
    elif args.command == 'analyze':
        # 单帖处理
        config = {
            'model_path': args.model,
            'load_model': False
        }
        
        processor = BatchProcessor(config)
        processor.process_single_post(
            title=args.title,
            body=args.body,
            output_file=args.output
        )
        
    elif args.command == 'create-sample':
        # 创建示例数据集
        create_sample_dataset(args.output, args.num_samples)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
