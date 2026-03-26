# AutoCBT 框架实现参考

## 核心类设计

### 1. CounsellorAgent (咨询师智能体)

```python
class CounsellorAgent:
    """
    咨询师智能体 - 用户与监督者之间的智能中介
    """
    
    def __init__(self, model, memory_config, routing_config):
        self.model = model
        self.short_term_memory = []  # 短期记忆
        self.long_term_memory = ""    # 长期记忆摘要
        self.routing_strategy = routing_config
        
    def receive_user_message(self, message):
        """接收用户消息，存储到短期记忆"""
        self.short_term_memory.append({
            "role": "user",
            "content": message,
            "timestamp": time.now()
        })
        self._update_long_term_memory()
        
    def route_decision(self):
        """
        动态路由决策
        返回: routing_type, target_supervisors
        """
        prompt = self._build_routing_prompt()
        decision = self.model.generate(prompt)
        
        # 解析决策
        if "[ENDCAST]" in decision:
            return "ENDCAST", []
        elif "[UNICAST]" in decision:
            target = self._parse_target(decision)
            return "UNICAST", [target]
        elif "[MULTICAST]" in decision:
            targets = self._parse_targets(decision)
            return "MULTICAST", targets
        elif "[BROADCAST]" in decision:
            return "BROADCAST", self.all_supervisors
        else:
            return "LOOPBACK", []
    
    def draft_response(self):
        """起草回应草稿"""
        context = self._build_context()
        prompt = f"""基于以下咨询上下文，起草一个初步回应：
        
        用户消息：{context['user_message']}
        对话历史：{context['history']}
        长期记忆：{self.long_term_memory}
        
        请生成一个初步回应草稿，等待监督者建议。"""
        
        return self.model.generate(prompt)
    
    def learn_and_refine(self, draft, advices):
        """学习监督者建议并优化回应"""
        prompt = f"""基于监督者的建议优化回应：
        
        草稿：{draft}
        建议：{advices}
        
        请生成改进后的回应。"""
        
        refined = self.model.generate(prompt)
        self._store_learning(advices)  # 存储学习到的内容
        return refined
    
    def _build_routing_prompt(self):
        """构建路由决策提示词"""
        return f"""作为CBT咨询师，分析以下情况并决定路由策略：

用户最新消息：{self.short_term_memory[-1]}
对话历史摘要：{self.long_term_memory}

可选的路由策略：
- [ENDCAST]: 直接回应用户，结束当前处理
- [UNICAST:supervisor_name]: 咨询特定监督者
- [MULTICAST:sup1,sup2]: 咨询多个监督者
- [BROADCAST]: 咨询所有监督者
- [LOOPBACK]: 继续当前处理

请分析：
1. 用户当前的情绪状态
2. 是否存在认知扭曲需要识别
3. 是否需要特定专业建议

然后选择合适的路由策略。"""
```

### 2. SupervisorAgent (监督智能体)

```python
class SupervisorAgent:
    """
    监督智能体 - 基于特定CBT原则提供建议
    """
    
    def __init__(self, name, cbt_principle, model):
        self.name = name
        self.principle = cbt_principle  # CBT核心原则
        self.model = model
        self.short_term_memory = []
        
    def review_draft(self, draft, user_context):
        """
        审查咨询师的草稿并提供建议
        """
        prompt = self._build_review_prompt(draft, user_context)
        advice = self.model.generate(prompt)
        
        # 确保建议格式正确
        if not advice.startswith("Hello counsellor"):
            advice = f"Hello counsellor, {advice}"
            
        return advice
    
    def _build_review_prompt(self, draft, user_context):
        return f"""你是一位专业的CBT {self.principle} 监督者。

你的职责：基于{self.principle}原则审查咨询师草稿并提供改进建议。

用户背景：{user_context}

咨询师草稿：{draft}

请从以下角度分析：
{self._get_principle_guidelines()}

请以"Hello counsellor"开头，提供具体、可执行的建议。
不要直接生成给用户的回应，只提供改进建议。"""
    
    def _get_principle_guidelines(self):
        """获取该原则的指导方针"""
        guidelines = {
            "Validation and Empathy": """
            - 是否真正理解并共情用户的情绪？
            - 是否创造了安全的表达环境？
            - 是否避免了评判性语言？
            """,
            "Identify Key Thought": """
            - 是否识别出用户的认知扭曲？
            - 是否深入挖掘了扭曲信念？
            - 是否帮助用户意识到这些扭曲？
            """,
            "Pose Challenge": """
            - 是否提出了开放性问题？
            - 问题是否促进深度思考？
            - 是否引导用户反思扭曲信念？
            """,
            "Provide Strategy": """
            - 策略是否实用可操作？
            - 是否能解决用户当前问题？
            - 是否基于专业心理方法？
            """,
            "Encouragement": """
            - 是否鼓励用户采取行动？
            - 是否预见了可能的困难？
            - 是否对挫折提供了安慰？
            """
        }
        return guidelines.get(self.principle, "")
```

