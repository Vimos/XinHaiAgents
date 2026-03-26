#!/usr/bin/env python3
"""
AutoCBT 主框架实现
基于论文《AutoCBT: An Autonomous Multi-agent Framework for CBT》

核心架构：(a₀, S, T, Σ)
- a₀: 咨询师智能体
- S: 监督智能体集合
- T: 拓扑结构
- Σ: 路由策略
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    """消息数据类"""
    role: str  # "user", "counsellor", "supervisor"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class RoutingDecision:
    """路由决策结果"""
    strategy: str  # LOOPBACK, UNICAST, MULTICAST, BROADCAST, ENDCAST
    targets: List[str] = field(default_factory=list)
    reasoning: str = ""


class CounsellorAgent:
    """
    咨询师智能体 (a₀)
    
    作为用户与监督者之间的智能中介，负责：
    1. 接收用户消息
    2. 动态路由决策
    3. 起草回应
    4. 学习监督者建议并优化
    """
    
    def __init__(self, model, memory_config: Dict = None):
        self.model = model
        self.memory_config = memory_config or {
            "short_term_limit": 10,
            "enable_long_term": True
        }
        self.short_term_memory: List[Message] = []
        self.long_term_memory: str = ""
        
    def receive_user_message(self, message: str):
        """接收用户消息"""
        msg = Message(role="user", content=message)
        self.short_term_memory.append(msg)
        self._maintain_memory()
        
    def _maintain_memory(self):
        """维护记忆（短期记忆限制 + 长期记忆更新）"""
        # 限制短期记忆数量
        if len(self.short_term_memory) > self.memory_config["short_term_limit"]:
            # 将旧消息摘要到长期记忆
            old_messages = self.short_term_memory[:-self.memory_config["short_term_limit"]]
            self.short_term_memory = self.short_term_memory[-self.memory_config["short_term_limit"]:]
            
            if self.memory_config["enable_long_term"]:
                self._update_long_term_memory(old_messages)
    
    def _update_long_term_memory(self, messages: List[Message]):
        """更新长期记忆"""
        # 简化的摘要逻辑（实际可用LLM生成摘要）
        summary_parts = []
        for msg in messages:
            if msg.role == "user":
                summary_parts.append(f"用户提到: {msg.content[:50]}...")
        
        if summary_parts:
            self.long_term_memory += "\n" + "\n".join(summary_parts)
    
    def route_decision(self, available_supervisors: List[str]) -> RoutingDecision:
        """
        动态路由决策
        
        根据当前对话状态，决定下一步路由策略
        """
        # 构建上下文
        context = self._build_context()
        
        # 构建路由提示词
        prompt = self._build_routing_prompt(context, available_supervisors)
        
        # 调用模型获取决策（示例用简单规则代替）
        decision = self._make_routing_decision(context, available_supervisors)
        
        return decision
    
    def _build_context(self) -> Dict:
        """构建当前上下文"""
        user_messages = [m for m in self.short_term_memory if m.role == "user"]
        
        return {
            "latest_user_message": user_messages[-1].content if user_messages else "",
            "conversation_history": self._format_history(),
            "long_term_summary": self.long_term_memory[:500]  # 限制长度
        }
    
    def _format_history(self) -> str:
        """格式化对话历史"""
        recent = self.short_term_memory[-5:]  # 最近5条
        return "\n".join([f"{m.role}: {m.content[:100]}..." for m in recent])
    
    def _build_routing_prompt(self, context: Dict, supervisors: List[str]) -> str:
        """构建路由决策提示词"""
        return f"""作为CBT咨询师，分析当前咨询情况并决定下一步路由策略。

【用户最新消息】
{context['latest_user_message']}

【对话历史摘要】
{context['conversation_history']}

【长期记忆摘要】
{context['long_term_summary']}

【可用监督者】
{', '.join(supervisors)}

请决定路由策略：
- [ENDCAST]: 直接回应用户
- [UNICAST:name]: 咨询特定监督者
- [MULTICAST:n1,n2]: 咨询多个监督者
- [BROADCAST]: 咨询所有监督者
- [LOOPBACK]: 继续处理"""
    
    def _make_routing_decision(self, context: Dict, supervisors: List[str]) -> RoutingDecision:
        """
        做出路由决策（简化版规则）
        
        实际实现应使用LLM进行智能决策
        """
        user_msg = context['latest_user_message'].lower()
        
        # 简单的启发式规则
        if not user_msg or len(user_msg) < 10:
            return RoutingDecision("LOOPBACK", [], "用户输入太短，需要更多信息")
        
        # 首次咨询，需要全面评估
        if len([m for m in self.short_term_memory if m.role == "user"]) == 1:
            return RoutingDecision("BROADCAST", supervisors, "首次咨询，全面评估")
        
        # 检测关键词决定路由
        if any(word in user_msg for word in ['焦虑', '抑郁', 'anxiety', 'depression']):
            return RoutingDecision("MULTICAST", ['empathy', 'identify'], "情绪问题，需要共情和识别")
        
        if any(word in user_msg for word in ['怎么办', 'how', '建议', 'advice']):
            return RoutingDecision("UNICAST", ['strategy'], "用户寻求策略建议")
        
        # 默认直接回应
        return RoutingDecision("ENDCAST", [], "可以直接回应")
    
    def draft_response(self, target_supervisor: str = None) -> str:
        """起草回应草稿"""
        context = self._build_context()
        
        prompt = f"""作为CBT咨询师，基于以下信息起草回应：

【用户背景】
{context['long_term_summary']}

【用户当前消息】
{context['latest_user_message']}

【对话历史】
{context['conversation_history']}

请生成一个初步回应草稿。要求：
1. 共情用户的情绪
2. 识别可能的认知扭曲（如果有）
3. 提供温暖的建议
4. 鼓励用户采取行动"""

        # 实际应调用LLM生成回应
        # 这里返回一个示例草稿
        return f"我理解你现在的感受。{context['latest_user_message'][:30]}... 这种情况确实令人困扰。"
    
    def learn_and_refine(self, draft: str, advices: List[Dict]) -> str:
        """学习监督者建议并优化回应"""
        if not advices:
            return draft
        
        prompt = f"""基于监督者的建议优化回应。

【原始草稿】
{draft}

【监督者建议】
"""
        for advice in advices:
            prompt += f"\n来自 {advice['supervisor']}:\n{advice['advice']}\n"
        
        prompt += """\n请生成改进后的最终回应。要求：
1. 保持温暖和专业的语气
2. 吸收监督者的改进建议
3. 确保回应自然流畅
4. 符合CBT咨询的专业标准"""

        # 实际应调用LLM生成优化后的回应
        # 这里简单拼接建议
        refined = draft + "\n\n【已根据专业建议优化】"
        return refined
    
    def get_context(self) -> str:
        """获取当前上下文用于监督者审查"""
        context = self._build_context()
        return f"""用户最新消息：{context['latest_user_message']}
对话历史：{context['conversation_history']}
长期记忆：{context['long_term_summary']}"""


class SupervisorAgent:
    """
    监督智能体
    
    基于特定CBT原则审查回应并提供建议
    """
    
    def __init__(self, name: str, principle: str, model):
        self.name = name
        self.principle = principle
        self.model = model
        
    def review_draft(self, draft: str, user_context: str) -> str:
        """
        审查草稿并提供建议
        
        Args:
            draft: 咨询师生成的草稿
            user_context: 用户背景信息
            
        Returns:
            建议文本（以"Hello counsellor"开头）
        """
        prompt = f"""你是一位专注于"{self.principle}"的CBT督导专家。

【用户背景】
{user_context}

【咨询师草稿】
{draft}