### 3. AutoCBTFramework (主框架)

```python
class AutoCBTFramework:
    """
    AutoCBT 主框架
    """
    
    def __init__(self, model="gpt-4", language="zh", temperature=0.98):
        self.model = model
        self.language = language
        self.temperature = temperature
        
        # 初始化咨询师
        self.counsellor = CounsellorAgent(
            model=model,
            memory_config={"short_term": 10, "long_term": True},
            routing_config="adaptive"
        )
        
        # 初始化5个监督者
        self.supervisors = {
            "empathy": SupervisorAgent("empathy", "Validation and Empathy", model),
            "identify": SupervisorAgent("identify", "Identify Key Thought", model),
            "challenge": SupervisorAgent("challenge", "Pose Challenge", model),
            "strategy": SupervisorAgent("strategy", "Provide Strategy", model),
            "encouragement": SupervisorAgent("encouragement", "Encouragement", model)
        }
        
        # 路由历史（防止循环）
        self.routing_history = []
        self.max_routing = 6  # 最多6次路由
        
    def consult(self, user_query):
        """
        主咨询流程
        """
        # 1. 接收用户消息
        self.counsellor.receive_user_message(user_query)
        
        # 2. 动态路由循环
        routing_count = 0
        current_draft = None
        
        while routing_count < self.max_routing:
            # 2.1 路由决策
            route_type, targets = self.counsellor.route_decision()
            
            # 2.2 处理路由
            if route_type == "ENDCAST":
                # 直接生成最终回应
                if current_draft:
                    return self._finalize_response(current_draft)
                else:
                    current_draft = self.counsellor.draft_response()
                    return self._finalize_response(current_draft)
                    
            elif route_type == "LOOPBACK":
                # 继续处理，生成草稿
                current_draft = self.counsellor.draft_response()
                
            elif route_type in ["UNICAST", "MULTICAST", "BROADCAST"]:
                # 咨询监督者
                if not current_draft:
                    current_draft = self.counsellor.draft_response()
                
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
                
                # 学习并优化
                current_draft = self.counsellor.learn_and_refine(
                    current_draft, 
                    advices
                )
            
            # 记录路由历史
            self.routing_history.append({
                "count": routing_count,
                "type": route_type,
                "targets": targets
            })
            routing_count += 1
        
        # 达到最大路由次数，强制结束
        return self._finalize_response(current_draft)
    
    def _finalize_response(self, draft):
        """生成最终回应"""
        # 可以在这里添加最后的润色
        return draft
    
    def configure_supervisors(self, enabled_supervisors):
        """配置启用的监督者"""
        for name in list(self.supervisors.keys()):
            if name not in enabled_supervisors:
                del self.supervisors[name]
    
    def detect_cognitive_distortion(self, user_message):
        """识别用户消息中的认知扭曲类型"""
        # 实现认知扭曲检测逻辑
        pass
```

## 拓扑结构

### 静态拓扑（默认）

```
        ┌─────────────┐
        │   用户      │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │  咨询师(a₀) │
        └──────┬──────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
   ┌─────┐ ┌─────┐ ┌─────┐
   │ S₁  │ │ S₂  │ │ S₃  │  ...
   │共情  │ │识别  │ │挑战  │
   └─────┘ └─────┘ └─────┘
```

### 动态拓扑（扩展）

允许运行时添加/移除监督者，根据用户类型调整拓扑结构。

## 记忆机制

### 短期记忆
- 存储最近的 N 条消息（默认10条）
- 用于即时上下文理解
- 每次咨询结束后可选择性清空

### 长期记忆
- 滑动窗口摘要
- 存储关键信息（用户主要问题、认知模式等）
- 跨咨询会话保持

## 路由冲突处理

### 1. 同时路由冲突
当用户消息和监督者响应同时出现时，优先结束会话。

### 2. 角色混淆
强制监督者以"Hello counsellor"开头，避免生成用户回应而非建议。

### 3. 路由循环
记录已访问的监督者，每个监督者最多访问一次。