请从"{self.principle}"角度分析，提供具体的改进建议。
以"Hello counsellor"开头，只提供建议，不直接生成给用户的回应。"""

        # 实际应调用LLM生成建议
        # 这里返回示例建议
        return f"Hello counsellor, 从{self.principle}角度，建议关注用户的情绪体验，并更温和地引导他们发现思维中的偏差。"


class AutoCBTFramework:
    """
    AutoCBT 主框架
    
    实现论文中的自主多智能体CBT系统
    """
    
    # 5个CBT核心原则
    DEFAULT_SUPERVISORS = {
        "empathy": "Validation and Empathy",
        "identify": "Identify Key Thought",
        "challenge": "Pose Challenge",
        "strategy": "Provide Strategy",
        "encouragement": "Encouragement"
    }
    
    def __init__(self, 
                 model: str = "gpt-4",
                 language: str = "zh",
                 temperature: float = 0.98,
                 max_routing: int = 6):
        """
        初始化AutoCBT框架
        
        Args:
            model: 使用的LLM模型
            language: 语言（"zh"或"en"）
            temperature: 生成温度
            max_routing: 最大路由次数
        """
        self.model = model
        self.language = language
        self.temperature = temperature
        self.max_routing = max_routing
        
        # 初始化咨询师
        self.counsellor = CounsellorAgent(
            model=model,
            memory_config={"short_term_limit": 10, "enable_long_term": True}
        )
        
        # 初始化监督者
        self.supervisors = {}
        for name, principle in self.DEFAULT_SUPERVISORS.items():
            self.supervisors[name] = SupervisorAgent(name, principle, model)
        
        # 路由历史
        self.routing_history: List[Dict] = []
        
    def consult(self, user_query: str) -> str:
        """
        主咨询流程
        
        Args:
            user_query: 用户咨询内容
            
        Returns:
            最终回应
        """
        # 1. 接收用户消息
        self.counsellor.receive_user_message(user_query)
        
        # 2. 路由循环
        routing_count = 0
        current_draft = None
        visited_supervisors = set()
        
        while routing_count < self.max_routing:
            # 2.1 获取可用监督者（排除已访问的）
            available = [
                name for name in self.supervisors.keys()
                if name not in visited_supervisors
            ]
            
            # 2.2 路由决策
            decision = self.counsellor.route_decision(available)
            
            # 2.3 处理路由
            if decision.strategy == "ENDCAST":
                # 生成最终回应
                if current_draft is None:
                    current_draft = self.counsellor.draft_response()
                return self._finalize_response(current_draft)
                
            elif decision.strategy == "LOOPBACK":
                # 继续处理，生成草稿
                current_draft = self.counsellor.draft_response()
                
            elif decision.strategy in ["UNICAST", "MULTICAST", "BROADCAST"]:
                # 咨询监督者
                if current_draft is None:
                    current_draft = self.counsellor.draft_response()
                
                # 确定目标监督者
                if decision.strategy == "BROADCAST":
                    targets = list(self.supervisors.keys())
                else:
                    targets = decision.targets
                
                # 收集建议
                advices = []
                for target_name in targets:
                    if target_name in self.supervisors:
                        supervisor = self.supervisors[target_name]
                        advice = supervisor.review_draft(
                            current_draft,
                            self.counsellor.get_context()
                        )
                        advices.append({
                            "supervisor": target_name,
                            "advice": advice
                        })
                        visited_supervisors.add(target_name)
                
                # 学习并优化
                current_draft = self.counsellor.learn_and_refine(
                    current_draft,
                    advices
                )
            
            # 记录路由历史
            self.routing_history.append({
                "count": routing_count,
                "strategy": decision.strategy,
                "targets": decision.targets,
                "reasoning": decision.reasoning
            })
            
            routing_count += 1
        
        # 达到最大路由次数，强制结束
        return self._finalize_response(current_draft)
    
    def _finalize_response(self, draft: str) -> str:
        """生成最终回应"""
        # 这里可以添加最后的润色
        # 例如：添加免责声明、资源链接等
        
        disclaimer = "\n\n---\n注：我是AI助手，提供基于CBT原则的支持性回应。如有严重心理困扰，建议寻求专业心理咨询师或医生的帮助。"
        
        return draft + disclaimer
    
    def configure_supervisors(self, enabled: List[str]):
        """
        配置启用的监督者
        
        Args:
            enabled: 启用的监督者名称列表
        """
        new_supervisors = {}
        for name in enabled:
            if name in self.DEFAULT_SUPERVISORS:
                principle = self.DEFAULT_SUPERVISORS[name]
                new_supervisors[name] = SupervisorAgent(name, principle, self.model)
        
        self.supervisors = new_supervisors
    
    def detect_cognitive_distortion(self, user_message: str) -> Dict:
        """
        识别用户消息中的认知扭曲
        
        Args:
            user_message: 用户消息
            
        Returns:
            识别结果
        """
        # 简化的关键词匹配（实际应用LLM进行分类）
        distortions = {
            "labeling": ["我一无是处", "我是个失败者", "我很差"],
            "catastrophizing": ["完了", "彻底", "永远", "不可能"],
            "overgeneralization": ["总是", "每次", "从来", "所有人"],
            "all_or_nothing": ["要么", "或者", "完美", "彻底失败"],
            "mind_reading": ["一定觉得", "肯定认为", "一定在想"],
        }
        
        detected = []
        user_lower = user_message.lower()
        
        for dist_type, keywords in distortions.items():
            for kw in keywords:
                if kw in user_lower:
                    detected.append({
                        "type": dist_type,
                        "keyword": kw,
                        "confidence": "medium"
                    })
                    break
        
        return {
            "has_distortion": len(detected) > 0,
            "distortions": detected
        }
    
    def consult_with_cd_detection(self, user_query: str, return_cd: bool = True) -> Dict:
        """
        带认知扭曲识别的咨询
        
        Args:
            user_query: 用户咨询内容
            return_cd: 是否返回认知扭曲识别结果
            
        Returns:
            包含回应和识别结果的字典
        """
        response = self.consult(user_query)
        
        result = {"response": response}
        
        if return_cd:
            cd_result = self.detect_cognitive_distortion(user_query)
            result["cognitive_distortion"] = cd_result
        
        return result
    
    def get_routing_history(self) -> List[Dict]:
        """获取路由历史"""
        return self.routing_history.copy()
    
    def reset_session(self):
        """重置会话状态"""
        self.counsellor = CounsellorAgent(
            model=self.model,
            memory_config={"short_term_limit": 10, "enable_long_term": True}
        )
        self.routing_history = []


# 使用示例
if __name__ == "__main__":
    # 初始化框架
    autocbt = AutoCBTFramework(
        model="gpt-4",
        language="zh",
        temperature=0.98
    )
    
    # 示例咨询
    test_queries = [
        "我最近工作压力大，总是很焦虑，感觉自己什么都做不好。",
        "我总觉得自己一无是处，没有人喜欢我。",
        "我和朋友吵架了，现在不知道该怎么办。"
    ]
    
    for query in test_queries:
        print("=" * 50)
        print(f"用户：{query}")
        print("-" * 50)
        
        # 带认知扭曲识别的咨询
        result = autocbt.consult_with_cd_detection(query)
        
        print(f"回应：{result['response'][:100]}...")
        print(f"认知扭曲识别：{result['cognitive_distortion']}")
        print(f"路由历史：{autocbt.get_routing_history()}")
        print()
        
        # 重置会话
        autocbt.reset_session()
